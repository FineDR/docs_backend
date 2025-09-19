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
        summary="Create or update references (bulk)",
    )
    def post(self, request, pk=None):
        user = request.user
        data = request.data.get('references', [])

        if pk:  # single reference creation/update
            try:
                reference = Reference.objects.get(user=user, pk=pk)
            except Reference.DoesNotExist:
                return Response({"detail": "Reference not found"}, status=status.HTTP_404_NOT_FOUND)
            serializer = ReferenceSerializer(reference, data=request.data)
            if serializer.is_valid():
                serializer.save(user=user)
                return Response({"message": "Reference updated successfully", "data": serializer.data})
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # bulk create
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
    def get(self, request, pk=None):
        user = request.user
        if pk:  # single reference
            try:
                reference = Reference.objects.get(user=user, pk=pk)
            except Reference.DoesNotExist:
                return Response({"detail": "Reference not found"}, status=status.HTTP_404_NOT_FOUND)
            serializer = ReferenceSerializer(reference)
            return Response(serializer.data)
        
        # all references
        references = user.references.all()
        serializer = ReferenceSerializer(references, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        request=ReferenceSerializer(many=True),
        responses=ReferenceSerializer(many=True),
        summary="Update references"
    )
    def put(self, request, pk=None):
        user = request.user

        if pk:  # single reference update
            try:
                reference = Reference.objects.get(user=user, pk=pk)
            except Reference.DoesNotExist:
                return Response({"detail": "Reference not found"}, status=status.HTTP_404_NOT_FOUND)
            serializer = ReferenceSerializer(reference, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({"message": "Reference updated successfully", "data": serializer.data})
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # bulk update
        data = request.data.get('references', [])
        Reference.objects.filter(user=user).delete()
        serializer = ReferenceSerializer(data=data, many=True)
        if serializer.is_valid():
            serializer.save(user=user)
            return Response({"message": "References updated successfully", "data": serializer.data})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        responses={200: None},
        summary="Delete references"
    )
    def delete(self, request, pk=None):
        user = request.user
        if pk:  # delete single reference
            try:
                reference = Reference.objects.get(user=user, pk=pk)
                reference.delete()
                return Response({"message": "Reference deleted successfully"}, status=status.HTTP_200_OK)
            except Reference.DoesNotExist:
                return Response({"detail": "Reference not found"}, status=status.HTTP_404_NOT_FOUND)
        
        # delete all references
        user.references.all().delete()
        return Response({"message": "References deleted successfully"}, status=status.HTTP_200_OK)
