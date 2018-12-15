from django.shortcuts import render, redirect
from django.views import generic
from django.urls import reverse, reverse_lazy
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.models import User
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from dal import autocomplete
from .models import Destination, Route, Trailhead, Profile, GoverningBody
from .models import Link, DestinationLink, RouteLink
from django.db.models import F
from .models import Jurisdiction, DriveTimeMajorCity
from .forms import UserForm, ProfileForm, TrailheadForm, DestinationSearchForm
from .forms import DestinationForm
from .forms import RouteForm, RouteInDestComboForm, RouteMainComboForm
from .forms import TrailheadComboForm
from .forms import LinkBaseForm
from .PlannerUtils import constructURL
from .PlannerUtils import accessAPI
from .PlannerUtils import parseAPI
from .PlannerUtils import updateTable
from .PlannerUtils import conversions
from .PlannerUtils import quickAPI


# Create your views here.
@login_required
def home_view(request):
    return render(request, 'planner_home.html')


def perm_denied(request):
    return render(request, 'planner/denied_permission.html')

# -------- Parent Autocomplete class ---------------
class BaseSelectAutocomplete(autocomplete.Select2QuerySetView):
    """
    Base class to create 'select' autocomplete views.
    Inheriting models MUST implement an instance attribute "self.model", which
    is a Model class defined in "models.py".
    """

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            # do not return results for non-logged in visitors
            return self.model.objects.none()

        # get all objects first
        qs = self.model.objects.all()

        # filter if values are present
        if self.q:
            qs = qs.filter(name__icontains=self.q)

        return qs


# -------- Destination views ------------------------
class DestinationListView(LoginRequiredMixin, generic.ListView):
    model = Destination

    def get_queryset(self):
        dest_name = self.request.GET.get("dest_name", "")
        if dest_name:
            return Destination.objects.filter(name__icontains=dest_name)
        else:
            return Destination.objects.all()



