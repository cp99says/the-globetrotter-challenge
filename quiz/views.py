from django.http import JsonResponse
from django.views import View
import json
from .models import Questionnaire, Clue, FunFact, Trivia
from django.db import transaction


class QuestionnaireCreateView(View):
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)

            # Ensure the "data" key exists in request
            if "data" not in data or not isinstance(data["data"], list):
                return JsonResponse({"error": "'data' key must be present and contain a list"}, status=400)

            questionnaire_entries = data["data"]
            created_questionnaires = []

            with transaction.atomic():  # Ensures all entries are committed together
                for entry in questionnaire_entries:
                    city = entry.get("city")
                    country = entry.get("country")
                    clues = entry.get("clues", [])
                    fun_facts = entry.get("fun_fact", [])
                    trivia = entry.get("trivia", [])

                    if not city or not country:
                        return JsonResponse({"error": "City and country are required"}, status=400)

                    # Create Questionnaire instance
                    questionnaire = Questionnaire.objects.create(city=city, country=country)

                    # Create Clues
                    for clue_text in clues:
                        Clue.objects.create(questionnaire=questionnaire, text=clue_text)

                    # Create Fun Facts
                    for fact_text in fun_facts:
                        FunFact.objects.create(questionnaire=questionnaire, text=fact_text)

                    # Create Trivia
                    for trivia_text in trivia:
                        Trivia.objects.create(questionnaire=questionnaire, text=trivia_text)

                    created_questionnaires.append({
                        "id": str(questionnaire.id),
                        "city": questionnaire.city,
                        "country": questionnaire.country
                    })

            return JsonResponse({"message": "Questionnaire(s) created successfully", "data": created_questionnaires},
                                status=201)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON format"}, status=400)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
