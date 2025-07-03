from django.contrib import admin
from django.urls import include, path, reverse_lazy
from django.shortcuts import redirect
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('users/', include('users.urls')),   # Kullanıcı uygulaması URL'leri
    path('events/', include('events.urls')), # Etkinlik uygulaması URL'leri
    path('chat/', include('chat.urls')),     # Sohbet uygulaması URL'leri
    path('', lambda request: redirect(reverse_lazy('dashboard'))), # Anasayfa yönlendirme
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
