from django.urls import path
from .views import StartGameView, AnswerSubmissionView, EndGameSessionView, EndGameView, CreateInviteLinkView, JoinSessionView, ViewFriendScoreView, NextQuestionView

urlpatterns = [
    path("start-game/", StartGameView.as_view(), name="start-game"),
    path("submit-answer/", AnswerSubmissionView.as_view(), name="submit-answer"),
    path("next-question/", NextQuestionView.as_view(), name="next-question"),
    path("end-session/", EndGameSessionView.as_view(), name="end-session"),
    path("end-game/", EndGameView.as_view(), name="end-game"),
    path('invite-link', CreateInviteLinkView.as_view(), name='invite-link'),
    path('join-session/', JoinSessionView.as_view(), name='join-session'),
    path('view-friend-score/', ViewFriendScoreView.as_view(), name='view-friend-score'),

]