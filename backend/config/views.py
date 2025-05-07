from django.shortcuts import render

from rest_framework import generics, filters
from rest_framework.views import APIView
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.pagination import PageNumberPagination
from django.core.cache import cache
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from datetime import datetime, timedelta
import pytz
from django.utils.timezone import make_aware

from config import models
from config import serializers

class DefaultPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 1000


# @receiver(post_save, sender=models.Company)
# @receiver(post_delete, sender=models.Company)
# def invalidate_and_reload_company_cache(sender, instance, **kwargs):
#     # Invalidate the existing cache
#     cache.delete('companies')

#     # Set cache with a timeout of 3600 seconds (1 hour)
#     cache.set('companies', models.Company.objects.all(), timeout=3600)

# # Pre-load data into cache
# cache.get_or_set('companies', models.Company.objects.all(), timeout=3600)

class CompanyListCreate(generics.ListCreateAPIView):
    # queryset = cache.get('companies', [])
    queryset = models.Company.objects.all()
    serializer_class = serializers.CompanySerializer
    pagination_class = DefaultPagination  # Set pagination class
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]
    filterset_fields = ['name', 'code', 'created_at', 'updated_at']  # Fields for filtering
    search_fields = ['name', 'code', 'created_at', 'updated_at']  # Fields for searching
    ordering_fields = '__all__'

class CompanyRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = models.Company.objects.all()
    serializer_class = serializers.CompanySerializer
    lookup_url_kwarg = "id"


# @receiver(post_save, sender=models.Location)
# @receiver(post_delete, sender=models.Location)
# def invalidate_and_reload_location_cache(sender, instance, **kwargs):
#     # Invalidate the existing cache
#     cache.delete('locations')

#     # Set cache with a timeout of 3600 seconds (1 hour)
#     cache.set('locations', models.Location.objects.all(), timeout=3600)

# # Pre-load data into cache
# cache.get_or_set('locations', models.Location.objects.all(), timeout=3600)

class LocationListCreate(generics.ListCreateAPIView):
    # queryset = cache.get('locations', [])
    queryset = models.Location.objects.all()
    serializer_class = serializers.LocationSerializer
    pagination_class = DefaultPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]
    filterset_fields = ['name', 'code', 'created_at', 'updated_at'] 
    search_fields = ['name', 'code', 'created_at', 'updated_at'] 
    ordering_fields = '__all__'

class LocationRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = models.Location.objects.all()
    serializer_class = serializers.LocationSerializer
    lookup_url_kwarg = "id"


# @receiver(post_save, sender=models.Department)
# @receiver(post_delete, sender=models.Department)
# def invalidate_and_reload_department_cache(sender, instance, **kwargs):
#     # Invalidate the existing cache
#     cache.delete('departments')

#     # Set cache with a timeout of 3600 seconds (1 hour)
#     cache.set('departments', models.Department.objects.all(), timeout=3600)

# # Pre-load data into cache
# cache.get_or_set('departments', models.Department.objects.all(), timeout=3600)

class DepartmentListCreate(generics.ListCreateAPIView):
    # queryset = cache.get('departments', [])
    queryset = models.Department.objects.all()
    serializer_class = serializers.DepartmentSerializer
    pagination_class = DefaultPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]
    filterset_fields = ['name', 'code', 'created_at', 'updated_at'] 
    search_fields = ['name', 'code', 'created_at', 'updated_at'] 
    ordering_fields = '__all__'

class DepartmentRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = models.Department.objects.all()
    serializer_class = serializers.DepartmentSerializer
    lookup_url_kwarg = "id"


# @receiver(post_save, sender=models.Designation)
# @receiver(post_delete, sender=models.Designation)
# def invalidate_and_reload_designation_cache(sender, instance, **kwargs):
#     # Invalidate the existing cache
#     cache.delete('designations')

#     # Set cache with a timeout of 3600 seconds (1 hour)
#     cache.set('designations', models.Designation.objects.all(), timeout=3600)

