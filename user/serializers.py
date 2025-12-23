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

        # Try to find user by email or phone
        try:
            user = User.objects.get(email=email_or_phone)
        except User.DoesNotExist:
            try:
                user = User.objects.get(phone=email_or_phone)
            except User.DoesNotExist:
                raise serializers.ValidationError("Invalid credentials")

        # Authenticate user
        user = authenticate(email=user.email, password=password)
        if not user:
            raise serializers.ValidationError("Invalid credentials")

        data['user'] = user
        return data
