from django.urls import include, path
from rest_framework.routers import SimpleRouter

from . import views

app_name = "notes"

router = SimpleRouter()
router.register("api/notes", views.NoteViewSet, basename="note")

urlpatterns = [
    path("", views.NotesPage.as_view(), name="list"),
    path("", include(router.urls)),
]
