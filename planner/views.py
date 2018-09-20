from django.shortcuts import render, redirect
from django.views import generic
from django.urls import reverse, reverse_lazy
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from .models import Destination, Route, Trailhead, Profile, GoverningBody
from django.db.models import Q, F
from .models import Jurisdiction, DriveTimeMajorCity
from .forms import ProfileForm, RouteForm, TrailheadForm
from .PlannerUtils import constructURL
from .PlannerUtils import accessAPI
from .PlannerUtils import parseAPI
from .PlannerUtils import updateTable
import json
import math


# Create your views here.
@login_required
def home_view(request):
    return render(request, 'planner_home.html')


# -------- Destination views ------------------------
class DestinationListView(LoginRequiredMixin, generic.ListView):
    model = Destination

class DestinationSearchView(LoginRequiredMixin, generic.ListView):
    """
    This is the main destination search view. It finds destinations based on
    the location of the starting trailhead.
    It starts from the DTMC model, searching through foreign keys:
    DTMC --> Trailhead --> Route --> Destination
    """
    model = Route
    template_name = 'planner/destination_search_list.html'

    def get_queryset(self):

        valid_routes = Route.objects.filter(
                trailhead__drive_data__api_call_status=DriveTimeMajorCity.OK
                ).filter(
                trailhead__drive_data__majorcity=self.request.user.profile.nearest_city
                ).order_by(
                "trailhead__drive_data__drive_time"
                ).select_related(
                "destination"
                ).annotate(
                trailhead_drive_time=F("trailhead__drive_data__drive_time"),
                trailhead_drive_distance=F("trailhead__drive_data__drive_distance")
                )

        queryset = valid_routes

        return queryset


    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)

    #     for key, val in context.items():
    #         print("key: " + str(key), " val: " + str(val))
    #     # # create dictionary of trailhead times to user's major city
    #     # DTMC = DriveTimeMajorCity.objects.filter(trailhead__in=self.get_queryset(), majorcity=self.request.user.profile.nearest_city, api_call_status=DriveTimeMajorCity.OK)
    #     # drivetime_dict = {}
    #     # drivedistance_dict = {}
    #     # for entry in DTMC:
    #     #     drivetime_dict[entry.trailhead.id] = entry.drive_time_str
    #     #     drivedistance_dict[entry.trailhead.id] = entry.drive_distance_miles

    #     # context['drivetime_dict'] = drivetime_dict
    #     # context['drivedistance_dict'] = drivedistance_dict

    #     return context




class DestinationDetailView(LoginRequiredMixin, generic.DetailView):
    model = Destination

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)

        # call NOAA forecast API
        noaa_api_url = self.object.noaa_api_url
        context['noaa_api_url'] = noaa_api_url
        weather_raw_data = accessAPI.NOAA_API(noaa_api_url)
        weather_data_by_day = parseAPI.NOAA_by_day(weather_raw_data)
        context['weather_by_day'] = weather_data_by_day

        return context


class DestinationCreate(LoginRequiredMixin, CreateView):
    model = Destination
    fields = '__all__'


class DestinationUpdate(LoginRequiredMixin, UpdateView):
    model = Destination
    fields = '__all__'


class DestinationDelete(LoginRequiredMixin, DeleteView):
    model = Destination
    success_url = reverse_lazy('destination-list')


# ------- Route views ------------------------------
class RouteListView(LoginRequiredMixin, generic.ListView):
    model = Route


class RouteDetailView(LoginRequiredMixin, generic.DetailView):
    model = Route


class RouteCreate(CreateView):
    model = Route
    template_name = "planner/route_form.html"
    form_class = RouteForm

    def get(self, request, *args, **kwargs):
        # set the initial destination if specified in GET request
        if request.GET.get('destinationpk'):
            dest_pk = int(request.GET.get('destinationpk'))
            destination = Destination.objects.get(pk=dest_pk)

            form = self.form_class(initial={'destination': destination})

        else:  # generate blank form
            form = self.form_class()

        return render(request, self.template_name, {'form': form})


class RouteUpdate(LoginRequiredMixin, UpdateView):
    model = Route
    fields = '__all__'


class RouteDelete(LoginRequiredMixin, DeleteView):
    model = Route
    success_url = reverse_lazy('route-list')


