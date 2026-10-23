# config/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Applications
    path('', include('apps.authentification.urls')),
    path('', include('apps.centres.urls')),
    path('', include('apps.dons.urls')),
    path('', include('apps.demandes.urls')),
    path('', include('apps.stocks.urls')),
    path('', include('apps.app_admin.urls')),
    path('', include('apps.notifications.urls')),
    path('', include('apps.profiles.urls')),
    path('', include('apps.matching.urls')),
    path('chatbot/', include('apps.chatbot.urls')),
    
    # Authentification standard
    path('login/', auth_views.LoginView.as_view(template_name='auth/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)