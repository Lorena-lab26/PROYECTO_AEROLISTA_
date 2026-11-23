
# ==============================================================
# app.py · El servidor de AeroLista
# ==============================================================

import traceback

from flask import Flask, jsonify, render_template, request
from werkzeug.exceptions import HTTPException

import verificador
import revisar
import persistencia

from lista_pasajeros import ListaPasajeros
from pasajero import Pasajero
from vuelo import VUELO, asiento_existe, total_asientos


# Crear la lista enlazada
lista = ListaPasajeros()

# Cargar las reservas guardadas
persistencia.cargar(lista)

print(f"Reservas cargadas en la lista enlazada: {lista.cantidad}")

app = Flask(__name__)


# ==============================================================
# PÁGINA PRINCIPAL
# ==============================================================

@app.get("/")
def inicio():
    return render_template("index.html", vuelo=VUELO)


# ==============================================================
# RESPUESTAS DE LA API
# ==============================================================

def respuesta_ok(datos=None, mensaje="", avisos=None, codigo=200):
    return jsonify({
        "ok": True,
        "datos": datos,
        "mensaje": mensaje,
        "avisos": avisos or [],
    }), codigo


def respuesta_error(mensaje, codigo=400):
    return jsonify({
        "ok": False,
        "mensaje": mensaje
    }), codigo


# ==============================================================
# CONVERTIR PASAJEROS A DICCIONARIOS
# ==============================================================

def a_diccionarios(pasajeros):
    resultado = []

    for pasajero in pasajeros:
        resultado.append(pasajero.a_diccionario())

    return resultado


# ==============================================================
# API: DATOS DEL VUELO
# ==============================================================

@app.get("/api/vuelo")
def ver_vuelo():
    return respuesta_ok(VUELO)


# ==============================================================
# API: RESUMEN DE RESERVAS
# ==============================================================

@app.get("/api/resumen")
def ver_resumen():
    cantidad = revisar.entero(lista.longitud(), "longitud")
    vacia = revisar.booleano(lista.esta_vacia(), "esta_vacia")

    return respuesta_ok({
        "cantidad": cantidad,
        "vacia": vacia,
        "total_asientos": total_asientos()
    })


# ==============================================================
# API: LISTAR RESERVAS
# ==============================================================

@app.get("/api/reservas")
def listar_reservas():
    clase = request.args.get("clase", "")

    if clase == "":
        pasajeros = revisar.lista_de_pasajeros(
            lista.listar(), "listar"
        )
    else:
        pasajeros = revisar.lista_de_pasajeros(
            lista.filtrar_por_clase(clase),
            "filtrar_por_clase"
        )

    return respuesta_ok(a_diccionarios(pasajeros))


# ==============================================================
# API: BUSCAR POR NÚMERO DE RESERVA
# ==============================================================

@app.get("/api/reservas/<int:numero>")
def buscar_reserva(numero):
    pasajero = revisar.pasajero_o_none(
        lista.buscar(numero), "buscar"
    )

    if pasajero is None:
        return respuesta_error(
            f"No existe la reserva #{numero}", 404
        )

    return respuesta_ok(
        pasajero.a_diccionario(),
        f"Reserva #{numero} encontrada"
    )


# ==============================================================
# API: BUSCAR POR ASIENTO
# ==============================================================

@app.get("/api/asientos/<asiento>")
def buscar_asiento(asiento):
    asiento = asiento.upper()

    pasajero = revisar.pasajero_o_none(
        lista.buscar_por_asiento(asiento),
        "buscar_por_asiento"
    )

    if pasajero is None:
        return respuesta_ok(
            None,
            f"El asiento {asiento} está libre"
        )

    return respuesta_ok(
        pasajero.a_diccionario(),
        f"En el {asiento} viaja {pasajero.nombre}"
    )


# ==============================================================
# API: BUSCAR POR CÉDULA
# ==============================================================

@app.get("/api/cedulas/<cedula>")
def buscar_cedula(cedula):
    pasajero = revisar.pasajero_o_none(
        lista.buscar_por_cedula(cedula),
        "buscar_por_cedula"
    )

    if pasajero is None:
        return respuesta_error(
            f"Ningún pasajero tiene la cédula {cedula}", 404
        )

    return respuesta_ok(
        pasajero.a_diccionario(),
        "Pasajero encontrado"
    )


# ==============================================================
# MANEJO DE ERRORES
# ==============================================================

@app.errorhandler(NotImplementedError)
def metodo_pendiente(error):
    metodo = str(error)

    return jsonify({
        "ok": False,
        "pendiente": True,
        "metodo": metodo,
        "mensaje": f"Falta implementar {metodo}() en lista_pasajeros.py"
    }), 501


@app.errorhandler(revisar.ErrorEnTuMetodo)
def metodo_con_problema(error):
    return jsonify({
        "ok": False,
        "error_codigo": True,
        "mensaje": str(error)
    }), 500


@app.errorhandler(Exception)
def error_inesperado(error):

    if isinstance(error, HTTPException):
        return jsonify({
            "ok": False,
            "mensaje": f"{error.code} {error.name}"
        }), error.code

    traceback.print_exc()

    return jsonify({
        "ok": False,
        "error_codigo": True,
        "mensaje": (
            f"Error en el código Python → "
            f"{type(error).__name__}: {error}"
        )
    }), 500


