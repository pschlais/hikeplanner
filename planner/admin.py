from django.contrib import admin
from .models import Destination, Route, Trailhead, County, Jurisdiction, GoverningBody, MajorCity, Profile

# Register your models here.
admin.site.register(Destination)
admin.site.register(Route)
admin.site.register(Trailhead)
admin.site.register(County)
admin.site.register(Jurisdiction)
admin.site.register(GoverningBody)
admin.site.register(MajorCity)
admin.site.register(Profile)
