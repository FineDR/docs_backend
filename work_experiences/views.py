from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema
from .models import WorkExperience
from .serializers import WorkExperienceSerializer

class WorkExperienceView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=WorkExperienceSerializer(many=True),
        responses={201: WorkExperienceSerializer(many=True)},
        summary="Create multiple work experiences",
        description="Authenticated users can add multiple work experiences with responsibilities."
    )
    def post(self, request):
        serializer = WorkExperienceSerializer(
            data=request.data.get("experiences", []),
            many=True,
            context={"request": request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Work experiences saved successfully", "data": serializer.data},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        responses=WorkExperienceSerializer(many=True),
        summary="List all work experiences for the authenticated user"
    )
    def get(self, request):
        experiences = WorkExperience.objects.filter(user=request.user)
        serializer = WorkExperienceSerializer(experiences, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        request=WorkExperienceSerializer,
        responses=WorkExperienceSerializer,
        summary="Update a work experience"
    )
    def put(self, request, pk=None):
        try:
            experience = WorkExperience.objects.get(pk=pk, user=request.user)
        except WorkExperience.DoesNotExist:
            return Response({"error": "Work experience not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = WorkExperienceSerializer(
            experience,
            data=request.data,
            partial=True,
            context={"request": request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Work experience updated successfully", "data": serializer.data},
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        summary="Delete a work experience",
        description="Delete a work experience by its ID."
    )
    def delete(self, request, pk=None):
        try:
            experience = WorkExperience.objects.get(pk=pk, user=request.user)
        except WorkExperience.DoesNotExist:
            return Response({"error": "Work experience not found"}, status=status.HTTP_404_NOT_FOUND)

        experience.delete()
        return Response({"message": "Work experience deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
