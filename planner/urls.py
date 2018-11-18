from django.urls import include, path
from . import views

urlpatterns = [
    path('', views.home_view, name='planner-home'),

    path('destination/', include([
            path('', views.DestinationListView.as_view(),
                 name='destination-list'),

            path('add/', views.destination_create_combo,
                 name='destination-add-combo'),
            path('search/', views.DestinationSearchView.as_view(),
                 name='destination-search'),
            # ----- detail pages
            path('<int:pk>/', views.DestinationDetailView.as_view(),
                 name='destination-detail'),
            path('<int:pk>/edit/', views.DestinationUpdate.as_view(),
                 name='destination-edit'),
            path('<int:pk>/delete/', views.DestinationDelete.as_view(),
                 name='destination-delete'),
            # ------ links
            path('<int:dest_pk>/link/add/', views.destination_create_link,
                 name='destination-link-add'),
            path('<int:dest_pk>/link/<int:link_pk>/edit/', views.destination_edit_link,
                 name='destination-link-edit'),
            path('<int:dest_pk>/link/<int:link_pk>/delete/', views.destination_delete_link,
                 name='destination-link-delete'),

            # path('destination/add_combo/', views.destination_create_combo,
            #      name='destination-add-combo'),
    ])),
    # # provide another permutation of destination search, no name hook
    # path('destinations/search/', views.DestinationSearchView.as_view()),


    path('route/', include([
            path('', views.RouteListView.as_view(), name='route-list'),
            path('add/', views.route_create_combo,
                 name='route-add-combo'),

            path('<int:pk>/', views.RouteDetailView.as_view(),
                 name='route-detail'),
            # path('add_combo/', views.route_create_combo,
            #      name='route-add-combo'),
            path('<int:pk>/edit/', views.RouteUpdate.as_view(),
                 name='route-edit'),
            path('<int:pk>/delete/', views.RouteDelete.as_view(),
                 name='route-delete'),

            path('<int:route_pk>/link/add/', views.route_create_link,
                 name='route-link-add'),
            path('<int:route_pk>/link/<int:link_pk>/edit/',
                 views.route_edit_link, name='route-link-edit'),
            path('<int:route_pk>/link/<int:link_pk>/delete/',
                 views.route_delete_link, name='route-link-delete'),
    ])),

    # path('trailhead/', views.TrailheadListView.as_view(),
    #      name='trailhead-list'),
    path('trailhead/<int:pk>/', views.TrailheadDetailView.as_view(),
         name='trailhead-detail'),
    path('trailhead/add/', views.TrailheadCreate.as_view(),
         name='trailhead-add'),
    path('trailhead/<int:pk>/edit/', views.TrailheadUpdate.as_view(),
         name='trailhead-edit'),
    path('trailhead/<int:pk>/delete/', views.TrailheadDelete.as_view(),
         name='trailhead-delete'),

    # path('govbody/<int:pk>/', views.GoverningBodyDetailView.as_view(),
    #      name='govbody-detail'),
    # path('govbodies/', views.GoverningBodyListView.as_view(),
    #      name='govbody-list'),
    # path('govbody/add/', views.GoverningBodyCreate.as_view(),
    #      name='govbody-add'),
    # path('govbody/<int:pk>/edit/', views.GoverningBodyUpdate.as_view(),
    #      name='govbody-edit'),
    # path('govbody/<int:pk>/delete/', views.GoverningBodyDelete.as_view(),
    #      name='govbody-delete'),

    # path('jurisdiction/<int:pk>/', views.JurisdictionDetailView.as_view(),
    #      name='jurisdiction-detail'),
    # path('jurisdictions/', views.JurisdictionListView.as_view(),
    #      name='jurisdiction-list'),
    # path('jurisdiction/add/', views.JurisdictionCreate.as_view(),
    #      name='jurisdiction-add'),
    # path('jurisdiction/<int:pk>/edit/', views.JurisdictionUpdate.as_view(),
    #      name='jurisdiction-edit'),
    # path('jurisdiction/<int:pk>/delete/', views.JurisdictionDelete.as_view(),
    #      name='jurisdiction-delete'),

    path('profile/', views.profile_overview, name='profile-detail'),
    path('profile/edit/', views.profile_update, name='profile-update'),

    # Autocomplete helper views
    path('autocomplete/', include([
            path('destination/', views.DestinationAutocomplete.as_view(),
                 name='destination-autocomplete'),
            path('route/', views.RouteAutocomplete.as_view(),
                 name='route-autocomplete'),
            path('trailhead/', views.TrailheadAutocomplete.as_view(),
                 name='trailhead-autocomplete'),
    ])),

    # Permission denied view
    path('permission_denied', views.perm_denied, name='permission-denied'),
]
