from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema
from .models import Language
from .serializers import LanguageSerializer

class LanguageView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=LanguageSerializer,
        responses={201: LanguageSerializer},
        summary="Submit Language Records",
        description="Authenticated users can submit multiple language entries at once"
    )
    def post(self, request):
        user = request.user
        languages = request.data.get("languages", [])
        created_entries = []

        for lang in languages:
            serializer = LanguageSerializer(data=lang, context={'request': request})
            if serializer.is_valid():
                # Attach the authenticated user here
                serializer.save(user=user)
                created_entries.append(serializer.data)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            {"message": "Languages submitted successfully", "data": created_entries},
            status=status.HTTP_201_CREATED
        )

    @extend_schema(
        responses=LanguageSerializer,
        summary="Get all language records for authenticated user"
    )
    def get(self, request):
        language_records = Language.objects.filter(user=request.user)
        serializer = LanguageSerializer(language_records, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class LanguageDetailView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={200: LanguageSerializer},
        summary="Retrieve a single language record by ID"
    )
    def get(self, request, pk):
        try:
            language = Language.objects.get(pk=pk, user=request.user)
        except Language.DoesNotExist:
            return Response({"error": "Language record not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = LanguageSerializer(language)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        request=LanguageSerializer,
        responses={200: LanguageSerializer},
        summary="Update a language record by ID"
    )
    def put(self, request, pk):
        try:
            language = Language.objects.get(pk=pk, user=request.user)
        except Language.DoesNotExist:
            return Response({"error": "Language record not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = LanguageSerializer(language, data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Language record updated successfully", "data": serializer.data})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        responses={204: None},
        summary="Delete a language record by ID"
    )
    def delete(self, request, pk):
        try:
            language = Language.objects.get(pk=pk, user=request.user)
        except Language.DoesNotExist:
            return Response({"error": "Language record not found"}, status=status.HTTP_404_NOT_FOUND)
        language.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
