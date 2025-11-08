from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema
from .models import AchievementProfile, Achievement
from .serializers import AchievementProfileSerializer, AchievementSerializer


class AchievementProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get_profile(self, user):
        """Helper to safely fetch the user's profile"""
        return getattr(user, "achievement_profile", None)

    @extend_schema(
        request=AchievementProfileSerializer,
        responses={200: AchievementProfileSerializer},
        summary="Create or update achievements",
    )
    def post(self, request):
        """
        Create achievements. Accepts:
        - multiple achievements via `achievements` array
        - single achievement via `value` field
        """
        user = request.user
        profile, _ = AchievementProfile.objects.get_or_create(
            user=user,
            defaults={
                "full_name": getattr(user, "full_name", ""),
                "email": getattr(user, "email", ""),
            },
        )

        # Handle multiple achievements
        achievements_data = request.data.get("achievements")
        single_value = request.data.get("value")

        created_achievements = []

        if achievements_data and isinstance(achievements_data, list):
            for ach in achievements_data:
                a = Achievement.objects.create(profile=profile, value=ach.get("value", ""))
                created_achievements.append(a)
        elif single_value:
            a = Achievement.objects.create(profile=profile, value=single_value)
            created_achievements.append(a)

        serializer = AchievementProfileSerializer(profile)
        return Response(
            {"message": "Achievements saved successfully", "data": serializer.data},
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        responses=AchievementProfileSerializer,
        summary="Retrieve achievements",
    )
    def get(self, request, pk=None):
        """Get all achievements or a single achievement if pk is provided"""
        if pk:
            try:
                achievement = Achievement.objects.get(id=pk, profile__user=request.user)
                serializer = AchievementSerializer(achievement)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except Achievement.DoesNotExist:
                return Response({"detail": "Achievement not found."}, status=status.HTTP_404_NOT_FOUND)

        profile = self.get_profile(request.user)
        if not profile:
            return Response({"detail": "Achievements not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = AchievementProfileSerializer(profile)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        request=AchievementSerializer,
        responses=AchievementSerializer,
        summary="Update achievements",
    )
    def put(self, request, pk=None):
        """Update a single achievement or profile info"""
        if pk:
            try:
                achievement = Achievement.objects.get(id=pk, profile__user=request.user)
                serializer = AchievementSerializer(achievement, data=request.data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    return Response(
                        {"message": "Achievement updated successfully", "data": serializer.data},
                        status=status.HTTP_200_OK,
                    )
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            except Achievement.DoesNotExist:
                return Response({"detail": "Achievement not found."}, status=status.HTTP_404_NOT_FOUND)

        profile = self.get_profile(request.user)
        if not profile:
            return Response({"detail": "Achievements not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = AchievementProfileSerializer(profile, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Profile updated successfully", "data": serializer.data},
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        responses={200: None},
        summary="Delete achievements",
    )
    def delete(self, request, pk=None):
        """Delete single achievement or entire profile"""
        if pk:
            try:
                achievement = Achievement.objects.get(id=pk, profile__user=request.user)
                achievement.delete()
                return Response({"message": "Achievement deleted successfully"}, status=status.HTTP_200_OK)
            except Achievement.DoesNotExist:
                return Response({"detail": "Achievement not found."}, status=status.HTTP_404_NOT_FOUND)

        profile = self.get_profile(request.user)
        if not profile:
            return Response({"detail": "Achievements not found."}, status=status.HTTP_404_NOT_FOUND)

        profile.delete()
        return Response({"message": "All achievements deleted successfully"}, status=status.HTTP_200_OK)
