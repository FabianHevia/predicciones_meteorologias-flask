from flask import Flask, render_template, jsonify, request
import requests
import json
import os
from datetime import datetime, timedelta
import pandas as pd
from sklearn.linear_model import LinearRegression
import numpy as np

app = Flask(__name__)

# Configuración de API (usaremos el servicio meteorológico de Chile)
API_URL = "https://api.meteored.cl/index.php"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_current_weather', methods=['GET'])
def get_current_weather():
    ciudad = request.args.get('ciudad', 'Santiago')
    
    # Hacer petición a la API
    try:
        params = {
            'api_lang': 'es',
            'localidad': ciudad,
            'affiliate_id': 'jlqmfkp5pept'  # ID afiliado de ejemplo (necesitarás registrarte para uno real)
        }
        response = requests.get(API_URL, params=params)
        
        if response.status_code == 200:
            # Procesar y formatear los datos recibidos
            data = response.json()
            return jsonify(data)
        else:
            return jsonify({"error": f"Error al obtener datos: {response.status_code}"}), 500
            
    except Exception as e:
        return jsonify({"error": f"Error: {str(e)}"}), 500

@app.route('/predict_weather', methods=['GET'])
def predict_weather():
    ciudad = request.args.get('ciudad', 'Santiago')
    days = int(request.args.get('days', 7))
    
    # Obtener datos históricos (simulado - en producción usaríamos datos reales)
    try:
        # En producción: Reemplazar esto con datos históricos reales
        historical_data = get_historical_data(ciudad)
        
        # Preparar datos para la predicción
        X = np.array(range(len(historical_data))).reshape(-1, 1)
        y_temp = np.array([day['temp'] for day in historical_data])
        y_precip = np.array([day['precip'] for day in historical_data])
        
        # Entrenar modelos simples
        model_temp = LinearRegression().fit(X, y_temp)
        model_precip = LinearRegression().fit(X, y_precip)
        
        # Hacer predicciones
        future_days = np.array(range(len(historical_data), len(historical_data) + days)).reshape(-1, 1)
        future_temps = model_temp.predict(future_days)
        future_precip = model_precip.predict(future_days)
        
        # Formatear resultados
        today = datetime.now()
        results = []
        
        for i in range(days):
            future_date = today + timedelta(days=i+1)
            results.append({
                'date': future_date.strftime('%Y-%m-%d'),
                'temp': round(float(future_temps[i]), 1),
                'precip': max(0, round(float(future_precip[i]), 1))  # No permitir precipitación negativa
            })
            
        return jsonify(results)
        
    except Exception as e:
        return jsonify({"error": f"Error al predecir: {str(e)}"}), 500

def get_historical_data(ciudad):
    """
    Función para obtener datos históricos (simulados para este ejemplo)
    En producción, esta función debería obtener datos reales de una API o base de datos
    """
    # Datos simulados para los últimos 30 días
    data = []
    base_temp = 22 if ciudad == "Santiago" else 18  # Temperaturas base según ciudad
    
    for i in range(30):
        day = {
            'date': (datetime.now() - timedelta(days=30-i)).strftime('%Y-%m-%d'),
            'temp': base_temp + np.sin(i/5) * 5 + np.random.normal(0, 2),  # Simular variación sinusoidal con ruido
            'precip': max(0, np.random.normal(5, 15) if i % 7 == 0 else np.random.normal(0, 3))  # Más lluvia cada 7 días
        }
        data.append(day)
    
    return data

if __name__ == '__main__':
    app.run(debug=True)