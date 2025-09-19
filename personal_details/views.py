from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema
from .models import PersonalDetail
from .serializers import PersonalDetailSerializer

class PersonalDetailView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=PersonalDetailSerializer,
        responses={200: None},
        summary="Create or update personal details",
        description="Authenticated users can submit or update their personal details."
    )
    def post(self, request):
        user = request.user
        serializer = PersonalDetailSerializer(data=request.data)
        if serializer.is_valid():
            # Create or update personal details for the user
            PersonalDetail.objects.update_or_create(
                user=user,
                defaults=serializer.validated_data
            )
            return Response(
                {"message": "Personal details saved successfully"},
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
            serializer = PersonalDetailSerializer(details)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except PersonalDetail.DoesNotExist:
            return Response(
                {"detail": "Personal details not found."},
                status=status.HTTP_404_NOT_FOUND
            )

    @extend_schema(
        request=PersonalDetailSerializer,
        responses=PersonalDetailSerializer,
        summary="Update personal details",
        description="Update existing personal details for the authenticated user."
    )
    def put(self, request):
        try:
            details = request.user.personal_detail
            serializer = PersonalDetailSerializer(details, data=request.data, partial=True)
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