# ------- Trailhead views --------------------------
class TrailheadDetailView(LoginRequiredMixin, generic.DetailView):
    model=Trailhead

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)

        # get Google Maps directions URL
        origin = self.request.user.profile.full_address
        destination = str(self.object.latitude) + "," + str(self.object.longitude)
        context['directions_external_url'] = constructURL.googleMapsDirectionsExternal(origin, destination)

        # create Google Distance Matrix API URL
        directions_api_url = constructURL.googleMapsDistanceAPI(origin, destination)
        context['directions_api_url'] = directions_api_url

        # call Google Distance Matrix API and parse results
        distRawData = accessAPI.googleMapsDistanceAPI(directions_api_url)
        distData = parseAPI.unpackDriveProperties(distRawData)

        context['directions_api_status'] = distData["APIStatus"]
        context['directions_api_message'] = distData["APIMessage"]
        context['directions_api_data_status'] = distData["dataStatus"]
        context['directions_api_data_status'] = distData["dataMessage"]
        context['directions_api_duration'] = distData["duration"]["text"]
        context['directions_api_distance'] = distData["distance"]["text"]

        # call NOAA forecast API
        noaa_api_url = self.object.noaa_api_url
        context['noaa_api_url'] = noaa_api_url
        weather_raw_data = accessAPI.NOAA_API(noaa_api_url)
        weather_data_by_day = parseAPI.NOAA_by_day(weather_raw_data)
        context['weather_by_day'] = weather_data_by_day

        # weather_data = weather_raw_data["properties"]["periods"][0]
        # context['noaa_weather_data'] = weather_data

        return context


class TrailheadListView(LoginRequiredMixin, generic.ListView):
    model = Trailhead


class TrailheadCreate(LoginRequiredMixin, CreateView):
    model = Trailhead
    form_class = TrailheadForm

    def form_valid(self, form):
        # save TH to database
        th = form.save()
        # trigger major city drive time table update functions
        updateTable.createNewDriveTimeEntries()
        # trigger calculation of new drive times into database
        updateTable.updateDriveTimeEntries()
        # redirect to newly-created trailhead detail page
        return HttpResponseRedirect(reverse('trailhead-detail',
                                            args=[str(th.pk)]))


class TrailheadUpdate(LoginRequiredMixin, UpdateView):
    model = Trailhead
    form_class = TrailheadForm

    def form_valid(self, form):
        # get old object lat/lon to check for changes
        lat_old = self.get_object().latitude
        lon_old = self.get_object().longitude
        # save TH to database
        th = form.save()
        # check if lat or lon have changed from update
        if (th.latitude != lat_old or th.longitude != lon_old):
            # set all instances with this trailhead as a new entry
            DriveTimeMajorCity.objects.filter(trailhead=self.get_object()).update(api_call_status=DriveTimeMajorCity.NEW_ITEM)
            # trigger calculation of new drive times into database
            updateTable.updateDriveTimeEntries()
        # redirect to newly-created trailhead detail page
        return HttpResponseRedirect(self.get_object().get_absolute_url())


class TrailheadDelete(LoginRequiredMixin, DeleteView):
    model = Trailhead
    success_url = reverse_lazy('trailhead-list')


# -------- Governing Body views --------------------
class GoverningBodyDetailView(LoginRequiredMixin, generic.DetailView):
    model = GoverningBody


class GoverningBodyListView(LoginRequiredMixin, generic.ListView):
    model = GoverningBody


class GoverningBodyCreate(LoginRequiredMixin, CreateView):
    model = GoverningBody
    fields = '__all__'


class GoverningBodyUpdate(LoginRequiredMixin, UpdateView):
    model = GoverningBody
    fields = '__all__'


class GoverningBodyDelete(LoginRequiredMixin, DeleteView):
    model = GoverningBody
    success_url = reverse_lazy('govbody-list')


# --------Jurisdiction views ---------------------
class JurisdictionDetailView(LoginRequiredMixin, generic.DetailView):
    model = Jurisdiction


class JurisdictionListView(LoginRequiredMixin, generic.ListView):
    model = Jurisdiction


class JurisdictionCreate(LoginRequiredMixin, CreateView):
    model = Jurisdiction
    fields = '__all__'


class JurisdictionUpdate(LoginRequiredMixin, UpdateView):
    model = Jurisdiction
    fields = '__all__'


class JurisdictionDelete(LoginRequiredMixin, DeleteView):
    model = Jurisdiction
    success_url = reverse_lazy('jurisdiction-list')


# ------- User Profile views ----------------------
class UserProfileDetailView(LoginRequiredMixin, generic.DetailView):
    model = User


@login_required
def profile_overview(request):
    return render(request, 'planner/profile_overview.html')


@login_required
def profile_update(request):
    # get profile data from database
    profile = Profile.objects.get(pk=request.user)
    # process form data if POST request
    if request.method == "POST":
        # create form instance and populate it with request:
        form = ProfileForm(request.POST, instance=profile)
        if form.is_valid():
            # save data
            form.save()
            return HttpResponseRedirect(reverse('profile-detail'))

    # create default form for GET or other method
    else:
        form = ProfileForm(instance=profile)

    return render(request, "planner/profile_update.html", {'form': form})

