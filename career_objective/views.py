from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema
from .models import CareerObjective
from .serializers import CareerObjectiveSerializer

class CareerObjectiveView(APIView):
    permission_classes = [IsAuthenticated]

    # GET all career objectives of the logged-in user
    @extend_schema(
        responses=CareerObjectiveSerializer,
        summary="Get all user's career objectives"
    )
    def get(self, request):
        objs = CareerObjective.objects.filter(user=request.user)
        serializer = CareerObjectiveSerializer(objs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # POST a new career objective
    @extend_schema(
        request=CareerObjectiveSerializer,
        responses=CareerObjectiveSerializer,
        summary="Create a career objective"
    )
    def post(self, request):
        serializer = CareerObjectiveSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # PUT to update a single career objective by ID
    @extend_schema(
        request=CareerObjectiveSerializer,
        responses=CareerObjectiveSerializer,
        summary="Update a career objective by ID"
    )
    def put(self, request, pk=None):
        if not pk:
            return Response({"detail": "Career objective ID is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            obj = CareerObjective.objects.get(pk=pk, user=request.user)
        except CareerObjective.DoesNotExist:
            return Response({"detail": "Career objective not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = CareerObjectiveSerializer(obj, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # DELETE a single career objective by ID
    @extend_schema(
        responses={200: None},
        summary="Delete a career objective by ID"
    )
    def delete(self, request, pk=None):
        if not pk:
            return Response({"detail": "Career objective ID is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            obj = CareerObjective.objects.get(pk=pk, user=request.user)
            obj.delete()
            return Response({"message": "Career objective deleted successfully"}, status=status.HTTP_200_OK)
        except CareerObjective.DoesNotExist:
            return Response({"detail": "Career objective not found."}, status=status.HTTP_404_NOT_FOUND)
