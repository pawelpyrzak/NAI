from django.urls import path
from myapp import views


urlpatterns = [
    path('', views.homepage, name='homepage'),  
    path('tasks/', views.tasks, name='tasks'),  
    path('calendar/', views.calendar, name='calendar'),  
    path('teams/', views.teams, name='teams'),  
    path('teamPage/', views.teamPage, name='teamPage'),  
    path('chat/', views.get_bot_response, name='chat_with_main_bot'),
]
