from rest_framework import serializers

class AnswerSubmissionSerializer(serializers.Serializer):
    game_id = serializers.CharField(max_length=36)  # Store as string
    session_id = serializers.CharField(max_length=36)
    questionnaire_id = serializers.CharField(max_length=36)
    response = serializers.CharField(max_length=255)
