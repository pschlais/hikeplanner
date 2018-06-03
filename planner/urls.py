from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='planner-home'),
    path('destinations/', views.DestinationListView.as_view(), name='destination-list'),
    path('destination/<int:pk>/', views.DestinationDetailView.as_view(), name='destination-detail'),
    path('routes/', views.RouteListView.as_view(), name='route-list'),
    path('route/<int:pk>/', views.RouteDetailView.as_view(), name='route-detail'),
    path('trailhead/<int:pk>/', views.TrailheadDetailView.as_view(), name='trailhead-detail'),
    path('profile/', views.profile_overview, name='profile-detail'),
    path('profile/edit/', views.profile_update, name='profile-update'),
]
