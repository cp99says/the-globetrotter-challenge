from django.urls import path, include

urlpatterns = [
    path("api/", include("user.urls")),  # Make sure this is included!
    path("api/", include("quiz.urls"))
]
