from django.db import models
from django.urls import reverse
from django.core.validators import MinLengthValidator, MaxLengthValidator, MinValueValidator, MaxValueValidator
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.db.models.signals import post_save
from django.dispatch import receiver
from datetime import date
import math

# from django.contrib.auth.models import User
from .PlannerUtils import constructURL

# Create your models here.
class Destination(models.Model):
    """
    Model for a physical point location of interest
    """

    # ---- FIELDS ----------------
    MOUNTAIN = 'm'
    LAKE = 'l'
    WATERFALL = 'w'
    OTHER = 'o'

    TYPE_CHOICES = (
        (MOUNTAIN, 'Mountain'),
        (LAKE, 'Lake'),
        (WATERFALL, 'Waterfall'),
        (OTHER, 'Other'),
    )

    name = models.CharField(max_length=100)
    latitude = models.FloatField(help_text='Degrees N/S, between -90 and 90')
    longitude = models.FloatField(help_text='Degrees E/W, between -180 and 180')
    elevation = models.FloatField(verbose_name='Elevation [ft]')
    county = models.ForeignKey('County', on_delete=models.SET_NULL, null=True)
    dest_type = models.CharField(max_length=2,
                                 choices=TYPE_CHOICES,
                                 verbose_name='Destination Type')
    jurisdiction = models.ForeignKey('Jurisdiction',on_delete=models.SET_NULL, null=True)
    description = models.TextField(max_length=5000, blank=True)
    # link_public = GenericRelation('PublicLink',
    #                               related_query_name='destination')

    # ---- METADATA ----------------
    class Meta:
        pass

    # ---- METHODS -------------------
    def get_absolute_url(self):
        return reverse('destination-detail', args=[str(self.pk)])

    @property
    def google_maps_terrain_url(self):
        lat = self.latitude
        lon = self.longitude
        layer = "terrain"
        zoom = 15
        return constructURL.googleMapsPointExternal(lat, lon, layer, zoom)

    @property
    def google_maps_satellite_url(self):
        lat = self.latitude
        lon = self.longitude
        layer = "satellite"
        zoom = 15
        return constructURL.googleMapsPointExternal(lat, lon, layer, zoom)

    @property
    def caltopo_url(self):
        return constructURL.buildCalTopoURL(self.latitude, self.longitude)

    @property
    def noaa_url(self):
        return constructURL.buildNOAAURL(self.latitude, self.longitude)

    @property
    def noaa_api_url(self):
        return constructURL.buildNOAAapiURL(self.latitude, self.longitude)

    # @property
    # def noaa_embed_widget_url(self):
    #     return constructURL.buildNOAAembedURL(self.latitude, self.longitude)

    @property
    def google_maps_embed_url(self):
        lat = self.latitude
        lon = self.longitude
        layer = "terrain"
        return constructURL.googleMapsStatic(lat, lon, maptype=layer)

    @property
    def dest_type_expanded(self):
        """
        Decodes destination type based on TYPE_CHOICES
        """
        return dict(self.TYPE_CHOICES)[self.dest_type]

    def __str__(self):
        return self.name


class Route(models.Model):
    """
    Model for a path of finite distance
    """

    # ----- FIELDS --------------------
    OUT_AND_BACK = 'oab'
    ONE_WAY = 'ow'
    LOOP = 'l'

    PATH_SEQ_CHOICES = (
        (OUT_AND_BACK, 'Out-And-Back'),
        (ONE_WAY, 'Through Hike'),
        (LOOP, 'Loop'),
    )

    CLASS_RATING_CHOICES = (
        (1, '1'),
        (2, '2'),
        (3, '3'),
        (4, '4'),
        (5, '5'),
        )

    name = models.CharField(max_length=100)
    total_distance = models.FloatField(verbose_name='Total Distance [mi]',
                                       help_text='Full trip distance, in miles: length for one-way routes, or round trip distance for loop and out-and-back routes')
    gain = models.IntegerField(verbose_name='Total Elevation Gain [ft]')
    path_seq = models.CharField(max_length=3, choices=PATH_SEQ_CHOICES,
                                verbose_name='Route Sequence')
    trailhead = models.ForeignKey('Trailhead', on_delete=models.SET_NULL, null=True)
    class_rating = models.PositiveSmallIntegerField(choices=CLASS_RATING_CHOICES,
                                                    verbose_name="Class",
                                                    help_text="Yosemite Decimal System (1-5)")
    destination = models.ForeignKey(Destination, on_delete=models.CASCADE)
    description = models.TextField(max_length=5000, blank=True)


    # ----- METADATA --------------
    class Meta:
        pass

    # ----- METHODS ----------------
    def get_absolute_url(self):
        return reverse('route-detail', args=[str(self.pk)])

    @property
    def path_seq_expanded(self):
        return dict(self.PATH_SEQ_CHOICES)[self.path_seq]

    def __str__(self):
        return self.name


