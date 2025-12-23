from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    
    class Meta:
        model = User
        fields = [
            'email',
            'first_name',
            'last_name',
            'phone_number',
            'password',
            'image'
        ]
    
    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User.objects.create_user(password=password, **validated_data)
        return user


class LoginSerializer(serializers.Serializer):
    email_or_phone = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email_or_phone = data.get('email_or_phone')
        password = data.get('password')

        # Try to find user by email
        try:
            user = User.objects.get(email=email_or_phone)
        except User.DoesNotExist:
            # If not found by email, try phone_number
            try:
                user = User.objects.get(phone_number=email_or_phone)
            except User.DoesNotExist:
                raise serializers.ValidationError("Invalid credentials")

        # Authenticate user - use email as username
        authenticated_user = authenticate(
            username=user.email,  # Use email as username for authentication
            password=password
        )
        
        if not authenticated_user:
            raise serializers.ValidationError("Invalid credentials")

        data['user'] = authenticated_user
        return data