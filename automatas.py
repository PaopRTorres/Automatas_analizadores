# Importar las bibliotecas necesarias
from flask import Flask, render_template, request
import sys
import ply.lex as lex

# Crear una instancia de la aplicación Flask
app = Flask(__name__)

# Función para realizar el análisis léxico de una expresión
def lexer(expression):
    tokens = []  # Lista para almacenar los tokens
    current_token = ""  # Variable para construir el token actual
    operators = set(["+", "-", "*", "/"])  # Conjunto de operadores válidos
    error_token = None  # Variable para almacenar un token de error, si hay alguno

    # Conjunto de secuencias a resaltar en rojo
    red_sequences = set(["++", "--", "//", "**", "mas mas", "menos menos"])

    # Iterar sobre cada caracter de la expresión
    for char in expression:
        if char.isalnum() or char in set([" ", "+", "-"]):
            # Si es alfanumérico o un espacio, añadir al token actual
            current_token += char
        elif char in operators:
            # Si es un operador, añadir el token actual y luego el operador
            if current_token:
                if current_token in tokens:
                    error_token = current_token
                    break
                tokens.append(current_token)
            tokens.append(char)
            current_token = ""
        else:
            # Para cualquier otro caracter, añadir al token actual y resaltar si es una secuencia en rojo
            current_token += char
            if current_token in red_sequences:
                tokens.append(f'<span style="color:red;">{current_token}</span>')
                current_token = ""

    # Añadir el último token si existe
    if current_token:
        if current_token in tokens:
            error_token = current_token
        tokens.append(current_token)

    return tokens, error_token

# Importar el analizador de sentimientos desde la biblioteca transformers
from transformers import pipeline
sentiment_analyzer = pipeline('sentiment-analysis')  # Crear un analizador de sentimientos

# Ruta para la página principal
@app.route('/')
def index():
    return render_template('index.html')

# Ruta para la página de autómatas
@app.route('/automatas')
def automatas():
    return render_template('automatas.html')

# Ruta para el analizador semántico
@app.route('/analizador_semantico', methods=['GET', 'POST'])
def analizador_semantico():
    if request.method == 'POST':
        # Obtener el mensaje del formulario
        mensaje = request.form['mensaje']

        # Realizar el análisis de sentimientos
        resultados = sentiment_analyzer(mensaje)[0]

        # Extraer información relevante
        clasificacion = resultados['label']
        score = resultados['score']

        # Convertir la clasificación a estrellas y emoji
        if clasificacion == 'POSITIVE':
            estrellas = 5
            emoji = '😃'
        elif clasificacion == 'NEGATIVE':
            estrellas = 1
            emoji = '😟'
        else:
            estrellas = 3
            emoji = '😐'

        # Enviar los resultados al template y retornar la respuesta
        return render_template('analizador_semantico.html', mensaje=mensaje, estrellas=estrellas, emoji=emoji, score=score)

    # Retornar una respuesta por defecto para solicitudes GET
    return render_template('analizador_semantico.html')

# Ruta para el analizador léxico
@app.route('/analizador_lexico', methods=['GET', 'POST'])
def analizador_lexico():
    result = None
    error_message = None

    if request.method == 'POST':
        # Obtener la expresión del formulario
        expression = request.form['expression']

        # Realizar el análisis léxico
        tokens, error_token = lexer(expression)

        # Manejar errores si hay un token repetido o no válido
        if error_token:
            error_message = f"Error: Token '{error_token}' repetido o no válido."
        elif tokens is not None:
            result = {'expression': expression, 'tokens': tokens}

    return render_template('analizador_lexico.html', result=result, error_message=error_message)

# Ejecutar la aplicación si el script es el principal
if __name__ == '__main__':
    app.run(debug=True)
