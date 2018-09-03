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
    path('route/add/', views.RouteCreate.as_view(), name='route-add'),
    path('route/<int:pk>/edit/', views.RouteUpdate.as_view(), name='route-edit'),
    path('route/<int:pk>/delete/', views.RouteDelete.as_view(), name='route-delete'),

    path('trailheads/', views.TrailheadListView.as_view(), name='trailhead-list'),
    path('trailhead/<int:pk>/', views.TrailheadDetailView.as_view(), name='trailhead-detail'),
    path('trailhead/add/', views.TrailheadCreate.as_view(), name='trailhead-add'),
    path('trailhead/<int:pk>/edit/', views.TrailheadUpdate.as_view(), name='trailhead-edit'),
    path('trailhead/<int:pk>/delete/', views.TrailheadDelete.as_view(), name='trailhead-delete'),

    path('govbody/<int:pk>/', views.GoverningBodyDetailView.as_view(), name='govbody-detail'),
    path('govbodies/', views.GoverningBodyListView.as_view(), name='govbody-list'),
    path('govbody/add/', views.GoverningBodyCreate.as_view(), name='govbody-add'),
    path('govbody/<int:pk>/edit/', views.GoverningBodyUpdate.as_view(), name='govbody-edit'),
    path('govbody/<int:pk>/delete/', views.GoverningBodyDelete.as_view(), name='govbody-delete'),

    path('profile/', views.profile_overview, name='profile-detail'),
    path('profile/edit/', views.profile_update, name='profile-update'),
]
