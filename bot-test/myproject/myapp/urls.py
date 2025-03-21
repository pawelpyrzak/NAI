from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r'tasks', views.TaskViewSet)

router.register(r'events', views.EventViewSet)
router.register(r'notifications', views.NotificationViewSet)

urlpatterns = [
    path('home/', views.homepage, name='homepage'),
    path('chatbot/', views.chatbot_view, name='chatbot'),

    path('tasks/', views.tasks, name='tasks'),
    path('tasks/create', views.create_task_view, name='create_task_view'),

    path('task/<int:task_id>/', views.singleTask, name='singleTask'),
    path('task/<int:task_id>/add_comment', views.add_comment, name='add_comment'),
    path('task/<int:task_id>/comment/<int:comment_id>/add_reply', views.add_reply, name='add_reply'),
    path('task/<int:task_id>/update_task', views.edit_task, name='edit_task'),

    path('calendar/', views.calendar, name='calendar'),

    path('teams/', views.teams, name='teams'),
    path('teams/create', views.create_group, name='teamCreate'),
    path('teams/join', views.join_group, name='teamJoin'),
    # path('reminders/', views.reminders_page, name='reminders_page'),

    path('teams/<int:group_id>/', views.team_page, name='teamPage'),
    path('teams/<int:group_id>/info/', views.GroupInfoView.as_view(), name='group_info'),

    path('teams/<int:group_id>/events/', views.event_list, name='event_list'),

    path('teams/<int:group_id>/files/', views.manage_files, name='manage_files'),
    path('teams/<int:group_id>/files/upload/', views.upload_file, name='upload_file'),
    path('teams/<int:group_id>/files/delete/<uuid:file_uuid>/', views.delete_file, name='delete_file'),
    path('file/download/<uuid:qdrant_id>/', views.download_file, name='download_file'),

    path('teams/<int:group_id>/projects/', views.group_projects, name='group_projects'),
    path('teams/<int:group_id>/projects/add/<str:jira_project_key>/', views.add_jira_project, name='add_jira_project'),
    path('teams/<int:group_id>/projects/create/', views.create_project, name='create_project'),

    path('teams/<int:group_id>/messages/', views.messages_view, name='messages'),
    path('teams/<int:group_id>/messages/slack/', views.slack_messages_view, name='slack_messages'),
    path('teams/<int:group_id>/messages/discord/', views.discord_messages_view, name='discord_messages'),

    path('teams/<int:group_id>/platforms/', views.view_platforms, name='group_platforms'),

    path('teams/<int:group_id>/trello_user_match/', views.trello_user_match, name='trello_user_match'),
    path('teams/<int:group_id>/trello_user_match/<str:trello_user_id>/', views.link_trello_user, name='link_trello_user'),

    path('teams/<int:group_id>/jira_user_match/', views.jira_user_match, name='jira_user_match'),
    path('teams/<int:group_id>/link_jira_user/<str:jira_user_id>/', views.link_jira_user, name='link_jira_user'),

    path('projects/', views.projects, name='projects'),
    path('projects/board', views.projects_board, name='projects-board'),

    path('project/<int:project_id>', views.project, name='project'),
    path('project/<int:project_id>/update_project', views.edit_project, name='edit_project'),

    path('posts-content/', views.posts_content, name='posts_content'),

    # path('chat/', views.get_bot_response, name='chat_with_main_bot'),
    path('register/', views.register, name='register'),
    path('registerr/', views.profile_update, name='profile_update'),
    path('login/', views.custom_login, name='login'),
    path('', views.home, name='home'),
    # path('update-profile/', update_profile, name='update_profile'),
    path('profile/', views.profile, name='profile'),
    path('logout/', views.logout_view, name='logout'),
    path('api/', include(router.urls)),

    path("load-user-statistics/", views.get_statistics, name="get_statistics"),
    path('load-reminder-content/<str:view_type>/', views.load_reminder_content, name='load_reminder_content'),
    path('load-task-content/<str:view_type>/', views.load_task_content, name='load_task_content'),
    path('load-project-content/<str:view_type>/', views.load_project_content, name='load_task_content'),

    path("update-widget-order/", views.update_widget_order, name="update_widget_order"),
    path("get-widget-settings/", views.get_widget_settings, name="get_widget_settings"),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