class County(models.Model):
    """
    Model containing USA county data
    """
    # ----- FIELDS --------------------
    state = models.CharField(max_length=2)
    name = models.CharField(max_length=50)
    sheriff_phone_number = models.CharField(max_length=12,
                                     help_text="Number must be in XXX-XXX-XXXX format",
                                     blank=True)

    # ----- METADATA --------------
    class Meta:
        ordering = ["state", "name"]

    # ----- METHODS ----------------
    def get_absolute_url(self):
        pass

    def __str__(self):
        return "({0}) {1}".format(self.state, self.name)


class Jurisdiction(models.Model):
    """
    Model containing the information for the local governing organization
    for a particular geographic location
    (e.g. Rocky Mountain National Park, Wenatchee State Forest)
    """
    # ----- FIELDS --------------------
    name = models.CharField(max_length=50)
    governing_body = models.ForeignKey('GoverningBody',
                                       on_delete=models.SET_NULL,
                                       null=True)
    website = models.URLField(help_text="Home page URL",
                              blank=True)
    parking_info = models.TextField(verbose_name="Parking Information",
                                    blank = True)
    camping_info = models.TextField(verbose_name="Camping Information",
                                    blank = True)

    # ----- METADATA --------------
    class Meta:
        pass

    # ----- METHODS ----------------
    def get_absolute_url(self):
        return reverse('jurisdiction-detail', args=[str(self.pk)])

    def __str__(self):
        return self.name


class GoverningBody(models.Model):
    """
    Model containing the information for overarching governing bodies
    (e.g. NPS, USFS, BLM, Washington State Parks, etc.)
    """
    # ----- FIELDS --------------------
    FEDERAL = 'f'
    STATE = 'st'
    COUNTY = 'co'
    CITY = 'ci'
    PRIVATE = 'p'

    LEVEL_OF_GOVT_CHOICES = (
        (FEDERAL, 'Federal'),
        (STATE, 'State'),
        (COUNTY, 'County'),
        (CITY, 'City'),
        (PRIVATE, 'Private'),
        )

    name = models.CharField(max_length=50)
    abbr = models.CharField(max_length=10, blank=True, null=True)
    level_of_government = models.CharField(max_length=20, choices=LEVEL_OF_GOVT_CHOICES)

    # ----- METADATA --------------
    class Meta:
        pass

    # ----- METHODS ----------------
    def get_absolute_url(self):
        return reverse('govbody-detail', args=[str(self.pk)])

    @property
    def level_of_government_expanded(self):
        return dict(self.LEVEL_OF_GOVT_CHOICES)[self.level_of_government]

    def __str__(self):
        return self.name


class Trailhead(models.Model):
    """
    Model containing trailhead info
    """
    # ----- FIELDS --------------------
    name = models.CharField(max_length=50)
    latitude = models.FloatField(help_text='Degrees N/S, between -90 and 90')
    longitude = models.FloatField(help_text='Degrees E/W, between -180 and 180')
    county = models.ForeignKey(County, on_delete=models.SET_NULL, null=True)
    jurisdiction = models.ForeignKey(Jurisdiction, on_delete=models.SET_NULL,
                                     null=True)
    majorcity = models.ManyToManyField('MajorCity',
                                       through='DriveTimeMajorCity')

    # ----- METADATA --------------
    class Meta:
        pass

    # ----- METHODS ----------------
    def get_absolute_url(self):
        return reverse('trailhead-detail', args=[str(self.pk)])

    @property
    def google_maps_terrain_url(self):
        lat = self.latitude
        lon = self.longitude
        layer = "terrain"
        zoom = 15
        return constructURL.googleMapsPointExternal(lat, lon, layer, zoom)

    @property
    def google_maps_satellite_url(self):
        lat = self.latitude
        lon = self.longitude
        layer = "satellite"
        zoom = 15
        return constructURL.googleMapsPointExternal(lat, lon, layer, zoom)

    @property
    def caltopo_url(self):
        return constructURL.buildCalTopoURL(self.latitude, self.longitude)

    @property
    def noaa_url(self):
        return constructURL.buildNOAAURL(self.latitude, self.longitude)

    @property
    def noaa_api_url(self):
        return constructURL.buildNOAAapiURL(self.latitude, self.longitude)

    @property
    def google_maps_embed_url(self):
        lat = self.latitude
        lon = self.longitude
        # layer = "terrain"
        return constructURL.googleMapsEmbed(lat, lon)

    @property
    def latlon_str(self):
        return str(self.latitude) + "," + str(self.longitude)

    def __str__(self):
        return self.name


