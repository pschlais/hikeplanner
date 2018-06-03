from django.shortcuts import render
from django.views import generic
from django.urls import reverse
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from .models import Destination, Route, Trailhead, Profile
from .forms import ProfileForm
from .PlannerUtils import constructURL
from .PlannerUtils import accessAPI
import json

# Create your views here.
@login_required
def home_view(request):
    return render(request, 'planner_home.html')


# -------- Destination views ------------------------
class DestinationListView(LoginRequiredMixin, generic.ListView):
    model=Destination

class DestinationDetailView(LoginRequiredMixin, generic.DetailView):
    model=Destination

# ------- Route views ------------------------------
class RouteListView(LoginRequiredMixin, generic.ListView):
    model=Route

class RouteDetailView(LoginRequiredMixin, generic.DetailView):
    model=Route

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
        distData = accessAPI.unpackDriveProperties(distRawData)

        context['directions_api_status'] = distData["APIStatus"]
        context['directions_api_message'] = distData["dataStatus"]
        context['directions_api_duration'] = distData["duration"]["text"]
        context['directions_api_distance'] = distData["distance"]["text"]

        # # call NOAA forecast API
        # noaa_api_url = self.object.noaa_api_url
        # context['noaa_api_url'] = noaa_api_url
        # weather_raw_data = accessAPI.NOAA_API(noaa_api_url)
        # weather_data = weather_raw_data["properties"]["periods"][0]
        # context['noaa_weather_data'] = weather_data

        return context

# ------- User Profile views ----------------------
class UserProfileDetailView(LoginRequiredMixin, generic.DetailView):
    model=User

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
