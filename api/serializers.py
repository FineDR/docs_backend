from rest_framework import serializers
from .models import UserTB
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password

class UserTBSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserTB
        fields = ["email","first_name","middle_name","last_name",'created_at',"password"]
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        validated_data["is_active"] = False
        user = UserTB.objects.create_user(**validated_data)
        return user

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get("email")
        password = data.get("password")
        user = authenticate(email=email, password=password)
        
        if user is None:
            raise serializers.ValidationError("Invalid credentials")
        if not user.is_active:
            raise serializers.ValidationError("Email not verified. Please check your email.")
        
        data["user"] = user
        return data

class UserProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserTB
        fields = ["email","first_name","middle_name","last_name" ,"is_active"]
        read_only_fields = ["email", "is_active"]



class PasswordResetSerializer(serializers.Serializer):
    new_password = serializers.CharField(write_only=True, required=True, min_length=8)

    def validate_new_password(self, value):
        try:
            validate_password(value)
        except Exception as e:
            raise serializers.ValidationError(str(e))
        return value