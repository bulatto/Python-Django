# recruiting URL Configuration
from django.contrib import admin
from django.urls import path
from recruiting_app import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index),
    path('recruit/', views.recruit),
    path('sith/<int:sith_id>/', views.sith_office),
    path('sith/', views.sith),
    path('testpage/<int:recruit_id>/', views.testpage),
    path('choice/', views.choice),
    path('sith/info/', views.sith_info)
]
