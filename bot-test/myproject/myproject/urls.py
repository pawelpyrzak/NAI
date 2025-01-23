from django.urls import path
from myapp import views


urlpatterns = [
    path('', views.homepage, name='homepage'),  
    path('tasks/', views.tasks, name='tasks'),  
    path('singleTask/', views.singleTask, name='singleTask'), 
    path('calendar/', views.calendar, name='calendar'),  
    path('calendar/month/', views.calendar_month, name='calendar_month'),
    path('calendar/week/', views.calendar_week, name='calendar_week'),
    path('calendar/day/', views.calendar_day, name='calendar_day'),
    path('teams/', views.teams, name='teams'),  
    path('teamPage/', views.teamPage, name='teamPage'),  
    path('projects/', views.projects, name='projects'),
    path('projects/board', views.projects_board, name='projects-board'),
    path('project/', views.project, name='project'),
    path('task/', views.task, name='task'),
    path('task-list/', views.task_list, name='task_list'),
    path('posts-content/', views.posts_content, name='posts_content'),
    path('files-content/', views.files_content, name='files_content'),
    path('chat/', views.get_bot_response, name='chat_with_main_bot'),
    path('load-reminder-content/<str:view_type>/', views.load_reminder_content, name='load_reminder_content'),
    path('load-task-content/<str:view_type>/', views.load_task_content, name='load_task_content'),
    path('get_calendar_widget/', views.get_calendar_widget, name='get_calendar_widget'),
    

]
