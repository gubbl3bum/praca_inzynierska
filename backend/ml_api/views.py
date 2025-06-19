from django.shortcuts import render

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import PredictionRequest, PredictionResult
from .serializers import PredictionRequestSerializer, PredictionResultSerializer
from .ml_model import predict
import os
from django.utils import timezone

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

@api_view(['GET'])
def api_status(request):
    """Endpoint pokazujący status API i statystyki"""
    try:
        # Zbierz statystyki
        prediction_count = PredictionRequest.objects.count()
        result_count = PredictionResult.objects.count()
        
        # Znajdź najnowszą predykcję
        latest_prediction = PredictionResult.objects.order_by('-created_at').first()
        
        # Sprawdź czy model istnieje
        model_path = os.path.join(os.path.dirname(__file__), 'model.pkl')
        model_exists = os.path.exists(model_path)
        
        # Przygotuj response
        response_data = {
            'status': 'healthy',
            'timestamp': timezone.now(),
            'version': '1.0.0',
            'database': {
                'connected': True,
                'total_predictions': prediction_count,
                'total_results': result_count
            },
            'ml_model': {
                'loaded': model_exists,
                'path': model_path
            },
            'latest_prediction': None
        }
        
        if latest_prediction:
            response_data['latest_prediction'] = {
                'id': latest_prediction.id,
                'prediction': latest_prediction.prediction,
                'confidence': latest_prediction.confidence,
                'created_at': latest_prediction.created_at
            }
            
        return Response(response_data)
        
    except Exception as e:
        return Response({
            'status': 'error',
            'message': str(e),
            'timestamp': timezone.now()
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)