from django.db import models

class PredictionRequest(models.Model):
    feature1 = models.FloatField()
    feature2 = models.FloatField()
    feature3 = models.FloatField()
    feature4 = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Prediction Request {self.id} ({self.created_at})"

class PredictionResult(models.Model):
    request = models.OneToOneField(PredictionRequest, on_delete=models.CASCADE, related_name='result')
    prediction = models.FloatField()
    confidence = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Prediction Result {self.id} ({self.created_at})"