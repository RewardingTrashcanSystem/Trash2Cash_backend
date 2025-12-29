# models.py - Only add History model
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class History(models.Model):
    ACTION_CHOICES = [
        ('scan', 'QR Scan'),
        ('transfer_in', 'Points Received'),
        ('transfer_out', 'Points Sent'),
    ]
    
    MATERIAL_CHOICES = [
        ('plastic', 'Plastic'),
        ('metal', 'Metal'),
        ('non-recycle', 'Non-Recyclable'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='history')
    points = models.IntegerField()
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    material_type = models.CharField(max_length=20, choices=MATERIAL_CHOICES, blank=True, null=True)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'History'
    
    def __str__(self):
        if self.material_type:
            return f"{self.user.email} - {self.action} - {self.material_type} - {self.points} points"
        return f"{self.user.email} - {self.action} - {self.points} points"