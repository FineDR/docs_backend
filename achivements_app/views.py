from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema
from .models import AchievementProfile
from .serializers import AchievementProfileSerializer

class AchievementProfileView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=AchievementProfileSerializer,
        responses={200: None},
        summary="Create or update achievements",
    )
    def post(self, request):
        serializer = AchievementProfileSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Achievements saved successfully"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        responses=AchievementProfileSerializer,
        summary="Retrieve achievements",
    )
    def get(self, request):
        try:
            profile = request.user.achievement_profile
            serializer = AchievementProfileSerializer(profile)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except AchievementProfile.DoesNotExist:
            return Response({"detail": "Achievements not found."}, status=status.HTTP_404_NOT_FOUND)

    @extend_schema(
        request=AchievementProfileSerializer,
        responses=AchievementProfileSerializer,
        summary="Update achievements",
    )
    def put(self, request):
        try:
            profile = request.user.achievement_profile
            serializer = AchievementProfileSerializer(profile, data=request.data, partial=True, context={'request': request})
            if serializer.is_valid():
                serializer.save()
                return Response({"message": "Achievements updated successfully", "data": serializer.data}, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except AchievementProfile.DoesNotExist:
            return Response({"detail": "Achievements not found."}, status=status.HTTP_404_NOT_FOUND)

    @extend_schema(
        responses={200: None},
        summary="Delete achievements",
    )
    def delete(self, request):
        try:
            profile = request.user.achievement_profile
            profile.delete()
            return Response({"message": "Achievements deleted successfully"}, status=status.HTTP_200_OK)
        except AchievementProfile.DoesNotExist:
            return Response({"detail": "Achievements not found."}, status=status.HTTP_404_NOT_FOUND)
