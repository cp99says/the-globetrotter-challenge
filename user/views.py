from django.http import JsonResponse
from django.views import View
from django.db import transaction
import random
import json
import uuid
from game.models import Game, GameSession, GameLink, GameInvitee
from quiz.models import Clue, Trivia, FunFact, Questionnaire
from .utils import get_funky_response, generate_invite_code, generate_random_username
from .models import User
from .serializer import AnswerSubmissionSerializer
from django.utils.timezone import now
from game.models import GameAttempts


class GameSessionManager:
    @staticmethod
    def create_game():
        """Creates a new game instance."""
        return Game.objects.create(game_status="active")

    @staticmethod
    def create_session(game, user):
        """Creates a new session for a given game."""
        return GameSession.objects.create(game=game, user=user)

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
                user = User.objects.create(username=generate_random_username())
                session = GameSessionManager.create_session(game, user)
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
                    "user_id": str(user.id),
                    "question": clues[:2],
                    "options": options
                }, status=201)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)


# class StartGameSessionView(View):
#     def post(self, request, *args, **kwargs):
#         try:
#             data = json.loads(request.body)
#             game_id = data.get("game_id")
#             if not game_id:
#                 return JsonResponse({"error": "game_id is required"}, status=400)
#
#             game = Game.objects.get(id=game_id)
#             session = GameSessionManager.create_session(game)
#             questionnaire, error = GameSessionManager.assign_questionnaire(session)
#             if error:
#                 return JsonResponse({"error": error}, status=400)
#
#             clues = list(Clue.objects.filter(questionnaire=questionnaire).values_list("text", flat=True))
#             if len(clues) < 2:
#                 return JsonResponse({"error": "Not enough clues available"}, status=400)
#
#             # Generate answer options
#             correct_answer = questionnaire.city
#             all_answers = list(Questionnaire.objects.exclude(id=questionnaire.id).values_list("city", flat=True))
#             wrong_answers = random.sample(all_answers, min(2, len(all_answers)))
#
#             options = [correct_answer] + wrong_answers
#             random.shuffle(options)
#
#             return JsonResponse({
#                 "session_id": str(session.id),
#                 "questionnaire_id": str(questionnaire.id),
#                 "question": clues[:2],
#                 "options": options  # Adding options for user selection
#             }, status=201)
#         except Game.DoesNotExist:
#             return JsonResponse({"error": "Invalid game_id"}, status=404)
#         except Exception as e:
#             return JsonResponse({"error": str(e)}, status=500)



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
    def process_attempt(game_id, session_id, questionnaire_id, user_response, user):
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
                user=user,
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

            if not is_correct and attempt_number == 1:
                return JsonResponse({
                    "message": get_funky_response(category="failure"),
                    "attempt_number": attempt_number
                }, status=200)

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
            user_id = serializer.validated_data["user_id"]


            session, error = GameManager.get_game_session(session_id)
            if error:
                return JsonResponse({"error": error}, status=403)

            user = User.objects.filter(id=user_id).first()

            response, error = GameManager.process_attempt(game_id, session_id, questionnaire_id, user_response, user)
            if error:
                return JsonResponse({"error": error}, status=400)

            return JsonResponse(response, status=200)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON format"}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)


class CreateInviteLinkView(View):
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            username = data.get("username")
            game_id = data.get("game_id")
            session_id = data.get("session_id")
            user_id = data.get("user_id")

            if not (username and game_id and session_id and user_id):
                return JsonResponse({"error": "username, game_id, session_id, and user_id are required"}, status=400)

            # Check if user_id exists
            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                return JsonResponse({"error": "Invalid user_id"}, status=404)

            # Ensure the provided username is not already taken by another user
            if User.objects.filter(username=username).exclude(id=user_id).exists():
                return JsonResponse({"error": "Username is already taken by another user"}, status=400)

            # Update username if all checks pass
            user.username = username
            user.user_type = "registered"
            user.save()

            session = GameSession.objects.get(id=session_id, game_id=game_id)

            # Ensure the inviter joins the session
            game_invitee, invitee_created = GameInvitee.objects.get_or_create(
                game=session.game, session=session, invitee=user,
                defaults={"invitor": user}  # The inviter joins as a player
            )

            if not invitee_created:
                # If the inviter already joined, ensure they are marked as the inviter
                if game_invitee.invitor != user:
                    game_invitee.invitor = user
                    game_invitee.save()

            # Update GameSession to set the user
            if session.user is None:
                session.user = user
                session.save()

            # Generate or retrieve an existing invite link
            game_link, created = GameLink.objects.get_or_create(game=session.game, session=session)
            if not created:
                return JsonResponse({
                    "message": "Invite link already exists",
                    "invite_link": f"https://dem-game.com/invite/{game_link.link}"
                }, status=200)

            invite_code = generate_invite_code()
            game_link.link = invite_code
            game_link.save()

            invite_link = f"https://dem-game.com/invite/{invite_code}"
            return JsonResponse({"invite_link": invite_link}, status=201)

        except GameSession.DoesNotExist:
            return JsonResponse({"error": "Invalid session_id"}, status=404)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)


