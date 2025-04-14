from django.shortcuts import render

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import PredictionRequest, PredictionResult
from .serializers import PredictionRequestSerializer, PredictionResultSerializer
from .ml_model import predict

@api_view(['POST'])
def prediction(request):
    serializer = PredictionRequestSerializer(data=request.data)
    if serializer.is_valid():
        prediction_request = serializer.save()
        
        # Przygotuj dane dla modelu ML
        features = [
            prediction_request.feature1,
            prediction_request.feature2,
            prediction_request.feature3,
            prediction_request.feature4,
        ]
        
        # Uzyskaj predykcję z modelu ML
        prediction_value, confidence = predict(features)
        
        # Zapisz wynik
        prediction_result = PredictionResult.objects.create(
            request=prediction_request,
            prediction=prediction_value,
            confidence=confidence
        )
        
        # Zwróć wynik
        result_serializer = PredictionResultSerializer(prediction_result)
        return Response(result_serializer.data, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def prediction_history(request):
    results = PredictionResult.objects.all().order_by('-created_at')[:10]
    serializer = PredictionResultSerializer(results, many=True)
    return Response(serializer.data)