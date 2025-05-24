import tkinter as tk
from tkinter import ttk, messagebox
from Tutorias_ba import GestorTutorias, Maestro, Alumno
from tkinter import colorchooser


gestor = GestorTutorias()

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Sistema de Tutorías")
        self.geometry("900x600")
        self.usuario = None
        self.pantalla_login()

    def limpiar_pantalla(self):
        for widget in self.winfo_children():
            widget.destroy()

    def pantalla_login(self):
        self.limpiar_pantalla()
        tk.Label(self, text="Iniciar Sesión", font=("Arial", 20)).pack(pady=20)

        tk.Label(self, text="Correo:").pack(pady=(10,0))
        correo = tk.Entry(self)
        correo.pack(pady=5)

        tk.Label(self, text="Contraseña:").pack(pady=(10,0))
        contra = tk.Entry(self, show="*")
        contra.pack(pady=5)

        def login():
            try:
                user = gestor.login(correo.get(), contra.get())
                self.usuario = user
                self.pantalla_principal()
            except Exception as e:
                messagebox.showerror("Error", str(e))

        tk.Button(self, text="Iniciar Sesión", command=login).pack(pady=10)
        tk.Button(self, text="Registrarse", command=self.pantalla_registro).pack()


    def pantalla_registro(self):
        self.limpiar_pantalla()
        tk.Label(self, text="Registro", font=("Arial", 20)).pack(pady=20)
        tipo = ttk.Combobox(self, values=["alumno", "maestro"])
        tipo.pack(pady=5)
        entradas = {}
        for campo in ["Nombre", "Correo", "Contraseña", "Edad", "Descripción"]:
            tk.Label(self, text=campo).pack()
            entradas[campo.lower()] = tk.Entry(self)
            entradas[campo.lower()].pack()

        def registrar():
                    try:
                        gestor.registrar_usuario(
                            tipo.get(),
                            entradas["nombre"].get(),
                            entradas["correo"].get(),
                            entradas["contraseña"].get(),
                            int(entradas["edad"].get()),
                            entradas["descripción"].get()
                        )
                        # Login automático
                        user = gestor.login(entradas["correo"].get(), entradas["contraseña"].get())
                        self.usuario = user
                        self.pantalla_principal()
                    except Exception as e:
                        messagebox.showerror("Error", str(e))

        tk.Button(self, text="Registrarse", command=registrar).pack(pady=10)
        tk.Button(self, text="Volver", command=self.pantalla_login).pack(pady=5)


    def pantalla_principal(self):
        self.limpiar_pantalla()
        tk.Label(self, text=f"Bienvenido {self.usuario.nombre}", font=("Arial", 16)).pack()
        tk.Button(self, text="Cerrar sesión", command=self.pantalla_login).pack()

        if isinstance(self.usuario, Alumno):
            self.mostrar_calendario(self.usuario.cursos)
            self.interfaz_alumno()
        elif isinstance(self.usuario, Maestro):
            cursos = [m["nombre"] for m in self.usuario.materias]
            self.mostrar_calendario(cursos)
            self.interfaz_maestro()

    def mostrar_calendario(self, materias):
        frame = tk.Frame(self)
        frame.pack(pady=10)

        dias = ["Lun", "Mar", "Mié", "Jue", "Vie"]
        horas = [f"{h}:00" for h in range(8, 20)]

        tk.Label(frame, text="Calendario", font=("Arial", 12, "bold")).grid(row=0, column=0, columnspan=6)

        # Etiquetas días
        for i, dia in enumerate([""] + dias):
            tk.Label(frame, text=dia, font=("Arial", 9)).grid(row=1, column=i)

        # Etiquetas horas y celdas más pequeñas
        for i, hora in enumerate(horas):
            tk.Label(frame, text=hora, font=("Arial", 8)).grid(row=i+2, column=0)
            for j in range(1, 6):
                cell = tk.Label(frame, text="", borderwidth=1, relief="solid", width=8, height=1)
                cell.grid(row=i+2, column=j, padx=1, pady=1)

        materias_obj = gestor.materias_disponibles()
        for m in materias_obj:
            if m["nombre"] in materias:
                bg_color = m.get("color_fondo", "lightblue")
                fg_color = m.get("color_texto", "black")
                for h in m["horario"]:
                    dia, hora = h.split("-")
                    col = dias.index(dia) + 1
                    row = horas.index(hora) + 2
                    tk.Label(frame,
                            text=m["nombre"],
                            bg=bg_color,
                            fg=fg_color,
                            borderwidth=1,
                            relief="solid",
                            width=8,
                            height=1,
                            font=("Arial", 8)
                            ).grid(row=row, column=col, padx=1, pady=1)

























    def interfaz_alumno(self):
        # Limpiar cualquier contenido previo en la ventana (opcional)
        # (Si ya haces self.limpiar_pantalla antes, no hace falta)

        # Crear un frame contenedor para que el canvas y scrollbar ocupen toda la ventana
        contenedor = tk.Frame(self)
        contenedor.pack(fill="both", expand=True)

        # Crear canvas y scrollbar vertical que abarcan todo el contenedor
        canvas = tk.Canvas(contenedor)
        scrollbar = ttk.Scrollbar(contenedor, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)

        # Ubicar scrollbar a la derecha y canvas al lado izquierdo, ocupando todo el espacio
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        # Frame dentro del canvas donde irán los widgets reales (scrollable_frame)
        scrollable_frame = tk.Frame(canvas)

        # Cuando cambia tamaño scrollable_frame, actualizar scrollregion del canvas
        def on_frame_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
        scrollable_frame.bind("<Configure>", on_frame_configure)

        # Insertar el scrollable_frame dentro del canvas
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

        # ------------------ CONTENIDO --------------------

        # Lista de materias del alumno
        tk.Label(scrollable_frame, text="Tus materias:").pack(pady=(10, 0))
        lista = tk.Listbox(scrollable_frame)
        lista.pack(fill="x", padx=10)
        for m in self.usuario.cursos:
            lista.insert(tk.END, m)

        def ver_detalles_materia():
            seleccionado = lista.get(tk.ACTIVE)
            if not seleccionado:
                messagebox.showwarning("Aviso", "Seleccione una materia primero")
                return
            nombre_materia = seleccionado.strip()
            materia = next((m for m in gestor.materias_disponibles() if m["nombre"] == nombre_materia), None)
            if not materia:
                messagebox.showinfo("Materia", "No se encontraron detalles de esta materia.")
                return

            maestros = gestor.obtener_maestros_por_materia(nombre_materia)
            texto_maestros = ""
            for m in maestros:
                texto_maestros += f"\nMaestro: {m.nombre}\nCalificación: {m.promedio():.1f}\nHoras: "
                for mat in m.materias:
                    if mat["nombre"] == nombre_materia:
                        texto_maestros += ", ".join(mat["horario"])
                        break
                texto_maestros += "\n\n"

            horarios = "\n".join(materia["horario"])
            detalles = f"Descripción: {materia['descripcion']}\n\nHorarios:\n{horarios}\n\n{texto_maestros}"
            messagebox.showinfo(f"Detalles de {materia['nombre']}", detalles)

        def mostrar_maestros_por_materia(materia):
            maestros = gestor.obtener_maestros_por_materia(materia)
            if not maestros:
                messagebox.showinfo("Maestros", f"No hay maestros disponibles para '{materia}'")
                return

            top = tk.Toplevel(self)
            top.title(f"Maestros de {materia}")
            top.geometry("450x400")

            canvas_m = tk.Canvas(top)
            scrollbar_m = tk.Scrollbar(top, orient="vertical", command=canvas_m.yview)
            scroll_frame = tk.Frame(canvas_m)

            scroll_frame.bind(
                "<Configure>",
                lambda e: canvas_m.configure(scrollregion=canvas_m.bbox("all"))
            )

            canvas_m.create_window((0, 0), window=scroll_frame, anchor="nw")
            canvas_m.configure(yscrollcommand=scrollbar_m.set)

            canvas_m.pack(side="left", fill="both", expand=True)
            scrollbar_m.pack(side="right", fill="y")

            for m in maestros:
                desc = m.descripcion
                materias_del_maestro = ", ".join([mat["nombre"] for mat in m.materias])

                horas = ""
                for mat in m.materias:
                    if mat["nombre"] == materia:
                        horas = ", ".join(mat["horario"])
                        break

                card = tk.Frame(scroll_frame, relief=tk.RIDGE, borderwidth=2, padx=10, pady=10)
                card.pack(fill="x", padx=5, pady=5)

                tk.Label(card, text=m.nombre, font=("Arial", 14, "bold")).pack(anchor="w")
                tk.Label(card, text=f"Calificación: {m.promedio():.1f}").pack(anchor="w")
                tk.Label(card, text=f"Materias: {materias_del_maestro}").pack(anchor="w")
                tk.Label(card, text=f"Horas de {materia}: {horas}").pack(anchor="w")
                tk.Label(card, text=desc, wraplength=350, justify="left").pack(anchor="w")

                def unirse(m=m):
                    try:
                        gestor.unirse_a_materia(self.usuario.correo, m.correo, materia)
                        messagebox.showinfo("Listo", f"Te has unido a la clase de {m.nombre} en {materia}.")
                        top.destroy()
                        self.pantalla_principal()
                    except Exception as e:
                        messagebox.showerror("Error", str(e))

                btn_unirse = tk.Button(card, text="Unirse a esta clase", command=unirse)
                btn_unirse.pack(anchor="e", pady=5)

        def eliminar_materia():
            seleccionado = lista.get(tk.ACTIVE)
            if not seleccionado:
                messagebox.showwarning("Aviso", "Seleccione una materia primero")
                return
            nombre_materia = seleccionado.strip()

            top = tk.Toplevel(self)
            top.title("Eliminar materia")

            tk.Label(top, text=f"¿Por qué quieres eliminar '{nombre_materia}'?").pack(pady=10)
            motivo_entry = tk.Text(top, height=4, width=40)
            motivo_entry.pack()

            def confirmar_eliminar():
                motivo = motivo_entry.get("1.0", tk.END).strip()
                if not motivo:
                    messagebox.showwarning("Aviso", "Por favor escribe un motivo")
                    return
                try:
                    gestor.eliminar_materia_alumno(self.usuario.correo, nombre_materia, motivo)
                    messagebox.showinfo("Listo", f"Materia '{nombre_materia}' eliminada.")
                    top.destroy()
                    self.pantalla_principal()
                except Exception as e:
                    messagebox.showerror("Error", str(e))

            tk.Button(top, text="Eliminar", command=confirmar_eliminar).pack(pady=10)

        tk.Button(scrollable_frame, text="Ver detalles de materia", command=ver_detalles_materia).pack(pady=5)
        tk.Button(scrollable_frame, text="Eliminar materia", command=eliminar_materia).pack(pady=5)

        tk.Label(scrollable_frame, text="Ver maestros por materia disponible:").pack(pady=10)

        materias_combo = ttk.Combobox(scrollable_frame, values=list(set([m["nombre"] for m in gestor.materias_disponibles()])))
        materias_combo.pack(pady=5)

        def ver_maestros_desde_combo():
            materia = materias_combo.get()
            if not materia:
                messagebox.showwarning("Aviso", "Seleccione una materia del menú desplegable.")
                return
            mostrar_maestros_por_materia(materia)

        tk.Button(scrollable_frame, text="Ver maestros de materia seleccionada", command=ver_maestros_desde_combo).pack(pady=5)


























    def interfaz_maestro(self):
        tk.Label(self, text="Tus materias:").pack()

        for m in self.usuario.materias:
            frame_materia = tk.Frame(self)
            frame_materia.pack(anchor="w", pady=2, fill='x')

            # Label con colores de fondo y texto
            tk.Label(frame_materia,
                    text=f'{m["nombre"]}: {", ".join(m["horario"])}',
                    bg=m.get("color_fondo", "#FFFFFF"),
                    fg=m.get("color_texto", "#000000"),
                    padx=5, pady=2
                    ).pack(side=tk.LEFT, fill='x', expand=True)

            btn_editar = tk.Button(frame_materia, text="Editar", command=lambda materia=m: self.ventana_editar_materia(materia))
            btn_editar.pack(side=tk.RIGHT, padx=(5, 20))

            btn_eliminar = tk.Button(frame_materia, text="Eliminar", command=lambda materia=m: self.eliminar_materia(materia))
            btn_eliminar.pack(side=tk.RIGHT, padx=(5, 0))

        tk.Button(self, text="Agregar Materia", command=self.agregar_materia).pack(pady=10)



    def eliminar_materia(self, materia):
        if messagebox.askyesno("Confirmar eliminación", f"¿Eliminar la materia '{materia['nombre']}'?"):
            gestor.eliminar_materia_maestro(self.usuario.correo, materia["nombre"])
            messagebox.showinfo("Éxito", f"Materia '{materia['nombre']}' eliminada")
            self.pantalla_principal()


    def ventana_editar_materia(self, materia):
        top = tk.Toplevel(self)
        top.title(f"Editar Materia: {materia['nombre']}")

        tk.Label(top, text="Nombre de la materia:").pack()
        nombre = tk.Entry(top)
        nombre.insert(0, materia["nombre"])
        nombre.pack()

        tk.Label(top, text="Descripción:").pack()
        descripcion = tk.Entry(top)
        descripcion.insert(0, materia["descripcion"])
        descripcion.pack()

        # Botones para elegir color de fondo y texto
        btn_color_fondo = tk.Button(top, text="Seleccionar color de fondo", bg=materia.get("color_fondo", "#FFFFFF"))
        btn_color_fondo.pack(pady=5)

        btn_color_texto = tk.Button(top, text="Seleccionar color de texto", bg=materia.get("color_texto", "#000000"))
        btn_color_texto.pack(pady=5)

        def elegir_color_fondo():
            color = colorchooser.askcolor(parent=top, color=btn_color_fondo["bg"], title="Selecciona color de fondo")
            if color[1]:
                btn_color_fondo.config(bg=color[1])

        def elegir_color_texto():
            color = colorchooser.askcolor(parent=top, color=btn_color_texto["bg"], title="Selecciona color de texto")
            if color[1]:
                btn_color_texto.config(bg=color[1])

        btn_color_fondo.config(command=elegir_color_fondo)
        btn_color_texto.config(command=elegir_color_texto)

        tk.Label(top, text="Selecciona días y horarios:").pack()

        dias = ["Lun", "Mar", "Mié", "Jue", "Vie"]
        dias_vars = {}
        rangos_por_dia = {}
        horas = [f"{h}:00" for h in range(8, 20)]

        horarios_por_dia = {dia: [] for dia in dias}
        for h in materia["horario"]:
            dia_h, hora_h = h.split("-")
            horarios_por_dia[dia_h].append(hora_h)

        for dia in dias:
            frame_dia = tk.Frame(top)
            frame_dia.pack(pady=2, anchor="w")
            dias_vars[dia] = tk.BooleanVar()

            if horarios_por_dia[dia]:
                dias_vars[dia].set(True)
                horas_del_dia = horarios_por_dia[dia]
                inicio_hora = min(horas_del_dia)
                fin_hora = max(horas_del_dia)
            else:
                dias_vars[dia].set(False)
                inicio_hora = ""
                fin_hora = ""

            chk = tk.Checkbutton(frame_dia, text=dia, variable=dias_vars[dia])
            chk.pack(side=tk.LEFT)

            tk.Label(frame_dia, text="Inicio:").pack(side=tk.LEFT, padx=2)
            inicio_cb = ttk.Combobox(frame_dia, values=horas, width=5)
            inicio_cb.pack(side=tk.LEFT)
            if inicio_hora:
                inicio_cb.set(inicio_hora)

            tk.Label(frame_dia, text="Fin:").pack(side=tk.LEFT, padx=2)
            fin_cb = ttk.Combobox(frame_dia, values=horas, width=5)
            fin_cb.pack(side=tk.LEFT)
            if fin_hora:
                fin_cb.set(fin_hora)

            rangos_por_dia[dia] = (inicio_cb, fin_cb)

        def confirmar_edicion():
            try:
                nombre_mat = nombre.get().strip()
                descripcion_mat = descripcion.get().strip()

                if not nombre_mat:
                    raise Exception("Debe ingresar el nombre de la materia")

                horario_nuevo = []

                for dia in dias:
                    if dias_vars[dia].get():
                        inicio = rangos_por_dia[dia][0].get()
                        fin = rangos_por_dia[dia][1].get()

                        if inicio == "" or fin == "":
                            raise Exception(f"Debe seleccionar hora inicio y fin para {dia}")

                        if inicio not in horas or fin not in horas:
                            raise Exception(f"Horario inválido en {dia}")

                        inicio_idx = horas.index(inicio)
                        fin_idx = horas.index(fin)

                        if fin_idx < inicio_idx:
                            raise Exception(f"Hora fin no puede ser antes que hora inicio en {dia}")

                        for idx in range(inicio_idx, fin_idx + 1):
                            horario_nuevo.append(f"{dia}-{horas[idx]}")

                if not horario_nuevo:
                    raise Exception("Debe seleccionar al menos un día y horario")

                for mat in self.usuario.materias:
                    if mat["nombre"] == nombre_mat and mat != materia:
                        raise Exception("Ya tienes otra materia con ese nombre")

                for mat in self.usuario.materias:
                    if mat != materia:
                        conflictos = set(horario_nuevo).intersection(mat["horario"])
                        if conflictos:
                            messagebox.showinfo("Advertencia", f"Se eliminarán horarios en conflicto de '{mat['nombre']}': {', '.join(conflictos)}")
                            gestor.eliminar_horarios_de_materia(self.usuario.correo, mat["nombre"], list(conflictos))

                materia["nombre"] = nombre_mat
                materia["descripcion"] = descripcion_mat
                materia["horario"] = horario_nuevo

                # Guardamos los colores seleccionados
                materia["color_fondo"] = btn_color_fondo["bg"]
                materia["color_texto"] = btn_color_texto["bg"]

                gestor.guardar_datos()

                messagebox.showinfo("Éxito", "Materia editada correctamente")
                top.destroy()
                self.pantalla_principal()

            except Exception as e:
                messagebox.showerror("Error", str(e))

        tk.Button(top, text="Guardar cambios", command=confirmar_edicion).pack(pady=10)


    def agregar_materia(self):
        top = tk.Toplevel(self)
        top.title("Agregar Materia")

        tk.Label(top, text="Nombre de la materia:").pack()
        nombre = tk.Entry(top)
        nombre.pack()

        tk.Label(top, text="Descripción:").pack()
        descripcion = tk.Entry(top)
        descripcion.pack()

        # Botones para elegir color de fondo y texto
        btn_color_fondo = tk.Button(top, text="Seleccionar color de fondo", bg="#FFFFFF")
        btn_color_fondo.pack(pady=5)

        btn_color_texto = tk.Button(top, text="Seleccionar color de texto", bg="#FFFFFF")
        
        btn_color_texto.pack(pady=5)

        def elegir_color_fondo():
            color = colorchooser.askcolor(parent=top, color=btn_color_fondo["bg"], title="Selecciona color de fondo")
            if color[1]:
                btn_color_fondo.config(bg=color[1])

        def elegir_color_texto():
            color = colorchooser.askcolor(parent=top, color=btn_color_texto["bg"], title="Selecciona color de texto")
            if color[1]:
                btn_color_texto.config(bg=color[1])

        btn_color_fondo.config(command=elegir_color_fondo)
        btn_color_texto.config(command=elegir_color_texto)

        tk.Label(top, text="Selecciona días y horarios:").pack()

        dias = ["Lun", "Mar", "Mié", "Jue", "Vie"]
        dias_vars = {}
        rangos_por_dia = {}
        horas = [f"{h}:00" for h in range(8, 20)]

        for dia in dias:
            frame_dia = tk.Frame(top)
            frame_dia.pack(pady=2, anchor="w")
            dias_vars[dia] = tk.BooleanVar()
            chk = tk.Checkbutton(frame_dia, text=dia, variable=dias_vars[dia])
            chk.pack(side=tk.LEFT)

            tk.Label(frame_dia, text="Inicio:").pack(side=tk.LEFT, padx=2)
            inicio_cb = ttk.Combobox(frame_dia, values=horas, width=5)
            inicio_cb.pack(side=tk.LEFT)

            tk.Label(frame_dia, text="Fin:").pack(side=tk.LEFT, padx=2)
            fin_cb = ttk.Combobox(frame_dia, values=horas, width=5)
            fin_cb.pack(side=tk.LEFT)

            rangos_por_dia[dia] = (inicio_cb, fin_cb)

        def confirmar():
            try:
                nombre_mat = nombre.get().strip()
                descripcion_mat = descripcion.get().strip()

                if not nombre_mat:
                    raise Exception("Debe ingresar el nombre de la materia")

                horario_nuevo = []

                for dia in dias:
                    if dias_vars[dia].get():
                        inicio = rangos_por_dia[dia][0].get()
                        fin = rangos_por_dia[dia][1].get()

                        if inicio == "" or fin == "":
                            raise Exception(f"Debe seleccionar hora inicio y fin para {dia}")

                        if inicio not in horas or fin not in horas:
                            raise Exception(f"Horario inválido en {dia}")

                        inicio_idx = horas.index(inicio)
                        fin_idx = horas.index(fin)

                        if fin_idx < inicio_idx:
                            raise Exception(f"Hora fin no puede ser antes que hora inicio en {dia}")

                        for idx in range(inicio_idx, fin_idx + 1):
                            horario_nuevo.append(f"{dia}-{horas[idx]}")

                if not horario_nuevo:
                    raise Exception("Debe seleccionar al menos un día y horario")

                for mat in self.usuario.materias:
                    conflicto = set(horario_nuevo).intersection(mat["horario"])
                    if conflicto:
                        messagebox.showinfo("Advertencia", f"Se eliminarán los siguientes horarios en conflicto de '{mat['nombre']}':\n{', '.join(conflicto)}")

                gestor.agregar_materia_maestro(self.usuario.correo, nombre_mat, horario_nuevo, descripcion_mat,
                                            color_fondo=btn_color_fondo["bg"], color_texto=btn_color_texto["bg"])
                messagebox.showinfo("Éxito", "Materia agregada correctamente")
                top.destroy()
                self.pantalla_principal()

            except Exception as e:
                messagebox.showerror("Error", str(e))

        tk.Button(top, text="Agregar", command=confirmar).pack(pady=10)





if __name__ == "__main__":
    app = App()
    app.mainloop()
