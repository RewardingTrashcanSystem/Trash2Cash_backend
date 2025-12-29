from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import RegisterSerializer, LoginSerializer, ProfileSerializer, CheckRegistrationSerializer
from rest_framework.parsers import MultiPartParser, FormParser
from django.core.exceptions import ValidationError


class CheckRegistrationView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = CheckRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            return Response(
                {
                    'status': 'success',
                    'message': 'Email and phone number are available for registration',
                    'data': {
                        'email': serializer.validated_data['email'],
                        'phone_number': serializer.validated_data['phone_number']
                    }
                },
                status=status.HTTP_200_OK
            )
        
        errors = serializer.errors
        error_message = ""
        login_suggestion = False
        
        if 'email' in errors and 'already registered' in str(errors['email'][0]).lower():
            error_message = errors['email'][0]
            login_suggestion = True
        elif 'phone_number' in errors and 'already registered' in str(errors['phone_number'][0]).lower():
            error_message = errors['phone_number'][0]
            login_suggestion = True
        else:
            # Format validation errors
            error_message = "Please check your input"
        
        response_data = {
            'status': 'error',
            'message': error_message,
            'suggest_login': login_suggestion,
            'errors': errors
        }
        return Response(response_data, status=status.HTTP_400_BAD_REQUEST)


class RegisterAPIView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = RegisterSerializer(data=request.data, context={'request': request})
        
        if serializer.is_valid():
            try:
                user = serializer.save()
                refresh = RefreshToken.for_user(user)
                
                # Get user data from serializer with image URL
                user_data = serializer.data
                
                return Response({
                    "status": "success",
                    "message": "User registered successfully",
                    "user": user_data,
                    "tokens": {
                        "access": str(refresh.access_token),
                        "refresh": str(refresh)
                    }
                }, status=status.HTTP_201_CREATED)
                
            except ValidationError as e:
                # Handle image validation errors from serializer.create()
                return Response({
                    "status": "error",
                    "message": "Registration failed",
                    "errors": {"image": [str(e)]}
                }, status=status.HTTP_400_BAD_REQUEST)
                
        else:
            # Return validation errors in consistent format
            return Response({
                "status": "error",
                "message": "Registration failed",
                "errors": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)


class LoginAPIView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = LoginSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            user = serializer.validated_data['user']
            refresh = RefreshToken.for_user(user)
            
            # Use ProfileSerializer to get consistent user data format
            profile_serializer = ProfileSerializer(user, context={'request': request})
            
            return Response({
                "message": "Login successful",
                "user": profile_serializer.data,  # Consistent format with profile
                "tokens": {
                    "access": str(refresh.access_token),
                    "refresh": str(refresh)
                }
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        return Response({"message": "Logout successful"})


class ProfileAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    
    def get(self, request):
        serializer = ProfileSerializer(request.user, context={'request': request})
        return Response(serializer.data)
    
    def put(self, request):
        serializer = ProfileSerializer(
            request.user,
            data=request.data,
            partial=True,
            context={'request': request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response({
                "message": "Profile updated successfully",
                "user": serializer.data
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)