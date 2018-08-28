from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='planner-home'),

    path('destinations/', views.DestinationListView.as_view(), name='destination-list'),
    path('destination/<int:pk>/', views.DestinationDetailView.as_view(), name='destination-detail'),
    path('destination/add/', views.DestinationCreate.as_view(), name='destination-add'),
    path('destination/<int:pk>/edit/', views.DestinationUpdate.as_view(), name='destination-edit'),
    path('destination/<int:pk>/delete/', views.DestinationDelete.as_view(), name='destination-delete'),

    path('routes/', views.RouteListView.as_view(), name='route-list'),
    path('route/<int:pk>/', views.RouteDetailView.as_view(), name='route-detail'),

    path('trailheads/', views.TrailheadListView.as_view(), name='trailhead-list'),
    path('trailhead/<int:pk>/', views.TrailheadDetailView.as_view(), name='trailhead-detail'),
    path('trailhead/add/', views.TrailheadCreate.as_view(), name='trailhead-add'),
    path('trailhead/<int:pk>/edit/', views.TrailheadUpdate.as_view(), name='trailhead-edit'),
    path('trailhead/<int:pk>/delete/', views.TrailheadDelete.as_view(), name='trailhead-delete'),

    path('profile/', views.profile_overview, name='profile-detail'),
    path('profile/edit/', views.profile_update, name='profile-update'),
]
