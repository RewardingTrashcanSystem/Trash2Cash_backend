from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import RegisterSerializer, LoginSerializer, ProfileSerializer,CheckRegistartionSerializer
from rest_framework.parsers import MultiPartParser, FormParser
from django.core.exceptions import ValidationError

class CheckRegistrationView(APIView):
    permission_classes = [permissions.AllowAny]
    def post(self, request):
        serializer = CheckRegistartionSerializer(data=request.data)
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
        error_message =""
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
        serializer = RegisterSerializer(data=request.data)
        
        if serializer.is_valid():
            try:
                user = serializer.save()
                refresh = RefreshToken.for_user(user)
                
                return Response({
                    "status": "success",
                    "message": "User registered successfully",
                    "user": {
                        "id": user.id,
                        "email": user.email,
                        "first_name": user.first_name,
                        "last_name": user.last_name,
                        "phone_number": user.phone_number,
                        "total_points": user.total_points,
                        "eco_level": user.eco_level,
                        "image": request.build_absolute_uri(user.image.url) if user.image else None,
                    },
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
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            refresh = RefreshToken.for_user(user)
            return Response({
                "message": "Login successful",
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "phone_number": user.phone_number,
                    'eco_level': user.eco_level,
                    'total_points': user.total_points,
                },
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
        serializer = ProfileSerializer(request.user)
        return Response(serializer.data)
    def put(self, request):
        serializer = ProfileSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Profile updated successfully", "user": serializer.data})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
