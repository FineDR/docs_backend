from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.conf import settings
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import UserTB
from .serializers import PasswordResetSerializer


class ForgotPasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")

        if not email:
            return Response(
                {"error": "Email is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = UserTB.objects.filter(email=email).first()
        if not user:
            return Response(
                {"error": "User with this email does not exist"},
                status=status.HTTP_404_NOT_FOUND
            )

        token = default_token_generator.make_token(user)

        frontend_url = getattr(settings, "FRONTEND_URL", "http://example.com")
        reset_url = f"{frontend_url}/reset-password/{token}/"

        subject = "Password Reset Request"
        message = (
            f"Hello {user.email},\n\n"
            "You requested a password reset. Click the link below to reset your password:\n\n"
            f"{reset_url}\n\n"
            "If you did not request this, please ignore this email.\n\n"
            "Best regards,\nYour Support Team"
        )

        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [email],
            fail_silently=False,
        )

        return Response(
            {"message": "Password reset link has been sent to your email."},
            status=status.HTTP_200_OK
        )


class PasswordResetView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, token):
        user = None
        for u in UserTB.objects.all():
            if default_token_generator.check_token(u, token):
                user = u
                break

        if not user:
            return Response(
                {"error": "Invalid or expired token"},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = PasswordResetSerializer(data=request.data)
        if serializer.is_valid():
            user.set_password(serializer.validated_data["new_password"])
            user.save()

            return Response(
                {"message": "Password has been reset successfully."},
                status=status.HTTP_200_OK
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




"""
### Password Reset Workflow:

1. Forgot Password Request (ForgotPasswordView)**
   - The user will initiate a password reset request by sending a `POST` request to the `ForgotPasswordView` API endpoint with their registered email address.
   - If the email is associated with a valid account in the system, a password reset token will be generated, and a password reset link will be sent to the user’s email.
   - **Expected Outcome:** The user receives a reset link in their inbox to proceed with resetting their password.

2. Check Email for Password Reset Link**
   - The user will receive an email with a password reset link.
   - The link will contain a token that allows the user to verify their identity.
   - **Action Required:** The user should click the reset link in their email, which will direct them to a page where they can reset their password.

3. Password Reset (PasswordResetView)**
   - After clicking the reset link, the user is directed to the password reset page, where they can input their new password.
   - The user will need to send a `POST` request to the `PasswordResetView` API endpoint with the new password and the token from the reset link.
   - **Expected Outcome:** If the token is valid, the password will be updated successfully, and the user will be notified of the successful password reset.

4. Login with New Password**
   - After resetting their password, the user can now log in with their new password using the normal login process.
   - **Action Required:** The user logs into their account with the new credentials.


### Instructions for Developers:

- ForgotPasswordView:**
  - **Endpoint:** `POST /forgot-password/`
  - **Input:** A request containing the user’s email in the body.
  - **Response:** A success message indicating that a reset link has been sent to the email if the user exists; an error message if the email is not found in the system.

- PasswordResetView:**
  - **Endpoint:** `POST /reset-password/{token}/`
  - **Input:** A request containing the new password and the reset token from the email link.
  - **Response:** A success message if the password is successfully reset; an error message if the token is invalid or expired.

### Additional Notes:

- Ensure that the **frontend URL** where the user will reset their password is correctly set in the `settings.py` file (under `FRONTEND_URL`).
- The **token generation and validation** process is handled by Django’s built-in `default_token_generator` and uses the user’s email to send the reset link.
- The **reset link** is dynamically created based on the provided frontend URL and contains the token to validate the user’s identity.

This file provides the essential functionality for resetting passwords and integrates with the user’s email system to facilitate a seamless password recovery process.
"""
