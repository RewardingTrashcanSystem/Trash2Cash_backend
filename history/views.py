from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.pagination import PageNumberPagination
from django.db import transaction
from django.db.models import F, Sum
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist

from .models import History
from .serializers import TransactionSerializer, QRScanSerializer, HistorySerializer

User = get_user_model()


# ============ TRANSFER VIEWS ============
class CheckReceiverAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        email_or_phone = request.data.get('email_or_phone', '').strip()
        
        if not email_or_phone:
            return Response(
                {
                    "success": False,
                    "message": "Email or phone number is required"
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            receiver = User.objects.get(email=email_or_phone)
        except User.DoesNotExist:
            try:
                receiver = User.objects.get(phone_number=email_or_phone)
            except User.DoesNotExist:
                return Response(
                    {
                        "success": False,
                        "message": "User not found",
                        "exists": False
                    },
                    status=status.HTTP_200_OK
                )
        
        if receiver == request.user:
            return Response(
                {
                    "success": False,
                    "message": "Cannot send points to yourself",
                    "exists": True,
                    "is_self": True
                },
                status=status.HTTP_200_OK
            )
        
        return Response({
            "success": True,
            "message": "User found",
            "exists": True,
            "user": {
                "id": receiver.id,
                "full_name": f"{receiver.first_name} {receiver.last_name}",
                "email": receiver.email,
                "phone_number": receiver.phone_number,
            }
        })


class TransactionAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        serializer = TransactionSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            sender = serializer.validated_data['sender']
            receiver = serializer.validated_data['receiver']
            points = serializer.validated_data['points']

            sender_name = f"{sender.first_name} {sender.last_name}".strip()
            receiver_name = f"{receiver.first_name} {receiver.last_name}".strip()

            # Update points
            sender.total_points = F('total_points') - points
            receiver.total_points = F('total_points') + points
            
            sender.save(update_fields=['total_points'])
            receiver.save(update_fields=['total_points'])
            
            sender.refresh_from_db()
            receiver.refresh_from_db()
            
            # Create history records
            History.objects.create(
                user=sender,
                points=points,
                action='transfer_out',
                description=f"Sent {points} points to {receiver_name}"
            )
            
            History.objects.create(
                user=receiver,
                points=points,
                action='transfer_in',
                description=f"Received {points} points from {sender_name}"
            )

            return Response(
                {
                    "success": True,
                    "message": f"{points} points sent to {receiver_name}",
                    "data": {
                        "sender_points": sender.total_points,
                        "receiver_name": receiver_name,
                        "receiver_email": receiver.email,
                    }
                },
                status=status.HTTP_200_OK
            )

        return Response(
            {
                "success": False,
                "message": "Transfer failed",
                "errors": serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )


# ============ QR SCAN VIEWS ============
class QRScanAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    @transaction.atomic
    def post(self, request):
        serializer = QRScanSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {
                    "success": False,
                    "message": "Invalid QR data",
                    "errors": serializer.errors
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        material_type = serializer.validated_data['materialType']
        points = serializer.validated_data['pointsToAdd']
        scan_date = serializer.validated_data['date']
        user = request.user
        
        material_display = {
            'plastic': 'Plastic',
            'metal': 'Metal',
            'non-recycle': 'Non-Recyclable'
        }.get(material_type, material_type)
        
        # Update user's points
        user.total_points = F('total_points') + points
        user.save(update_fields=['total_points'])
        user.refresh_from_db()
        
        # Create scan history record
        description = f"QR Scan: Recycled {material_display}"
        
        History.objects.create(
            user=user,
            points=points,
            action='scan',
            material_type=material_type,
            description=description,
            created_at=scan_date
        )
        
        return Response(
            {
                "success": True,
                "message": f"{points} points added for recycling {material_display}",
                "data": {
                    "total_points": user.total_points,
                    "material": material_display,
                    "points_added": points,
                    "scan_date": scan_date,
                }
            },
            status=status.HTTP_200_OK
        )


# ============ HISTORY VIEWS ============
class HistoryPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class HistoryListAPIView(ListAPIView):
    serializer_class = HistorySerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = HistoryPagination
    
    def get_queryset(self):
        user = self.request.user
        
        action = self.request.query_params.get('action')
        days = self.request.query_params.get('days')
        
        queryset = History.objects.filter(user=user)
        
        if action and action != 'all':
            queryset = queryset.filter(action=action)
        
        if days and days.isdigit():
            days_int = int(days)
            start_date = timezone.now() - timedelta(days=days_int)
            queryset = queryset.filter(created_at__gte=start_date)
        
        return queryset
    
    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        
        user = request.user
        all_history = History.objects.filter(user=user)
        
        total_received = all_history.filter(action='transfer_in').aggregate(
            total=Sum('points')
        )['total'] or 0
        
        total_sent = all_history.filter(action='transfer_out').aggregate(
            total=Sum('points')
        )['total'] or 0
        
        total_scanned = all_history.filter(action='scan').aggregate(
            total=Sum('points')
        )['total'] or 0
        
        response.data.update({
            'summary': {
                'total_transactions': all_history.count(),
                'total_points_received': total_received,
                'total_points_sent': total_sent,
                'total_points_scanned': total_scanned,
                'net_points': user.total_points,
            }
        })
        
        return response


class RecentTransactionsAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        user = request.user
        limit = request.query_params.get('limit', 10)
        
        try:
            limit = int(limit)
        except ValueError:
            limit = 10
        
        recent_transactions = History.objects.filter(user=user).order_by('-created_at')[:limit]
        
        serializer = HistorySerializer(recent_transactions, many=True)
        
        return Response({
            "success": True,
            "transactions": serializer.data,
            "count": recent_transactions.count()
        })