import csv
import os

# Definición de clases para los usuarios y sus respectivos métodos para manejar la lógica de la aplicación
class Usuario:
    def __init__(self, nombre, correo, contra, edad, descripcion):
        self.nombre = nombre
        self.correo = correo
        self.contra = contra
        self.edad = edad
        self.descripcion = descripcion

class Alumno(Usuario):
    def __init__(self, *args):
        super().__init__(*args)
        self.cursos = []

class Maestro(Usuario):
    def __init__(self, *args):
        super().__init__(*args)
        self.materias = []
        self.evaluaciones = []

    def promedio(self):
        return sum(self.evaluaciones)/len(self.evaluaciones) if self.evaluaciones else 0

class GestorTutorias:
    def __init__(self):
        self.usuarios = []
        self.csv_file = "usuarios.csv"
        self.crear_archivo_si_no_existe()
        self.cargar_datos()

    # Método para crear el archivo CSV si no existe
    def crear_archivo_si_no_existe(self):
        if not os.path.exists(self.csv_file):
            with open(self.csv_file, "w", newline='', encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=[
                    "tipo", "nombre", "correo", "contra", "edad", "descripcion",
                    "cursos", "materias", "evaluaciones"
                ])
                writer.writeheader()

    # Método para guardar los datos de los usuarios en el archivo CSV, Se utiliza DictWriter para escribir los datos de forma estructurada
    def guardar_datos(self):
        with open(self.csv_file, "w", newline='', encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=[
                "tipo", "nombre", "correo", "contra", "edad", "descripcion",
                "cursos", "materias", "evaluaciones"
            ])
            writer.writeheader()
            for u in self.usuarios:
                if isinstance(u, Alumno):
                    writer.writerow({
                        "tipo": "alumno",
                        "nombre": u.nombre,
                        "correo": u.correo,
                        "contra": u.contra,
                        "edad": u.edad,
                        "descripcion": u.descripcion,
                        "cursos": ";".join(u.cursos),
                        "materias": "",
                        "evaluaciones": ""
                    })
                elif isinstance(u, Maestro):
                    materias_serializadas = []
                    for m in u.materias:
                        color_fondo = m.get("color_fondo", "#FFFFFF")
                        color_texto = m.get("color_texto", "#000000")
                        materia_str = f'{m["nombre"]}|{",".join(m["horario"])}|{m["descripcion"]}|{color_fondo}|{color_texto}'
                        materias_serializadas.append(materia_str)
                    writer.writerow({
                        "tipo": "maestro",
                        "nombre": u.nombre,
                        "correo": u.correo,
                        "contra": u.contra,
                        "edad": u.edad,
                        "descripcion": u.descripcion,
                        "cursos": "",
                        "materias": ";".join(materias_serializadas),
                        "evaluaciones": ";".join(map(str, u.evaluaciones))
                    })

    # Método para cargar los datos de los usuarios desde el archivo CSV, Se utiliza DictReader para leer los datos de forma estructurada
    def cargar_datos(self):
        with open(self.csv_file, "r", newline='', encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row["tipo"] == "alumno":
                    u = Alumno(row["nombre"], row["correo"], row["contra"], int(row["edad"]), row["descripcion"])
                    u.cursos = row["cursos"].split(";") if row["cursos"] else []
                elif row["tipo"] == "maestro":
                    u = Maestro(row["nombre"], row["correo"], row["contra"], int(row["edad"]), row["descripcion"])
                    u.materias = []
                    if row["materias"]:
                        for m in row["materias"].split(";"):
                            partes = m.split("|")
                            if len(partes) == 5:
                                nombre, horario_str, desc, color_fondo, color_texto = partes
                            else:
                                nombre, horario_str, desc = partes[:3]
                                color_fondo = "#FFFFFF"
                                color_texto = "#000000"
                            u.materias.append({
                                "nombre": nombre,
                                "horario": horario_str.split(","),
                                "descripcion": desc,
                                "color_fondo": color_fondo,
                                "color_texto": color_texto
                            })
                    u.evaluaciones = list(map(int, row["evaluaciones"].split(";"))) if row["evaluaciones"] else []
                self.usuarios.append(u)
    
    # Métodos para manejar la lógica de la aplicación
    def eliminar_materia_alumno(self, correo_alumno, nombre_materia, motivo):
        alumno = next((u for u in self.usuarios if isinstance(u, Alumno) and u.correo == correo_alumno), None)
        if not alumno:
            raise Exception("Alumno no encontrado")

        if nombre_materia not in alumno.cursos:
            raise Exception("El alumno no tiene esa materia")

        alumno.cursos.remove(nombre_materia)
        self.guardar_datos()

        # Guardar motivo en un archivo de log
        with open("eliminaciones.log", "a", encoding="utf-8") as f:
            f.write(f"Alumno: {alumno.nombre} ({alumno.correo}), Materia eliminada: {nombre_materia}, Motivo: {motivo}\n")

    # Método para registrar un nuevo usuario, ya sea alumno o maestro        
    def registrar_usuario(self, tipo, nombre, correo, contra, edad, descripcion):
        if "@" not in correo:
            raise ValueError("El correo debe contener un '@'")
        if len(contra) > 6:
            raise ValueError("La contraseña debe tener 6 caracteres o menos")
        if not (6 <= edad <= 80):
            raise ValueError("La edad debe estar entre 6 y 80 años")
        if any(u.correo == correo for u in self.usuarios):
            raise ValueError("Correo ya registrado")
        if tipo == "alumno":
            self.usuarios.append(Alumno(nombre, correo, contra, edad, descripcion))
        elif tipo == "maestro":
            self.usuarios.append(Maestro(nombre, correo, contra, edad, descripcion))
        self.guardar_datos()

    # Método para iniciar sesión, verifica el correo y la contraseña del usuario
    def login(self, correo, contra):
        for u in self.usuarios:
            if u.correo == correo and u.contra == contra:
                return u
        raise ValueError("Usuario o contraseña incorrectos")

    # Métodos para manejar las materias y la lógica de inscripción
    def materias_disponibles(self):
        materias = []
        for u in self.usuarios:
            if isinstance(u, Maestro):
                materias.extend(u.materias)
        return materias

    # Método para obtener los maestros que imparten una materia específica
    def obtener_maestros_por_materia(self, nombre_materia):
        return [u for u in self.usuarios if isinstance(u, Maestro)
                and any(m["nombre"] == nombre_materia for m in u.materias)]

    # Método para agregar una materia a un maestro, verifica que no haya conflictos de horario y que no exceda el límite de materias
    def agregar_materia_maestro(self, correo, nombre_materia, horario_nuevo, descripcion, color_fondo="#FFFFFF", color_texto="#000000"):
        maestro = next((u for u in self.usuarios if isinstance(u, Maestro) and u.correo == correo), None)
        if not maestro:
            raise ValueError("Maestro no encontrado")
        if len(maestro.materias) >= 3 and all(m["nombre"] != nombre_materia for m in maestro.materias):
            raise ValueError("Máximo 3 materias permitidas")

        for m in maestro.materias[:]:
            if any(h in m["horario"] for h in horario_nuevo):
                m["horario"] = [h for h in m["horario"] if h not in horario_nuevo]
                if not m["horario"]:
                    maestro.materias.remove(m)

        if any(m["nombre"] == nombre_materia for m in maestro.materias):
            raise ValueError("Materia ya registrada")

        maestro.materias.append({
            "nombre": nombre_materia,
            "horario": horario_nuevo,
            "descripcion": descripcion,
            "color_fondo": color_fondo,
            "color_texto": color_texto
        })
        self.guardar_datos()


    def agregar_materia_alumno(self, correo, nombre_materia):
        alumno = next((u for u in self.usuarios if isinstance(u, Alumno) and u.correo == correo), None)
        if not alumno:
            raise ValueError("Alumno no encontrado")
        if nombre_materia in alumno.cursos:
            raise ValueError("Materia ya agregada")
        if len(alumno.cursos) >= 3:
            raise ValueError("Máximo 3 materias permitidas")

        materias_actuales = [m for m in self.materias_disponibles() if m["nombre"] in alumno.cursos]
        nueva_materia = next((m for m in self.materias_disponibles() if m["nombre"] == nombre_materia), None)
        if not nueva_materia:
            raise ValueError("Materia no encontrada")
        for m in materias_actuales:
            if any(h in nueva_materia["horario"] for h in m["horario"]):
                raise ValueError("Conflicto de horario")
        alumno.cursos.append(nombre_materia)
        self.guardar_datos()


    def unirse_a_materia(self, correo_alumno, correo_maestro, nombre_materia):
        alumno = next((u for u in self.usuarios if isinstance(u, Alumno) and u.correo == correo_alumno), None)
        if not alumno:
            raise ValueError("Alumno no encontrado")
        
        maestro = next((u for u in self.usuarios if isinstance(u, Maestro) and u.correo == correo_maestro), None)
        if not maestro:
            raise ValueError("Maestro no encontrado")
        
        # Verificar que el maestro imparte esa materia
        if not any(m["nombre"] == nombre_materia for m in maestro.materias):
            raise ValueError(f"El maestro no imparte la materia {nombre_materia}")
        
        # Verificar que el alumno no tenga ya la materia
        if nombre_materia in alumno.cursos:
            raise ValueError("Ya estás inscrito en esta materia con este maestro")
        
        # Verificar límite de materias
        if len(alumno.cursos) >= 3:
            raise ValueError("Máximo 3 materias permitidas")
        
        # Verificar conflictos de horario
        materias_actuales = [m for m in self.materias_disponibles() if m["nombre"] in alumno.cursos]
        nueva_materia = next((m for m in maestro.materias if m["nombre"] == nombre_materia), None)
        
        for m in materias_actuales:
            if any(h in nueva_materia["horario"] for h in m["horario"]):
                raise ValueError("Conflicto de horario con otras materias")
        
        # Agregar la materia al alumno
        alumno.cursos.append(nombre_materia)
        self.guardar_datos()

    def evaluar_maestro(self, correo_maestro, calificacion):
        maestro = next((u for u in self.usuarios if isinstance(u, Maestro) and u.correo == correo_maestro), None)
        if maestro:
            maestro.evaluaciones.append(calificacion)
            self.guardar_datos()

    def eliminar_materia_maestro(self, correo_maestro, nombre_materia):
        maestro = next((u for u in self.usuarios if isinstance(u, Maestro) and u.correo == correo_maestro), None)
        if not maestro:
            raise Exception("Maestro no encontrado")

        nuevas = [m for m in maestro.materias if m["nombre"] != nombre_materia]
        if len(nuevas) == len(maestro.materias):
            raise Exception("La materia no existe para este maestro")

        maestro.materias = nuevas
        self.guardar_datos()
