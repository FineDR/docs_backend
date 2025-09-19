from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema
from .models import Education
from .serializers import EducationSerializer

class EducationView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=EducationSerializer,
        responses={201: EducationSerializer},
        summary="Submit Education Records",
        description="Authenticated users can submit multiple education entries at once"
    )
    def post(self, request):
        educations = request.data.get("education", [])
        created_entries = []

        for edu in educations:
            serializer = EducationSerializer(data=edu, context={'request': request})
            if serializer.is_valid():
                serializer.save()  # user is automatically set in serializer
                created_entries.append(serializer.data)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            {"message": "Education records submitted successfully", "data": created_entries},
            status=status.HTTP_201_CREATED
        )


    @extend_schema(
        responses=EducationSerializer,
        summary="Get all education records for authenticated user"
    )
    def get(self, request):
        education_records = Education.objects.filter(user=request.user)
        serializer = EducationSerializer(education_records, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class EducationDetailView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={200: EducationSerializer},
        summary="Retrieve a single education record by ID"
    )
    def get(self, request, pk):
        try:
            education = Education.objects.get(pk=pk, user=request.user)
        except Education.DoesNotExist:
            return Response({"error": "Education record not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = EducationSerializer(education)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        request=EducationSerializer,
        responses={200: EducationSerializer},
        summary="Update an education record by ID"
    )
    def put(self, request, pk):
        try:
            education = Education.objects.get(pk=pk, user=request.user)
        except Education.DoesNotExist:
            return Response({"error": "Education record not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = EducationSerializer(education, data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Education record updated successfully", "data": serializer.data})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        responses={204: None},
        summary="Delete an education record by ID"
    )
    def delete(self, request, pk):
        try:
            education = Education.objects.get(pk=pk, user=request.user)
        except Education.DoesNotExist:
            return Response({"error": "Education record not found"}, status=status.HTTP_404_NOT_FOUND)
        education.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