# ==============================================================
# LEER DATOS DEL FORMULARIO
# ==============================================================

def leer_formulario():
    datos = request.get_json(silent=True) or {}

    nombre = str(datos.get("nombre", "")).strip()
    cedula = str(datos.get("cedula", "")).strip()
    edad = str(datos.get("edad", "")).strip()
    asiento = str(datos.get("asiento", "")).strip().upper()

    return nombre, cedula, edad, asiento


# ==============================================================
# VALIDAR DATOS
# ==============================================================

def validar_campos(nombre, cedula, edad, asiento):

    if len(nombre) < 2:
        return "Escribe el nombre del pasajero"

    if not (cedula.isdigit() and len(cedula) == 10):
        return "La cédula debe tener 10 dígitos"

    if not str(edad).isdigit() or int(edad) > 120:
        return "La edad debe ser un número entre 0 y 120"

    if not asiento_existe(asiento):
        return f"El asiento '{asiento}' no existe en este avión"

    return ""


# ==============================================================
# API: CREAR RESERVA
# ==============================================================

@app.post("/api/reservas")
def reservar():

    nombre, cedula, edad, asiento = leer_formulario()

    problema = validar_campos(
        nombre, cedula, edad, asiento
    )

    if problema != "":
        return respuesta_error(problema)

    avisos = []

    try:
        if lista.buscar_por_asiento(asiento) is not None:
            return respuesta_error(
                f"El asiento {asiento} ya está reservado"
            )

    except NotImplementedError:
        avisos.append(
            "No se revisó si el asiento estaba libre: "
            "falta buscar_por_asiento()"
        )

    try:
        if lista.buscar_por_cedula(cedula) is not None:
            return respuesta_error(
                f"La cédula {cedula} ya tiene una reserva en este vuelo"
            )

    except NotImplementedError:
        avisos.append(
            "No se revisó si la cédula se repetía: "
            "falta buscar_por_cedula()"
        )

    pasajero = Pasajero(
        persistencia.nuevo_numero(),
        nombre,
        cedula,
        int(edad),
        asiento
    )

    lista.ingresar(pasajero)

    persistencia.guardar(lista)

    mensaje = (
        f"Reserva #{pasajero.numero} creada: "
        f"{nombre} en el asiento {asiento}"
    )

    return respuesta_ok(
        pasajero.a_diccionario(),
        mensaje,
        avisos,
        201
    )


# ==============================================================
# API: MODIFICAR RESERVA
# ==============================================================

@app.put("/api/reservas/<int:numero>")
def modificar_reserva(numero):

    nombre, cedula, edad, asiento = leer_formulario()

    pasajero = revisar.pasajero_o_none(
        lista.buscar(numero), "buscar"
    )

    if pasajero is None:
        return respuesta_error(
            f"No existe la reserva #{numero}", 404
        )

    problema = validar_campos(
        nombre, pasajero.cedula, edad, asiento
    )

    if problema != "":
        return respuesta_error(problema)

    avisos = []

    try:
        ocupante = lista.buscar_por_asiento(asiento)

        if ocupante is not None and ocupante.numero != numero:
            return respuesta_error(
                f"El asiento {asiento} ya es de {ocupante.nombre}"
            )

    except NotImplementedError:
        avisos.append(
            "No se revisó si el asiento nuevo estaba libre: "
            "falta buscar_por_asiento()"
        )

    cambiado = revisar.booleano(
        lista.modificar(numero, nombre, int(edad), asiento),
        "modificar"
    )

    if not cambiado:
        return respuesta_error(
            f"No se pudo modificar la reserva #{numero}", 404
        )

    persistencia.guardar(lista)

    actualizado = lista.buscar(numero)

    return respuesta_ok(
        actualizado.a_diccionario(),
        f"Reserva #{numero} actualizada",
        avisos
    )


# ==============================================================
# API: ELIMINAR RESERVA
# ==============================================================

@app.delete("/api/reservas/<int:numero>")
def eliminar_reserva(numero):

    eliminado = revisar.pasajero_o_none(
        lista.eliminar(numero), "eliminar"
    )

    if eliminado is None:
        return respuesta_error(
            f"No existe la reserva #{numero}", 404
        )

    persistencia.guardar(lista)

    mensaje = (
        f"Reserva #{numero} cancelada: "
        f"el asiento {eliminado.asiento} quedó libre"
    )

    return respuesta_ok(
        eliminado.a_diccionario(),
        mensaje
    )


# ==============================================================
# API: RESTAURAR DATOS DE EJEMPLO
# ==============================================================

@app.post("/api/restaurar")
def restaurar_datos():
    persistencia.restaurar(lista)

    return respuesta_ok(
        None,
        "Se restauraron las 12 reservas de ejemplo"
    )


# ==============================================================
# API: PROGRESO DE LAS PRUEBAS
# ==============================================================

@app.get("/api/progreso")
def ver_progreso():
    return respuesta_ok(verificador.revisar_todo())


# ==============================================================
# ENCENDER EL SERVIDOR
# ==============================================================

if __name__ == "__main__":
    app.run(debug=True, port=5050)
