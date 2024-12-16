from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views
from .views import TaskViewSet, GroupInfoView

router = DefaultRouter()
router.register(r'tasks', TaskViewSet)
urlpatterns = [
    path('home/', views.homepage, name='homepage'),
    path('tasks/', views.tasks, name='tasks'),
    path('calendar/', views.calendar, name='calendar'),
    path('teams/', views.teams, name='teams'),
    path('teams/create', views.create_group, name='teamCreate'),
    path('teams/join', views.join_group, name='teamJoin'),

    path('teams/<int:group_id>/', views.team_page, name='teamPage'),
    path('teams/<int:group_id>/info/', GroupInfoView.as_view(), name='group_info'),
    path('teams/<int:group_id>/files/', views.search_files, name='search_files'),
    path('teams/<int:group_id>/files/upload/', views.upload_file, name='upload_file'),
    path('teams/<int:group_id>/files/delete/<uuid:file_uuid>/', views.delete_file, name='delete_file'),

    path('file/download/<uuid:qdrant_id>/', views.download_file, name='download_file'),
    path('chat/', views.get_bot_response, name='chat_with_main_bot'),
    path('register/', views.register, name='register'),
    path('register2/', views.register_step2, name='register_step2'),
    path('login/', views.custom_login, name='login'),
    path('', views.home, name='home'),
    # path('update-profile/', views.update_profile, name='update_profile'),
    path('profile/', views.profile, name='profile'),
    path('logout/', views.logout_view, name='logout'),
    path('api/', include(router.urls)),


]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
