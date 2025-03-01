from django.test import TestCase, Client
from django.urls import reverse
from game.models import Game, GameSession, GameAttempts, GameInvitee, GameLink
from quiz.models import Questionnaire, Clue, Trivia, FunFact
from .models import User
import json

class GameAPITestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.game = Game.objects.create(game_status="active")
        self.user = User.objects.create(username="testuser")
        self.session = GameSession.objects.create(game=self.game, user=self.user)
        self.questionnaire = Questionnaire.objects.create(city="Paris")
        self.clue1 = Clue.objects.create(questionnaire=self.questionnaire, text="It's known as the city of love.")
        self.clue2 = Clue.objects.create(questionnaire=self.questionnaire, text="It has the Eiffel Tower.")
        self.fun_fact = FunFact.objects.create(questionnaire=self.questionnaire, text="Paris has over 130 museums.")
        self.trivia = Trivia.objects.create(questionnaire=self.questionnaire, text="The Louvre is the world's most visited museum.")

    def test_start_game(self):
        response = self.client.post(reverse("start-game"))
        self.assertEqual(response.status_code, 201)
        self.assertIn("game_id", response.json())

    def test_submit_correct_answer(self):
        data = {
            "game_id": str(self.game.id),
            "session_id": str(self.session.id),
            "questionnaire_id": str(self.questionnaire.id),
            "response": "Paris",
            "user_id": str(self.user.id)
        }
        response = self.client.post(reverse("submit-answer"), data=json.dumps(data), content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.assertIn("message", response.json())
        self.assertIn("fun_fact", response.json())

    def test_submit_wrong_answer(self):
        data = {
            "game_id": str(self.game.id),
            "session_id": str(self.session.id),
            "questionnaire_id": str(self.questionnaire.id),
            "response": "London",
            "user_id": str(self.user.id)
        }
        response = self.client.post(reverse("submit-answer"), data=json.dumps(data), content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.assertIn("message", response.json())

    def test_end_game_session(self):
        data = {"session_id": str(self.session.id)}
        response = self.client.post(reverse("end-session"), data=json.dumps(data), content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["message"], "Session ended successfully")

    def test_end_game(self):
        data = {"game_id": str(self.game.id)}
        response = self.client.post(reverse("end-game"), data=json.dumps(data), content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["message"], "Game and all associated sessions ended successfully")

    def test_create_invite_link(self):
        data = {
            "username": "newplayer",
            "game_id": str(self.game.id),
            "session_id": str(self.session.id),
            "user_id": str(self.user.id)
        }
        response = self.client.post(reverse("invite-link"), data=json.dumps(data), content_type="application/json")
        self.assertEqual(response.status_code, 201)
        self.assertIn("invite_link", response.json())

    def test_join_session(self):
        invite_code = "test123"
        GameLink.objects.create(game=self.game, session=self.session, link=invite_code)
        data = {"invite_code": invite_code, "username": "joiner"}
        response = self.client.post(reverse("join-session"), data=json.dumps(data), content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["message"], "You've successfully joined the session! Let's play!")

    def test_view_friend_score(self):
        GameInvitee.objects.create(game=self.game, session=self.session, invitor=self.user, invitee=self.user)
        data = {"username": "testuser"}
        response = self.client.get(reverse("view-friend-score"), data)
        self.assertEqual(response.status_code, 200)
        self.assertIn("correct_answers", response.json())

    def test_next_question(self):
        data = {
            "session_id": str(self.session.id),
            "game_id": str(self.game.id),
            "user_id": str(self.user.id),
            "current_question_id": str(self.questionnaire.id)
        }
        response = self.client.get(reverse("next-question"), data)
        self.assertEqual(response.status_code, 200)