class MajorCity(models.Model):
    """
    Model containing the major cities used as a rough driving time indicator
    """
    # ----- FIELDS ---------------------
    name = models.CharField(max_length=50)
    latitude = models.FloatField(help_text='Degrees N/S, between -90 and 90')
    longitude = models.FloatField(help_text='Degrees E/W, between -180 and 180')

    # ----- METADATA --------------------
    class Meta:
        pass

    # ----- METHODS ---------------------
    @property
    def latlon_str(self):
        return str(self.latitude) + "," + str(self.longitude)

    def __str__(self):
        return self.name


class DriveTimeMajorCity(models.Model):
    """
    Through model managing MajorCity and Trailhead many-to-many relationship.
    Contains drive time and timer about last update.
    """
    NEW_ITEM = 1
    OK = 2
    ERROR = 3

    LAST_API_CALL_STATUS = (
        (NEW_ITEM, 'New Item'),
        (OK, 'OK'),
        (ERROR, 'Error'),
        )

    trailhead = models.ForeignKey(Trailhead, on_delete=models.CASCADE, related_name="drive_data")
    majorcity = models.ForeignKey(MajorCity, on_delete=models.CASCADE)
    drive_distance = models.FloatField(validators=[MinValueValidator(0)], null=True)
    drive_time = models.FloatField(validators=[MinValueValidator(0)], null=True)
    # default date_updated to 1900 so hook will mark it for update if not set
    date_updated = models.DateField(default=date(1900, 1, 1))
    api_call_status = models.IntegerField(choices=LAST_API_CALL_STATUS,
                    default=NEW_ITEM)
    error_message = models.CharField(max_length=1000, default="")

    @property
    def api_call_status_expanded(self):
        return dict(self.LAST_API_CALL_STATUS)[self.api_call_status]

    @property
    def drive_distance_miles(self):
        # Google Distance Matrix API returns distance in meters
        return self.drive_distance / 1609.34

    @property
    def drive_time_minutes(self):
        # Google Distance Matrix API returns duration in seconds
        return self.drive_time / 60

    @property
    def drive_time_str(self):
        # return data in 'X hr Y min' format
        hours = int(math.floor(self.drive_time / 3600))
        minutes = int(math.floor((self.drive_time - hours * 3600) / 60))
        return str(hours) + ' hr ' + str(minutes) + ' min'


class Profile(models.Model):
    """
    Model containing data specific to a given user
    """
    # ----- FIELDS ---------------------
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    nearest_city = models.ForeignKey(MajorCity, on_delete=models.SET_NULL, null=True, blank=True)
    street = models.CharField(max_length=100, verbose_name="Street Address", blank=True)
    city = models.CharField(max_length=50, blank=True)
    state = models.CharField(max_length=2, blank=True)
    zip_code = models.CharField(max_length=5, blank=True)

    @property
    def street_line(self):
        return self.street

    @property
    def city_line(self):
        return "{0}, {1} {2}".format(self.city, self.state, self.zip_code)

    @property
    def full_address(self):
        return "{0}, {1}, {2} {3}".format(self.street, self.city,
                                          self.state, self.zip_code)

    # ----- METADATA --------------------
    class Meta:
        pass

    # ----- METHODS ---------------------
    def __str__(self):
        return self.user.username


# hooks for Profile model to User model
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


class PublicLink(models.Model):
    """
    Model representing a link on a page that any user of the site can see.
    """
    label = models.CharField(max_length=50)
    url = models.URLField()
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    def __str__(self):
        return "({0}) {1}".format(self.label, self.url)
