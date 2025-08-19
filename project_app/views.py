from django.db import transaction
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema
from .models import Project, Technology
from .serializers import ProjectSerializer

class ProjectView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=ProjectSerializer,
        responses={201: ProjectSerializer},
        summary="Submit multiple projects",
        description="Authenticated users can submit multiple projects with technologies at once"
    )
    def post(self, request):
        user = request.user
        projects = request.data.get("projects", [])

        if not projects:
            return Response({"error": "No projects provided"}, status=status.HTTP_400_BAD_REQUEST)

        created_projects = []

        for proj in projects:
            technologies_data = proj.pop("technologies", [])
            serializer = ProjectSerializer(data=proj, context={'request': request})
            if serializer.is_valid():
                with transaction.atomic():
                    # Pass user directly to save() instead of adding it to data
                    project_instance = serializer.save(user=user)

                    for tech in technologies_data:
                        Technology.objects.create(project=project_instance, **tech)

                created_projects.append(ProjectSerializer(project_instance, context={'request': request}).data)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            {"message": "Projects submitted successfully", "data": created_projects},
            status=status.HTTP_201_CREATED
        )

    @extend_schema(
        responses=ProjectSerializer,
        summary="Get all projects for authenticated user"
    )
    def get(self, request):
        projects = Project.objects.filter(user=request.user)
        serializer = ProjectSerializer(projects, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class ProjectDetailView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={200: ProjectSerializer},
        summary="Retrieve a single project by ID"
    )
    def get(self, request, pk):
        try:
            project = Project.objects.get(pk=pk, user=request.user)
        except Project.DoesNotExist:
            return Response({"error": "Project not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = ProjectSerializer(project, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        request=ProjectSerializer,
        responses={200: ProjectSerializer},
        summary="Update a project by ID"
    )
    def put(self, request, pk):
        try:
            project = Project.objects.get(pk=pk, user=request.user)
        except Project.DoesNotExist:
            return Response({"error": "Project not found"}, status=status.HTTP_404_NOT_FOUND)

        technologies_data = request.data.pop("technologies", [])
        serializer = ProjectSerializer(project, data=request.data, context={'request': request})
        if serializer.is_valid():
            with transaction.atomic():
                project_instance = serializer.save()
                project_instance.technologies.all().delete()
                for tech in technologies_data:
                    Technology.objects.create(project=project_instance, **tech)

            return Response(
                {"message": "Project updated successfully", "data": ProjectSerializer(project_instance, context={'request': request}).data}
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        responses={204: None},
        summary="Delete a project by ID"
    )
    def delete(self, request, pk):
        try:
            project = Project.objects.get(pk=pk, user=request.user)
        except Project.DoesNotExist:
            return Response({"error": "Project not found"}, status=status.HTTP_404_NOT_FOUND)

        project.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
