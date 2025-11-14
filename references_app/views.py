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
        data = request.data

        # 🔹 Handle single create/update via pk
        if pk:
            try:
                reference = Reference.objects.get(user=user, pk=pk)
            except Reference.DoesNotExist:
                return Response(
                    {"detail": "Reference not found"},
                    status=status.HTTP_404_NOT_FOUND
                )

            # ✅ Accept both direct object or wrapped under "references"
            if isinstance(data.get("references"), list):
                data = data["references"][0]

            serializer = ReferenceSerializer(reference, data=data, partial=False)
            if serializer.is_valid():
                serializer.save(user=user)
                return Response(
                    {"message": "Reference updated successfully", "data": serializer.data},
                    status=status.HTTP_200_OK
                )
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # 🔹 Handle bulk or single create (no pk)
        # if body is a single object instead of wrapped "references"
        if isinstance(data, dict) and "references" not in data:
            serializer = ReferenceSerializer(data=data)
            if serializer.is_valid():
                serializer.save(user=user)
                return Response(
                    {"message": "Reference created successfully", "data": serializer.data},
                    status=status.HTTP_201_CREATED
                )
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # 🔹 If "references" is present — bulk creation
        references_data = data.get("references", [])
        if not isinstance(references_data, list):
            return Response(
                {"detail": "Invalid format: 'references' must be a list"},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = ReferenceSerializer(data=references_data, many=True)
        if serializer.is_valid():
            serializer.save(user=user)
            return Response(
                {"message": "References saved successfully", "data": serializer.data},
                status=status.HTTP_200_OK
            )
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

        # 🔹 Handle single reference update
        if pk:
            try:
                reference = Reference.objects.get(user=user, pk=pk)
            except Reference.DoesNotExist:
                return Response({"detail": "Reference not found"}, status=status.HTTP_404_NOT_FOUND)

            # ✅ Accept both direct object or wrapped under "references"
            data = request.data
            if isinstance(data.get("references"), list):
                data = data["references"][0]

            serializer = ReferenceSerializer(reference, data=data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({
                    "message": "Reference updated successfully",
                    "data": serializer.data
                }, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # 🔹 Handle bulk updates
        data = request.data.get('references', [])
        response_data = []

        for item in data:
            ref_id = item.get("id")
            if ref_id:
                try:
                    ref = Reference.objects.get(user=user, pk=ref_id)
                    serializer = ReferenceSerializer(ref, data=item, partial=True)
                    if serializer.is_valid():
                        serializer.save()
                        response_data.append(serializer.data)
                except Reference.DoesNotExist:
                    continue
            else:
                serializer = ReferenceSerializer(data=item)
                if serializer.is_valid():
                    serializer.save(user=user)
                    response_data.append(serializer.data)

        return Response({
            "message": "References updated successfully",
            "data": response_data
        }, status=status.HTTP_200_OK)



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
