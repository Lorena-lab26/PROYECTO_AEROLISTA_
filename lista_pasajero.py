
# ==============================================================
# lista_pasajeros.py
# Lista enlazada de pasajeros de AeroLista
# ==============================================================

from pasajero import Pasajero


# ==============================================================
# CLASE NODO
# ==============================================================

class Nodo:
    """Cada nodo guarda un pasajero y apunta al siguiente."""

    def __init__(self, data):
        self.data = data
        self.next = None


# ==============================================================
# CLASE LISTA PASAJEROS
# ==============================================================

class ListaPasajeros:
    """Lista enlazada de las reservas del vuelo."""

    def __init__(self):
        self.head = None
        self.cantidad = 0

    # Agregar un pasajero al final de la lista
    def ingresar(self, pasajero):
        nuevo = Nodo(pasajero)

        if self.head is None:
            self.head = nuevo
        else:
            actual = self.head

            while actual.next is not None:
                actual = actual.next

            actual.next = nuevo

        self.cantidad = self.cantidad + 1
        return True

    # ==========================================================
    # 1. COMPROBAR SI LA LISTA ESTÁ VACÍA
    # ==========================================================

    def esta_vacia(self):
        return self.head is None

    # ==========================================================
    # 2. OBTENER LA CANTIDAD DE PASAJEROS
    # ==========================================================

    def longitud(self):
        return self.cantidad

    # ==========================================================
    # 3. LISTAR TODOS LOS PASAJEROS
    # ==========================================================

    def listar(self):
        resultado = []
        actual = self.head

        while actual is not None:
            resultado.append(actual.data)
            actual = actual.next

        return resultado

    # ==========================================================
    # 4. BUSCAR POR NÚMERO DE RESERVA
    # ==========================================================

    def buscar(self, numero):
        actual = self.head

        while actual is not None:
            if actual.data.numero == numero:
                return actual.data

            actual = actual.next

        return None

    # ==========================================================
    # 5. BUSCAR POR ASIENTO
    # ==========================================================

    def buscar_por_asiento(self, asiento):
        actual = self.head

        while actual is not None:
            if actual.data.asiento == asiento:
                return actual.data

            actual = actual.next

        return None

    # ==========================================================
    # 6. BUSCAR POR CÉDULA
    # ==========================================================

    def buscar_por_cedula(self, cedula):
        actual = self.head

        while actual is not None:
            if actual.data.cedula == cedula:
                return actual.data

            actual = actual.next

        return None

    # ==========================================================
    # 7. MODIFICAR LOS DATOS DE UN PASAJERO
    # ==============================================================

    def modificar(self, numero, nuevo_nombre, nueva_edad, nuevo_asiento):
        pasajero = self.buscar(numero)

        if pasajero is None:
            return False

        pasajero.nombre = nuevo_nombre
        pasajero.edad = nueva_edad
        pasajero.asiento = nuevo_asiento

        return True

    # ==========================================================
    # 8. ELIMINAR UN PASAJERO
    # ==============================================================

    def eliminar(self, numero):

        # Comprobar si la lista está vacía
        if self.head is None:
            return None

        # Comprobar si el pasajero está en el primer nodo
        if self.head.data.numero == numero:
            eliminado = self.head.data
            self.head = self.head.next
            self.cantidad = self.cantidad - 1
            return eliminado

        # Buscar el nodo anterior al que queremos eliminar
        anterior = self.head

        while anterior.next is not None and anterior.next.data.numero != numero:
            anterior = anterior.next

        # Comprobar si no se encontró el pasajero
        if anterior.next is None:
            return None

        # Desconectar el nodo que se va a eliminar
        eliminado = anterior.next.data
        anterior.next = anterior.next.next
        self.cantidad = self.cantidad - 1

        return eliminado

    # ==========================================================
    # 9. FILTRAR PASAJEROS POR CLASE
    # ==============================================================

    def filtrar_por_clase(self, clase):
        resultado = []
        actual = self.head

        while actual is not None:
            pasajero = actual.data

            if pasajero.clase() == clase:
                resultado.append(pasajero)

            actual = actual.next

        return resultado
