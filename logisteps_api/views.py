from rest_framework import status
from rest_framework.response import Response
from logisteps.models import Location, Step, LogistepsUser
from logisteps_api.serializer import LocationSerializer, UserSerializer, LogistepsUserSerializer, StepSerializer
from django.http import Http404
from rest_framework.views import APIView
from rest_framework import mixins
from rest_framework import generics
from django.contrib.auth.models import User
from rest_framework import permissions
from logisteps_api.permissions import IsOwnerOrReadOnly, IsOwner, UserDetailPermissions
from django.db.models import Q
from datetime import datetime
from utils.step_utils import getMostActiveHour, getLeastActiveHour, getInactiveTime, avgStepsPerHour, getStepsOnDate, getDateSummary

class UserList(generics.ListAPIView):
    queryset = LogistepsUser.objects.all()
    serializer_class = LogistepsUserSerializer
    permission_classes = (permissions.IsAdminUser,)

class UserCreate(APIView):
    permission_classes = (permissions.AllowAny,)
   
    def post(self, request, format=None):
        serializer = LogistepsUserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserDetail(mixins.RetrieveModelMixin,
                     mixins.UpdateModelMixin,
                     mixins.DestroyModelMixin,
                     generics.GenericAPIView):
    lookup_field = 'username'
    queryset = User.objects.all()
    serializer_class = User
    permission_classes = (UserDetailPermissions,)

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)

class LogistepsUserDetail(mixins.RetrieveModelMixin,
                     mixins.UpdateModelMixin,
                     mixins.DestroyModelMixin,
                     generics.GenericAPIView):
    queryset = LogistepsUser.objects.all().select_related('user')
    serializer_class = LogistepsUserSerializer
    lookup_field = 'user__username'
    permission_classes = (UserDetailPermissions,)

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)

class StepList(mixins.CreateModelMixin,
               generics.GenericAPIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, format=None):
        context = {
            "request": self.request
        }

        serializer = StepSerializer(data=request.data, context=context, many=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LocationList(mixins.ListModelMixin,
                   mixins.CreateModelMixin,
                   generics.GenericAPIView):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,) #Authenticated users: read-write; others: read-only

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

class LocationDetail(mixins.RetrieveModelMixin,
                     mixins.UpdateModelMixin,
                     mixins.DestroyModelMixin,
                     generics.GenericAPIView):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                          IsOwnerOrReadOnly)

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)

#TODO: Combine with StepList view
class StepsListByDay(mixins.ListModelMixin,
                   generics.GenericAPIView):

    permission_classes = (permissions.AllowAny,)
    serializer_class = StepSerializer

    def get_queryset(self):
        return getStepsOnDate(self.request.user, self.request.query_params.get('date', None))
        
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

class StepSummary(StepsListByDay):

    def get(self, request, *args, **kwargs):
        stats = getDateSummary(request.user, request.query_params.get('date', datetime.now().date()))
        return Response(stats)

