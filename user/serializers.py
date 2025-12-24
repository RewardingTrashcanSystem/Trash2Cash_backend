from rest_framework import serializers
from django.contrib.auth import authenticate
from django.core.files.images import get_image_dimensions
from django.core.exceptions import ValidationError
from .models import User

# Constants matching your settings
MAX_UPLOAD_SIZE = 2 * 1024 * 1024  # 2MB
ALLOWED_IMAGE_EXTENSIONS = ['jpg', 'jpeg', 'png', 'gif']


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
            'total_points',    # Read-only (has default)
            'eco_level',       # Read-only (has default)
        ]
        read_only_fields = ['total_points', 'eco_level']
    
    def create(self, validated_data):
        password = validated_data.pop('password')
        # Handle image if present
        image = validated_data.get('image')
        if image:
            # Validate image size
            if image.size > MAX_UPLOAD_SIZE:
                raise ValidationError(f"Image size must be less than {MAX_UPLOAD_SIZE/1024/1024}MB")
            
            # Validate image extension
            ext = image.name.split('.')[-1].lower()
            if ext not in ALLOWED_IMAGE_EXTENSIONS:
                raise ValidationError(f"Only {', '.join(ALLOWED_IMAGE_EXTENSIONS)} files are allowed")
        
        user = User.objects.create_user(password=password, **validated_data)
        return user


class LoginSerializer(serializers.Serializer):
    email_or_phone = serializers.CharField()
    password = serializers.CharField(write_only=True)
    
    def validate(self, data):
        email_or_phone = data.get('email_or_phone')
        password = data.get('password')
        request = self.context.get('request')
        
        user = None
        try:
            user = User.objects.get(email=email_or_phone)
        except User.DoesNotExist:
            try:
                user = User.objects.get(phone_number=email_or_phone)
            except User.DoesNotExist:
                raise serializers.ValidationError("Invalid credentials")
        
        # Authenticate with request context
        authenticated_user = authenticate(
            request=request,
            username=user.email,
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
        ]
        read_only_fields = ['id', 'email', 'total_points', 'eco_level']
    
    def validate_image(self, value):
        """
        Custom validation for image field
        """
        if value:
            # 1. Check file size
            if value.size > MAX_UPLOAD_SIZE:
                raise serializers.ValidationError(
                    f"Image size must be less than {MAX_UPLOAD_SIZE/1024/1024}MB"
                )
            
            # 2. Check file extension
            ext = value.name.split('.')[-1].lower()
            if ext not in ALLOWED_IMAGE_EXTENSIONS:
                raise serializers.ValidationError(
                    f"File type not allowed. Allowed types: {', '.join(ALLOWED_IMAGE_EXTENSIONS)}"
                )
            
            # 3. Optional: Check image dimensions
            try:
                width, height = get_image_dimensions(value)
                if width > 5000 or height > 5000:
                    raise serializers.ValidationError(
                        "Image dimensions too large. Maximum 5000x5000 pixels"
                    )
            except:
                # If we can't read dimensions, still accept the file
                pass
        
        return value
    
    def update(self, instance, validated_data):
        # Update allowed fields
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.phone_number = validated_data.get('phone_number', instance.phone_number)
        
        # Handle image separately to use validation
        image = validated_data.get('image')
        if image:
            instance.image = image
        
        instance.save()
        return instance