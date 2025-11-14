import logging
from django.db import transaction
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema
from .models import Project, Technology
from .serializers import ProjectSerializer
logger = logging.getLogger(__name__)
class ProjectView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=ProjectSerializer,
        responses={201: ProjectSerializer},
        summary="Submit multiple projects",
        description="Authenticated users can submit multiple projects with technologies at once"
    )

    def post(self, request):
       
        projects_data = request.data.get("projects")
        if projects_data is None:
            # Check if request.data itself looks like a project object
            if "title" in request.data and "description" in request.data:
                projects_data = [request.data.copy()]
            else:
                return Response({"error": "No projects provided"}, status=status.HTTP_400_BAD_REQUEST)

        created_projects = []

        for idx, proj_data in enumerate(projects_data):
            # Remove unwanted fields
            proj_data.pop("email", None)

            serializer = ProjectSerializer(data=proj_data, context={'request': request})
            if serializer.is_valid():
                with transaction.atomic():
                    project_instance = serializer.save()
                created_projects.append(ProjectSerializer(project_instance, context={'request': request}).data)
            else:
            
                return Response(
                    {"error": f"Project #{idx} validation failed", "details": serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST
                )

        return Response(
            {"message": "Projects submitted successfully", "data": created_projects},
            status=status.HTTP_201_CREATED
        )

    

    @extend_schema(
        responses=ProjectSerializer,
        summary="Get all projects for authenticated user"
    )

    def put(self, request, pk):
        try:
            project = Project.objects.get(pk=pk, user=request.user)
        except Project.DoesNotExist:
            return Response({"error": "Project not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = ProjectSerializer(project, data=request.data, context={'request': request})
        if serializer.is_valid():
            with transaction.atomic():
                project_instance = serializer.save()  # handles technologies already

            return Response(
                {"message": "Project updated successfully", "data": ProjectSerializer(project_instance, context={'request': request}).data}
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



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
