from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import*

import zipfile  
import os
import virtuallab_client

from PySpice.Spice.Parser import SpiceParser  



class VentanaEstudiante(QMainWindow):

   
    def __init__(self, url, id_estudiante):
        super().__init__()  
        self.url = url  
        self.id_estudiante = id_estudiante  # Guarda el ID del estudiante que inició sesión
        self.netlist = ""  # Aquí se guardará el texto del circuito cuando se descargue
        self.setWindowTitle("Virtual Lab - Estudiante ID: " + id_estudiante)  # Título de la ventana

        # --- Etiquetas de título ---
        etiqueta_labs = QLabel("Mis laboratorios")  # Título de la lista
        etiqueta_circuito = QLabel("Circuito")  # Título de la imagen

        # --- Lista con los laboratorios asignados ---
        self.lista_labs = QListWidget()  # Lista donde el estudiante escoge un laboratorio
        # Cada vez que el estudiante escoge otro laboratorio se llama a self.labCambiado
        self.lista_labs.currentItemChanged.connect(self.labCambiado)

        # --- Etiqueta donde se mostrará la imagen del circuito ---
        self.imagen = QLabel("Descargue un laboratorio para ver el circuito")
        self.imagen.setAlignment(Qt.AlignCenter)
        self.imagen.setFixedSize(450, 300)
        self.imagen.setScaledContents(False)
        self.imagen.setWordWrap(True)

        # --- Cuadro de texto para mostrar resultados ---
        self.resultados = QTextEdit()  # Caja de texto de varias líneas
        self.resultados.setReadOnly(True)  # El estudiante solo puede leer, no escribir

        # --- Botones ---
        boton_actualizar = QPushButton("Actualizar lista")  # Botón para volver a pedir los laboratorios
        boton_actualizar.clicked.connect(self.cargarLabs)  # Al hacer clic se llama a self.cargarLabs
        self.boton_descargar = QPushButton("Descargar laboratorio")  # Botón para descargar
        self.boton_descargar.clicked.connect(self.descargarLab)  # Al hacer clic se llama a self.descargarLab
        self.boton_simular = QPushButton("Simular")  # Botón para simular
        self.boton_simular.clicked.connect(self.simularLab)  # Al hacer clic se llama a self.simularLab
        self.boton_simular.setEnabled(False)  # Queda apagado hasta que se descargue un laboratorio
        boton_salir = QPushButton("Cerrar sesión")  # Botón para salir
        boton_salir.clicked.connect(self.cerrarSesion)  # Al hacer clic se llama a self.cerrarSesion

        # --- Layout de cuadrícula: addWidget(widget, fila, columna, filas que ocupa, columnas que ocupa) ---
        layout = QGridLayout()  # Crea la cuadrícula
        layout.addWidget(etiqueta_labs, 0, 0)  # Fila 0, columna 0
        layout.addWidget(etiqueta_circuito, 0, 1)  # Fila 0, columna 1
        layout.addWidget(self.lista_labs, 1, 0)  # Fila 1, columna 0
        layout.addWidget(self.imagen, 1, 1)  # Fila 1, columna 1
        layout.addWidget(boton_actualizar, 2, 0)  # Fila 2, columna 0
        layout.addWidget(self.boton_descargar, 3, 0)  # Fila 3, columna 0
        layout.addWidget(self.boton_simular, 3, 1)  # Fila 3, columna 1
        layout.addWidget(self.resultados, 4, 0, 1, 2)  # Fila 4, ocupa 2 columnas
        layout.addWidget(boton_salir, 5, 0, 1, 2)  # Fila 5, ocupa 2 columnas

        widget_central = QWidget()  # QMainWindow necesita un widget central
        widget_central.setLayout(layout)  # Se le pone la cuadrícula al widget central
        self.setCentralWidget(widget_central)  # Se coloca el widget central en la ventana

        self.cargarLabs()  # Llena la lista apenas se abre la ventana

    # Función que pide al servidor los laboratorios asignados y llena la lista
    def cargarLabs(self):
        self.lista_labs.clear()  # Borra lo que tenía la lista
        labs = virtuallab_client.listStudentLabs(self.url, self.id_estudiante)  # Pide los laboratorios

        if labs == "No labs assigned" or labs == "error":  # Si no tiene laboratorios (o hubo un error)
            # Se explica en la caja de texto por qué no se puede descargar nada
            self.resultados.setText("No tiene laboratorios asignados.\n"
                                    "Pídale a su profesor que le asigne uno y luego presione 'Actualizar lista'.")
            self.boton_descargar.setEnabled(False)  # Se apaga Descargar porque no hay nada que descargar
            return  # Sale de la función

        sin_repetidos = sorted(set(labs.splitlines()))  # set() quita los repetidos y sorted() los ordena
        self.lista_labs.addItems(sin_repetidos)  # Agrega los laboratorios a la lista
        self.lista_labs.setCurrentRow(0)  # Deja escogido el primero para no tener que hacer clic
        self.boton_descargar.setEnabled(True)  # Se enciende Descargar porque sí hay laboratorios
        self.resultados.setText("Escoja un laboratorio y presione 'Descargar laboratorio'.")  # Instrucción

    # Función que se llama cuando el estudiante escoge otro laboratorio de la lista
    def labCambiado(self):
        self.boton_simular.setEnabled(False)  # Se apaga Simular: primero hay que descargar el nuevo
        self.imagen.setText("Descargue un laboratorio para ver el circuito")  # Se quita la imagen anterior

    
    def descargarLab(self):
        lab_escogido = self.lista_labs.currentItem()

        if lab_escogido is None:
            QMessageBox.warning(
                self, "Alerta", "Escoja un laboratorio de la lista"
            )
            return

        self.nombre_lab = lab_escogido.text().replace(".zip", "")
        nombre_zip = self.nombre_lab + ".zip"

        try:
            # Descargar laboratorio
            respuesta = virtuallab_client.downloadLab(
                self.url,
                self.id_estudiante,
                nombre_zip
            )

            ruta_zip = os.path.join("client", "labs", nombre_zip)

            print("Ruta del ZIP:", os.path.abspath(ruta_zip))
            print("¿Existe el ZIP?:", os.path.exists(ruta_zip))

            if not os.path.exists(ruta_zip):
                QMessageBox.warning(
                    self, "Error",
                    "No se encontró el ZIP descargado."
                )
                return

            if not zipfile.is_zipfile(ruta_zip):
                QMessageBox.warning(
                    self, "Error",
                    "El archivo descargado no es un ZIP válido."
                )
                return

            with zipfile.ZipFile(ruta_zip, "r") as z:

                archivos = z.namelist()
                print("Contenido del ZIP:", archivos)

                archivo_cir = next(
                    (f for f in archivos
                    if os.path.basename(f).lower() ==
                    (self.nombre_lab + ".cir").lower()),
                    None
                )

                archivo_png = next(
                    (f for f in archivos
                    if os.path.basename(f).lower() ==
                    (self.nombre_lab + ".png").lower()),
                    None
                )

                print("Archivo CIR:", archivo_cir)
                print("Archivo PNG:", archivo_png)

                if archivo_cir is None:
                    QMessageBox.warning(
                        self, "Error",
                        "El ZIP no contiene el archivo .cir."
                    )
                    return

                self.netlist = z.read(archivo_cir).decode("utf-8")

                if archivo_png is None:
                    self.imagen.clear()
                    self.imagen.setText(
                        "Este laboratorio no contiene imagen."
                    )
                    print("No se encontró la imagen.")
                else:
                    datos_imagen = z.read(archivo_png)

                    pixmap = QPixmap()
                    imagen_cargada = pixmap.loadFromData(datos_imagen)

                    print("Bytes de imagen:", len(datos_imagen))
                    print("¿Imagen cargada?:", imagen_cargada)
                    print("Tamaño original:", pixmap.size())

                    if not imagen_cargada or pixmap.isNull():
                        QMessageBox.warning(
                            self, "Error",
                            "El archivo PNG existe, pero no se puede leer."
                        )
                        return

                    self.imagen.setPixmap(
                        pixmap.scaled(
                            self.imagen.size(),
                            Qt.KeepAspectRatio,
                            Qt.SmoothTransformation
                        )
                    )
                    self.imagen.setText("")
                    self.imagen.setAlignment(Qt.AlignCenter)

                self.boton_simular.setEnabled(True)

                self.resultados.setText(
                    "Laboratorio " + self.nombre_lab +
                    " descargado correctamente.\nYa puede simular."
                )

        except Exception as e:
            QMessageBox.critical(
                self,
                "Error al cargar laboratorio",
                str(e)
            )
            print("Error:", repr(e))


  # Función (slot) del botón "Simular": calcula el punto de operación, igual que en la entrega 1
    def simularLab(self):
        parser = SpiceParser(source=self.netlist)  # Lee el texto del circuito
        circuito = parser.build_circuit()  # Construye el circuito a partir del texto
        simulador = circuito.simulator(temperature=25, nominal_temperature=25)  # Crea el simulador a 25 °C
        analisis = simulador.operating_point()  # Calcula el punto de operación (voltajes en DC)

        texto = "Resultados de " + self.nombre_lab + ":\n"  # Primera línea del resultado
        for nombre, nodo in analisis.nodes.items():  # Recorre cada nodo del circuito
            texto = texto + "Nodo " + nombre + ": " + f"{float(nodo[0]):.4f}" + " V\n"  # Agrega su voltaje
        self.resultados.setText(texto)  # Muestra los voltajes en la caja de texto

    # Función (slot) del botón "Cerrar sesión"
    def cerrarSesion(self):
        virtuallab_client.closeSession(self.url, self.id_estudiante)  # Cierra la sesión en el servidor
        self.close()  # Cierra esta ventana
