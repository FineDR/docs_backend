from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import WorkExperience
from .serializers import WorkExperienceSerializer

class WorkExperienceView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = WorkExperienceSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            experience = serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)  # return saved object
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        experiences = WorkExperience.objects.filter(user=request.user)
        serializer = WorkExperienceSerializer(experiences, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk=None):
        try:
            experience = WorkExperience.objects.get(pk=pk, user=request.user)
        except WorkExperience.DoesNotExist:
            return Response({"error": "Work experience not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = WorkExperienceSerializer(experience, data=request.data, partial=True, context={"request": request})
        if serializer.is_valid():
            updated_exp = serializer.save()
            return Response(WorkExperienceSerializer(updated_exp).data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk=None):
        try:
            experience = WorkExperience.objects.get(pk=pk, user=request.user)
        except WorkExperience.DoesNotExist:
            return Response({"error": "Work experience not found"}, status=status.HTTP_404_NOT_FOUND)

        experience.delete()
        return Response({"message": "Work experience deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
