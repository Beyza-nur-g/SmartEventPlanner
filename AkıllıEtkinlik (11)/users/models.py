from django.contrib.auth.models import AbstractUser
from django.db import models
from geopy.geocoders import Nominatim

class User(AbstractUser):
    email = models.EmailField(unique=True)
    birth_date = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=[('M', 'Male'), ('F', 'Female')], null=True, blank=True)
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    interests = models.TextField(null=True, blank=True)  # İlgi alanları ekleniyor
    profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
    location = models.CharField(max_length=300, null=True, blank=True)  # Konum bilgisi eklendi
    latitude = models.FloatField(blank=True, null=True)  # Enlem bilgisi
    longitude = models.FloatField(blank=True, null=True)  # Boylam bilgisi

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'first_name', 'last_name']

    def save(self, *args, **kwargs):
        if self.location:
            coordinates = get_coordinates_from_address(self.location)
            if coordinates:
                self.latitude, self.longitude = coordinates
        super(User, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.username} (ID: {self.id})"


def get_coordinates_from_address(address):
    geolocator = Nominatim(user_agent="myGeocoder")
    location = geolocator.geocode(address)
    if location:
        print(f"Coordinates for {address}: {location.latitude}, {location.longitude}")
        return [location.latitude, location.longitude]
    else:
        print(f"Could not find coordinates for {address}")
        return None


class Event(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    date = models.DateTimeField()
    location = models.CharField(max_length=300)
    category = models.CharField(max_length=100)
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


class Participation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_participations')
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    joined_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} joined {self.event.name}"


class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_received_messages')
    text = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"From: {self.sender.username} To: {self.receiver.username} - {self.text[:20]}..."


class Score(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    points = models.IntegerField()
    earned_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} (ID: {self.user.id}) - {self.points} points"
