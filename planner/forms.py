from django.forms import ModelForm
from .models import Profile, Destination, Route

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
