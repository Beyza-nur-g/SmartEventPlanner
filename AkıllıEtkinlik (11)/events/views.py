# events/views.py - Güncellenmiş Hali
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages 

from django.contrib import messages as django_messages

from users.views import recommend_events_for_user
from .models import Event ,  Participation , Message
from .forms import EventForm
from django.db.models import Q
from datetime import timedelta, datetime
from django.utils import timezone
from users.models import Score


@login_required
def event_list(request):
    events = Event.objects.all()
    return render(request, 'events/event_list.html', {'events': events})

@login_required
def event_detail(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    is_participating = Participation.objects.filter(event=event, user=request.user).exists()

    if request.method == 'POST':
        if 'add_participation' in request.POST:
            Participation.objects.create(event=event, user=request.user)
        elif 'remove_participation' in request.POST:
            Participation.objects.filter(event=event, user=request.user).delete()
        elif 'add_message' in request.POST:
            message_text = request.POST.get('message')
            if message_text:
                new_message = Message.objects.create(
                    sender=request.user,
                    text=message_text,
                    event=event
                )
                new_message.save()
                django_messages.success(request, 'Yorum başarıyla eklendi.')
            else:
                django_messages.error(request, 'Yorum boş olamaz.')
        return redirect('event_detail', event_id=event.id)

    messages_list = Message.objects.filter(event=event)
    return render(request, 'events/event_detail.html', {
        'event': event,
        'is_participating': is_participating,
        'messages_list': messages_list
    })

# events/views.py - Güncellenmiş Hali
@login_required
def create_event(request):
    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            new_event = form.save(commit=False)
            new_event.owner = request.user  # Etkinliği oluşturan kullanıcıyı owner olarak ekle
            try:
                duration_minutes = int(request.POST.get('duration'))  # Süreyi integer olarak al
                new_event.duration = timedelta(minutes=duration_minutes)  # Süreyi timedelta olarak kaydet
            except ValueError:
                messages.error(request, 'Süre geçerli bir sayı olmalıdır. Lütfen tekrar deneyin.')
                return render(request, 'events/create_event.html', {'form': form})
            
            # Etkinliği kaydet
            new_event.save()
            Score.objects.create(user=request.user, points=15)
            # Çakışma olup olmadığını kontrol et
            overlapping_events = check_event_conflicts(new_event, request.user)
            if overlapping_events.exists():
                # Çakışma varsa etkinliği sil
                new_event.delete()
                messages.error(request, 'Oluşturmak istediğiniz etkinlik, başka etkinliklerle çakışıyor. Lütfen farklı bir zaman seçin.')
                return render(request, 'events/create_event.html', {'form': form, 'overlapping_events': overlapping_events})
            else:
                # Çakışma yoksa kullanıcıyı katılımcı olarak ekle
                new_event.participants.add(request.user)
                messages.success(request, 'Etkinlik başarıyla oluşturuldu.')
                return redirect('event_list')
        else:
            messages.error(request, 'Etkinlik oluşturulurken bir hata oluştu. Lütfen formu kontrol edin.')
    else:
        form = EventForm()
    return render(request, 'events/create_event.html', {'form': form})

@login_required
def update_event(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    if event.owner != request.user:
        messages.error(request, 'Bu etkinliği güncelleme yetkiniz yok.')
        return redirect('event_detail', event_id=event.id)

    if request.method == 'POST':
        form = EventForm(request.POST, instance=event)
        if form.is_valid():
            try:
                duration_minutes = int(request.POST.get('duration'))
                event.duration = timedelta(minutes=duration_minutes)
            except ValueError:
                messages.error(request, 'Süre geçerli bir sayı olmalıdır. Lütfen tekrar deneyin.')
                return render(request, 'events/update_event.html', {'form': form, 'event': event})

            overlapping_events = check_event_conflicts(event, request.user)
            if overlapping_events.exists():
                messages.error(request, 'Güncellemek istediğiniz etkinlik, başka etkinliklerle çakışıyor. Lütfen farklı bir zaman seçin.')
                return render(request, 'events/update_event.html', {'form': form, 'event': event, 'overlapping_events': overlapping_events})

            form.save()
            messages.success(request, 'Etkinlik başarıyla güncellendi.')
            return redirect('event_detail', event_id=event.id)
        else:
            messages.error(request, 'Etkinlik güncellenirken bir hata oluştu. Lütfen formu kontrol edin.')
    else:
        form = EventForm(instance=event)
    return render(request, 'events/update_event.html', {'form': form, 'event': event})

@login_required
def delete_event(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    if request.method == 'POST':
        event.delete()
        messages.success(request, 'Etkinlik başarıyla silindi.')
        return redirect('event_list')
    return render(request, 'events/delete_event.html', {'event': event})





@login_required
def recommend_eventsssss(request):
    user = request.user
    profile = getattr(user, 'userprofile', None)

    filter_option = request.GET.get('filter', 'interest')

    if filter_option == 'interest':
        interests_list = []
        if profile and profile.interests:
            interests_list = profile.interests.split(',')
            interests_list = [interest.strip().lower() for interest in interests_list]
        if interests_list:
            recommended_events = Event.objects.filter(category__in=interests_list).distinct().exclude(date__lt=timezone.now()).order_by('date')
        else:
            recommended_events = Event.objects.none()

    elif filter_option == 'date':
        past_participations = Event.objects.filter(participants=user)
        participated_categories = set(past_participations.values_list('category', flat=True))
        if participated_categories:
            recommended_events = Event.objects.filter(category__in=participated_categories).distinct().exclude(date__lt=timezone.now()).order_by('date')
        else:
            recommended_events = Event.objects.none()

    elif filter_option == 'location':
        user_location = getattr(profile, 'location', None) if profile else None
        if user_location:
            recommended_events = Event.objects.filter(location__icontains=user_location).distinct().exclude(date__lt=timezone.now()).order_by('date')
        else:
            recommended_events = Event.objects.none()

    else:
        recommended_events = Event.objects.none()

    return render(request, 'events/recommend_events.html', {
        'recommended_events': recommended_events,
        'filter_option': filter_option
    })


def recommend_events(request):
    filter_option = request.GET.get('filter', 'interest')
    
    if filter_option == 'interest':
        return recommend_events_by_interests(request)
    elif filter_option == 'participation':
        return recommend_events_by_participation(request)
    elif filter_option == 'location':
        return recommend_events_by_location(request)
    else:
        return recommend_events_by_participation(request)

def check_event_conflicts(event, user):
    event_start = datetime.combine(event.date.date(), event.date.time())
    event_end = event_start + event.duration

    overlapping_events = Event.objects.filter(
        Q(date__date=event.date.date()) & (
            (Q(date__time__lte=event_end.time()) & Q(date__time__gte=event_start.time())) |
            (Q(date__time__gte=event_start.time()) & Q(date__time__lte=event_end.time()))
        ),
        owner=user  # owner alanını kullanarak kontrol yap
    ).exclude(pk=event.pk)

    return overlapping_events


@login_required
def myevent_detail(request, event_id):
    event = get_object_or_404(Event, pk=event_id, participants=request.user)

    if request.method == 'POST':
        if 'update_event' in request.POST:
            return redirect('update_event', event_id=event.id)
        elif 'delete_event' in request.POST:
            event.delete()
            return redirect('my_events')
        elif 'add_message' in request.POST:
            message_text = request.POST.get('message')
            if message_text:
                new_message = Message.objects.create(
                    sender=request.user,
                    text=message_text,
                    event=event
                )
                new_message.save()
                django_messages.success(request, 'Yorum başarıyla eklendi.')
            else:
                django_messages.error(request, 'Yorum boş olamaz.')
        return redirect('myevent_detail', event_id=event.id)

    messages_list = Message.objects.filter(event=event)
    return render(request, 'events/myevent_detail.html', {'event': event, 'messages_list': messages_list})

@login_required
def my_events(request):
    my_events = Event.objects.filter(participants=request.user)
    return render(request, 'events/my_events.html', {'my_events': my_events})

@login_required
def participate_event(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    user = request.user

    if Participation.objects.filter(user=user, event=event).exists():
        messages.warning(request, 'Bu etkinliğe zaten katıldınız.')
    else:
        Participation.objects.create(user=user, event=event)
        # Kullanıcıya puan ekleyin (10 puan)
        Score.objects.create(user=user, points=10)
        messages.success(request, 'Etkinliğe başarıyla katıldınız.')

    return redirect('event_detail', event_id=event.id)


@login_required
def add_message(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    if request.method == 'POST':
        message_text = request.POST.get('message')
        if message_text:
            new_message = Message.objects.create(
                sender=request.user,
                text=message_text,
                event=event
            )
            new_message.save()
            django_messages.success(request, 'Yorum başarıyla eklendi.')
        else:
            django_messages.error(request, 'Yorum boş olamaz.')
    return redirect('event_detail', event_id=event.id)


@login_required
def remove_participation(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    participation = get_object_or_404(Participation, event=event, user=request.user)

    if request.method == 'POST':
        participation.delete()
        Score.objects.create(user=request.user, points=-10)
        messages.success(request, 'Etkinlikten başarıyla çıkarıldınız.')
        return redirect('my_events')

    messages.error(request, 'Etkinlikten çıkma işlemi başarısız oldu.')
    return redirect('myevent_detail', event_id=event_id)

import re

@login_required
def recommend_events_by_interests(request):
    user = request.user

    interests_list = []
    if hasattr(user, 'interests') and user.interests:
        # Virgül ve boşluğa göre ilgi alanlarını bölme
        interests_list = [interest.strip().lower() for interest in re.split(r'[ ,]+', user.interests) if interest]

    if interests_list:
        recommended_events = Event.objects.filter(
            category__in=interests_list
        ).exclude(
            date__lt=timezone.now()
        ).exclude(
            participants=user
        ).distinct().order_by('date')
    else:
        recommended_events = Event.objects.none()  # İlgi alanı yoksa öneri yapma

    return render(request, 'events/recommend_events.html', {'recommended_events': recommended_events, 'filter_option': 'interest'})

@login_required
def recommend_events_by_participation(request):
    user = request.user

    # Kullanıcının geçmiş etkinlik katılımlarını al
    past_participations = Event.objects.filter(participants=user)
    participated_categories = set(past_participations.values_list('category', flat=True))

    if participated_categories:
        recommended_events = Event.objects.filter(
            category__in=participated_categories
        ).exclude(
            date__lt=timezone.now()
        ).exclude(
            participants=user
        ).distinct().order_by('date')
    else:
        recommended_events = Event.objects.none()  # Katılım yoksa öneri yapma

    return render(request, 'events/recommend_events.html', {'recommended_events': recommended_events, 'filter_option': 'participation'})

@login_required
def recommend_events_by_location(request):
    user = request.user

    user_location = getattr(user, 'location', None)

    if user_location:
        recommended_events = Event.objects.filter(
            location__icontains=user_location
        ).exclude(
            date__lt=timezone.now()
        ).exclude(
            participants=user
        ).distinct().order_by('date')
    else:
        recommended_events = Event.objects.none()  # Konum yoksa öneri yapma

    return render(request, 'events/recommend_events.html', {'recommended_events': recommended_events, 'filter_option': 'location'})
