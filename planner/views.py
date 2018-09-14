from django.shortcuts import render, redirect
from django.views import generic
from django.urls import reverse, reverse_lazy
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from .models import Destination, Route, Trailhead, Profile, GoverningBody
from .models import Jurisdiction
from .forms import ProfileForm, RouteForm
from .PlannerUtils import constructURL
from .PlannerUtils import accessAPI
from .PlannerUtils import parseAPI
import json


# Create your views here.
@login_required
def home_view(request):
    return render(request, 'planner_home.html')


# -------- Destination views ------------------------
class DestinationListView(LoginRequiredMixin, generic.ListView):
    model = Destination


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
        distData = accessAPI.unpackDriveProperties(distRawData)

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
    fields = '__all__'


class TrailheadUpdate(LoginRequiredMixin, UpdateView):
    model = Trailhead
    fields = '__all__'


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

