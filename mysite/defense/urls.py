from django.urls import path

from . import views

urlpatterns = [
    #/defense/
    path('', views.index, name='index'),
    # this is going to be my graph example
    path('custom/', views.test, name='test'),
    #/defense/player/stats_player_id#/
    path('player/<str:player_id>/', views.player_indv, name='player_indv'),
    #this will be the path to me testing a new database search engine using ajax
    path('ajax_demo/', views.ajax_demo, name='ajax_demo'),
]
