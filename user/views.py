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


class StartGameView(View):
    def post(self, request, *args, **kwargs):
        try:
            with transaction.atomic():  # Ensure atomicity
                game = Game.objects.create(game_status="active") #geme creation

                session = GameSession.objects.create(game=game) #game session creation

                questionnaire = Questionnaire.objects.order_by("?").first() #random question selection
                if not questionnaire:
                    return JsonResponse({"error": "No questionnaires available"}, status=400)

                clues = list(Clue.objects.filter(questionnaire=questionnaire).values_list("text", flat=True)) #fetch clues for the quiz id in line 19
                if len(clues) < 2:
                    return JsonResponse({"error": "Not enough clues available"}, status=400)

                correct_answer = questionnaire.city
                all_answers = list(Questionnaire.objects.exclude(id=questionnaire.id).values_list("city", flat=True))
                wrong_answers = random.sample(all_answers, min(2, len(all_answers)))

                options = [correct_answer] + wrong_answers
                random.shuffle(options)  # Shuffle options

                session.questionnaire = questionnaire
                session.save() #commiting the transactions

                # Step 7: Return response
                return JsonResponse({
                    "game_id": str(game.id),
                    "session_id": str(session.id),
                    "questionnaire_id": str(questionnaire.id),
                    "question": clues[:2],  # Send only two clues
                    "options": options
                }, status=201)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)




class AnswerSubmissionView(View):
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            serializer = AnswerSubmissionSerializer(data=data)

            if not serializer.is_valid():
                return JsonResponse({"error": serializer.errors}, status=400)

            try:
                game_id = uuid.UUID(serializer.validated_data["game_id"])  # No need for .replace("-", "")
                session_id = uuid.UUID(serializer.validated_data["session_id"])
                questionnaire_id = uuid.UUID(serializer.validated_data["questionnaire_id"])
            except ValueError:
                return JsonResponse({"error": "Invalid UUID format"}, status=400)

            game_id = serializer.validated_data["game_id"]
            session_id = serializer.validated_data["session_id"]
            questionnaire_id = serializer.validated_data["questionnaire_id"]
            user_response = serializer.validated_data["response"]


            # Fetch game session and check if it's active
            try:
                session = GameSession.objects.get(id=session_id)
                if session.session_status == "completed":
                    return JsonResponse({"error": "This session has already been completed. No further attempts allowed."}, status=403)
            except GameSession.DoesNotExist:
                return JsonResponse({"error": "Invalid session_id"}, status=404)

            # Fetch correct answer from the Questionnaire
            try:
                questionnaire = Questionnaire.objects.get(id=questionnaire_id)
                correct_answer = questionnaire.city
            except Questionnaire.DoesNotExist:
                return JsonResponse({"error": "Invalid questionnaire_id"}, status=404)

            existing_attempts = GameAttempts.objects.filter(session_id=session_id, questionnaire_id=questionnaire_id)
            attempt_count = existing_attempts.count()

            print(attempt_count)

            with transaction.atomic():
                # Create a new attempt record
                is_correct = user_response.strip().lower() == correct_answer.strip().lower()
                attempt_number = attempt_count + 1
                print('attempt_number ->', attempt_number)
                attempt = GameAttempts.objects.create(
                    game_id=game_id,
                    session_id=session_id,
                    questionnaire_id=questionnaire_id,
                    user_response=user_response,
                    is_correct=is_correct,
                    attempt_number=attempt_number,
                    attempted_at=now(),
                )


                # Successful attempt
                if is_correct:
                    fun_facts = list(FunFact.objects.filter(questionnaire=questionnaire).values_list("text", flat=True))
                    trivias = list(Trivia.objects.filter(questionnaire=questionnaire).values_list("text", flat=True))

                    fun_fact = random.choice(fun_facts) if fun_facts else "No fun fact available."
                    trivia = random.choice(trivias) if trivias else "No trivia available."

                    return JsonResponse({
                        "message": get_funky_response(category="success"),
                        "fun_fact": fun_fact,
                        "trivia": trivia,
                        "attempt_number": attempt_number
                    }, status=200)

                # Failed attempt # 1
                if not is_correct and attempt_number == 1:
                    print("inside failed #1", attempt_number)
                    return JsonResponse({
                        "message": get_funky_response(category="failure"),
                        "attempt_number": attempt_number
                    }, status=200)

                # Failed attempt # 2
                if not is_correct and attempt_number >= 2:
                    session.session_status = "completed" # end session
                    session.save()
                    return JsonResponse({
                        "message": get_funky_response(category="game-over"),
                        "correct_answer": correct_answer,
                        "attempt_number": attempt_number
                    }, status=200)


                return JsonResponse({
                    "message": "Try again",
                    "attempt_number": attempt_number
                }, status=200)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON format"}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)