# # Pre-load data into cache
# cache.get_or_set('designations', models.Designation.objects.all(), timeout=3600)

class DesignationListCreate(generics.ListCreateAPIView):
    # queryset = cache.get('designations', [])
    queryset = models.Designation.objects.all()
    serializer_class = serializers.DesignationSerializer
    pagination_class = DefaultPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]
    filterset_fields = ['name', 'code', 'created_at', 'updated_at'] 
    search_fields = ['name', 'code', 'created_at', 'updated_at'] 
    ordering_fields = '__all__'

class DesignationRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = models.Designation.objects.all()
    serializer_class = serializers.DesignationSerializer
    lookup_url_kwarg = "id"


# @receiver(post_save, sender=models.Division)
# @receiver(post_delete, sender=models.Division)
# def invalidate_and_reload_division_cache(sender, instance, **kwargs):
#     # Invalidate the existing cache
#     cache.delete('divisions')

#     # Set cache with a timeout of 3600 seconds (1 hour)
#     cache.set('divisions', models.Division.objects.all(), timeout=3600)

# # Pre-load data into cache
# cache.get_or_set('divisions', models.Division.objects.all(), timeout=3600)

class DivisionListCreate(generics.ListCreateAPIView):
    # queryset = cache.get('divisions', [])
    queryset = models.Division.objects.all()
    serializer_class = serializers.DivisionSerializer
    pagination_class = DefaultPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]
    filterset_fields = ['name', 'code', 'created_at', 'updated_at'] 
    search_fields = ['name', 'code', 'created_at', 'updated_at'] 
    ordering_fields = '__all__'

class DivisionRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = models.Division.objects.all()
    serializer_class = serializers.DivisionSerializer
    lookup_url_kwarg = "id"


# @receiver(post_save, sender=models.SubDivision)
# @receiver(post_delete, sender=models.SubDivision)
# def invalidate_and_reload_subdivision_cache(sender, instance, **kwargs):
#     # Invalidate the existing cache
#     cache.delete('subdivisions')

#     # Set cache with a timeout of 3600 seconds (1 hour)
#     cache.set('subdivisions', models.SubDivision.objects.all(), timeout=3600)

# # Pre-load data into cache
# cache.get_or_set('subdivisions', models.SubDivision.objects.all(), timeout=3600)

class SubDivisionListCreate(generics.ListCreateAPIView):
    # queryset = cache.get('subdivisions', [])
    queryset = models.SubDivision.objects.all()
    serializer_class = serializers.SubDivisionSerializer
    pagination_class = DefaultPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]
    filterset_fields = ['name', 'code', 'created_at', 'updated_at'] 
    search_fields = ['name', 'code', 'created_at', 'updated_at'] 
    ordering_fields = '__all__'

class SubDivisionRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = models.SubDivision.objects.all()
    serializer_class = serializers.SubDivisionSerializer
    lookup_url_kwarg = "id"


# @receiver(post_save, sender=models.Shopfloor)
# @receiver(post_delete, sender=models.Shopfloor)
# def invalidate_and_reload_shopfloor_cache(sender, instance, **kwargs):
#     # Invalidate the existing cache
#     cache.delete('shopfloors')

#     # Set cache with a timeout of 3600 seconds (1 hour)
#     cache.set('shopfloors', models.Shopfloor.objects.all(), timeout=3600)

# # Pre-load data into cache
# cache.get_or_set('shopfloors', models.Shopfloor.objects.all(), timeout=3600)

class ShopfloorListCreate(generics.ListCreateAPIView):
    # queryset = cache.get('shopfloors', [])
    queryset = models.Shopfloor.objects.all()
    serializer_class = serializers.ShopfloorSerializer
    pagination_class = DefaultPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]
    filterset_fields = ['name', 'code', 'created_at', 'updated_at'] 
    search_fields = ['name', 'code', 'created_at', 'updated_at'] 
    ordering_fields = '__all__'

class ShopfloorRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = models.Shopfloor.objects.all()
    serializer_class = serializers.ShopfloorSerializer
    lookup_url_kwarg = "id"

class ShiftListCreate(generics.ListCreateAPIView):
    queryset = models.Shift.objects.all()
    serializer_class = serializers.ShiftSerializer
    pagination_class = DefaultPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]
    filterset_fields = ['name', 'created_at', 'updated_at'] 
    search_fields = ['name', 'created_at', 'updated_at'] 
    ordering_fields = '__all__'

class ShiftRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = models.Shift.objects.all()
    serializer_class = serializers.ShiftSerializer
    lookup_url_kwarg = "id"


class LastUpdatedAtAPIView(APIView):
    def get(self, request):
        data = {}

        # Define a list of models to iterate over
        model_classes = [
            models.Company,
            models.Location,
            models.Department,
            models.Designation,
            models.Division,
            models.SubDivision,
            models.Shopfloor,
            models.Shift,
        ]

        # Iterate over each model to get the latest updated_at timestamp
        for model_class in model_classes:
            try:
                latest_object = model_class.objects.latest('updated_at')
                latest_update_time = latest_object.updated_at
                data[model_class.__name__] = latest_update_time
            except model_class.DoesNotExist:
                data[model_class.__name__] = None

        # Convert the current time to Indian Standard Time (IST)
        ist_timezone = pytz.timezone('Asia/Kolkata')
        current_time = datetime.now(ist_timezone)

        # Calculate the 'last updated at' time based on the current time and the latest update time from the model
        for key, value in data.items():
            if value:
                # Convert the value to Indian Standard Time (IST)
                value_ist = value.astimezone(ist_timezone)
                time_difference = current_time - value_ist

                # Calculate years, months, days, hours, and minutes in the time difference
                years = time_difference.days // 365
                months = (time_difference.days % 365) // 30
                weeks = (time_difference.days % 365) // 7
                days = time_difference.days % 7
                hours = time_difference.seconds // 3600
                minutes = (time_difference.seconds % 3600) // 60

                # Round off the time difference to the nearest minute, hour, day, month, or year
                if years > 1:
                    last_updated_at = f"Updated {years} years ago"
                elif 0 < years >= 1:
                    last_updated_at = f"Updated {years} year ago"
                elif months > 1:
                    last_updated_at = f"Updated {months} months ago"
                elif 0 < months >= 1:
                    last_updated_at = f"Updated {months} month ago"
                elif weeks > 0:
                    last_updated_at = f"Updated {weeks} weeks ago"
                elif 0 < weeks >= 1:
                    last_updated_at = f"Updated {weeks} week ago"
                elif days > 1:
                    last_updated_at = f"Updated {days} days ago"      
                elif 0 < days >= 1:
                    last_updated_at = f"Updated {days} day ago"                
                elif hours > 1:
                    last_updated_at = f"Updated {hours} hours ago"
                elif 0 < hours >= 1:
                    last_updated_at = f"Updated {hours} hour ago"
                elif minutes > 1:
                    last_updated_at = f"Updated {minutes} minutes ago"
                elif 0 < minutes >= 1:
                    last_updated_at = f"Updated {minutes} minute ago"
                else:
                    last_updated_at = "Updated just now"

                data[key] = last_updated_at
            else:
                data[key] = 'Never Updated'

        return Response(data)

class AttendanceCorrectionConfigListCreate(generics.ListCreateAPIView):
    queryset = models.AttendanceCorrectionConfig.objects.all()
    serializer_class = serializers.AttendanceCorrectionConfigSerializer
    pagination_class = None

    def list(self, request, *args, **kwargs):
        instance = self.queryset.first()
        if not instance:
            instance = models.AttendanceCorrectionConfig.objects.create()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

class AttendanceCorrectionConfigRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = models.AttendanceCorrectionConfig.objects.all()
    serializer_class = serializers.AttendanceCorrectionConfigSerializer

    def get_object(self):
        return self.queryset.first()