from django.forms import ModelForm
from .models import Profile

# Form classes
class ProfileForm(ModelForm):
    class Meta:
        model = Profile
        exclude = ["user"]
