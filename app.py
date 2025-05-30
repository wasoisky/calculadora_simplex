from flask import Flask, render_template, request, redirect, url_for
from solver import resolver_problema
import os

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/resolver', methods=['POST'])
def resolver():
    try:
        tipo = request.form['tipo']
        coef_objetivo = list(map(float, request.form['objetivo'].strip().split()))

        # Procesar restricciones
        restricciones_raw = request.form['restricciones'].strip().split('\n')
        restricciones = []
        num_vars = len(coef_objetivo)

        for i, linea in enumerate(restricciones_raw):
            if not linea.strip():
                continue
            partes = linea.strip().split()
            if len(partes) != num_vars:
                # DEBUG: Imprime el error antes de renderizar
                print(f"DEBUG: Error de validación en restricción #{i+1}: número de valores incorrecto.")
                return render_template('resultado.html', resultado={"error": f"Restricción #{i+1} inválida: se esperaban {num_vars} valores, pero hay {len(partes)}."})
            try:
                fila = list(map(float, partes))
            except ValueError:
                # DEBUG: Imprime el error antes de renderizar
                print(f"DEBUG: Error de validación en restricción #{i+1}: valores no numéricos.")
                return render_template('resultado.html', resultado={"error": f"Restricción #{i+1} contiene valores no numéricos."})
            restricciones.append(fila)

        # Procesar signos
        signos = [line.strip() for line in request.form['signos'].strip().split('\n') if line.strip()]
        rhs = [float(x.strip()) for x in request.form['rhs'].strip().split('\n') if x.strip()]

        if not (len(signos) == len(restricciones) == len(rhs)):
            # DEBUG: Imprime el error antes de renderizar
            print("DEBUG: Error de validación: el número de restricciones, signos y RHS no coincide.")
            return render_template('resultado.html', resultado={"error": "El número de restricciones, signos y RHS debe coincidir."})

        # DEBUG: Imprime los inputs antes de llamar a resolver_problema
        print("\nDEBUG: Inputs recibidos para resolver_problema:")
        print(f"  Tipo: {tipo}")
        print(f"  Objetivo: {coef_objetivo}")
        print(f"  Restricciones: {restricciones}")
        print(f"  Signos: {signos}")
        print(f"  RHS: {rhs}")

        # Llama a la función resolver_problema
        resultado = resolver_problema(tipo, coef_objetivo, restricciones, signos, rhs)

        # DEBUG: Imprime el diccionario 'resultado' completo devuelto por resolver_problema
        print("\nDEBUG: Diccionario 'resultado' devuelto por resolver_problema:")
        print(resultado)

        modelo_lp_contenido = ""
        # Leer el contenido del archivo .lp si se generó
        if "lp_path" in resultado and resultado["lp_path"] and os.path.exists(resultado["lp_path"]):
            try:
                with open(resultado["lp_path"], 'r', encoding='utf-8') as f:
                    modelo_lp_contenido = f.read()
                os.unlink(resultado["lp_path"]) # Eliminar el archivo temporal después de leerlo
            except Exception as e:
                modelo_lp_contenido = f"Error al leer el archivo LP: {e}"
        
        # DEBUG: Confirma qué se va a renderizar
        print("\nDEBUG: Renderizando resultado.html con:")
        print(f"  resultado: {resultado}")
        print(f"  modelo_lp_contenido (primeras 100 chars): {modelo_lp_contenido[:100]}...")

        return render_template('resultado.html', resultado=resultado, modelo_lp_contenido=modelo_lp_contenido)

    except Exception as e:
        # Captura cualquier error inesperado y lo pasa a la plantilla de resultados
        # DEBUG: Imprime la excepción exacta
        print(f"\nDEBUG: Excepción inesperada capturada en app.py: {e}")
        return render_template('resultado.html', resultado={"error": f"Ocurrió un error inesperado al procesar: {str(e)}"})

if __name__ == '__main__':
    app.run(debug=True)