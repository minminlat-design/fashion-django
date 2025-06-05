from django.contrib.auth import views as auth_views
from django.urls import path
from accounts import views





urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('logut/', views.logout, name='logout'),
       
    
]
