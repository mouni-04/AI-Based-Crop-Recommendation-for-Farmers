from django.db import models
from django.conf import settings

class CropRecommendationLog(models.Model):
    # Link to the Farmer
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    
    # Soil and Climate Inputs (Standard 5A Feature Set)
    n_value = models.FloatField(verbose_name="Nitrogen")
    p_value = models.FloatField(verbose_name="Phosphorus")
    k_value = models.FloatField(verbose_name="Potassium")
    ph_value = models.FloatField(verbose_name="Soil pH")
    temperature = models.FloatField()
    humidity = models.FloatField()
    rainfall = models.FloatField()
    
    # ML Result
    recommended_crop = models.CharField(max_length=100)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} - {self.recommended_crop} ({self.timestamp})"

class YieldPredictionLog(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    crop_name = models.CharField(max_length=100)
    season = models.CharField(max_length=50, null=True, blank=True) # Added
    area = models.FloatField(default=0.0) # Added
    predicted_yield = models.FloatField() 
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.crop_name} Yield: {self.predicted_yield}"