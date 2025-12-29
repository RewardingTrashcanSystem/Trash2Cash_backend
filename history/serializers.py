from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from .models import History

User = get_user_model()

class TransactionSerializer(serializers.Serializer):
    receiver_email_or_phone = serializers.CharField()
    points = serializers.IntegerField(min_value=5)
    
    def validate_receiver_email_or_phone(self, value):
        sender = self.context['request'].user
        receiver_query = value.strip()
        
        try:
            receiver = User.objects.get(email=receiver_query)
        except ObjectDoesNotExist:
            try:
                receiver = User.objects.get(phone_number=receiver_query)
            except ObjectDoesNotExist:
                raise serializers.ValidationError("User not found. Please check the email or phone number.")
        
        if sender == receiver:
            raise serializers.ValidationError("You cannot send points to yourself")
        
        return receiver_query
    
    def validate(self, data):
        sender = self.context['request'].user
        receiver_query = data['receiver_email_or_phone']
        points_to_send = data['points']
        
        try:
            receiver = User.objects.get(email=receiver_query)
        except ObjectDoesNotExist:
            receiver = User.objects.get(phone_number=receiver_query)
        
        if sender.total_points < points_to_send:
            raise serializers.ValidationError(
                f"Insufficient points. You have {sender.total_points} points."
            )
        
        data['sender'] = sender
        data['receiver'] = receiver
        return data


class QRScanSerializer(serializers.Serializer):
    materialType = serializers.CharField()
    pointsToAdd = serializers.IntegerField(min_value=1)
    date = serializers.DateTimeField()
    
    def validate_materialType(self, value):
        valid_materials = ['plastic', 'metal', 'non-recycle']
        if value.lower() not in valid_materials:
            raise serializers.ValidationError(
                f"Invalid material type. Must be one of: {', '.join(valid_materials)}"
            )
        return value.lower()


class HistorySerializer(serializers.ModelSerializer):
    formatted_date = serializers.SerializerMethodField()
    formatted_time = serializers.SerializerMethodField()
    icon = serializers.SerializerMethodField()
    color = serializers.SerializerMethodField()
    material_display = serializers.SerializerMethodField()
    
    class Meta:
        model = History
        fields = [
            'id', 'points', 'action', 'description', 'material_type', 'material_display',
            'created_at', 'formatted_date', 'formatted_time', 'icon', 'color'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_formatted_date(self, obj):
        return obj.created_at.strftime('%b %d, %Y')
    
    def get_formatted_time(self, obj):
        return obj.created_at.strftime('%I:%M %p')
    
    def get_icon(self, obj):
        icons = {
            'transfer_out': 'send',
            'transfer_in': 'receipt',
            'scan': 'qr_code_scanner',
        }
        return icons.get(obj.action, 'history')
    
    def get_color(self, obj):
        colors = {
            'transfer_out': 'red',
            'transfer_in': 'green',
            'scan': 'blue',
        }
        return colors.get(obj.action, 'gray')
    
    def get_material_display(self, obj):
        if obj.material_type:
            material_map = {
                'plastic': 'Plastic',
                'metal': 'Metal',
                'non-recycle': 'Non-Recyclable',
            }
            return material_map.get(obj.material_type, obj.material_type)
        return None