class DestinationSearchView(LoginRequiredMixin, generic.ListView):
    """
    This is the main destination search view. It finds destinations based on
    the location of the starting trailhead.
    It starts from the DTMC model, searching through foreign keys:
    DTMC --> Trailhead --> Route --> Destination
    """
    model = Route
    search_form_class = DestinationSearchForm
    template_name = 'planner/destination_search_list.html'

    def get_queryset(self):

        # Get base set of routes before user filters (routes with valid
        # drive times from the user's selected closest major city)

        # set up base query for Route object
        base_query = {
            "trailhead__drive_data__api_call_status": DriveTimeMajorCity.OK,
            "trailhead__drive_data__majorcity": self.request.user.profile.nearest_city,
            }

        # compile all query filters based on user input
        all_query = self._get_all_filter_kwargs(base_query)

        # get queryset in single filter request to ensure ManyToMany are
        # occuring at the same time as "AND" requests:
        # https://docs.djangoproject.com/en/2.1/topics/db/queries/#spanning-multi-valued-relationships
        valid_routes = Route.objects.filter(**all_query)

        # # ----- Order data by increasing drive time ---------
        valid_routes = valid_routes.order_by("trailhead__drive_data__drive_time")
        # select related (prefetch) destination data, and annotate data
        valid_routes = valid_routes.select_related("destination").annotate(
                trailhead_drive_time=F("trailhead__drive_data__drive_time"),
                trailhead_drive_distance=F("trailhead__drive_data__drive_distance")
                )

        # return final queryset
        queryset = valid_routes

        return queryset

    def _get_all_filter_kwargs(self, base_kwargs=None):
        """
        Utility function to get user filter GET parameters and return as dict
        for kwarg inputs to QuerySet.filter(). Adds them to input dict

        INPUTS:
        base_kwargs [dict] (OPTIONAL) --> base QuerySet to add to. Otherwise creates a new dictionary.

        OUTPUT:
        dict --> All QuerySet filers to apply, to be unpacked with **
        """
        if base_kwargs is None:
            out_dict = {}
        else:
            out_dict = base_kwargs

        for param in self.request.GET:
            value = self.request.GET[param]
            # only search on non-empty parameters from form request
            if value != "":
                # apply applicable filters based on parameter
                # print("filter param: {0}, value: {1}".format(param, value))
                if param == "dest_name":
                    out_dict["destination__name__icontains"] = value
                elif param == "min_length":
                    out_dict["total_distance__gte"] = float(value)
                elif param == "max_length":
                    out_dict["total_distance__lte"] = float(value)
                elif param == "min_gain":
                    out_dict["gain__gte"] = float(value)
                elif param == "max_gain":
                    out_dict["gain__lte"] = float(value)
                elif param == "min_class":
                    out_dict["class_rating__gte"] = int(value)
                elif param == "max_class":
                    out_dict["class_rating__lte"] = int(value)
                elif param == "max_drive_distance":
                    out_dict["trailhead__drive_data__drive_distance__lte"] = conversions.miles_to_m(float(value))
                elif param == "max_drive_time":
                    # Template filter truncates the minute level, so set cutoff of the database search at the next minute
                    out_dict["trailhead__drive_data__drive_time__lte"] = conversions.min_to_sec(float(value)+1)
                elif param == "dest_type":
                    out_dict["destination__dest_type__exact"] = value
                elif param == "path_seq":
                    out_dict["path_seq__exact"] = value

        return out_dict

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search_form"] = self.search_form_class(self.request.GET)

        return context


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

        # # get sunrise and sunset times
        # sunrise_api_url = constructURL.sunriseSunsetAPI(
        #                     self.object.latitude, self.object.longitude)
        # api_response = accessAPI.sunriseSunset_API(sunrise_api_url)
        # context['sun_data'] = parseAPI.sunrise_sunset_properties(api_response)
        context['sun_data'] = quickAPI.sunTimeData(self.object.latitude, self.object.longitude)

        # get links
        context['public_links'] = DestinationLink.objects.filter(owner_model=self.object, link_type=Link.PUBLIC)
        context['private_links'] = DestinationLink.objects.filter(owner_model=self.object, link_type=Link.PRIVATE, user=self.request.user)

        return context


class DestinationCreate(LoginRequiredMixin, PermissionRequiredMixin,
                        CreateView):
    model = Destination
    fields = '__all__'
    permission_required = "destination.can_add"


@login_required
@permission_required("destination.can_add")
def destination_create_combo(request):
    template = "planner/destination_combo_create.html"
    return _destination_route_trailhead_create_combo(request, True, template)