class JoinSessionView(View):
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            invite_code = data.get("invite_code")
            username = data.get("username")

            if not (invite_code and username):
                return JsonResponse({"error": "invite_code and username are required"}, status=400)

            if User.objects.filter(username=username).exists():
                return JsonResponse({"error": "Username already exists"}, status=400)

            if not GameLink.objects.filter(link=invite_code).exists():
                return JsonResponse({"error": "This invite code does not exist in our system"}, status=404)

            game_link = GameLink.objects.get(link=invite_code)
            session = game_link.session
            game = session.game

            if not session.user:
                return JsonResponse({"error": "Session does not have a valid invitor"}, status=400)

            with transaction.atomic():
                invitee = User.objects.create(username=username, user_type="registered")
                GameInvitee.objects.create(game=game, session=session, invitor=session.user, invitee=invitee)

            return JsonResponse({
                "message": "You've successfully joined the session! Let's play!"
            }, status=200)
        except GameLink.DoesNotExist:
            return JsonResponse({"error": "Invalid invite code"}, status=404)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)


class ViewFriendScoreView(View):
    def get(self, request, *args, **kwargs):
        try:
            invitee_username = request.GET.get("username")

            if not invitee_username:
                return JsonResponse({"error": "Username is required"}, status=400)

            invitee = User.objects.get(username=invitee_username)
            game_invitee = GameInvitee.objects.get(invitee=invitee)
            invitor = game_invitee.invitor

            corrects = GameAttempts.objects.filter(game=game_invitee.game, session=game_invitee.session,
                                                   is_correct=True).count()
            incorrects = GameAttempts.objects.filter(game=game_invitee.game, session=game_invitee.session,
                                                     is_correct=False).count()
            attempts = GameAttempts.objects.filter(game=game_invitee.game, session=game_invitee.session).count()

            return JsonResponse({
                "invitor": invitor.username,
                "correct_answers": corrects,
                "incorrect_answers": incorrects,
                "total_attempts": attempts
            }, status=200)
        except User.DoesNotExist:
            return JsonResponse({"error": "User not found"}, status=404)
        except GameInvitee.DoesNotExist:
            return JsonResponse({"error": "Invitee has not joined any game"}, status=404)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)


class NextQuestionView(View):
    def get(self, request, *args, **kwargs):
        try:
            session_id = request.GET.get("session_id", "").strip()
            game_id = request.GET.get("game_id", "").strip()
            user_id = request.GET.get("user_id", "").strip()
            current_question_id = request.GET.get("current_question_id", "").strip()

            if not (session_id and game_id and user_id):
                return JsonResponse({"error": "session_id, game_id, and user_id are required"}, status=400)

                # Validate session
            try:
                session = GameSession.objects.get(id=session_id, game_id=game_id)
            except GameSession.DoesNotExist:
                return JsonResponse({"error": "Invalid session_id or game_id"}, status=404)

                # Fetch next question different from the current question
            next_question = Questionnaire.objects.exclude(id=current_question_id).first()
            clues = list(Clue.objects.filter(questionnaire=next_question).values_list("text", flat=True))
            correct_answer = next_question.city
            all_answers = list(Questionnaire.objects.exclude(id=next_question.id).values_list("city", flat=True))
            wrong_answers = random.sample(all_answers, min(2, len(all_answers)))

            options = [correct_answer] + wrong_answers
            random.shuffle(options)
            if not next_question:
                return JsonResponse({"message": "No more questions available. Game completed!"}, status=200)

            return JsonResponse({
                    "session_id": session_id,
                    "game_id": game_id,
                    "user_id": user_id,
                    "question_id": next_question.id,
                    "options": options,
                    "clue": clues
                }, status=200)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

