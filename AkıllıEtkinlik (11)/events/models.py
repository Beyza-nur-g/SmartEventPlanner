from django.db import models
from users.models import User
from django.conf import settings
from geopy.geocoders import Nominatim

class Event(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    date = models.DateTimeField()
    duration = models.DurationField(null=True, blank=True)
    location = models.CharField(max_length=300)
    category = models.CharField(max_length=100)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='owned_events')  # Etkinliğin sahibi
    participants = models.ManyToManyField(User, through='Participation')
    latitude = models.FloatField(blank=True, null=True)  # Enlem bilgisi
    longitude = models.FloatField(blank=True, null=True)  # Boylam bilgisi

    def save(self, *args, **kwargs):
        if self.location:
            coordinates = get_coordinates_from_address(self.location)
            if coordinates:
                self.latitude, self.longitude = coordinates
        super(Event, self).save(*args, **kwargs)

    def __str__(self):
        return self.name


def get_coordinates_from_address(address):
    geolocator = Nominatim(user_agent="myGeocoder")
    location = geolocator.geocode(address)
    if location:
        return [location.latitude, location.longitude]
    else:
        return None


class Participation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='event_participations')  # 'user_participations' yerine 'event_participations' kullanıldı
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'event')



class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='event_sent_messages')  # related_name değiştirildi
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='messages')
    text = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.sender.username} - {self.text[:20]}'


