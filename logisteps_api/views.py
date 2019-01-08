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
from utils.step_utils import getMostActiveHour, getLeastActiveHour, getInactiveTime, avgStepsPerHour

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

# class LocationList(APIView):
#     def get(self, request, format=None):
#         locations = Location.objects.all()
#         serializer = LocationSerializer(locations, many=True)
#         return Response(serializer.data)

#     def post(self, request, format=None):
#         serializer = LocationSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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
        
        """
        Optionally restricts the returned purchases to a given user,
        by filtering against a `username` query parameter in the URL.
        """
        queryset = Step.objects.all()
        query_date = self.request.query_params.get('date', None) #TODO Perform date validation

        if query_date is None:
            query_date = datetime.today()
        else:
            query_date = datetime.strptime(query_date, '%m-%d-%Y')

        logistepsUser = LogistepsUser.objects.get(user_id=self.request.user.id)

        if logistepsUser is not None:
            queryset = queryset.filter(user=logistepsUser.id,
                                       datetime__year=query_date.year,
                                       datetime__month=query_date.month,
                                       datetime__day=query_date.day)
        return queryset

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

class StepSummary(StepsListByDay):
    def summarize(self, request, *args, **kwargs):
        """This can be moved to a Mixin class."""
        # make sure the filters of the parent class get applied
        queryset = self.filter_queryset(self.get_queryset())
        logistepsUser = LogistepsUser.objects.get(user_id=self.request.user.id)

        steps = queryset.count()
        goal = logistepsUser.step_goal
        percent_complete = float(steps)/goal * 100

        most_active_hour = getMostActiveHour(queryset)
        least_active_hour = getLeastActiveHour(queryset)
        inactive_time = getInactiveTime(queryset)
        steps_per_hour = avgStepsPerHour(queryset, self.request.query_params.get('date', datetime.now().date()))

        # do statistics here, e.g.
        stats = {
            'steps': steps,
            'goal': goal,
            'percent': percent_complete,
            'least_active': {
                'hour': least_active_hour.get('datetime__hour'),
                'steps': least_active_hour.get('id__count')
            },
            'most_active': {
                'hour': most_active_hour.get('datetime__hour'),
                'steps': most_active_hour.get('id__count')
            },
            'inactive_time': inactive_time,
            'steps_per_hour': steps_per_hour
        }

        # not using a serializer here since it is already a 
        # form of serialization
        return Response(stats)

    def get(self, request, *args, **kwargs):
        return self.summarize(request, *args, **kwargs)


# class LocationDetail(APIView):
#     def get_object(self, pk):
#         try:
#             return Location.objects.get(pk=pk)
#         except Location.DoesNotExist:
#             raise Http404
        
#     def get(self, request, pk, format=None):
#         loc = self.get_object(pk)
#         serializer = LocationSerializer(loc)
#         return Response(serializer.data)
    
#     def put(self, request, pk, format=None):
#         loc = self.get_object(pk)
#         serializer = Location(loc, data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#     def delete(self, request, pk, format=None):
#         loc = self.get_object(pk)
#         loc.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)

