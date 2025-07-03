# users/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('profile/<int:user_id>/', views.profile, name='profile'),
    path('edit_profile/<int:user_id>/', views.edit_profile, name='edit_profile'),
    path('reset_password/', views.reset_password, name='reset_password'),
    path('resend_verification_code/', views.resend_verification_code, name='resend_verification_code'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('homepage/', views.homepage, name='homepage'),  # homepage URL tanımı
    path('dashboard/', views.dashboard, name='dashboard'),
    


]
