from django.forms import ModelForm
from .models import Profile, Destination

# Form classes
class ProfileForm(ModelForm):
    class Meta:
        model = Profile
        exclude = ["user"]

class DestinationForm(ModelForm):
    class Meta:
        model = Destination
        fields = '__all__'
