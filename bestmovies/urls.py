from django.urls import path
from django.conf import settings

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('individual_movie_information', views.individual_movie_information, name='individual_movie_information'),
]
