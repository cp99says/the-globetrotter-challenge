from django.urls import path
from .views import QuestionnaireCreateView

urlpatterns = [
    path("create-questionnaire/", QuestionnaireCreateView.as_view(), name="create_questionnaire"),
]