@login_required
def _destination_route_trailhead_create_combo(request, useDestForm, template):
    """
    # request is passed by the URL route
    # useDestForm (bool) - if Destination form should be included in the view
    # template (str) - django HTML template to render
    """
    if useDestForm:
        # use route form that does not include the destination field
        route_form_class = RouteInDestComboForm
    else:
        # use a route form that requires a destination field input
        route_form_class = RouteMainComboForm

    if request.POST:
        # default
        forms_valid = True
        add_trailhead = (request.POST.get("add_trailhead") == "Yes")
        print("add trailhead: " + str(add_trailhead))

        if useDestForm:
            # check destination form
            dest_form = DestinationForm(request.POST, prefix="dest")
            forms_valid = forms_valid and dest_form.is_valid()

        # check route and trailhead forms
        if not add_trailhead:
            route_form = route_form_class(True, request.POST, prefix="route")
            forms_valid = forms_valid and route_form.is_valid()
        else:  # add new trailhead
            route_form = route_form_class(False, request.POST, prefix="route")
            trailhead_form = TrailheadComboForm(True, request.POST, prefix="th")
            forms_valid = forms_valid and route_form.is_valid() and trailhead_form.is_valid()

        if forms_valid:

            if useDestForm:
                # save destination
                new_dest = dest_form.save()

            # set up route, then populate with destination and TH objects as
            # applicable
            new_route = route_form.save(commit=False)

            if useDestForm:
                new_route.destination = new_dest

            # save trailhead
            if add_trailhead:
                new_th = trailhead_form.save()
                # add new trailhead to route
                new_route.trailhead = new_th
                # trigger major city drive time table row create function
                updateTable.createNewDriveTimeEntries()
                # trigger calculation of new drive times into database
                updateTable.updateDriveTimeEntries(origin_type="trailhead")

            # if using existing trailhead, already in form object from request
            new_route.save()

            if useDestForm:
                # redirect to newly created destination page
                return redirect(new_dest.get_absolute_url())
            else:
                # redirect to newly created route page
                return redirect(new_route.get_absolute_url())

        else:  # forms not valid, return populated forms
            # dest_form already created and validation errors included
            # route_form needs to reset
            route_form.reset_default_required_fields()
            # trailhead_form needs to be reset. If a new trailhead wasn't
            # requested by the route, send back an empty TH form
            if add_trailhead:
                trailhead_form.reset_default_required_fields()
            else:
                trailhead_form = TrailheadComboForm(False, prefix="th")

    else:
        # serve empty forms
        if useDestForm:
            dest_form = DestinationForm(prefix="dest")

        # if this is a primary route create view and a predefined destination
        # pk is provided in the GET request, pre-populate the route form
        if not useDestForm and request.GET and request.GET.get('destinationpk'):
                dest_pk = int(request.GET.get('destinationpk'))
                init_destination = Destination.objects.get(pk=dest_pk)
                route_form = route_form_class(False, prefix="route",
                                 initial={'destination': init_destination})
        else:
            # empty route form
            route_form = route_form_class(False, prefix="route")

        # create empty trailhead form
        trailhead_form = TrailheadComboForm(False, prefix="th")

    # get context data
    context_dict = {'route_form': route_form, 'trailhead_form': trailhead_form}

    if useDestForm:
        context_dict['dest_form'] = dest_form

    return render(request, template, context_dict)


class DestinationUpdate(LoginRequiredMixin, PermissionRequiredMixin,
                        UpdateView):
    model = Destination
    fields = '__all__'
    permission_required = "destination.can_change"


class DestinationDelete(LoginRequiredMixin, PermissionRequiredMixin,
                        DeleteView):
    model = Destination
    success_url = reverse_lazy('destination-list')
    permission_required = "destination.can_delete"


# Autocomplete query view
class DestinationAutocomplete(BaseSelectAutocomplete):
    model = Destination


# ------- Route views ------------------------------
class RouteListView(LoginRequiredMixin, generic.ListView):
    model = Route

    def get_queryset(self):
        route_name = self.request.GET.get("route_name", "")
        if route_name:
            return Route.objects.filter(name__icontains=route_name)
        else:
            return Route.objects.all()


class RouteDetailView(LoginRequiredMixin, generic.DetailView):
    model = Route

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)

        # get Google Maps directions URL
        origin = self.request.user.profile.full_address
        destination = (str(self.object.trailhead.latitude) + ","
                       + str(self.object.trailhead.longitude))

        context['directions_external_url'] = constructURL.googleMapsDirectionsExternal(origin, destination)

        # call NOAA forecast API
        noaa_api_url = self.object.destination.noaa_api_url
        context['noaa_api_url'] = noaa_api_url
        weather_raw_data = accessAPI.NOAA_API(noaa_api_url)
        weather_data_by_day = parseAPI.NOAA_by_day(weather_raw_data)
        context['weather_by_day'] = weather_data_by_day

        # get generic drive time data
        if (self.request.user.is_authenticated
            and self.request.user.profile.nearest_city is not None):

            mc = self.request.user.profile.nearest_city
            try:
                drive_obj = DriveTimeMajorCity.objects.get(
                            trailhead=self.object.trailhead,
                            majorcity=mc,
                            api_call_status=DriveTimeMajorCity.OK)
            except DriveTimeMajorCity.DoesNotExist:
                context['general_drive_flag'] = False
            else:
                context['general_drive_flag'] = True
                context['general_drive_time'] = drive_obj.drive_time_str
                context['general_drive_dist'] = drive_obj.drive_distance_miles
        else:
            context['general_drive_flag'] = False

        # get links
        context['public_links'] = RouteLink.objects.filter(owner_model=self.object, link_type=Link.PUBLIC)
        context['private_links'] = RouteLink.objects.filter(owner_model=self.object, link_type=Link.PRIVATE, user=self.request.user)

        return context


