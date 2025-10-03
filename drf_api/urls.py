from django.contrib import admin
from django.urls import path, include
# from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse

def home(request):
    return JsonResponse({"message": "Welcome to Docs API"})
# Define Swagger schema view
# schema_view = get_schema_view(
#    openapi.Info(
#       title="It Is Possible API",
#       default_version='v1',
#       description="Detailed API documentation",
#       terms_of_service="https://www.google.com/policies/terms/",
#       contact=openapi.Contact(email="contact@myapi.com"),
#       license=openapi.License(name="MIT License"),
#    ),
#    public=True,
#    permission_classes=(permissions.AllowAny,),
# )
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)

urlpatterns = [
    path('grappelli/', include('grappelli.urls')),
    path('admin/', admin.site.urls),
    path('', home),
    path('auth/', include('api.urls')),
    path('sms/', include('smsparser.urls')),
    path('api/', include('personal_details.urls')),
    path('api/', include('work_experiences.urls')),
    path('api/', include('career_objective.urls')),
    path('api/', include('skills_app.urls')),
    path('api/', include('education_app.urls')),
    path('api/', include('language_app.urls')),
    path('api/', include('project_app.urls')),
    path('api/', include('certificate_app.urls')),
    path('api/', include('references_app.urls')),
    path('api/', include('achivements_app.urls')),
    path('api/', include('cv_payments.urls')),
    # project/urls.py
    path("api/", include("jobs.urls")),
    path("api/", include("letterApp.urls")),
    path('api/', include('payments.urls')),
    path('api/', include('project_report.urls')),



    # Swagger UI documentation
   #  path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='swagger-ui'),
    
    # ReDoc UI documentation (optional)
   #  path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='redoc'),
   #  path('swagger.json', schema_view.without_ui(cache_timeout=0), name='schema-json'),
   #  path('swagger.yaml', schema_view.without_ui(cache_timeout=0), name='schema-yaml'),


    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("swagger/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
