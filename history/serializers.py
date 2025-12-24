from rest_framework import serializers
from .models import History
from django.contrib.auth import get_user_model

User = get_user_model()
class TransactionSerializer(serializers.Serializer):
    receiver_email_or_phone = serializers.CharField()
    points = serializers.IntegerField(min_value=5)  # minimum 5 points to send

    def validate(self, data):
        from django.core.exceptions import ObjectDoesNotExist

        sender = self.context['request'].user
        receiver_query = data.get('receiver_email_or_phone')

        # Find receiver by email or phone
        try:
            receiver = User.objects.get(email=receiver_query)
        except ObjectDoesNotExist:
            try:
                receiver = User.objects.get(phone_number=receiver_query)
            except ObjectDoesNotExist:
                raise serializers.ValidationError("Receiver not found")

        if sender == receiver:
            raise serializers.ValidationError("You cannot send points to yourself")

        points_to_send = data['points']
        if sender.total_points < points_to_send:
            raise serializers.ValidationError(
                f"Insufficient points. You only have {sender.total_points} points"
            )

        data['sender'] = sender
        data['receiver'] = receiver
        return data
