from rest_framework.views import APIView # type: ignore
from rest_framework.response import Response # pyright: ignore[reportMissingImports]
from rest_framework import status, permissions # type: ignore
from django.shortcuts import get_object_or_404
from .models import Letter
from .serializers import LetterSerializer
from .services.letter_ai import generate_clean_letter


class GenerateLetterAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        """
        Accept letter fields, return AI-cleaned professional letter body.
        """
        data = request.data
        # Inject user info if needed
        data.setdefault("sender", request.user.get_full_name())
        ai_response = generate_clean_letter(data)
        return Response(ai_response, status=status.HTTP_200_OK)



class LetterListCreateAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """
        List all letters for the authenticated user.
        """
        letters = Letter.objects.filter(user=request.user)
        serializer = LetterSerializer(letters, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        """
        Create a new letter (can include AI-cleaned fields).
        """
        serializer = LetterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LetterDetailAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, pk, user):
        return get_object_or_404(Letter, pk=pk, user=user)

    def get(self, request, pk):
        """
        Retrieve a single letter.
        """
        letter = self.get_object(pk, request.user)
        serializer = LetterSerializer(letter)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        """
        Update a letter completely.
        """
        letter = self.get_object(pk, request.user)
        serializer = LetterSerializer(letter, data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        """
        Partially update a letter.
        """
        letter = self.get_object(pk, request.user)
        serializer = LetterSerializer(letter, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        """
        Delete a letter.
        """
        letter = self.get_object(pk, request.user)
        letter.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
