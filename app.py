import pyrebase
from flask import Flask, jsonify

# Configuración de Flask
app = Flask(__name__)

#nuevo

# Implementación del patrón Singleton para la conexión a Firebase
class FirebaseSingleton:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            config = {
                "apiKey": "AIzaSyB_l89ywSTO1KHvV5ogxx_CniLSfx2p5S4",
                "authDomain": "jpaezdemo.firebaseapp.com",
                "databaseURL": "https://jpaezdemo-default-rtdb.firebaseio.com",
                "projectId": "jpaezdemo",
                "storageBucket": "jpaezdemo.appspot.com",
                "messagingSenderId": "175584888592",
                "appId": "1:175584888592:web:d8ae6447fe91eedcf7c795",
                "measurementId": "G-VKGPDPGLXS"
            }
            cls._instance = super(FirebaseSingleton, cls).__new__(cls)
            cls._instance.firebase = pyrebase.initialize_app(config)
            cls._instance.db = cls._instance.firebase.database()
        return cls._instance

# Uso del Singleton para acceder a la base de datos de Firebase
firebase_singleton = FirebaseSingleton()
fdb = firebase_singleton.db

# API para el análisis ABC
@app.route('/')
def api_abc_analisis():
    # Obtener los datos de Firebase
    inventario = fdb.child("Inventario").get()

    # Multiplicamos el stock por el precio para obtener el valor de los diferentes articulos en inventario
    inventory_data = {}
    for item in inventario.each():
        item_data = item.val()
        inventory_data[item_data['codigo']] = item_data['precio'] * item_data['estado']['9 de Octubre']['stock']

    # Realizamos el análisis ABC
    # Realizamos una sumatoria del total del costo del inventario
    total_value = sum(inventory_data.values())
    #Ordenamos los datos de manera descendente, lo usaremos en el grafico de valor de producto
    inventory_items = sorted(inventory_data.items(), key=lambda x: x[1], reverse=True)

    # Segun la formula del análsiis ABC para determinar en qué rango de porcentaje del valor acumulativo total se encuentra se usa lo siguiente:
    cumulative_value = 0
    abc_analysis = {}
    for item, value in inventory_items:
        cumulative_value += value
        if cumulative_value / total_value <= 0.8:
            abc_analysis[item] = 'A'
        elif cumulative_value / total_value <= 0.95:
            abc_analysis[item] = 'B'
        else:
            abc_analysis[item] = 'C'

    #Valores acumulados para grafica de tendencia
    cumulative_values = [sum([value for item, value in inventory_items][:i+1]) for i in range(len(inventory_items))]
    result = list(zip(range(len(inventory_data)), cumulative_values))

    category_start = 0

    #Envio los detalles de las secciones del grafico de tendencia
    rectangles = []
    for i in range(1, len(inventory_items)):
        if abc_analysis[inventory_items[i][0]] != abc_analysis[inventory_items[i-1][0]]:
            bottom_left = (category_start-0.4, cumulative_values[category_start])
            top_right = (i+0.4, cumulative_values[i-1])
            rectangles.append((bottom_left, top_right))
            category_start = i
    bottom_left = (category_start-0.4, cumulative_values[category_start])
    top_right = (len(inventory_items)-0.6, cumulative_values[-1])
    rectangles.append((bottom_left, top_right))

    print(abc_analysis)

    return jsonify(abc_analysis)

# Inicio de la aplicación Flask
if __name__ == "__main__":
    app.run(debug=True)
