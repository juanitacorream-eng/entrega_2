
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QFont

import requests
import virtuallab_client

from ventana_profesor import VentanaProfesor
from ventana_estudiante import VentanaEstudiante


# ==========================================
# CONFIGURACION DEL SERVIDOR
# ==========================================

URL = "http://127.0.0.1:80"

ROLES = {
    "Profesor": "professor",
    "Estudiante": "student"
}


# ==========================================
# VENTANA DE LOGIN
# ==========================================

class VentanaLogin(QMainWindow):

    def __init__(self):

        super().__init__()

        self.setWindowTitle("Virtual Lab - Login")

        # Etiquetas

        etiqueta_nombre = QLabel("Nombre:")
        etiqueta_id = QLabel("ID:")
        etiqueta_rol = QLabel("Rol:")
        etiqueta_clave = QLabel("Contraseña:")

        # Campos

        self.campo_nombre = QLineEdit()
        self.campo_id = QLineEdit()
        self.campo_clave = QLineEdit()

        self.campo_clave.setEchoMode(QLineEdit.Password)

        # Lista de roles

        self.combo_rol = QComboBox()

        self.combo_rol.addItems([
            "Profesor",
            "Estudiante"
        ])

        # Botones

        boton_registrar = QPushButton("Registrarse")
        boton_entrar = QPushButton("Iniciar sesión")

        boton_registrar.clicked.connect(self.registrar)
        boton_entrar.clicked.connect(self.iniciarSesion)

        # Layout

        layout = QGridLayout()

        layout.addWidget(etiqueta_nombre, 0, 0)
        layout.addWidget(self.campo_nombre, 0, 1)

        layout.addWidget(etiqueta_id, 1, 0)
        layout.addWidget(self.campo_id, 1, 1)

        layout.addWidget(etiqueta_rol, 2, 0)
        layout.addWidget(self.combo_rol, 2, 1)

        layout.addWidget(etiqueta_clave, 3, 0)
        layout.addWidget(self.campo_clave, 3, 1)

        layout.addWidget(boton_registrar, 4, 0)
        layout.addWidget(boton_entrar, 4, 1)

        widget_central = QWidget()
        widget_central.setLayout(layout)

        self.setCentralWidget(widget_central)

        self.setFixedSize(400, 220)

    # ==========================================
    # REGISTRAR USUARIO
    # ==========================================

    def registrar(self):

        nombre = self.campo_nombre.text().strip()

        id_usuario = self.campo_id.text().strip()

        clave = self.campo_clave.text()

        rol = ROLES[self.combo_rol.currentText()]

        if not nombre or not id_usuario or not clave:

            QMessageBox.warning(
                self,
                "Alerta",
                "Ingrese nombre, ID y contraseña"
            )

            return

        try:

            respuesta = virtuallab_client.registerUser(
                URL,
                nombre,
                id_usuario,
                rol,
                clave
            )

        except requests.exceptions.RequestException as e:

            QMessageBox.critical(
                self,
                "Error de conexión",
                str(e)
            )

            return

        if respuesta.strip() == "User already registered":

            QMessageBox.warning(
                self,
                "Usuario existente",
                "Este ID ya está registrado.\n"
                "Utilice otro ID o inicie sesión."
            )

            return

        if "registered" in respuesta.lower():

            QMessageBox.information(
                self,
                "Registro exitoso",
                "Usuario registrado correctamente.\n"
                "Ahora puede iniciar sesión."
            )

            self.campo_clave.clear()

        else:

            QMessageBox.warning(
                self,
                "Error de registro",
                respuesta
            )

    # ==========================================
    # INICIAR SESION
    # ==========================================

    def iniciarSesion(self):

        id_usuario = self.campo_id.text().strip()

        clave = self.campo_clave.text()

        rol_escogido = self.combo_rol.currentText()

        if not id_usuario or not clave:

            QMessageBox.warning(
                self,
                "Alerta",
                "Ingrese ID y contraseña"
            )

            return

        try:

            respuesta = virtuallab_client.openSession(
                URL,
                id_usuario,
                clave
            )

        except requests.exceptions.RequestException as e:

            QMessageBox.critical(
                self,
                "Error de conexión",
                str(e)
            )

            return

        if respuesta.strip() != "Session was succesfully opened":

            QMessageBox.warning(
                self,
                "Error de acceso",
                "ID o contraseña incorrectos.\n"
                "Verifique sus datos."
            )

            return

        # ======================================
        # COMPROBAR ROL
        # ======================================

        try:

            if rol_escogido == "Profesor":

                prueba = virtuallab_client.listProfessorsLabs(
                    URL,
                    id_usuario
                )

            else:

                prueba = virtuallab_client.listStudentLabs(
                    URL,
                    id_usuario
                )

        except requests.exceptions.RequestException as e:

            virtuallab_client.closeSession(URL, id_usuario)

            QMessageBox.critical(
                self,
                "Error",
                str(e)
            )

            return

        if prueba.strip() == "error":

            virtuallab_client.closeSession(
                URL,
                id_usuario
            )

            QMessageBox.warning(
                self,
                "Rol incorrecto",
                "El usuario no corresponde al rol seleccionado."
            )

            return

        # ======================================
        # ABRIR VENTANA SEGUN EL ROL
        # ======================================

        if rol_escogido == "Profesor":

            self.ventana_nueva = VentanaProfesor(
                URL,
                id_usuario
            )

        else:

            self.ventana_nueva = VentanaEstudiante(
                URL,
                id_usuario
            )

        self.ventana_nueva.show()

        self.hide()

        self.campo_clave.clear()


# ==========================================
# INICIAR APLICACION
# ==========================================

if __name__ == "__main__":

    app = QApplication([])

    app.setFont(QFont("Arial", 11))

    ventana = VentanaLogin()

    ventana.show()

    app.exec()
