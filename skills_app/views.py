from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema
from .models import SkillSet
from .serializers import SkillSetSerializer


class SkillSetView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=SkillSetSerializer,
        responses={201: SkillSetSerializer},
        summary="Submit skills",
        description="Authenticated users can submit technical and soft skills"
    )
    def post(self, request):
        serializer = SkillSetSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            # ✅ Remove user=request.user here, serializer handles it
            serializer.save()
            return Response(
                {"message": "Skills submitted successfully", "data": serializer.data},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        responses=SkillSetSerializer,
        summary="Get all skill sets for authenticated user"
    )
    def get(self, request):
        skill_sets = SkillSet.objects.filter(user=request.user)
        serializer = SkillSetSerializer(skill_sets, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class SkillSetDetailView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=SkillSetSerializer,
        responses={200: SkillSetSerializer},
        summary="Retrieve a skill set by ID"
    )
    def get(self, request, pk):
        try:
            skill_set = SkillSet.objects.get(pk=pk, user=request.user)
        except SkillSet.DoesNotExist:
            return Response({"error": "SkillSet not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = SkillSetSerializer(skill_set)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        request=SkillSetSerializer,
        responses={200: SkillSetSerializer},
        summary="Update a skill set by ID"
    )
    def put(self, request, pk):
        try:
            skill_set = SkillSet.objects.get(pk=pk, user=request.user)
        except SkillSet.DoesNotExist:
            return Response({"error": "SkillSet not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = SkillSetSerializer(skill_set, data=request.data, context={"request": request})
        if serializer.is_valid():
            # ✅ Remove user=request.user here too
            serializer.save()
            return Response({"message": "Skills updated successfully", "data": serializer.data})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        responses={204: None},
        summary="Delete a skill set by ID"
    )
    def delete(self, request, pk):
        try:
            skill_set = SkillSet.objects.get(pk=pk, user=request.user)
        except SkillSet.DoesNotExist:
            return Response({"error": "SkillSet not found"}, status=status.HTTP_404_NOT_FOUND)
        skill_set.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
