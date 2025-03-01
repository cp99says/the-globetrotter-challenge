from django.db import transaction
from game.models import Game, GameSession

class UserService:
    @staticmethod
    def create_game_session():
        """Creates a new game session for an anonymous user."""
        try:
            with transaction.atomic():
                game = Game.objects.create()
                game_session = GameSession.objects.create(game=game)

                return {"game_id": game.id, "game_session_id": game_session.id}

        except Exception as e:
            return {"error": str(e)}