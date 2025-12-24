from django.db import models
from django.conf import settings

class History(models.Model):
    ACTION_CHOICES = [
        ('scan', 'QR Scan'),
        ('transfer_in', 'Points Received'),
        ('transfer_out', 'Points Sent'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='history')
    points = models.PositiveIntegerField()
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.action} - {self.points} pts"