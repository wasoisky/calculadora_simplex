from flask import Flask, render_template, request,redirect, url_for
from solver import resolver_problema

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
                continue  # ignorar líneas vacías
            partes = linea.strip().split()
            if len(partes) != num_vars:
                return f"❌ Restricción #{i+1} inválida: se esperaban {num_vars} valores, pero hay {len(partes)}.", 400
            try:
                fila = list(map(float, partes))
            except ValueError:
                return f"❌ Restricción #{i+1} contiene valores no numéricos.", 400
            restricciones.append(fila)

        # Procesar signos
        signos = [line.strip() for line in request.form['signos'].strip().split('\n') if line.strip()]
        rhs = [float(x.strip()) for x in request.form['rhs'].strip().split('\n') if x.strip()]

        if not (len(signos) == len(restricciones) == len(rhs)):
            return "❌ El número de restricciones, signos y RHS debe coincidir.", 400

        resultado = resolver_problema(tipo, coef_objetivo, restricciones, signos, rhs)

        # Leer archivo .lp generado por PuLP
        with open(resultado['lp_path'], 'r', encoding='utf-8') as f:
            modelo_lp = f.read()

        return render_template('resultado.html', resultado=resultado, modelo_lp=modelo_lp)

    except Exception as e:
        return f"❌ Error inesperado: {str(e)}", 500

if __name__ == '__main__':
    app.run(debug=True)
