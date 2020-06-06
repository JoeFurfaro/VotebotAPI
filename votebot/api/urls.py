from django.urls import path
from . import views

urlpatterns = [
    path('auth/superuser', views.view_auth_superuser), 
    path('auth/host', views.view_auth_host),

    path('superusers', views.view_superusers),
    path('superusers/<str:id>', views.view_superusers_id),

    path('hosts', views.view_hosts),
    path('hosts/<str:id>', views.view_hosts_id),
    path('hosts/<str:id>/sessions', views.view_host_sessions),
    path('hosts/<str:id>/voters', views.view_host_voters),

    path('sessions/<str:id>/topics/<str:tid>', views.view_session_topics_id),
    path('sessions/<str:id>/topics', views.view_session_topics),
    path('sessions/<str:id>/voters', views.view_session_voters),
    path('sessions/<str:id>', views.view_sessions_id),

    path('servers/launch/<str:id>', views.view_launch), # <- Takes a session ID
    path('servers/kill/<str:id>', views.view_kill), # <- Takes a server ID
    path('servers', views.view_servers),

    path('voters/<str:id>', views.view_voters_id),
]