from django.urls import path
from . import views


urlpatterns = [
    path('auth/superuser', views.view_auth_superuser), 
    path('auth/host', views.view_auth_host),

    path('superusers', views.view_superusers),
    path('superusers/<str:id>', views.view_superusers_id)
]