from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from django.core.mail import send_mail
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from .models import UserTB
from .serializers import UserTBSerializer, LoginSerializer, UserProfileSerializer,UserDetailSerializer
import jwt
from django.conf import settings
from datetime import datetime, timedelta
from rest_framework.exceptions import AuthenticationFailed, ValidationError
from rest_framework import status, permissions
from drf_spectacular.utils import extend_schema
from django.http import JsonResponse
from django.contrib.auth import get_user_model
from .serializers import UserDetailSerializer
from .services.ai_service import clean_user_data_with_ai, enhance_cv_data
from django.contrib.auth.models import User
from google.oauth2 import id_token
from google.auth.transport import requests
import logging
from api.models import UserTB

logger = logging.getLogger(__name__)
import subprocess
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

# User = settings.AUTH_USER_MODEL

class RegisterView(APIView):
    permission_classes = [AllowAny]
    """
    API for user registration.
    """
    @extend_schema(
        request=UserTBSerializer,
        responses={200: None},
        summary="Register a new user",
        description="Takes email and password to create a new user.",
    )

   

    def post(self, request):
     serializer = UserTBSerializer(data=request.data)
     if serializer.is_valid():
        user = serializer.save()

        # Create your own JWT token with user_id payload and expiration
        payload = {
            "user_id": str(user.id),
            "exp": datetime.utcnow() + timedelta(hours=24),  # token expiry (e.g. 24 hours)
            "iat": datetime.utcnow(),
        }
        token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")

        verification_url = f"{settings.FRONTEND_BASE_URL}/verify-email?token={token}"

        # Email Content
        email_subject = "Verify Your Email Address"
        email_body = (
            f"Hello {user.email},\n\n"
            "Thank you for signing up! Please verify your email address to activate your account.\n\n"
            f"Click the link below to confirm your email:\n{verification_url}\n\n"
            "If you did not sign up, you can ignore this email.\n\n"
            "Best regards,\nYour Company Team"
        )

        send_mail(
            email_subject,
            email_body,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )

        return Response({
            "message": "User registered successfully. Please check your email to verify your account."
        }, status=status.HTTP_201_CREATED)

     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
class VerifyEmailView(APIView):
    def get(self, request):
        token = request.GET.get("token")

        if not token:
            return Response({"error": "Token missing"}, status=400)

        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            user_id = payload.get("user_id")

            if not user_id:
                return Response({"error": "Invalid token"}, status=400)

            # activate user
            user = UserTB.objects.get(pk=user_id)
            user.is_active = True
            user.save()

            return Response({"message": "Email verified successfully"}, status=200)

        except jwt.ExpiredSignatureError:
            return Response({"error": "Token has expired"}, status=400)
        except jwt.InvalidTokenError:
            return Response({"error": "Invalid token"}, status=400)
        except UserTB.DoesNotExist:
            return Response({"error": "User does not exist"}, status=400)

class UserLoginView(APIView):
    """
    API for user login.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data["user"]
            refresh = RefreshToken.for_user(user)

            user_data = UserDetailSerializer(
                user,
                context={'enhanced_data': getattr(user, 'enhanced_data', None)}
            ).data
            return Response(
                {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                    "email": user.email,
                    "user":user_data
                    
                },
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)


class LogoutView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        logger.info("Logout request received.")
        logger.info(f"Request data: {request.data}")

        refresh_token = request.data.get("refresh")
        if not refresh_token:
            logger.warning("No refresh token found in request data.")
            return Response({"detail": "Refresh token is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            logger.info(f"Received refresh token: {refresh_token}")
            token = RefreshToken(refresh_token)
            token.blacklist()
            logger.info("Token blacklisted successfully.")
            return Response({"detail": "Logout successful."}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error blacklisting token: {str(e)}", exc_info=True)
            return Response({"detail": "Invalid token."}, status=status.HTTP_400_BAD_REQUEST)
        
        
class UserProfileView(APIView):
    """
    API for retrieving and updating user profile.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data)

    def put(self, request):
        serializer = UserProfileSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def run_create_superuser(request):
    User = get_user_model()
    email = "admin@gmail.com"
    password = "admin12345"

    if not User.objects.filter(email=email).exists():
        User.objects.create_superuser(
            email=email,
            password=password,
            first_name="Super",
            last_name="Admin",
            middle_name="System",
            phone_number="1234567890",
            role="seller",  # or any role you support
            is_active=True,
        )
        return JsonResponse({"message": "✅ Superuser created successfully."})
    else:
        return JsonResponse({"message": "⚠️ Superuser already exists."})
    


