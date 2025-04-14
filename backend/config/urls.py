from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse

def home(request):
    return HttpResponse("<h1>Strona startowa</h1>")

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('ml_api.urls')),  
    path('', home),  
]