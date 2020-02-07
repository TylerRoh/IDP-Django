from django.urls import path

from . import views

urlpatterns = [
    #/defense/         this is the main page
    path('', views.index, name='index'),
    # /defense/custom      this is the view to add custom scoring options
    path('custom/', views.test, name='test'),
    #/defense/player/stats_player_id#/          this is the player detail page
    path('player/<str:player_id>/', views.player_indv, name='player_indv'),
    #/defense/position/"db,lb or dl"            this is the view that will show the top in position groups
    path('position/<str:position>/', views.position_group, name='position_group')
]
