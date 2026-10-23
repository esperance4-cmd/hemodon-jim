# apps/profiles/urls.py
from django.urls import path
from . import views

app_name = 'profiles'

urlpatterns = [
    # Profil
    path('profile/', views.profile_view, name='profile'),
    path('profile/<str:username>/', views.profile_view, name='profile_detail'),
    path('profile/edit/', views.profile_edit_view, name='profile_edit'),
    
    # Gestion des utilisateurs (admin)
    path('admin/users/', views.users_list_view, name='users_list'),
    path('admin/user/<int:user_id>/', views.user_detail_view, name='user_detail'),
    path('admin/user/<int:user_id>/edit/', views.user_edit_view, name='user_edit'),
    path('admin/user/<int:user_id>/delete/', views.user_delete_view, name='user_delete'),
    path('admin/user/<int:user_id>/role/', views.user_role_change_view, name='user_role'),
    
    # API
    path('api/eligibility/', views.api_eligibility_check, name='api_eligibility'),
    path('api/stats/', views.api_user_stats, name='api_stats'),
    path('api/stats/<int:user_id>/', views.api_user_stats, name='api_stats_user'),
]