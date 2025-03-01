from django.urls import path
from .views import StartGameView

urlpatterns = [
    path("start-game/", StartGameView.as_view(), name="start-game"),
]