class RouteCreate(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Route
    fields = '__all__'
    permission_required = 'route.can_add'
    # template_name = "planner/route_form.html"
    # form_class = RouteForm

    def get_form_kwargs(self):
        # set the initial destination if specified in GET request
        if self.request.GET.get('destinationpk'):
            dest_pk = int(self.request.GET.get('destinationpk'))
            destination = Destination.objects.get(pk=dest_pk)
            self.initial.update({'destination': destination})

        # get call superclass function
        kwargs = super().get_form_kwargs()

        return kwargs

@login_required
@permission_required("route.can_add")
def route_create_combo(request):
    template = "planner/route_combo_create.html"
    return _destination_route_trailhead_create_combo(request, False, template)


class RouteUpdate(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Route
    form_class = RouteForm
    permission_required = 'route.can_change'


class RouteDelete(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Route
    success_url = reverse_lazy('route-list')
    permission_required = 'route.can_delete'


# Autocomplete query view
class RouteAutocomplete(BaseSelectAutocomplete):
    model = Route


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

        # get generic drive time data
        if (self.request.user.is_authenticated
            and self.request.user.profile.nearest_city is not None):

            mc = self.request.user.profile.nearest_city
            try:
                drive_obj = DriveTimeMajorCity.objects.get(
                            trailhead=self.object,
                            majorcity=mc,
                            api_call_status=DriveTimeMajorCity.OK)
            except DriveTimeMajorCity.DoesNotExist:
                context['general_drive_flag'] = False
            else:
                context['general_drive_flag'] = True
                context['general_drive_time'] = drive_obj.drive_time_str
                context['general_drive_dist'] = drive_obj.drive_distance_miles
        else:
            context['general_drive_flag'] = False

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


class TrailheadCreate(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Trailhead
    form_class = TrailheadForm
    permission_required = 'trailhead.can_add'

    def form_valid(self, form):
        # save TH to database
        th = form.save()
        # trigger major city drive time table row create function
        updateTable.createNewDriveTimeEntries()
        # trigger calculation of new drive times into database
        updateTable.updateDriveTimeEntries(origin_type="trailhead")
        # redirect to newly-created trailhead detail page
        return redirect(reverse('trailhead-detail',
                                            args=[str(th.pk)]))


class TrailheadUpdate(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Trailhead
    form_class = TrailheadForm
    permission_required = 'trailhead.can_change'

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
        return redirect(self.get_object().get_absolute_url())


class TrailheadDelete(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Trailhead
    success_url = reverse_lazy('trailhead-list')
    permission_required = 'trailhead.can_delete'


# Autocomplete query view
class TrailheadAutocomplete(BaseSelectAutocomplete):
    model = Trailhead


# -------- Governing Body views --------------------
class GoverningBodyDetailView(LoginRequiredMixin,
                              generic.DetailView):
    model = GoverningBody


class GoverningBodyListView(LoginRequiredMixin, generic.ListView):
    model = GoverningBody


class GoverningBodyCreate(LoginRequiredMixin, PermissionRequiredMixin,
                          CreateView):
    model = GoverningBody
    fields = '__all__'
    permission_required = 'governingbody.can_add'


class GoverningBodyUpdate(LoginRequiredMixin, PermissionRequiredMixin,
                          UpdateView):
    model = GoverningBody
    fields = '__all__'
    permission_required = 'governingbody.can_change'


class GoverningBodyDelete(LoginRequiredMixin, PermissionRequiredMixin,
                          DeleteView):
    model = GoverningBody
    success_url = reverse_lazy('govbody-list')
    permission_required = 'governingbody.can_delete'


# --------Jurisdiction views ---------------------
class JurisdictionDetailView(LoginRequiredMixin, generic.DetailView):
    model = Jurisdiction


class JurisdictionListView(LoginRequiredMixin, generic.ListView):
    model = Jurisdiction


class JurisdictionCreate(LoginRequiredMixin, PermissionRequiredMixin,
                         CreateView):
    model = Jurisdiction
    fields = '__all__'
    permission_required = 'jurisdiction.can_add'


class JurisdictionUpdate(LoginRequiredMixin, PermissionRequiredMixin,
                         UpdateView):
    model = Jurisdiction
    fields = '__all__'
    permission_required = 'jurisdiction.can_change'


class JurisdictionDelete(LoginRequiredMixin, PermissionRequiredMixin,
                         DeleteView):
    model = Jurisdiction
    success_url = reverse_lazy('jurisdiction-list')
    permission_required = 'jurisdiction.can_delete'


# ------- User Profile views ----------------------
@login_required
def profile_overview(request):
    return render(request, 'planner/profile_overview.html')


@login_required
def profile_update(request):
    # get profile data from database
    user = request.user
    profile = request.user.profile
    # process form data if POST request
    if request.method == "POST":
        # create form instance and populate it with request:
        user_form = UserForm(request.POST, instance=user, prefix="user")
        profile_form = ProfileForm(request.POST, instance=profile,
                                   prefix="profile")
        if user_form.is_valid() and profile_form.is_valid():
            # save data
            user_form.save()
            profile_form.save()
            return redirect(reverse('profile-detail'))

    # create default form for GET or other method
    else:
        user_form = UserForm(instance=user, prefix="user")
        profile_form = ProfileForm(instance=profile, prefix="profile")

    context = {'user_form': user_form, 'profile_form': profile_form}

    return render(request, "planner/profile_update.html", context)


# ---------- Public Link views ----------------------
def base_create_edit_link(request, base_model, base_model_pk,
                          link_model, link_model_pk=None):

    denied_perm_template = "planner/denied_permission.html"
    link_form_template = "planner/link_form.html"

    # get link model name
    link_model_name = link_model.__name__.lower()
    if link_model_pk:  # link is being edited
        edit_type = "change"
        link = link_model.objects.get(pk=link_model_pk)
    else:  # link is being created
        edit_type = "add"

    # get model instance the link is related to
    owner_model = base_model.objects.get(pk=base_model_pk)

    # get privilege of user
    has_perm = request.user.has_perm("planner.{0}_{1}".format(
                                        edit_type, link_model_name))

    # process form data from POST request
    if request.method == "POST":

        # deny permission for unauthorized change/add requests
        if edit_type == "change":
            # deny change access for public links for users without permissions
            if link.link_type == Link.PUBLIC and not has_perm:
                return render(request, denied_perm_template)
            # deny change access of private links for other users' private
            # links, unless the user has admin link permissions
            elif (link.link_type == Link.PRIVATE and
                  link.user != request.user and not has_perm):
                return render(request, denied_perm_template)

        # create form instance and populate it
        form = LinkBaseForm(request.POST, user_is_admin=has_perm)

        if form.is_valid():
            # take cleaned data from form and populate link object
            if edit_type == "change":
                link.label = form.cleaned_data['label']
                link.url = form.cleaned_data['url']
                link.link_type = form.cleaned_data['link_type']
                # public link has no attached user, private does
                if form.cleaned_data['link_type'] == Link.PUBLIC:
                    link.user = None
                else:
                    link.user = request.user
                # owner model is already set, not meant to be changed

                link.save()

            else:  # edit_type == "add"
                # populate new link
                if form.cleaned_data['link_type'] == Link.PUBLIC:
                    # prevent unauthorized user from POSTing a new public link
                    if not has_perm:
                        return render(request, denied_perm_template)
                    # otherwise, valid. Set null user for public links.
                    link_user = None
                else:
                    link_user = request.user
                new_link = link_model(label=form.cleaned_data['label'],
                                url=form.cleaned_data['url'],
                                link_type=form.cleaned_data['link_type'],
                                user=link_user,
                                owner_model=owner_model)
                new_link.save()

            # redirect to owning page
            return redirect(owner_model.get_absolute_url())

    elif request.method == "GET":

        # create form instance. Blank for create, with data for edit
        initial = {}

        if edit_type == "change":
            # deny change access for public links for users without permissions
            if link.link_type == Link.PUBLIC and not has_perm:
                return render(request, denied_perm_template)
            # deny change access of private links for other users' private
            # links, unless the user has admin link permissions
            elif (link.link_type == Link.PRIVATE and
                  link.user != request.user and not has_perm):
                return render(request, denied_perm_template)

            else:  # change access granted
                initial['label'] = link.label
                initial['url'] = link.url
                initial['link_type'] = link.link_type

        form = LinkBaseForm(user_is_admin=has_perm, initial=initial)

    else:  # default all other request methods to empty form
        form = LinkBaseForm(user_is_admin=has_perm)

    return render(request, link_form_template, {"form": form})


def base_delete_link(request, link_model, link_model_pk):
    denied_perm_template = "planner/denied_permission.html"
    link_delete_template = "planner/link_delete.html"

    # get object instances for base model and link
    link = link_model.objects.get(pk=link_model_pk)
    owner = link.owner_model

    # get link model name
    link_model_name = link_model.__name__.lower()

    # check user for admin link delete privileges
    has_perm = request.user.has_perm("planner.delete_{0}".format(
                                                link_model_name))

    if request.method == "POST":
        # check permissions before allowing delete
        if has_perm:
            # admin deleting public (or private) link
            link.delete()
            return redirect(owner.get_absolute_url())

        if link.link_type == Link.PRIVATE and request.user == link.user:
            # user deleting their own private link
            link.delete()
            return redirect(owner.get_absolute_url())

        # else: user does not have permission to delete the current link
        return render(request, denied_perm_template)

    else:  # treat everything else like a "GET" request
        # check permissions before allowing delete
        if has_perm:
            # admin deleting public (or private) link
            return render(request, link_delete_template, {'link': link,
                          'owner': owner})

        if link.link_type == Link.PRIVATE and request.user == link.user:
            # user deleting their own private link
            return render(request, link_delete_template, {'link': link,
                          'owner': owner})

        # else: user does not have permission to delete the current link
        return render(request, denied_perm_template)


@login_required
def destination_create_link(request, dest_pk):
    return base_create_edit_link(request, Destination, dest_pk,
                                 DestinationLink)


@login_required
def destination_edit_link(request, dest_pk, link_pk):
    return base_create_edit_link(request, Destination, dest_pk,
                                 DestinationLink, link_pk)


@login_required
def destination_delete_link(request, dest_pk, link_pk):
    return base_delete_link(request, DestinationLink, link_pk)


@login_required
def route_create_link(request, route_pk):
    return base_create_edit_link(request, Route, route_pk,
                                 RouteLink)


@login_required
def route_edit_link(request, route_pk, link_pk):
    return base_create_edit_link(request, Route, route_pk,
                                 RouteLink, link_pk)


@login_required
def route_delete_link(request, route_pk, link_pk):
    return base_delete_link(request, RouteLink, link_pk)
