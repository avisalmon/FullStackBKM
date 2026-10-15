from rest_framework import serializers

from .models import Note


class NoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Note
        fields = ["id", "title", "body", "image", "created_at", "updated_at"]
        # Ownership is never client-supplied. Two independent things hold this:
        # `owner` is not a serializer field at all, and the viewset's perform_create
        # sets it from the session. Tests break each separately.
        read_only_fields = ["id", "created_at", "updated_at"]
