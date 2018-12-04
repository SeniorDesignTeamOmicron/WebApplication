from rest_framework import status
from rest_framework.response import Response
from logisteps.models import Location
from logisteps_api.serializer import LocationSerializer
from django.http import Http404
from rest_framework.views import APIView
from rest_framework import mixins
from rest_framework import generics

class LocationList(mixins.ListModelMixin,
                   mixins.CreateModelMixin,
                   generics.GenericAPIView):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer

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

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)

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

