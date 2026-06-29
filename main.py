from tkinter import *
from tkinter import messagebox, simpledialog
from clases import Vehiculo, Voucher, Espacio
from datetime import datetime

listaEspacios = []
listaVehiculos = []
listaVouchers = []

montoPorHora = 1000

"""
Funcionalidad:
Crea los espacios iniciales del estacionamiento.

Entrada:
No recibe parámetros.

Salida:
Llena la lista de espacios con objetos de tipo Espacio.
"""
def crearEstacionamiento():
    for numero in range(1, 21):
        if numero == 1 or numero == 2:
            tipo = "Especial"
        elif numero == 3:
            tipo = "Electrico"
        else:
            tipo = "General"

        espacio = Espacio(numero, tipo)
        listaEspacios.append(espacio)

"""
Funcionalidad:
Crea algunos vehículos de prueba para poder usar el sistema.

Entrada:
No recibe parámetros.

Salida:
Agrega vehículos a la lista de vehículos.
"""
def crearVehiculosYVouchers():
    vehiculo1 = Vehiculo("ABC123", "Toyota", "Rojo")
    vehiculo2 = Vehiculo("DEF456", "Hyundai", "Blanco")
    vehiculo3 = Vehiculo("GHI789", "Nissan", "Negro")

    listaVehiculos.append(vehiculo1)
    listaVehiculos.append(vehiculo2)
    listaVehiculos.append(vehiculo3)

    messagebox.showinfo("Vehículos", "Vehículos obtenidos correctamente.")

"""
Funcionalidad:
Busca un espacio libre de tipo general.

Entrada:
No recibe parámetros.

Salida:
Retorna un objeto Espacio si encuentra uno libre.
Retorna None si no hay espacios disponibles.
"""
def buscarEspacioLibre():
    for espacio in listaEspacios:
        if espacio.estado == "Libre" and espacio.tipo == "General":
            return espacio

    return None

"""
Funcionalidad:
Estaciona un vehículo en el primer espacio libre disponible.

Entrada:
No recibe parámetros directamente.
Solicita la placa mediante una ventana emergente.

Salida:
Coloca el vehículo en un espacio y genera su voucher.
"""
def estacionarVehiculo():
    if len(listaVehiculos) == 0:
        messagebox.showwarning("Error", "Primero debe obtener vehículos.")
        return

    placa = simpledialog.askstring("Estacionar", "Digite la placa:")
    vehiculoEncontrado = None

    for vehiculo in listaVehiculos:
        if vehiculo.placa == placa:
            vehiculoEncontrado = vehiculo

    if vehiculoEncontrado == None:
        messagebox.showwarning("Error", "Vehículo no encontrado.")
        return

    espacioLibre = buscarEspacioLibre()

    if espacioLibre == None:
        messagebox.showwarning("Error", "No hay espacios libres.")
        return

    horaEntrada = datetime.now().strftime("%H:%M")
    voucher = Voucher(placa, horaEntrada)

    espacioLibre.estacionarVehiculo(vehiculoEncontrado, voucher)
    listaVouchers.append(voucher)

    messagebox.showinfo("Correcto", "Vehículo estacionado en espacio " + str(espacioLibre.numero))

"""
Funcionalidad:
Muestra la información de un espacio seleccionado.

Entrada:
espacio: objeto de tipo Espacio.

Salida:
Muestra los datos del espacio en una ventana emergente.
"""
def observarEspacio(espacio):
    if espacio.estado == "Libre":
        mensaje = "Espacio: " + str(espacio.numero) + "\nTipo: " + espacio.tipo + "\nEstado: Libre"
    else:
        placa, marca, color = espacio.vehiculo.obtenerDatosVehiculo()

        mensaje = "Espacio: " + str(espacio.numero)
        mensaje += "\nTipo: " + espacio.tipo
        mensaje += "\nEstado: Ocupado"
        mensaje += "\nPlaca: " + placa
        mensaje += "\nMarca: " + marca
        mensaje += "\nColor: " + color
        mensaje += "\nHora entrada: " + espacio.voucher.horaEntrada

    messagebox.showinfo("Información del espacio", mensaje)

"""
Funcionalidad:
Factura un espacio ocupado y luego lo libera.

Entrada:
espacio: objeto de tipo Espacio.

Salida:
Muestra la factura y libera el espacio.
"""
def facturarEspacio(espacio):
    if espacio.estado == "Libre":
        messagebox.showwarning("Error", "Ese espacio está libre.")
        return

    tipoPago = simpledialog.askstring("Pago", "Tipo de pago: efectivo, sinpe o tarjeta")
    horaSalida = datetime.now().strftime("%H:%M")
    monto = montoPorHora

    espacio.voucher.asignarSalida(horaSalida, tipoPago, monto)

    mensaje = "Factura generada"
    mensaje += "\nPlaca: " + espacio.vehiculo.placa
    mensaje += "\nHora entrada: " + espacio.voucher.horaEntrada
    mensaje += "\nHora salida: " + horaSalida
    mensaje += "\nTipo pago: " + tipoPago
    mensaje += "\nMonto: " + str(monto)

    espacio.liberarEspacio()

    messagebox.showinfo("Factura", mensaje)


"""
Funcionalidad:
Crea una ventana con las opciones para un espacio seleccionado.

Entrada:
espacio: objeto de tipo Espacio.

Salida:
Muestra botones para observar o facturar el espacio.
"""
def crearMenuEspacio(espacio):
    ventana = Toplevel()
    ventana.title("Espacio " + str(espacio.numero))

    Button(ventana, text="Observar espacio", width=25, command=lambda: observarEspacio(espacio)).pack(pady=5)
    Button(ventana, text="Facturar espacio", width=25, command=lambda: facturarEspacio(espacio)).pack(pady=5)

"""
Funcionalidad:
Crea la ventana principal del sistema de parqueo.

Entrada:
No recibe parámetros.

Salida:
Muestra el menú principal del sistema.
"""
def crearVentanaPrincipal():
    ventana = Tk()
    ventana.title("Sistema de Parqueo")

    Button(ventana, text="Obtener vehículos", width=30, command=crearVehiculosYVouchers).pack(pady=5)
    Button(ventana, text="Ver estacionamiento", width=30, command=crearVentanaEstacionamiento).pack(pady=5)
    Button(ventana, text="Estacionar vehículo", width=30, command=estacionarVehiculo).pack(pady=5)
    Button(ventana, text="Salir", width=30, command=ventana.destroy).pack(pady=5)

    ventana.mainloop()

crearEstacionamiento()
crearVentanaPrincipal()