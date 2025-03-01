from django.urls import path
from .views import StartGameView, AnswerSubmissionView

urlpatterns = [
    path("start-game/", StartGameView.as_view(), name="start-game"),
    path("submit-answer/", AnswerSubmissionView.as_view(), name="submit-answer"),
]