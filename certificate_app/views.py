from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema
from .models import Profile, Certificate
from .serializers import ProfileSerializer, CertificateSerializer


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
            # Create or update profile
            profile, _ = Profile.objects.update_or_create(
                user=user,
                defaults={
                    "full_name": serializer.validated_data["full_name"],
                    "email": serializer.validated_data["email"]
                }
            )
            # Let serializer handle certificates
            serializer.update(profile, serializer.validated_data)

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
                serializer.save()  # serializer handles profile and certificates
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


class CertificateDetailView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=CertificateSerializer,
        responses=CertificateSerializer,
        summary="Update a single certificate",
        description="Update one certificate belonging to the authenticated user."
    )
    def put(self, request, id):
        try:
            cert = Certificate.objects.get(id=id, profile=request.user.profile)
        except Certificate.DoesNotExist:
            return Response({"detail": "Certificate not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = CertificateSerializer(cert, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()  # profile is read-only, no need to pass
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        responses={200: None},
        summary="Delete a single certificate",
        description="Delete one certificate belonging to the authenticated user."
    )
    def delete(self, request, id):
        try:
            cert = Certificate.objects.get(id=id, profile=request.user.profile)
            cert.delete()
            return Response({"message": "Certificate deleted"}, status=status.HTTP_200_OK)
        except Certificate.DoesNotExist:
            return Response({"detail": "Certificate not found"}, status=status.HTTP_404_NOT_FOUND)
