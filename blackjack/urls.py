from django.urls import path
from . import views

urlpatterns = [
    path('blackjack/', views.blackjack_page, name='blackjack_page'),
    path('blackjack/start/', views.blackjack_start, name='blackjack_start'),
    path('blackjack/hit/', views.blackjack_hit, name='blackjack_hit'),
    path('blackjack/stand/', views.blackjack_stand, name='blackjack_stand'),
]
