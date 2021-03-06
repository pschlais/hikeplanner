from django import forms
from django.forms import widgets
from django.contrib.auth.models import User
from dal import autocomplete
from .models import Profile, Destination, Route, GoverningBody, Jurisdiction, Trailhead
from .models import Link


# Form classes
class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "email"]


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        exclude = ["user"]


class DestinationForm(forms.ModelForm):
    class Meta:
        model = Destination
        fields = '__all__'


class DestinationSearchForm(forms.Form):
    dest_name = forms.CharField(max_length=40, required=False, label="Destination Name")
    min_length = forms.DecimalField(min_value=0, decimal_places=1, required=False, label="Min Length [mi]")
    max_length = forms.DecimalField(min_value=0, decimal_places=1, required=False, label="Max Length [mi]")
    min_gain = forms.IntegerField(min_value=0, required=False, label="Min Elevation Gain [ft]")
    max_gain = forms.IntegerField(min_value=0, required=False, label="Max Elevation Gain [ft]")
    max_drive_distance = forms.IntegerField(min_value=0, required=False, label="Max Drive Distance [mi]")
    max_drive_time = forms.IntegerField(min_value=0, required=False, label="Max Drive Time [min]")
    min_class = forms.IntegerField(min_value=1, max_value=5, required=False, label="Min Class")
    max_class = forms.IntegerField(min_value=1, max_value=5, required=False, label="Max Class")
    # add a blank option that comes up first in input field
    dest_type = forms.ChoiceField(choices=(('', '-------'), *Destination.TYPE_CHOICES), required=False, label="Destination Type")
    path_seq = forms.ChoiceField(choices=(('', '-------'), *Route.PATH_SEQ_CHOICES), required=False, label="Route Sequence")

    def clean(self):
        cleaned_data = super().clean()
        # get custom fields to validate
        min_length = cleaned_data.get("min_length")
        max_length = cleaned_data.get("max_length")
        min_gain = cleaned_data.get("min_gain")
        max_gain = cleaned_data.get("max_gain")
        min_class = cleaned_data.get("min_class")
        max_class = cleaned_data.get("max_class")

        val_errors = []
        # Validation 1: min_length <= max_length
        if min_length and max_length:  # if both inputs were supplied
            if min_length > max_length:
                val_errors.append(forms.ValidationError("Min route length cannot be greater than max route length."))
        # Validation 2: min_gain <= max_gain
        if min_gain and max_gain:
            if min_gain > max_gain:
                val_errors.append(forms.ValidationError("Min elevation gain cannot be greater than the max elevation gain."))

        # Validation 3: min_class <= max_class
        if min_class and max_class:
            if min_class > max_class:
                val_errors.append(forms.ValidationError("Min class rating cannot be greater than the max class rating."))

        # raise ValidationErrors if they are present
        if len(val_errors) > 0:
            raise forms.ValidationError(val_errors)


class RouteForm(forms.ModelForm):
    class Meta:
        model = Route
        fields = '__all__'
        widgets = {
            'destination': autocomplete.ModelSelect2(url='destination-autocomplete'),
            'trailhead': autocomplete.ModelSelect2(url='trailhead-autocomplete'),
        }



class RouteInDestComboForm(forms.ModelForm):
    """
    This form class is used in combination with creating a Destination.
    """
    class Meta:
        model = Route
        exclude = ['destination']
        widgets = {
            'trailhead': autocomplete.ModelSelect2(url='trailhead-autocomplete'),
        }


    def __init__(self, trailhead_required, *args, **kwargs):

        if type(trailhead_required) is not bool:
            raise TypeError("trailhead_required must be True or False")

        super().__init__(*args, **kwargs)
        self.fields['trailhead'].required = trailhead_required

    def reset_default_required_fields(self):
        # Sets the route form to the default empty form state (existing trailhead not required, assume new trailhead will be input)
        self.fields['trailhead'].required = False


class RouteMainComboForm(forms.ModelForm):
    """
    This form class is used in combination with creating a trailhead.
    """
    class Meta:
        model = Route
        fields = '__all__'
        widgets = {
            'destination': autocomplete.ModelSelect2(url='destination-autocomplete'),
            'trailhead': autocomplete.ModelSelect2(url='trailhead-autocomplete'),
        }


    def __init__(self, trailhead_required, *args, **kwargs):

        if type(trailhead_required) is not bool:
            raise TypeError("trailhead_required must be True or False")

        super().__init__(*args, **kwargs)
        self.fields['trailhead'].required = trailhead_required

    def reset_default_required_fields(self):
        # Sets the route form to the default empty form state (existing
        # trailhead not required, assume new trailhead will be input)
        self.fields['trailhead'].required = False


class TrailheadForm(forms.ModelForm):
    class Meta:
        model = Trailhead
        exclude = ['majorcity']


class TrailheadComboForm(TrailheadForm):
    """
    This form class is used in combination with a Route.
    All inputs are set as not required in HTML. A separate form element determines this, and ensuring values are not empty is done in the clean() method.
    """

    def __init__(self, new_entry_required, *args, **kwargs):

        if type(new_entry_required) is not bool:
            raise TypeError("new_entry_required must be True or False")
        self.new_entry_required = new_entry_required

        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].required = new_entry_required

    def reset_default_required_fields(self):
        # Sets the trailhead form to the default empty form state (not required, assume existing trailhead will be selected)
        for field in self.fields:
            self.fields[field].required = False


class LinkBaseForm(forms.ModelForm):
    """
    This form class generates the visible fields of the Link abstract model.
    The logic of which version of the form to render must be in the logic of
    the view.
    """
    # label = forms.CharField(max_length=Link.LABEL_MAX_LENGTH)
    # url = forms.URLField()

    # link type defaults to private, becomes disabled for those without access
    link_type = forms.ChoiceField(choices=Link.LINK_TYPES,
                                  initial=Link.PRIVATE)

    class Meta:
        model = Link
        exclude = ['user']


    def __init__(self, *args, user_is_admin=False, **kwargs):
        # call parent constructor
        super().__init__(*args, **kwargs)
        # adjust inputs based on user privileges
        if not user_is_admin:
            # make link type disabled and hidden
            self.fields['link_type'].disabled = True
            self.fields['link_type'].widget = widgets.MultipleHiddenInput()

