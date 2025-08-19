# career_objective/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema
from .models import CareerObjective
from .serializers import CareerObjectiveSerializer

class CareerObjectiveView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=CareerObjectiveSerializer,
        responses={200: CareerObjectiveSerializer},
        summary="Create or update career objective",
        description="Authenticated users can create or update their career objective"
    )
    def post(self, request):
        user = request.user
        serializer = CareerObjectiveSerializer(data=request.data)
        if serializer.is_valid():
            CareerObjective.objects.update_or_create(
                user=user,
                defaults=serializer.validated_data
            )
            return Response({"message": "Career objective saved successfully"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        responses=CareerObjectiveSerializer,
        summary="Get user's career objective"
    )
    def get(self, request):
        try:
            obj = request.user.career_objective
            serializer = CareerObjectiveSerializer(obj)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except CareerObjective.DoesNotExist:
            return Response({"detail": "Career objective not found."}, status=status.HTTP_404_NOT_FOUND)

    @extend_schema(
        request=CareerObjectiveSerializer,
        responses=CareerObjectiveSerializer,
        summary="Update career objective"
    )
    def put(self, request):
        try:
            obj = request.user.career_objective
            serializer = CareerObjectiveSerializer(obj, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({"message": "Career objective updated successfully", "data": serializer.data}, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except CareerObjective.DoesNotExist:
            return Response({"detail": "Career objective not found."}, status=status.HTTP_404_NOT_FOUND)

    @extend_schema(
        responses={200: None},
        summary="Delete career objective"
    )
    def delete(self, request):
        try:
            obj = request.user.career_objective
            obj.delete()
            return Response({"message": "Career objective deleted successfully"}, status=status.HTTP_200_OK)
        except CareerObjective.DoesNotExist:
            return Response({"detail": "Career objective not found."}, status=status.HTTP_404_NOT_FOUND)
