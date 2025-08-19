from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema
from .models import Reference
from .serializers import ReferenceSerializer

class ReferenceView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=ReferenceSerializer(many=True),
        responses={200: None},
        summary="Create or update references",
    )
    def post(self, request):
        user = request.user
        data = request.data.get('references', [])

        # Remove old references
        Reference.objects.filter(user=user).delete()

        serializer = ReferenceSerializer(data=data, many=True)
        if serializer.is_valid():
            serializer.save(user=user)
            return Response({"message": "References saved successfully"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        responses=ReferenceSerializer(many=True),
        summary="Retrieve references"
    )
    def get(self, request):
        user = request.user
        references = user.references.all()
        serializer = ReferenceSerializer(references, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        request=ReferenceSerializer(many=True),
        responses=ReferenceSerializer(many=True),
        summary="Update references"
    )
    def put(self, request):
        user = request.user
        data = request.data.get('references', [])
        # Replace all references
        Reference.objects.filter(user=user).delete()
        serializer = ReferenceSerializer(data=data, many=True)
        if serializer.is_valid():
            serializer.save(user=user)
            return Response({"message": "References updated successfully", "data": serializer.data}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        responses={200: None},
        summary="Delete references"
    )
    def delete(self, request):
        user = request.user
        user.references.all().delete()
        return Response({"message": "References deleted successfully"}, status=status.HTTP_200_OK)
