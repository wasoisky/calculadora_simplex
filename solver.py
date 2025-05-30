import pulp
import tempfile
import os
import re # ¡Importa el módulo de expresiones regulares!
import sys
from io import StringIO

def resolver_problema(tipo, coef_objetivo, restricciones, signos, rhs):
    problema = pulp.LpProblem("Problema_Lineal", pulp.LpMaximize if tipo == "max" else pulp.LpMinimize)
    n = len(coef_objetivo)
    variables = [pulp.LpVariable(f"x{i+1}", lowBound=0) for i in range(n)]

    problema += pulp.lpSum([coef_objetivo[i] * variables[i] for i in range(n)]), "Z"

    for i in range(len(restricciones)):
        lhs = pulp.lpSum([restricciones[i][j] * variables[j] for j in range(n)])
        if signos[i] == "<=":
            problema += lhs <= rhs[i]
        elif signos[i] == ">=":
            problema += lhs >= rhs[i]
        elif signos[i] == "=":
            problema += lhs == rhs[i]

    # Generar el archivo .lp temporal
    with tempfile.NamedTemporaryFile(delete=False, suffix=".lp", mode='w', encoding='utf-8') as tmpfile_lp:
        problema.writeLP(tmpfile_lp.name)
        ruta_lp = tmpfile_lp.name

    # Generar un archivo temporal para el log del solver
    temp_log_file = tempfile.NamedTemporaryFile(delete=False, suffix=".log", mode='w+', encoding='utf-8')
    ruta_log = temp_log_file.name
    temp_log_file.close() # Cerrar el archivo para que el solver pueda escribir en él

    solver_log = ""
    num_iteraciones = "N/A" # Inicializamos con "N/A" por si no se encuentra
    tiempo_solver = "N/A" # Inicializamos con "N/A" por si no se encuentra

    try:
        # Resolver el problema, dirigiendo la salida a nuestro archivo de log temporal
        # Asegúrate de NO incluir 'path_to_solver' aquí si tu versión de PuLP no lo soporta
        problema.solve(pulp.PULP_CBC_CMD(msg=True, timeLimit=None, logPath=ruta_log))

        # Leer el contenido del archivo de log
        with open(ruta_log, 'r', encoding='utf-8') as f:
            solver_log = f.read()

        # --- Extracción de iteraciones y tiempo del log ---
        # Buscar el número de iteraciones (ej: "3 iterations")
        match_iter = re.search(r'Optimal objective [\d.-]+ - (\d+)\s+iterations', solver_log)
        if match_iter:
            num_iteraciones = match_iter.group(1) # El primer grupo capturado es el número

        # Buscar el tiempo total (ej: "Total time (Wallclock seconds): 0.00")
        match_total_time = re.search(r'Total time \(Wallclock seconds\):\s+([\d.]+)', solver_log)
        if match_total_time:
            tiempo_solver = match_total_time.group(1) + "s" # El primer grupo es el valor, le añadimos 's' de segundos

    except Exception as e:
        solver_log = f"Error al ejecutar o leer el log del solver: {e}"
        num_iteraciones = "Error" # Indicar error en la extracción si ocurre una excepción
        tiempo_solver = "Error"
    finally:
        # Limpiar: eliminar el archivo de log temporal
        if os.path.exists(ruta_log):
            os.unlink(ruta_log)

    # --- Usar valores enteros directos de status de PuLP ---
    status_int = problema.status

    status_str_for_display = "Undefined"
    if status_int == 1:
        status_str_for_display = "Optimal"
    elif status_int == 0:
        status_str_for_display = "Not Solved"
    elif status_int == -1:
        status_str_for_display = "Infeasible"
    elif status_int == -2:
        status_str_for_display = "Unbounded"
    elif status_int == -3:
        status_str_for_display = "Undefined"
    else:
        status_str_for_display = f"UNKNOWN_STATUS_CODE_{status_int}"

    resultado = {
        "estado": status_str_for_display,
        "funcion_objetivo": None,
        "variables": {},
        "lp_path": ruta_lp,
        "log": solver_log, # El log completo se mantiene por si lo necesitas para depuración
        "num_iteraciones": num_iteraciones, # Nuevo campo
        "tiempo_solver": tiempo_solver # Nuevo campo
    }

    if status_int == 1:
        resultado["funcion_objetivo"] = pulp.value(problema.objective)
        resultado["variables"] = {v.name: v.varValue for v in variables}
    elif status_int == -1:
        resultado["mensaje"] = "El problema no tiene solución factible (Inviable)."
    elif status_int == -2:
        resultado["mensaje"] = "El problema no tiene una solución finita (Ilimitado)."
    else:
        resultado["mensaje"] = f"El problema no pudo ser resuelto: {status_str_for_display}"

    return resultado