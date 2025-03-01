from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .services import UserService
class StartGameView(APIView):
    def post(self, request):
        """Start a game session for an anonymous user"""
        result = UserService.create_game_session()

        if "error" in result:
            return Response(result, status=status.HTTP_400_BAD_REQUEST)

        return Response(result, status=status.HTTP_200_OK)


