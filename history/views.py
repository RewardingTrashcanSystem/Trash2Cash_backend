# history/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from .models import History
from .serializers import HistorySerializer, TransactionSerializer

class HistoryListAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        history = History.objects.filter(user=request.user)
        serializer = HistorySerializer(history, many=True)
        return Response(serializer.data)


class TransactionAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = TransactionSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            sender = serializer.validated_data['sender']
            receiver = serializer.validated_data['receiver']
            points = serializer.validated_data['points']

            # Deduct from sender and add to receiver
            sender.total_points -= points
            receiver.total_points += points
            sender.update_eco_level()
            receiver.update_eco_level()
            sender.save(update_fields=['total_points', 'eco_level'])
            receiver.save(update_fields=['total_points', 'eco_level'])

            # Create history records
            History.objects.bulk_create([
                History(
                    user=sender,
                    points=points,
                    action='transfer_out',
                    description=f"Sent {points} points to {receiver.get_full_name()}"
                ),
                History(
                    user=receiver,
                    points=points,
                    action='transfer_in',
                    description=f"Received {points} points from {sender.get_full_name()}"
                ),
            ])

            return Response(
                {"message": f"{points} points sent to {receiver.get_full_name()}"},
                status=status.HTTP_200_OK
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)