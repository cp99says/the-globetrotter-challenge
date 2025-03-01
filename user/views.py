from django.http import JsonResponse
from django.views import View
from django.db import transaction
import random
import json
import uuid
from game.models import Game, GameSession
from quiz.models import Clue, Trivia, FunFact, Questionnaire
from .utils import get_funky_response
from .serializer import AnswerSubmissionSerializer
from django.utils.timezone import now
from game.models import GameAttempts


class GameSessionManager:
    @staticmethod
    def create_game():
        """Creates a new game instance."""
        return Game.objects.create(game_status="active")

    @staticmethod
    def create_session(game):
        """Creates a new session for a given game."""
        return GameSession.objects.create(game=game)

    @staticmethod
    def assign_questionnaire(session):
        """Assigns a random questionnaire to the session."""
        questionnaire = Questionnaire.objects.order_by("?").first()
        if not questionnaire:
            return None, "No questionnaires available"
        session.questionnaire = questionnaire
        session.save()
        return questionnaire, None


class StartGameView(View):
    def post(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                game = GameSessionManager.create_game()
                session = GameSessionManager.create_session(game)
                questionnaire, error = GameSessionManager.assign_questionnaire(session)
                if error:
                    return JsonResponse({"error": error}, status=400)

                clues = list(Clue.objects.filter(questionnaire=questionnaire).values_list("text", flat=True))
                if len(clues) < 2:
                    return JsonResponse({"error": "Not enough clues available"}, status=400)

                correct_answer = questionnaire.city
                all_answers = list(Questionnaire.objects.exclude(id=questionnaire.id).values_list("city", flat=True))
                wrong_answers = random.sample(all_answers, min(2, len(all_answers)))

                options = [correct_answer] + wrong_answers
                random.shuffle(options)

                return JsonResponse({
                    "game_id": str(game.id),
                    "session_id": str(session.id),
                    "questionnaire_id": str(questionnaire.id),
                    "question": clues[:2],
                    "options": options
                }, status=201)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)


class StartGameSessionView(View):
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            game_id = data.get("game_id")
            if not game_id:
                return JsonResponse({"error": "game_id is required"}, status=400)

            game = Game.objects.get(id=game_id)
            session = GameSessionManager.create_session(game)
            questionnaire, error = GameSessionManager.assign_questionnaire(session)
            if error:
                return JsonResponse({"error": error}, status=400)

            clues = list(Clue.objects.filter(questionnaire=questionnaire).values_list("text", flat=True))
            if len(clues) < 2:
                return JsonResponse({"error": "Not enough clues available"}, status=400)

            # Generate answer options
            correct_answer = questionnaire.city
            all_answers = list(Questionnaire.objects.exclude(id=questionnaire.id).values_list("city", flat=True))
            wrong_answers = random.sample(all_answers, min(2, len(all_answers)))

            options = [correct_answer] + wrong_answers
            random.shuffle(options)

            return JsonResponse({
                "session_id": str(session.id),
                "questionnaire_id": str(questionnaire.id),
                "question": clues[:2],
                "options": options  # Adding options for user selection
            }, status=201)
        except Game.DoesNotExist:
            return JsonResponse({"error": "Invalid game_id"}, status=404)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)



class EndGameSessionView(View):
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            session_id = data.get("session_id")
            if not session_id:
                return JsonResponse({"error": "session_id is required"}, status=400)

            session = GameSession.objects.get(id=session_id)
            correct_submissions = GameAttempts.objects.filter(session_id=session_id, is_correct=True).count()
            total_attempts = GameAttempts.objects.filter(session_id=session_id).count()

            session.session_status = "completed"
            session.save()

            return JsonResponse({
                "message": "Session ended successfully",
                "correct_submissions": correct_submissions,
                "total_attempts": total_attempts
            }, status=200)
        except GameSession.DoesNotExist:
            return JsonResponse({"error": "Invalid session_id"}, status=404)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)


class EndGameView(View):
    """
    if a game ends, all the session spawned up from that game must end
    """
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            game_id = data.get("game_id")
            if not game_id:
                return JsonResponse({"error": "game_id is required"}, status=400)

            with transaction.atomic():
                game = Game.objects.get(id=game_id)
                GameSession.objects.filter(game=game, session_status="active").update(session_status="completed")
                game.game_status = "completed"
                game.save()

            return JsonResponse({"message": "Game and all associated sessions ended successfully"}, status=200)
        except Game.DoesNotExist:
            return JsonResponse({"error": "Invalid game_id"}, status=404)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)






class GameManager:
    @staticmethod
    def get_game_session(session_id):
        try:
            session = GameSession.objects.get(id=session_id)
            if session.session_status == "completed":
                return None, "This session has already been completed. No further attempts allowed."
            return session, None
        except GameSession.DoesNotExist:
            return None, "Invalid session_id"

    @staticmethod
    def get_questionnaire(questionnaire_id):
        try:
            questionnaire = Questionnaire.objects.get(id=questionnaire_id)
            return questionnaire, None
        except Questionnaire.DoesNotExist:
            return None, "Invalid questionnaire_id"

    @staticmethod
    def process_attempt(game_id, session_id, questionnaire_id, user_response):
        questionnaire, error = GameManager.get_questionnaire(questionnaire_id)
        if error:
            return None, error

        correct_answer = questionnaire.city
        existing_attempts = GameAttempts.objects.filter(session_id=session_id, questionnaire_id=questionnaire_id)
        attempt_number = existing_attempts.count() + 1
        is_correct = user_response.strip().lower() == correct_answer.strip().lower()

        with transaction.atomic():
            attempt = GameAttempts.objects.create(
                game_id=game_id,
                session_id=session_id,
                questionnaire_id=questionnaire_id,
                user_response=user_response,
                is_correct=is_correct,
                attempt_number=attempt_number,
                attempted_at=now(),
            )

            if is_correct:
                fun_facts = list(FunFact.objects.filter(questionnaire=questionnaire).values_list("text", flat=True))
                trivias = list(Trivia.objects.filter(questionnaire=questionnaire).values_list("text", flat=True))
                return {
                    "message": get_funky_response(category="success"),
                    "fun_fact": random.choice(fun_facts) if fun_facts else "No fun fact available.",
                    "trivia": random.choice(trivias) if trivias else "No trivia available.",
                    "attempt_number": attempt_number
                }, None

            if attempt_number == 2:
                session = GameSession.objects.get(id=session_id)
                session.session_status = "completed"
                session.save()
                return {
                    "message": get_funky_response(category="game-over"),
                    "correct_answer": correct_answer,
                    "attempt_number": attempt_number
                }, None

            return {
                "message": get_funky_response(category="failure"),
                "attempt_number": attempt_number
            }, None


class AnswerSubmissionView(View):
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            serializer = AnswerSubmissionSerializer(data=data)

            if not serializer.is_valid():
                return JsonResponse({"error": serializer.errors}, status=400)

            game_id = serializer.validated_data["game_id"]
            session_id = serializer.validated_data["session_id"]
            questionnaire_id = serializer.validated_data["questionnaire_id"]
            user_response = serializer.validated_data["response"]

            session, error = GameManager.get_game_session(session_id)
            if error:
                return JsonResponse({"error": error}, status=403)

            response, error = GameManager.process_attempt(game_id, session_id, questionnaire_id, user_response)
            if error:
                return JsonResponse({"error": error}, status=400)

            return JsonResponse(response, status=200)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON format"}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
