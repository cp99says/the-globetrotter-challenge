from django.urls import path
from .views import StartGameView, AnswerSubmissionView, EndGameSessionView, EndGameView

urlpatterns = [
    path("start-game/", StartGameView.as_view(), name="start-game"),
    path("submit-answer/", AnswerSubmissionView.as_view(), name="submit-answer"),
    path("end-session/", EndGameSessionView.as_view(), name="end-session"),
    path("end-game/", EndGameView.as_view(), name="end-game"),
]