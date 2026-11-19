# Ventana del profesor: subir laboratorios y asignarlos a estudiantes.
# Esta ventana la abre ventana_login.py cuando entra un profesor.

from PyQt5.QtCore import *  # Clases base de Qt
from PyQt5.QtGui import *  # Clases gráficas de Qt
from PyQt5.QtWidgets import *  # Widgets de Qt (botones, listas, etc.)
import virtuallab_client  # Funciones que hablan con el servidor


# Clase de la ventana del profesor; hereda de QMainWindow
class VentanaProfesor(QMainWindow):

    # Constructor: recibe la dirección del servidor y el ID del profesor
    def __init__(self, url, id_profesor):
        super().__init__()  # Llama al constructor de QMainWindow
        self.url = url  # Guarda la dirección del servidor para usarla en los botones
        self.id_profesor = id_profesor  # Guarda el ID del profesor que inició sesión
        self.setWindowTitle("Virtual Lab - Profesor ID: " + id_profesor)  # Título de la ventana

        # --- Etiquetas que van encima de cada lista ---
        etiqueta_labs = QLabel("Laboratorios en el servidor")  # Título de la lista de laboratorios
        etiqueta_estudiantes = QLabel("Estudiantes (clic para marcar varios)")  # Título de la lista de estudiantes

        # --- Listas (QListWidget) donde el profesor escoge con un clic ---
        self.lista_labs = QListWidget()  # Lista de laboratorios subidos (se escoge uno solo)
        self.lista_estudiantes = QListWidget()  # Lista de estudiantes
        # MultiSelection: cada clic marca o desmarca un estudiante, así se pueden escoger varios
        self.lista_estudiantes.setSelectionMode(QAbstractItemView.MultiSelection)

        # --- Botones ---
        boton_subir = QPushButton("Subir laboratorio")  # Botón para subir un .zip
        boton_subir.clicked.connect(self.subirLab)  # Al hacer clic se llama a self.subirLab
        boton_asignar = QPushButton("Asignar laboratorio")  # Botón para asignar
        boton_asignar.clicked.connect(self.asignarLab)  # Al hacer clic se llama a self.asignarLab
        boton_salir = QPushButton("Cerrar sesión")  # Botón para salir
        boton_salir.clicked.connect(self.cerrarSesion)  # Al hacer clic se llama a self.cerrarSesion

        # --- Layout de cuadrícula: addWidget(widget, fila, columna, filas que ocupa, columnas que ocupa) ---
        layout = QGridLayout()  # Crea la cuadrícula
        layout.addWidget(etiqueta_labs, 0, 0)  # Fila 0, columna 0
        layout.addWidget(etiqueta_estudiantes, 0, 1)  # Fila 0, columna 1
        layout.addWidget(self.lista_labs, 1, 0)  # Fila 1, columna 0
        layout.addWidget(self.lista_estudiantes, 1, 1)  # Fila 1, columna 1
        layout.addWidget(boton_subir, 2, 0)  # Fila 2, columna 0
        layout.addWidget(boton_asignar, 2, 1)  # Fila 2, columna 1
        layout.addWidget(boton_salir, 3, 0, 1, 2)  # Fila 3, ocupa 1 fila y 2 columnas

        widget_central = QWidget()  # QMainWindow necesita un widget central
        widget_central.setLayout(layout)  # Se le pone la cuadrícula al widget central
        self.setCentralWidget(widget_central)  # Se coloca el widget central en la ventana

        self.actualizarListas()  # Llena las dos listas apenas se abre la ventana

    # Función que pide al servidor los laboratorios y los estudiantes y llena las listas
    def actualizarListas(self):
        self.lista_labs.clear()  # Borra lo que tenía la lista de laboratorios
        labs = virtuallab_client.listProfessorsLabs(self.url, self.id_profesor)  # Pide los laboratorios
        if labs != "No labs uploaded":  # Si hay laboratorios subidos
            self.lista_labs.addItems(labs.splitlines())  # Agrega uno por renglón

        self.lista_estudiantes.clear()  # Borra lo que tenía la lista de estudiantes
        estudiantes = virtuallab_client.listStudents(self.url, self.id_profesor)  # Pide los estudiantes
        if estudiantes != "No students registered":  # Si hay estudiantes registrados
            self.lista_estudiantes.addItems(estudiantes.splitlines())  # Agrega uno por renglón ("Nombre, ID")

    # Función (slot) del botón "Subir laboratorio"
    def subirLab(self):
        # Abre la ventana de Windows para escoger un archivo .zip (empieza en la carpeta client)
        ruta, _ = QFileDialog.getOpenFileName(self, "Escoger laboratorio", "client", "Laboratorio (*.zip)")
        if ruta == "":  # Si el profesor cerró la ventana sin escoger nada
            return  # Sale de la función
        respuesta = virtuallab_client.uploadLab(self.url, self.id_profesor, ruta)  # Envía el archivo al servidor
        QMessageBox.information(self, "Subir laboratorio", respuesta)  # Muestra lo que respondió el servidor
        self.actualizarListas()  # Refresca las listas para que aparezca el laboratorio nuevo

    # Función (slot) del botón "Asignar laboratorio"
    def asignarLab(self):
        lab_escogido = self.lista_labs.currentItem()  # Laboratorio seleccionado (None si no hay)
        estudiantes_escogidos = self.lista_estudiantes.selectedItems()  # Lista con TODOS los estudiantes marcados

        # Si no hay laboratorio o la lista de estudiantes marcados está vacía
        if lab_escogido is None or len(estudiantes_escogidos) == 0:
            QMessageBox.warning(self, "Alerta", "Escoja un laboratorio y al menos un estudiante")  # Avisa
            return  # Sale de la función

        nombre_lab = lab_escogido.text().replace(".zip", "")  # "rc.zip" -> "rc" (así lo guarda el servidor)
        resumen = "Laboratorio " + nombre_lab + ":\n"  # Texto donde se juntan las respuestas del servidor

        for estudiante in estudiantes_escogidos:  # Se repite una vez por cada estudiante marcado
            id_estudiante = estudiante.text().split(",")[1].strip()  # "Juan, 989898" -> "989898"
            # Pide al servidor que asigne el laboratorio a este estudiante
            respuesta = virtuallab_client.assignLab(self.url, self.id_profesor, nombre_lab, id_estudiante)
            resumen = resumen + estudiante.text() + " -> " + respuesta + "\n"  # Agrega una línea al resumen

        QMessageBox.information(self, "Asignar laboratorio", resumen)  # Muestra el resumen de todas
        self.lista_estudiantes.clearSelection()  # Desmarca a los estudiantes para la próxima asignación

    # Función (slot) del botón "Cerrar sesión"
    def cerrarSesion(self):
        virtuallab_client.closeSession(self.url, self.id_profesor)  # Cierra la sesión en el servidor
        self.close()  # Cierra esta ventana
