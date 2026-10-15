from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from rest_framework import viewsets

from .models import Note
from .serializers import NoteSerializer


class NoteViewSet(viewsets.ModelViewSet):
    """Full CRUD for the signed-in person's own notes.

    list / create:            /notes/api/notes/
    retrieve/update/destroy:  /notes/api/notes/<id>/

    Browse and try it at those URLs while signed in: DRF's browsable API is the
    documentation (docs/building_an_app.md, Rule 6).
    """

    serializer_class = NoteSerializer
    # Permission comes from REST_FRAMEWORK's deny-by-default (IsAuthenticated).

    def get_queryset(self):
        # Scoping the queryset (not checking in each method) means another person's
        # note is a 404 for retrieve, update AND delete: it does not exist for you.
        return Note.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class NotesPage(LoginRequiredMixin, TemplateView):
    """The screen is just one consumer of the API above."""

    template_name = "notes/list.html"
