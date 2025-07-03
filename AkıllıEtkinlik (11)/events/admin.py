# events/admin.py
from django.contrib import admin
from .models import Event, Participation, Message
from users.models import Score

class EventAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'date', 'location', 'category')
    search_fields = ('name', 'location', 'category', 'owner__username')
    list_filter = ('category', 'date')
    autocomplete_fields = ['owner']  # Kullanıcı ilgi alanlarını daha iyi kontrol edebilmek için öneri ekleme

class ParticipationAdmin(admin.ModelAdmin):
    list_display = ('user', 'event', 'joined_at')
    search_fields = ('user__username', 'event__name')
    list_filter = ('joined_at',)
    autocomplete_fields = ['user', 'event']

class MessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'event', 'text', 'timestamp')
    search_fields = ('sender__username', 'event__name', 'text')
    list_filter = ('timestamp',)
    autocomplete_fields = ['sender', 'event']

class ScoreAdmin(admin.ModelAdmin):
    list_display = ('user', 'points', 'earned_date')
    search_fields = ('user__username',)
    list_filter = ('earned_date',)
    autocomplete_fields = ['user']

admin.site.register(Event, EventAdmin)
admin.site.register(Participation, ParticipationAdmin)
admin.site.register(Message, MessageAdmin)
admin.site.register(Score, ScoreAdmin)
