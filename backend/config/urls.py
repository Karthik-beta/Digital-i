from django.urls import re_path
from config import views


urlpatterns = [

    re_path(r'^company/$', views.CompanyListCreate.as_view(), name='company-list-create'),
    re_path(r'^company/(?P<id>\d+)/$', views.CompanyRetrieveUpdateDestroy.as_view(), name='company-retrieve-update-destroy'),

    re_path(r'^location/$', views.LocationListCreate.as_view(), name='location-list-create'),
    re_path(r'^location/(?P<id>\d+)/$', views.LocationRetrieveUpdateDestroy.as_view(), name='location-retrieve-update-destroy'),

    re_path(r'^department/$', views.DepartmentListCreate.as_view(), name='department-list-create'),
    re_path(r'^department/(?P<id>\d+)/$', views.DepartmentRetrieveUpdateDestroy.as_view(), name='department-retrieve-update-destroy'),

    re_path(r'^designation/$', views.DesignationListCreate.as_view(), name='designation-list-create'),
    re_path(r'^designation/(?P<id>\d+)/$', views.DesignationRetrieveUpdateDestroy.as_view(), name='designation-retrieve-update-destroy'),

    re_path(r'^division/$', views.DivisionListCreate.as_view(), name='division-list-create'),
    re_path(r'^division/(?P<id>\d+)/$', views.DivisionRetrieveUpdateDestroy.as_view(), name='division-retrieve-update-destroy'),

    re_path(r'^subdivision/$', views.SubDivisionListCreate.as_view(), name='subdivision-list-create'),
    re_path(r'^subdivision/(?P<id>\d+)/$', views.SubDivisionRetrieveUpdateDestroy.as_view(), name='subdivision-retrieve-update-destroy'),

    re_path(r'^shopfloor/$', views.ShopfloorListCreate.as_view(), name='shopfloor-list-create'),
    re_path(r'^shopfloor/(?P<id>\d+)/$', views.ShopfloorRetrieveUpdateDestroy.as_view(), name='shopfloor-retrieve-update-destroy'),

    re_path(r'^shift/$', views.ShiftListCreate.as_view(), name='shift-list-create'),
    re_path(r'^shift/(?P<id>\d+)/$', views.ShiftRetrieveUpdateDestroy.as_view(), name='shift-retrieve-update-destroy'),

    re_path(r'^updated_at/$', views.LastUpdatedAtAPIView.as_view(), name='last-updated-at'),

    re_path(r'^auto_absence_config/$', views.AttendanceCorrectionConfigListCreate.as_view(), name='employee-list-create'),
    re_path(r'^auto_absence_config/(?P<id>\d+)/$', views.AttendanceCorrectionConfigRetrieveUpdateDestroy.as_view(), name='employee-retrieve-update-destroy'),
]