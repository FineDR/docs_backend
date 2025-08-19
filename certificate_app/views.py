from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema
from .models import Profile, Certificate
from .serializers import ProfileSerializer

class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=ProfileSerializer,
        responses={200: None},
        summary="Create or update profile with certificates",
        description="Authenticated users can submit or update their profile and certificates."
    )
    def post(self, request):
        user = request.user
        serializer = ProfileSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            Profile.objects.update_or_create(
                user=user,
                defaults={
                    "full_name": serializer.validated_data["full_name"],
                    "email": serializer.validated_data["email"]
                }
            )
            # Handle certificates
            profile = Profile.objects.get(user=user)
            profile.certificates.all().delete()  # Remove old certs to avoid duplicates
            certificates_data = serializer.validated_data.get("certificates", [])
            for cert_data in certificates_data:
                Certificate.objects.create(profile=profile, **cert_data)

            return Response({"message": "Profile and certificates saved successfully"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        responses=ProfileSerializer,
        summary="Retrieve profile with certificates",
        description="Get the profile and certificates of the authenticated user."
    )
    def get(self, request):
        try:
            profile = request.user.profile
            serializer = ProfileSerializer(profile)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Profile.DoesNotExist:
            return Response({"detail": "Profile not found."}, status=status.HTTP_404_NOT_FOUND)

    @extend_schema(
        request=ProfileSerializer,
        responses=ProfileSerializer,
        summary="Update profile with certificates",
        description="Update existing profile and certificates for the authenticated user."
    )
    def put(self, request):
        try:
            profile = request.user.profile
            serializer = ProfileSerializer(profile, data=request.data, partial=True, context={'request': request})
            if serializer.is_valid():
                serializer.save(user=request.user)
                # Handle certificates
                profile.certificates.all().delete()
                certificates_data = serializer.validated_data.get("certificates", [])
                for cert_data in certificates_data:
                    Certificate.objects.create(profile=profile, **cert_data)

                return Response(
                    {"message": "Profile and certificates updated successfully", "data": serializer.data},
                    status=status.HTTP_200_OK
                )
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Profile.DoesNotExist:
            return Response({"detail": "Profile not found."}, status=status.HTTP_404_NOT_FOUND)

    @extend_schema(
        responses={200: None},
        summary="Delete profile and certificates",
        description="Delete profile and all associated certificates of the authenticated user."
    )
    def delete(self, request):
        try:
            profile = request.user.profile
            profile.delete()
            return Response({"message": "Profile and certificates deleted successfully"}, status=status.HTTP_200_OK)
        except Profile.DoesNotExist:
            return Response({"detail": "Profile not found."}, status=status.HTTP_404_NOT_FOUND)
