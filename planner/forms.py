from django import forms
from .models import Profile, Destination, Route, GoverningBody, Jurisdiction, Trailhead


# Form classes
class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        exclude = ["user"]


class DestinationForm(forms.ModelForm):
    class Meta:
        model = Destination
        fields = '__all__'

class DestinationSearchForm(forms.Form):
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


class TrailheadForm(forms.ModelForm):
    class Meta:
        model = Trailhead
        exclude = ['majorcity']


class JurisdictionForm(forms.ModelForm):
    class Meta:
        model = Jurisdiction
        fields = '__all__'


class GoverningBodyForm(forms.ModelForm):
    class Meta:
        model = GoverningBody
        fields = '__all__'
