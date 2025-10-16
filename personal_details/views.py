from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from drf_spectacular.utils import extend_schema
from .models import PersonalDetail
from .serializers import PersonalDetailSerializer

class PersonalDetailView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]  # Support file uploads

    @extend_schema(
        request=PersonalDetailSerializer,
        responses={200: None},
        summary="Create or update personal details with profile image",
        description="Authenticated users can submit or update their personal details, including profile image."
    )
    def post(self, request):
        user = request.user
        try:
            # If personal detail exists, update it
            details = user.personal_detail
            serializer = PersonalDetailSerializer(details, data=request.data, partial=True, context={'request': request})
        except PersonalDetail.DoesNotExist:
            # Otherwise, create a new one
            serializer = PersonalDetailSerializer(data=request.data, context={'request': request})

        if serializer.is_valid():
            serializer.save(user=user)  # This correctly saves the profile_image
            return Response(
                {"message": "Personal details saved successfully", "data": serializer.data},
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    @extend_schema(
        responses=PersonalDetailSerializer,
        summary="Retrieve personal details",
        description="Get the personal details of the authenticated user."
    )
    def get(self, request):
        try:
            details = request.user.personal_detail
            serializer = PersonalDetailSerializer(details, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)
        except PersonalDetail.DoesNotExist:
            return Response(
                {"detail": "Personal details not found."},
                status=status.HTTP_404_NOT_FOUND
            )

    @extend_schema(
        request=PersonalDetailSerializer,
        responses=PersonalDetailSerializer,
        summary="Update personal details including profile image",
        description="Update existing personal details for the authenticated user."
    )
    def put(self, request):
        try:
            details = request.user.personal_detail
            serializer = PersonalDetailSerializer(details, data=request.data, partial=True, context={'request': request})
            if serializer.is_valid():
                serializer.save()
                return Response(
                    {"message": "Personal details updated successfully", "data": serializer.data},
                    status=status.HTTP_200_OK
                )
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except PersonalDetail.DoesNotExist:
            return Response(
                {"detail": "Personal details not found."},
                status=status.HTTP_404_NOT_FOUND
            )

    @extend_schema(
        responses={200: None},
        summary="Delete personal details",
        description="Delete personal details of the authenticated user."
    )
    def delete(self, request):
        try:
            details = request.user.personal_detail
            details.delete()
            return Response(
                {"message": "Personal details deleted successfully"},
                status=status.HTTP_200_OK
            )
        except PersonalDetail.DoesNotExist:
            return Response(
                {"detail": "Personal details not found."},
                status=status.HTTP_404_NOT_FOUND
            )
