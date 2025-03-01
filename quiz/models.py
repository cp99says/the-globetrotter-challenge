from django.db import models
from uuid6 import uuid7

class Questionnaire(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid7, editable=False)
    city = models.CharField(max_length=255)
    country = models.CharField(max_length=255)

class Clue(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid7, editable=False)
    questionnaire = models.ForeignKey(Questionnaire, related_name="clues", on_delete=models.CASCADE)
    text = models.TextField()

class FunFact(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid7, editable=False)
    questionnaire = models.ForeignKey(Questionnaire, related_name="fun_facts", on_delete=models.CASCADE)
    text = models.TextField()

class Trivia(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid7, editable=False)
    questionnaire = models.ForeignKey(Questionnaire, related_name="trivia", on_delete=models.CASCADE)
    text = models.TextField()
