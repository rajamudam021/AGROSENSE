import json

from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15)

    def __str__(self):
        return self.user.get_full_name() or self.user.username


class Prediction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='prediction')
    N = models.FloatField()
    P = models.FloatField()
    K = models.FloatField()
    temperature = models.FloatField()
    humidity = models.FloatField()
    ph = models.FloatField()
    rainfall = models.FloatField()
    predicted_label = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    # New fields (all with defaults so existing data is preserved)
    city = models.CharField(max_length=100, blank=True, default='')
    confidence_scores = models.TextField(blank=True, default='')  # JSON string of top-3 predictions
    soil_health_score = models.FloatField(null=True, blank=True)
    land_size = models.FloatField(null=True, blank=True, help_text='Land size in acres')
    top2_crop = models.CharField(max_length=100, blank=True, default='')
    top3_crop = models.CharField(max_length=100, blank=True, default='')

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} -> {self.predicted_label}"

    def get_confidence_scores(self):
        """Parse and return the JSON confidence_scores field as a Python list."""
        if self.confidence_scores:
            try:
                return json.loads(self.confidence_scores)
            except (json.JSONDecodeError, TypeError):
                return []
        return []
