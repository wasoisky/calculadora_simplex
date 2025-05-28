import pulp
import tempfile

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

    with tempfile.NamedTemporaryFile(delete=False, suffix=".lp", mode='w', encoding='utf-8') as tmpfile:
        problema.writeLP(tmpfile.name)
        ruta_lp = tmpfile.name

    problema.solve()

    resultado = {
        "estado": pulp.LpStatus[problema.status],
        "funcion_objetivo": pulp.value(problema.objective),
        "variables": {v.name: v.varValue for v in variables},
        "lp_path": ruta_lp
    }
    return resultado
