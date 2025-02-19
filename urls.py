from django.urls import path
from . import views

urlpatterns = [
    path('home/', views.home, name='home'),  # Maps root URL to `home` view
    #path('about/', views.about, name='about'),  # Example additional route
]
