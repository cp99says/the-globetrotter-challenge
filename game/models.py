from django.db import models
from uuid6 import uuid7
from user.models import User

class GameStatus(models.TextChoices):
    ACTIVE = "active", "Active"
    COMPLETED = "completed", "Completed"

class Game(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid7, editable=False)
    game_status = models.CharField(
        max_length=10, choices=GameStatus.choices, default=GameStatus.ACTIVE
    )

class GameLink(models.Model):
    game = models.OneToOneField(Game, on_delete=models.CASCADE)
    link = models.TextField(unique=True)

class GameSession(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid7, editable=False)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    user = models.ForeignKey("user.User", on_delete=models.CASCADE, null=True, blank=True)
    score = models.IntegerField(default=0)

class GameInvitee(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid7, editable=False)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    invitor = models.ForeignKey(User, on_delete=models.CASCADE, related_name="invites_sent")
    invitee = models.ForeignKey(User, on_delete=models.CASCADE, related_name="invites_received")

class Leaderboard(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid7, editable=False)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    score = models.IntegerField()
    rank = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
