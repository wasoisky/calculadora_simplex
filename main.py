import tkinter as tk
from tkinter import messagebox
from solver import resolver_problema

def resolver():
    try:
        tipo = tipo_var.get()
        coef_objetivo = list(map(float, entry_objetivo.get().split()))
        rhs = list(map(float, entry_rhs.get("1.0", "end").strip().split("\n")))
        signos = entry_signos.get("1.0", "end").strip().split("\n")
        restricciones = [
            list(map(float, fila.split())) for fila in entry_restricciones.get("1.0", "end").strip().split("\n")
        ]

        resultado = resolver_problema(tipo, coef_objetivo, restricciones, signos, rhs)
        # Mostrar contenido LP
        with open(resultado["lp_path"], "r", encoding="utf-8") as f:
            contenido_lp = f.read()

        ventana_lp = tk.Toplevel(ventana)
        ventana_lp.title("Modelo en formato LP")
        ventana_lp.geometry("600x400")

        texto_lp = tk.Text(ventana_lp, wrap=tk.NONE)
        texto_lp.insert("1.0", contenido_lp)
        texto_lp.pack(fill=tk.BOTH, expand=True)

        scrollbar_y = tk.Scrollbar(ventana_lp, orient=tk.VERTICAL, command=texto_lp.yview)
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        texto_lp.config(yscrollcommand=scrollbar_y.set)

        scrollbar_x = tk.Scrollbar(ventana_lp, orient=tk.HORIZONTAL, command=texto_lp.xview)
        scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
        texto_lp.config(xscrollcommand=scrollbar_x.set)

        texto_resultado = f"Estado: {resultado['estado']}\n"
        texto_resultado += f"Valor óptimo: {resultado['funcion_objetivo']}\n"
        for nombre, valor in resultado["variables"].items():
            texto_resultado += f"{nombre} = {valor}\n"

        messagebox.showinfo("Resultado", texto_resultado)
    except Exception as e:
        messagebox.showerror("Error", f"Hubo un problema: {e}")


        


# Ventana principal
ventana = tk.Tk()
ventana.title("Calculadora de Programación Lineal (PuLP + Tkinter)")
ventana.geometry("600x600")

# Tipo de problema
tipo_var = tk.StringVar(value="max")
tk.Label(ventana, text="Tipo de problema:").pack()
tk.Radiobutton(ventana, text="Maximizar", variable=tipo_var, value="max").pack()
tk.Radiobutton(ventana, text="Minimizar", variable=tipo_var, value="min").pack()

# Coeficientes función objetivo
tk.Label(ventana, text="Coef. función objetivo (ej: 3 5):").pack()
entry_objetivo = tk.Entry(ventana, width=50)
entry_objetivo.pack()

# Restricciones
tk.Label(ventana, text="Coef. de restricciones (una por línea):").pack()
entry_restricciones = tk.Text(ventana, height=5, width=50)
entry_restricciones.pack()

# Signos
tk.Label(ventana, text="Signos de restricciones (<=, >=, =):").pack()
entry_signos = tk.Text(ventana, height=5, width=20)
entry_signos.pack()

# RHS (lado derecho)
tk.Label(ventana, text="Término independiente (RHS):").pack()
entry_rhs = tk.Text(ventana, height=5, width=20)
entry_rhs.pack()

# Botón resolver
tk.Button(ventana, text="Resolver", command=resolver).pack(pady=10)

ventana.mainloop()
