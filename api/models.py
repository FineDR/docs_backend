from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin
from django.db import models

class UserTBManager(BaseUserManager):
 
    def create_user(self, email: str, password: str = None, **extra_fields) -> "UserTB":
      if not email:
          raise ValueError("Email is required")
      email = self.normalize_email(email)

      # Don't set is_active here — let the serializer or calling function decide
      user = self.model(email=email, **extra_fields)
      user.set_password(password)
      user.save(using=self._db)
      return user

    def create_superuser(self, email: str, password: str = None, **extra_fields) -> "UserTB":
      extra_fields.setdefault("is_staff", True)
      extra_fields.setdefault("is_superuser", True)
      extra_fields.setdefault("is_active", True)  # ✅ Allow superuser to log in

      if not extra_fields.get("is_staff"):
          raise ValueError("Superuser must have is_staff=True.")
      if not extra_fields.get("is_superuser"):
          raise ValueError("Superuser must have is_superuser=True.")

      return self.create_user(email, password, **extra_fields)

class UserTB(AbstractBaseUser, PermissionsMixin):
   
    email = models.EmailField(unique=True, verbose_name="Email Address")
    first_name = models.CharField(max_length=100, blank=True, null=True)
    middle_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100, blank=True, null=True)
    is_active = models.BooleanField(default=False)  
    is_staff = models.BooleanField(default=False)  
    is_superuser = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    enhanced_data = models.JSONField(null=True, blank=True)

    USERNAME_FIELD = "email" 

    objects = UserTBManager()

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"

    def __str__(self) -> str:
        return self.email


"""
### Guide to Adding More Fields to the Custom User Model:

1.Introduction:
   This guide is for adding more fields to the custom `UserTB` model, which extends `AbstractBaseUser` and `PermissionsMixin`. The model is designed to use email as the primary identifier (`USERNAME_FIELD = "email"`), and additional fields can be added to meet your application's requirements.

2.Adding More Fields to the Model:
   To add new fields, simply define them as class attributes within the `UserTB` model. For example:
   
   - First Name and Last Name:
     To add fields like `first_name` and `last_name`:
     ```python
     first_name = models.CharField(max_length=100, blank=True, null=True)
     last_name = models.CharField(max_length=100, blank=True, null=True)
     ```

   - Date of Birth:
     To add a date of birth field:
     ```python
     date_of_birth = models.DateField(null=True, blank=True)
     ```

   - Profile Picture:
     To add a profile picture field:
     ```python
     profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
     ```

   - Role:
     You can also add a `role` field to categorize users (e.g., student, admin):
     ```python
     role = models.CharField(max_length=50, choices=[('student', 'Student'), ('admin', 'Admin')])
     ```

   - Address:
     To add an address field:
     ```python
     address = models.TextField(null=True, blank=True)
     ```

3. Updating the Manager:
   After adding the new fields, make sure to update the `UserTBManager` to handle these fields correctly. You might want to add them to the `extra_fields` in the `create_user` and `create_superuser` methods. For instance:
   ```python
   def create_user(self, email: str, password: str = None, role: str = 'student', **extra_fields) -> "UserTB":
       if not email:
           raise ValueError("Email is required")
       email = self.normalize_email(email)
       extra_fields.setdefault("is_active", False)

       user = self.model(email=email, role=role, **extra_fields)
       user.set_password(password)
       user.save(using=self._db)
       return user
       
       
       
       
"""
