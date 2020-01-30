from django.urls import path

from . import views

urlpatterns = [
    #/polls/
    path('', views.index, name='index'),
    #/polls/id#
    path('<int:question_id>/', views.detail, name='detail'),  #the brackets tell it to pass the id as a kwarg
    #/polls/id#/results
    path('<int:question_id>/results/', views.results, name='results'),
    #/polls/id#/vote
    path('<int:question_id>/vote/', views.vote, name='vote'),
]
