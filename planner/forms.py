from django.forms import ModelForm
from .models import Profile, Destination, Route, GoverningBody, Jurisdiction, Trailhead


# Form classes
class ProfileForm(ModelForm):
    class Meta:
        model = Profile
        exclude = ["user"]


class DestinationForm(ModelForm):
    class Meta:
        model = Destination
        fields = '__all__'


class RouteForm(ModelForm):
    class Meta:
        model = Route
        fields = '__all__'


class TrailheadForm(ModelForm):
    class Meta:
        model = Trailhead
        exclude = ['majorcity']


class JurisdictionForm(ModelForm):
    class Meta:
        model = Jurisdiction
        fields = '__all__'


class GoverningBodyForm(ModelForm):
    class Meta:
        model = GoverningBody
        fields = '__all__'
