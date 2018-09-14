from django.contrib import admin
from .models import Destination, Route, Trailhead, County, Jurisdiction, GoverningBody, MajorCity, Profile, DriveTimeMajorCity

# Register your models here.
admin.site.register(Destination)
admin.site.register(Route)
admin.site.register(Trailhead)
admin.site.register(County)
admin.site.register(Jurisdiction)
admin.site.register(GoverningBody)
admin.site.register(MajorCity)
admin.site.register(Profile)

# Admin classes
@admin.register(DriveTimeMajorCity)
class DriveTimeMajorCityAdmin(admin.ModelAdmin):
    list_display = ('majorcity', 'trailhead', 'drive_time',
        'drive_distance', 'date_updated', 'api_call_status', 'error_message')
    list_filter = ('majorcity', 'trailhead', 'drive_time',
        'drive_distance', 'date_updated', 'api_call_status', 'error_message')
