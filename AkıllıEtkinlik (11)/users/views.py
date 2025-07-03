# views.py - Güncellenmiş Hali
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import User, Score
from events.models import Event
from django.db.models import Q
from django.db.models import Sum
from django.utils import timezone
import random
from django.core.mail import send_mail
from .forms import UserRegistrationForm, EditProfileForm, ResetPasswordForm
import json


@login_required
def dashboard(request):
    user = request.user
    interests = user.interests.split(',') if user.interests else []
    suggested_events = Event.objects.filter(Q(category__in=interests)).distinct()

    context = {
        'suggested_events': suggested_events,
        'user': user
    }
    return render(request, 'users/dashboard.html', context)  # Template yolunu güncelleyin


def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            user.set_password(form.cleaned_data['password'])
            user.save()
            login(request, user)
            return redirect('homepage')
    else:
        form = UserRegistrationForm()
    return render(request, 'users/register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        try:
            user = User.objects.get(username=username)
            if user.check_password(password):
                login(request, user)
                return redirect('homepage')  # Başarılı giriş sonrası anasayfaya yönlendirme
            else:
                messages.error(request, 'Şifre yanlış.')
        except User.DoesNotExist:
            messages.error(request, 'Kullanıcı adı yanlış.')
    return render(request, 'users/login.html')


def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def profile(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    total_points = Score.objects.filter(user=user).aggregate(total=Sum('points'))['total'] or 0

    # Kullanıcının süresi geçmiş etkinlik sayısını al ve 10 ile çarp
    past_events_count = Event.objects.filter(participants=user, date__lt=timezone.now()).count()
    past_events_points = past_events_count * 10

    # Toplam puana süresi geçmiş etkinlik puanını ekle
    total_points += past_events_points

    total_points += past_events_points + 20

    return render(request, 'users/profile.html', {'user': user, 'total_points': total_points})


def edit_profile(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    if request.method == 'POST':
        form = EditProfileForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profiliniz başarıyla güncellendi.')
            return redirect('profile', user_id=user.id)
        else:
            messages.error(request, 'Profil güncellenirken bir hata oluştu. Lütfen formu kontrol edin.')
    else:
        form = EditProfileForm(instance=user)
    return render(request, 'users/edit_profile.html', {'form': form, 'user': user})


@login_required
def reset_password(request):
    user = request.user
    if request.method == 'POST' and 'resend_verification_code' in request.POST:
        verification_code = random.randint(1000, 9999)
        request.session['verification_code'] = verification_code
        send_verification_code(user, verification_code)
        messages.success(request, 'Yeni doğrulama kodu gönderildi.')
        return redirect('reset_password')

    if request.method == 'POST':
        form = ResetPasswordForm(request.POST)
        if form.is_valid():
            input_code = request.POST.get('verification_code')
            if str(input_code) != str(request.session.get('verification_code')):
                messages.error(request, 'Doğrulama kodu geçersiz. Lütfen tekrar deneyin.')
                return render(request, 'users/reset_password.html', {'form': form, 'user': user})

            new_password = form.cleaned_data['new_password']
            user.set_password(new_password)
            user.save()
            messages.success(request, 'Şifreniz başarıyla güncellendi. Lütfen yeniden giriş yapın.')
            return redirect('login')
        else:
            messages.error(request, 'Şifre sıfırlanırken bir hata oluştu. Lütfen formu kontrol edin.')
    else:
        form = ResetPasswordForm()
    return render(request, 'users/reset_password.html', {'form': form, 'user': user})


@login_required
def resend_verification_code(request):
    user = request.user
    verification_code = random.randint(1000, 9999)
    request.session['verification_code'] = verification_code
    send_verification_code(user, verification_code)
    messages.success(request, 'Doğrulama kodu yeniden gönderildi.')
    return redirect('reset_password')


def send_verification_code(user, verification_code):
    # Doğrulama kodunu kullanıcıya e-posta ile gönder
    send_mail(
        'Şifre Sıfırlama Doğrulama Kodu',
        f"Merhaba {user.first_name},\n\nŞifreni sıfırlamak için doğrulama kodun: {verification_code}\n\nBu kodu kullanarak şifrenizi sıfırlayabilirsiniz.",
        'noreply@akillietkinlik.com',
        [user.email],
        fail_silently=False,
    )


def recommend_events_for_user(user):
    # Kullanıcının ilgi alanlarını ve daha önce katıldığı etkinliklerin kategorilerini al
    user_interests = user.interests.split(',') if user.interests else []
    user_participations = user.event_participations.all().values_list('event__category', flat=True)

    # İlgi alanlarına ve katılım geçmişine göre önerilen etkinlikleri al
    recommended_events = Event.objects.filter(
        Q(category__in=user_interests) | Q(category__in=user_participations)
    ).distinct().exclude(participants=user)

    return recommended_events


@login_required
def homepage(request):
    current_datetime = timezone.now()
    future_events = Event.objects.filter(date__gte=current_datetime)
    past_events = Event.objects.filter(date__lt=current_datetime)
    all_events = Event.objects.all()

    # Geocode edilmesi gereken adresleri JSON listesi olarak hazırlayın
    all_events_list = [
        {"position": [event.latitude, event.longitude], "title": event.name, "id": event.id}
        for event in all_events if event.latitude and event.longitude
    ]
    all_events_json = json.dumps(all_events_list)

    context = {
        'future_events': future_events,
        'past_events': past_events,
        'all_events_json': all_events_json
    }

    return render(request, 'users/homepage.html', context)
