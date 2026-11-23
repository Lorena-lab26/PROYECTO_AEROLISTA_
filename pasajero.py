
# ==============================================================
# pasajero.py · La clase Pasajero
# --------------------------------------------------------------
# Cada reserva del vuelo es un objeto Pasajero.
# La lista enlazada guarda un Pasajero dentro de cada Nodo
# (en nodo.data).
# ==============================================================

from vuelo import clase_de_asiento


class Pasajero:
    """Un pasajero con su reserva en el vuelo AL-204."""

    # El constructor se ejecuta al crear un objeto Pasajero
    def __init__(self, numero, nombre, cedula, edad, asiento):

        self.numero = numero
        self.nombre = nombre
        self.cedula = cedula
        self.edad = edad
        self.asiento = asiento

    def clase(self):
        """Retorna 'Ejecutiva' o 'Económica'."""
        return clase_de_asiento(self.asiento)

    def es_menor_de_edad(self):
        """True si tiene menos de 18 años."""
        return self.edad < 18

    def a_diccionario(self):
        """Convierte el objeto en un diccionario."""

        return {
            "numero": self.numero,
            "nombre": self.nombre,
            "cedula": self.cedula,
            "edad": self.edad,
            "asiento": self.asiento,
        }

    def __str__(self):
        """Define cómo se muestra el pasajero con print()."""

        return (
            f"#{self.numero} | {self.nombre:<8} | {self.cedula} | "
            f"{self.edad:>2} años | asiento {self.asiento:<3} | "
            f"{self.clase()}"
        )
