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
from utils.step_utils import getMostActiveHour, getLeastActiveHour, getInactiveTime, \
                             avgStepsPerHour, getStepsOnDate, getDateSummary, \
                             getStepCounts, getStepBreakdown, getPressureSnapshot

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

# class LocationList(mixins.ListModelMixin,
#                    mixins.CreateModelMixin,
#                    generics.GenericAPIView):
#     queryset = Location.objects.all()
#     serializer_class = LocationSerializer
#     permission_classes = (permissions.IsAuthenticatedOrReadOnly,) #Authenticated users: read-write; others: read-only

#     def perform_create(self, serializer):
#         serializer.save(owner=self.request.user)

#     def get(self, request, *args, **kwargs):
#         return self.list(request, *args, **kwargs)

#     def post(self, request, *args, **kwargs):
#         return self.create(request, *args, **kwargs)

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

class StepCount(generics.GenericAPIView):

    def get(self, request, *args, **kwards):
        start_date = request.query_params.get('start', None)
        end_date = request.query_params.get('end', None)
        today = datetime.today()

        if start_date is None and end_date is None:
            #Only return step count for today
            step_counts = getStepCounts(self.request.user, today, today)
            response = Response(step_counts, status=status.HTTP_200_OK)
        elif start_date is not None and end_date is not None:
            #client provided custom date range
            try:
                start_date = datetime.strptime(start_date, '%m-%d-%Y')
                end_date = datetime.strptime(end_date, '%m-%d-%Y')

                if start_date > end_date:
                    response = Response({'message': 'start date must come before end date'}, status=status.HTTP_400_BAD_REQUEST)
                elif start_date > today or end_date > today:
                    response = Response({'message': 'start and end date must not be in the future'}, status=status.HTTP_400_BAD_REQUEST)
                elif (end_date - start_date).days > 365:
                    response = Response({'message': 'date range must be less than a year'}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    step_counts = getStepCounts(self.request.user, start_date, end_date)
                    response = Response(step_counts, status=status.HTTP_200_OK)
            except:
                response = Response({'message': 'Invalid date format'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            response = Response({'message': 'Provide both date paremters or omit both'}, status=status.HTTP_400_BAD_REQUEST)

        return response

class StepsBreakdown(generics.GenericAPIView):
    """
        Endpoint should return an object breaking down steps, active time, and inactive time
        for the entire year, grouped according to the GET parameter. If no parameter is passed,
        the groupby term is defaulted to "weekly". Valid parameters are weekly and monthly
    """

    def get(self, request, *args, **kwards):
        groupby = request.query_params.get('groupby', 'weekly')

        if (groupby == 'weekly' or groupby == 'monthly') and len(request.query_params) == 1:
            step_breakdown = getStepBreakdown(self.request.user, groupby)
            response = Response(step_breakdown, status=status.HTTP_200_OK)
        else:
            response = Response({'message': 'valid groupby parameters are weekly or monthly'}, status=status.HTTP_400_BAD_REQUEST)

        return response

class PressureSnapshot(generics.GenericAPIView):
    """
        This endpoint should return an average pressure a user has placed on their shoes for 
        the past day, the past month, and the past year. This endpoint expects a GET parameter
        for the date, and defaults to the current date if none are provided.
    """

    def get(self, request, *args, **kwargs):
        query_date = request.query_params.get('date', None)

        if query_date is not None and datetime.strptime(query_date, "%m-%d-%Y") > datetime.today():
            response = Response({'message': 'date must not be in the future'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            try:
                query_date = datetime.today() if query_date is None else datetime.strptime(query_date, '%m-%d-%Y')

                pressure_snap = getPressureSnapshot(self.request.user, query_date)
                response = Response(pressure_snap, status=status.HTTP_200_OK)
            except:
                response = Response({'message': 'Invalid date format'}, status=status.HTTP_400_BAD_REQUEST)
        
        return response

class LocationList(mixins.ListModelMixin,
                   generics.GenericAPIView):
    # queryset = Location.objects.all()
    serializer_class = LocationSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,) #Authenticated users: read-write; others: read-only

    def get_queryset(self):
        steps = getStepsOnDate(self.request.user, self.request.query_params.get('date', datetime.today().strftime("%m-%d-%Y")))
        return Location.objects.all().filter(id__in=steps.values_list('location_id', flat=True))

    def get(self, request, *args, **kwargs):
        query_date = self.request.query_params.get('date', None)

        if query_date is not None and datetime.strptime(query_date, "%m-%d-%Y") > datetime.today():
            response = Response({'message': 'date must not be in the future'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            data = {
                'query_date': query_date,
                'locations': self.serializer_class(self.get_queryset(*args, **kwargs), many=True).data
            }
            response = Response(data, status=status.HTTP_200_OK)

        return response 