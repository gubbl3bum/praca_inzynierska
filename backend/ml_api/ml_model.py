import os
import numpy as np
import pickle
from sklearn.ensemble import RandomForestRegressor
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split

MODEL_PATH = os.path.join(os.path.dirname(__file__), 'model.pkl')

def train_model():
    """Trenuj i zapisz model scikit-learn jeśli nie istnieje."""
    if os.path.exists(MODEL_PATH):
        return
    
    # Dla demonstracji używamy zbioru Iris
    data = load_iris()
    X = data.data
    y = data.target
    
    # Trenowanie modelu
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    # Zapisz model
    with open(MODEL_PATH, 'wb') as f:
        pickle.dump(model, f)
    
    print("Model wytrenowany i zapisany.")

def load_model():
    """Załaduj zapisany model lub wytrenuj nowy."""
    if not os.path.exists(MODEL_PATH):
        train_model()
    
    with open(MODEL_PATH, 'rb') as f:
        model = pickle.load(f)
    
    return model

def predict(features):
    """Wykonaj predykcję dla podanych cech."""
    model = load_model()
    
    # Konwersja na numpy array
    features_array = np.array(features).reshape(1, -1)
    
    # Predykcja
    prediction = model.predict(features_array)[0]
    
    # Tu możesz dodać logikę dla przedziału ufności
    # W tym przykładzie po prostu zwracamy losową wartość
    confidence = 0.8 + np.random.random() * 0.2
    
    return float(prediction), float(confidence)