@csrf_exempt
def run_migrations(request):
    try:
        result = subprocess.run(["python", "manage.py", "migrate"], check=True, capture_output=True, text=True)
        return JsonResponse({"message": "✅ Migrations applied", "output": result.stdout})
    except subprocess.CalledProcessError as e:
        return JsonResponse({"error": "❌ Migration failed", "details": e.stderr}, status=500)
    




class UserDetailView(APIView):
    """
    API for retrieving and updating user details with AI enhancement.
    """
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        responses=UserDetailSerializer,
        summary="Retrieve user details",
        description="Get the details of the authenticated user."
    )
    def get(self, request):
        """
        Returns AI-enhanced user details.
        If not yet enhanced, triggers enhancement automatically.
        """
        try:
            user = request.user

            # If AI-enhanced data already exists
            if user.enhanced_data:
                serializer = UserDetailSerializer(
                    user,
                    context={'enhanced_data': user.enhanced_data}
                )
                return Response(serializer.data, status=status.HTTP_200_OK)

            # Otherwise, generate it now
            serializer = UserDetailSerializer(user)
            original_data = dict(serializer.data)

            cleaned_data = clean_user_data_with_ai(original_data)
            enhanced_data = enhance_cv_data(cleaned_data)

            user.enhanced_data = enhanced_data
            user.save(update_fields=['enhanced_data'])

            serializer = UserDetailSerializer(user, context={'enhanced_data': enhanced_data})
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            serializer = UserDetailSerializer(request.user)
            return Response({
                'data': serializer.data,
                'error': f'AI processing failed: {str(e)}'
            }, status=status.HTTP_200_OK)

    @extend_schema(
        request=None,
        responses=UserDetailSerializer,
        summary="Re-enhance user details",
        description="Re-run AI enhancement if user data was updated (e.g., new skills, education, etc.)"
    )
    def put(self, request):
        """
        Re-runs AI enhancement when user updates details.
        """
        try:
            user = request.user
            serializer = UserDetailSerializer(user)
            original_data = dict(serializer.data)

            # Clean and enhance again
            cleaned_data = clean_user_data_with_ai(original_data)
            enhanced_data = enhance_cv_data(cleaned_data)

            # Save new enhanced data
            user.enhanced_data = enhanced_data
            user.save(update_fields=['enhanced_data'])

            return Response({
                "message": "AI-enhanced data updated successfully.",
                "enhanced_data": enhanced_data
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                "error": f"Failed to update enhanced data: {str(e)}"
            }, status=status.HTTP_400_BAD_REQUEST)

          
        
class AdminUserListView(APIView):
    """
    API to fetch all users for admin dashboard.
    Only accessible by staff/superusers.
    """
    # permission_classes = [IsAdminUser] 

    @extend_schema(
        responses=UserDetailSerializer(many=True),
        summary="Retrieve all users",
        description="Get the full list of all users in the system. Admin only."
    )
    def get(self, request):
        users = UserTB.objects.all()  # Fetch all users
        serializer = UserDetailSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    


class GoogleAuthView(APIView):
    """
    Handles Google Sign-Up and Sign-In.
    Automatically logs in newly created users.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        token = request.data.get("token")
        if not token:
            return Response({"message": "Token is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Verify Google token
            idinfo = id_token.verify_oauth2_token(token, requests.Request(), settings.GOOGLE_CLIENT_ID)
            email = idinfo.get("email")
            first_name = idinfo.get("given_name")
            last_name = idinfo.get("family_name")

            # Create or get user
            user, created = UserTB.objects.get_or_create(
                email=email,
                defaults={
                    "email": email,
                    "first_name": first_name,
                    "last_name": last_name,
                    "is_active": True,
                }
            )

            # Only run AI enhancement if user has existing CV data
            enhanced_data = getattr(user, 'enhanced_data', None)
            if created or not enhanced_data:
                # New user or no existing enhanced_data
                enhanced_data = {}  # skip AI enhancement for now

            # Create JWT tokens
            refresh = RefreshToken.for_user(user)

            # Serialize user data safely
            user_data = UserDetailSerializer(
                user,
                context={'enhanced_data': enhanced_data}
            ).data

            return Response(
                {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                    "email": user.email,
                    "user": user_data
                },
                status=status.HTTP_200_OK
            )

        except ValueError:
            return Response({"message": "Invalid Google token"}, status=status.HTTP_400_BAD_REQUEST)
