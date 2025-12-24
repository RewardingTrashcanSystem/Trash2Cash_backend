# user/serializers.py
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
            'image',           # Optional
            'total_points',    # Include but make read-only below
            'eco_level',       # Include but make read-only below
        ]
        # Make these fields read-only so they use model defaults
        read_only_fields = ['total_points', 'eco_level', 'image']
    
    def create(self, validated_data):
        password = validated_data.pop('password')
        # total_points and eco_level will use model defaults (10, "Newbie")
        user = User.objects.create_user(password=password, **validated_data)
        return user


class LoginSerializer(serializers.Serializer):
    email_or_phone = serializers.CharField()
    password = serializers.CharField(write_only=True)
    
    def validate(self, data):
        email_or_phone = data.get('email_or_phone')
        password = data.get('password')
        request = self.context.get('request')  # Important for Django 4.2+
        
        user = None
        try:
            user = User.objects.get(email=email_or_phone)
        except User.DoesNotExist:
            try:
                user = User.objects.get(phone_number=email_or_phone)
            except User.DoesNotExist:
                raise serializers.ValidationError("Invalid credentials")
        
        # Pass request to authenticate() for Django 4.2+
        authenticated_user = authenticate(
            request=request,
            username=user.email,  # Your USERNAME_FIELD is email
            password=password
        )
        
        if not authenticated_user:
            raise serializers.ValidationError("Invalid credentials")
        
        data['user'] = authenticated_user
        return data


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name',
            'phone_number', 'image', 'total_points', 'eco_level'
            # Remove 'user_type' - your model doesn't have it!
        ]
        # These fields can be seen but not changed directly by user
        read_only_fields = ['id', 'email', 'total_points', 'eco_level']
    
    def update(self, instance, validated_data):
        # Only allow updating these specific fields
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.phone_number = validated_data.get('phone_number', instance.phone_number)
        instance.image = validated_data.get('image', instance.image)
        instance.save()
        return instance