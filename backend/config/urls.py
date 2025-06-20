from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse
from django.template import Template, Context
from ml_api.models import PredictionRequest, PredictionResult
import os

def home(request):
    # Zbierz informacje o systemie
    try:
        prediction_count = PredictionRequest.objects.count()
        result_count = PredictionResult.objects.count()
        latest_predictions = PredictionResult.objects.order_by('-created_at')[:5]
    except:
        prediction_count = 0
        result_count = 0
        latest_predictions = []
    
    # Sprawdź czy model ML istnieje
    model_path = os.path.join(os.path.dirname(__file__), '..', 'ml_api', 'model.pkl')
    model_exists = os.path.exists(model_path)
    
    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>WolfRead Backend - Dashboard</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
            .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            h1 { color: #2563eb; text-align: center; margin-bottom: 30px; }
            .section { margin: 20px 0; padding: 20px; background: #f8fafc; border-radius: 8px; border-left: 4px solid #2563eb; }
            .status-ok { color: #059669; font-weight: bold; }
            .status-warning { color: #d97706; font-weight: bold; }
            .api-endpoint { background: #1f2937; color: #f9fafb; padding: 10px; border-radius: 5px; font-family: monospace; margin: 5px 0; }
            .prediction-item { background: white; padding: 10px; margin: 5px 0; border-radius: 5px; border: 1px solid #e5e7eb; }
            .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
            .stat-box { text-align: center; padding: 20px; background: white; border-radius: 8px; border: 1px solid #e5e7eb; }
            .stat-number { font-size: 2em; font-weight: bold; color: #2563eb; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>📚 WolfRead Backend Dashboard</h1>
            
            <div class="grid">
                <div class="stat-box">
                    <div class="stat-number">{{ prediction_count }}</div>
                    <div>Total Predictions</div>
                </div>
                <div class="stat-box">
                    <div class="stat-number">{{ result_count }}</div>
                    <div>Results Generated</div>
                </div>
            </div>
            
            <div class="section">
                <h3>🏥 System Status</h3>
                <p><strong>Database:</strong> <span class="status-ok">✅ Connected</span></p>
                <p><strong>ML Model:</strong> 
                    {% if model_exists %}
                        <span class="status-ok">✅ Loaded</span>
                    {% else %}
                        <span class="status-warning">⚠️ Not found (will be created on first prediction)</span>
                    {% endif %}
                </p>
                <p><strong>API:</strong> <span class="status-ok">✅ Running</span></p>
            </div>
            
            <div class="section">
                <h3>🔗 API Endpoints</h3>
                <div class="api-endpoint">POST /api/predict/ - Make ML predictions</div>
                <div class="api-endpoint">GET /api/history/ - Get prediction history</div>
                <div class="api-endpoint">GET /admin/ - Django admin panel</div>
            </div>
            
            {% if latest_predictions %}
            <div class="section">
                <h3>📊 Latest Predictions</h3>
                {% for prediction in latest_predictions %}
                <div class="prediction-item">
                    <strong>ID:</strong> {{ prediction.id }} | 
                    <strong>Result:</strong> {{ prediction.prediction|floatformat:2 }} | 
                    <strong>Confidence:</strong> {{ prediction.confidence|floatformat:2 }} | 
                    <strong>Date:</strong> {{ prediction.created_at|date:"Y-m-d H:i" }}
                </div>
                {% endfor %}
            </div>
            {% endif %}
            
            <div class="section">
                <h3>🧪 Test API</h3>
                <p>Przetestuj API z poziomu terminala:</p>
                <div class="api-endpoint">
curl -X POST http://localhost:8000/api/predict/ \\<br>
&nbsp;&nbsp;-H "Content-Type: application/json" \\<br>
&nbsp;&nbsp;-d '{"feature1": 1.0, "feature2": 2.0, "feature3": 3.0, "feature4": 4.0}'
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    
    template = Template(html_template)
    context = Context({
        'prediction_count': prediction_count,
        'result_count': result_count,
        'latest_predictions': latest_predictions,
        'model_exists': model_exists
    })
    
    return HttpResponse(template.render(context))

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('ml_api.urls')),  
    path('', home),  
]