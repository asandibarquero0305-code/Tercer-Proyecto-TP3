from tkinter import *
from tkinter import messagebox, simpledialog
from clases import Vehiculo, Voucher, Espacio
from datetime import datetime
import urllib.request
import json
import pickle
import random
import os
import csv
import webbrowser
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from fpdf import FPDF
import qrcode

listaEspacios = []
listaVehiculos = []
listaVouchers = []
listaReporteDia = []
listaBotonesEspacios = []

montoPorHora = 1000
tiempoGracia = 15
tiempoEstacionamiento=20
tieneElectrico=True

montoPorHora = 1000

"""
Funcionalidad:
Crea los espacios iniciales del estacionamiento tomando en cuenta
el tamaño configurado, los espacios especiales y el espacio eléctrico.

Entrada:
No recibe parámetros.

Salida:
Llena la lista de espacios con objetos de tipo Espacio.
"""
def crearEstacionamiento():
    listaEspacios.clear()

    cantidadEspeciales = round(tamanoEstacionamiento * 0.05)

    if cantidadEspeciales < 2:
        cantidadEspeciales = 2

    for numero in range(1, tamanoEstacionamiento + 1):
        if numero <= cantidadEspeciales:
            tipo = "Especial"
        elif tieneElectrico == True and numero == cantidadEspeciales + 1:
            tipo = "Electrico"
        else:
            tipo = "General"

        espacio = Espacio(numero, tipo)
        listaEspacios.append(espacio)

"""
Funcionalidad:
Obtiene vehículos desde una API utilizando urllib.request y json. La cantidad
de vehículos se calcula según los espacios generales disponibles del parqueo,
reservando un 5% de estos para que permanezcan libres.

Entrada:
No recibe parámetros.

Salida:
Llena la lista de vehículos con la información obtenida desde la API.
"""
def crearVehiculosYVouchers():
    listaVehiculos.clear()

    cantidadGenerales = 0

    for espacio in listaEspacios:
        if espacio.tipo == "General":
            cantidadGenerales += 1

    espaciosLibresReserva = round(cantidadGenerales * 0.05)

    if espaciosLibresReserva < 1:
        espaciosLibresReserva = 1

    cantidadVehiculos = cantidadGenerales - espaciosLibresReserva

    try:
        url = "https://vpic.nhtsa.dot.gov/api/vehicles/getallmanufacturers?format=json"

        respuesta = urllib.request.urlopen(url)
        datos = json.load(respuesta)

        resultados = datos["Results"]

        for numero in range(cantidadVehiculos):
            marca = resultados[numero]["Mfr_CommonName"]

            if marca == None:
                marca = resultados[numero]["Mfr_Name"]

            placa = "API" + str(100 + numero)
            color = "Color" + str(numero + 1)

            vehiculo = Vehiculo(placa, marca, color)
            listaVehiculos.append(vehiculo)

        messagebox.showinfo(
            "Vehículos",
            "Vehículos obtenidos desde la API correctamente.\nCantidad creada: " + str(len(listaVehiculos))
        )

    except:
        messagebox.showwarning(
            "Error",
            "No se pudo obtener la información desde la API."
        )

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
Calcula el monto que debe pagar un vehículo según el tiempo utilizado.

Entrada:
horaEntrada: hora en que ingresó el vehículo.
horaSalida: hora en que salió el vehículo.

Salida:
Retorna el monto total a pagar.
"""
def calcularMonto(horaEntrada, horaSalida):
    formato = "%H:%M"

    entrada = datetime.strptime(horaEntrada, formato)
    salida = datetime.strptime(horaSalida, formato)

    diferencia = salida - entrada
    minutos = diferencia.seconds // 60

    if minutos <= tiempoGracia:
        return 0

    horas = minutos // 60

    if minutos % 60 != 0:
        horas += 1

    monto = horas * montoPorHora

    return monto


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
    monto = calcularMonto(espacio.voucher.horaEntrada, horaSalida)

    espacio.voucher.asignarSalida(horaSalida, tipoPago, monto)

    mensaje = "Factura generada"
    mensaje += "\nPlaca: " + espacio.vehiculo.placa
    mensaje += "\nHora entrada: " + espacio.voucher.horaEntrada
    mensaje += "\nHora salida: " + horaSalida
    mensaje += "\nTipo pago: " + tipoPago
    mensaje += "\nMonto: " + str(monto)



    datoReporte = [
        espacio.numero,
        espacio.vehiculo.placa,
        espacio.voucher.horaEntrada,
        horaSalida,
        tipoPago,
        monto
    ]

    listaReporteDia.append(datoReporte)

    espacio.liberarEspacio()

    messagebox.showinfo("Factura", mensaje)


"""
Funcionalidad:
Crea una ventana para mostrar gráficamente los espacios del parqueo.

Entrada:
No recibe parámetros.

Salida:
Muestra una ventana con botones que representan los espacios.
"""
def crearVentanaEstacionamiento():
    ventana = Toplevel()
    ventana.title("Estacionamiento")

    listaBotonesEspacios.clear()

    fila = 0
    columna = 0

    for espacio in listaEspacios:
        if espacio.estado == "Libre":
            color = "green"
        else:
            color = "red"

        boton = Button(
            ventana,
            text=str(espacio.numero) + "\n" + espacio.tipo,
            bg=color,
            width=12,
            height=3,
            command=lambda e=espacio: crearMenuEspacio(e)
        )

        boton.grid(row=fila, column=columna, padx=5, pady=5)

        columna += 1

        if columna == 5:
            columna = 0
            fila += 1


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
Actualiza los colores de los botones del estacionamiento según el estado
de cada espacio.

Entrada:
No recibe parámetros.

Salida:
Cambia el color de los botones del parqueo.
"""
def actualizarVentanaEstacionamiento():
    contador = 0

    for espacio in listaEspacios:
        if espacio.estado == "Libre":
            color = "green"
        else:
            color = "red"

        if contador < len(listaBotonesEspacios):
            listaBotonesEspacios[contador].config(bg=color)

        contador += 1




"""
Funcionalidad:
Solicita el tipo de pago para una factura del cierre diario.

Entrada:
placa: placa del vehículo que se va a facturar.

Salida:
Retorna el tipo de pago ingresado por el usuario.
"""
def solicitarTipoPago(placa):
    tipoPago = simpledialog.askstring(
        "Tipo de pago",
        "Digite el tipo de pago para la placa " + placa + "\nefectivo, sinpe o tarjeta:"
    )

    if tipoPago == None:
        tipoPago = "efectivo"

    tipoPago = tipoPago.lower()

    if tipoPago != "efectivo" and tipoPago != "sinpe" and tipoPago != "tarjeta":
        tipoPago = "efectivo"

    return tipoPago



"""
Funcionalidad:
Realiza el cierre diario del parqueo, factura todos los espacios ocupados
y genera un resumen con los montos recaudados.

Entrada:
No recibe parámetros.

Salida:
Muestra el reporte del cierre diario y libera los espacios ocupados.
"""
def crearCierreDiario():
    totalEfectivo = 0
    totalSinpe = 0
    totalTarjeta = 0
    totalDia = 0

    huboFacturas = False

    fecha = datetime.now().strftime("%d/%m/%Y")
    horaSalida = datetime.now().strftime("%H:%M")

    reporte = "CIERRE DIARIO\n"
    reporte += "Fecha: " + fecha + "\n\n"
    reporte += "Ubicación | Placa | Entrada | Salida | Pago | Monto\n"
    reporte += "--------------------------------------------------\n"

    for espacio in listaEspacios:
        if espacio.estado == "Ocupado":
            huboFacturas = True

            placa = espacio.vehiculo.placa
            tipoPago = solicitarTipoPago(placa)
            monto = calcularMonto(espacio.voucher.horaEntrada, horaSalida)

            espacio.voucher.asignarSalida(horaSalida, tipoPago, monto)

            datoReporte = [
                espacio.numero,
                placa,
                espacio.voucher.horaEntrada,
                horaSalida,
                tipoPago,
                monto
            ]

            listaReporteDia.append(datoReporte)
            reporte += str(espacio.numero) + " | "
            reporte += placa + " | "
            reporte += espacio.voucher.horaEntrada + " | "
            reporte += horaSalida + " | "
            reporte += tipoPago + " | "
            reporte += str(monto) + "\n"

            if tipoPago == "efectivo":
                totalEfectivo += monto
            elif tipoPago == "sinpe":
                totalSinpe += monto
            elif tipoPago == "tarjeta":
                totalTarjeta += monto

            totalDia += monto

            espacio.liberarEspacio()

            if huboFacturas == False:
                messagebox.showinfo("Cierre diario", "No existen espacios ocupados para facturar.")
                return

            reporte += "\nTOTAL EFECTIVO: " + str(totalEfectivo)
            reporte += "\nTOTAL SINPE: " + str(totalSinpe)
            reporte += "\nTOTAL TARJETA: " + str(totalTarjeta)
            reporte += "\nTOTAL DEL DÍA: " + str(totalDia)

            actualizarVentanaEstacionamiento()

            messagebox.showinfo("Cierre diario", reporte)


"""
Funcionalidad:
Exporta la información del cierre diario a un archivo CSV para poder
abrirlo posteriormente en Excel.

Entrada:
No recibe parámetros.

Salida:
Crea un archivo llamado cierreDiario.csv con la información almacenada
en listaReporteDia.
"""
def exportarCierreCSV():
    if len(listaReporteDia) == 0:
        messagebox.showwarning("Error", "No hay datos de cierre diario para exportar.")
        return

    archivo = open("cierreDiario.csv", "w")

    for dato in listaReporteDia:
        linea = str(dato[0]) + ","
        linea += dato[1] + ","
        linea += dato[2] + ","
        linea += dato[3] + ","
        linea += dato[4] + ","
        linea += str(dato[5]) + "\n"

        archivo.write(linea)

    archivo.close()

    messagebox.showinfo("CSV", "Archivo cierreDiario.csv creado correctamente.")

"""
Funcionalidad:
Crea un archivo XML separando la información del cierre diario por tipo
de pago: efectivo, sinpe y tarjeta.

Entrada:
No recibe parámetros.

Salida:
Crea un archivo llamado cierrePorTipoPago.xml.
"""
def crearCierreXML():
    if len(listaReporteDia) == 0:
        messagebox.showwarning("Error", "No hay datos de cierre diario para crear el XML.")
        return

    archivo = open("cierrePorTipoPago.xml", "w")

    archivo.write("<cierre>\n")

    archivo.write("  <efectivo>\n")
    for dato in listaReporteDia:
        if dato[4] == "efectivo":
            archivo.write("    <factura>\n")
            archivo.write("      <ubicacion>" + str(dato[0]) + "</ubicacion>\n")
            archivo.write("      <placa>" + dato[1] + "</placa>\n")
            archivo.write("      <horaEntrada>" + dato[2] + "</horaEntrada>\n")
            archivo.write("      <horaSalida>" + dato[3] + "</horaSalida>\n")
            archivo.write("      <tipoPago>" + dato[4] + "</tipoPago>\n")
            archivo.write("      <monto>" + str(dato[5]) + "</monto>\n")
            archivo.write("    </factura>\n")
    archivo.write("  </efectivo>\n")

    archivo.write("  <sinpe>\n")
    for dato in listaReporteDia:
        if dato[4] == "sinpe":
            archivo.write("    <factura>\n")
            archivo.write("      <ubicacion>" + str(dato[0]) + "</ubicacion>\n")
            archivo.write("      <placa>" + dato[1] + "</placa>\n")
            archivo.write("      <horaEntrada>" + dato[2] + "</horaEntrada>\n")
            archivo.write("      <horaSalida>" + dato[3] + "</horaSalida>\n")
            archivo.write("      <tipoPago>" + dato[4] + "</tipoPago>\n")
            archivo.write("      <monto>" + str(dato[5]) + "</monto>\n")
            archivo.write("    </factura>\n")
    archivo.write("  </sinpe>\n")

    archivo.write("  <tarjeta>\n")
    for dato in listaReporteDia:
        if dato[4] == "tarjeta":
            archivo.write("    <factura>\n")
            archivo.write("      <ubicacion>" + str(dato[0]) + "</ubicacion>\n")
            archivo.write("      <placa>" + dato[1] + "</placa>\n")
            archivo.write("      <horaEntrada>" + dato[2] + "</horaEntrada>\n")
            archivo.write("      <horaSalida>" + dato[3] + "</horaSalida>\n")
            archivo.write("      <tipoPago>" + dato[4] + "</tipoPago>\n")
            archivo.write("      <monto>" + str(dato[5]) + "</monto>\n")
            archivo.write("    </factura>\n")
    archivo.write("  </tarjeta>\n")

    archivo.write("</cierre>\n")

    archivo.close()

    messagebox.showinfo("XML", "Archivo cierrePorTipoPago.xml creado correctamente.")



"""
Funcionalidad:
Permite modificar la configuración general del parqueo: tamaño del
estacionamiento, tiempo de gracia, monto por hora y espacio eléctrico.

Entrada:
No recibe parámetros directamente.
Solicita datos mediante ventanas emergentes.

Salida:
Actualiza la configuración y vuelve a crear los espacios del parqueo.
"""
def crearConfiguracion():
    global montoPorHora
    global tiempoGracia
    global tamanoEstacionamiento
    global tieneElectrico

    confirmar = messagebox.askyesno(
        "Configuración",
        "¿Desea modificar la configuración del parqueo?"
    )

    if confirmar == False:
        return

    nuevoTamano = simpledialog.askinteger(
        "Configuración",
        "Digite el tamaño del estacionamiento:"
    )

    nuevoTiempo = simpledialog.askinteger(
        "Configuración",
        "Digite el tiempo de gracia en minutos:"
    )

    nuevoMonto = simpledialog.askinteger(
        "Configuración",
        "Digite el monto por hora:"
    )

    respuestaElectrico = simpledialog.askstring(
        "Configuración",
        "¿El estacionamiento tiene espacio para vehículo eléctrico? si/no:"
    )

    if nuevoTamano != None:
        if nuevoTamano >= 3:
            tamanoEstacionamiento = nuevoTamano
        else:
            messagebox.showwarning("Error", "El tamaño mínimo debe ser 3.")

    if nuevoTiempo != None:
        if nuevoTiempo >= 0:
            tiempoGracia = nuevoTiempo
        else:
            messagebox.showwarning("Error", "El tiempo de gracia no puede ser negativo.")

    if nuevoMonto != None:
        if nuevoMonto >= 0:
            montoPorHora = nuevoMonto
        else:
            messagebox.showwarning("Error", "El monto por hora no puede ser negativo.")

    if respuestaElectrico != None:
        respuestaElectrico = respuestaElectrico.lower()

        if respuestaElectrico == "si":
            tieneElectrico = True
        elif respuestaElectrico == "no":
            tieneElectrico = False
        else:
            messagebox.showwarning(
                "Error",
                "Respuesta inválida para espacio eléctrico. Se mantiene el valor anterior."
            )

    crearEstacionamiento()
    actualizarVentanaEstacionamiento()

    mensaje = "Configuración actualizada correctamente."
    mensaje += "\nTamaño del estacionamiento: " + str(tamanoEstacionamiento)
    mensaje += "\nTiempo de gracia: " + str(tiempoGracia)
    mensaje += "\nMonto por hora: " + str(montoPorHora)

    if tieneElectrico == True:
        mensaje += "\nEspacio eléctrico: Sí"
    else:
        mensaje += "\nEspacio eléctrico: No"

    messagebox.showinfo("Configuración", mensaje)

"""
Funcionalidad:
Muestra una ventana con la información general del sistema y los
desarrolladores de la aplicación.

Entrada:
No recibe parámetros.

Salida:
Muestra una ventana informativa con los datos del proyecto.
"""
def crearAcercaDe():
    ventana = Toplevel()
    ventana.title("Acerca de")
    ventana.geometry("350x250")

    Label(ventana, text="Sistema de Parqueo", font=("Arial", 16)).pack(pady=10)
    Label(ventana, text="Tarea Programada #3").pack(pady=5)
    Label(ventana, text="Taller de Programación").pack(pady=5)
    Label(ventana, text="I Semestre 2026").pack(pady=5)

    Label(ventana, text="Desarrollado por:").pack(pady=5)
    Label(ventana, text="Estudiante 1: [Tu nombre]").pack()
    Label(ventana, text="Estudiante 2: [Nombre compañero]").pack()

    Button(ventana, text="Regresar", width=20, command=ventana.destroy).pack(pady=15)



"""
Funcionalidad:
Estaciona automáticamente los vehículos creados en los espacios generales
disponibles del parqueo.

Entrada:
No recibe parámetros.

Salida:
Asigna vehículos a espacios generales libres y crea sus respectivos vouchers.
"""
def estacionarVehiculosMasivo():
    if len(listaVehiculos) == 0:
        messagebox.showwarning("Error", "Primero debe obtener vehículos.")
        return

    contadorVehiculos = 0

    for espacio in listaEspacios:
        if espacio.tipo == "General" and espacio.estado == "Libre":
            if contadorVehiculos < len(listaVehiculos):
                vehiculo = listaVehiculos[contadorVehiculos]
                horaEntrada = datetime.now().strftime("%H:%M")
                voucher = Voucher(vehiculo.placa, horaEntrada)

                espacio.estacionarVehiculo(vehiculo, voucher)
                listaVouchers.append(voucher)

                contadorVehiculos += 1

    actualizarVentanaEstacionamiento()

    messagebox.showinfo(
        "Reserva masiva",
        "Se estacionaron " + str(contadorVehiculos) + " vehículos automáticamente."
    )


def cargarConfiguracion():
    """
    Funcionalidad: Carga la configuracion del estacionamiento desde memoria secundaria.
    Entrada: No recibe parametros.
    Salida: cfg (Configuracion): Objeto de configuracion si existe el archivo.
    None si no se ha creado configuracion aun.
    """
    try:
        archivo = open(ARCHIVO_CONFIG, "rb")
        cfg = pickle.load(archivo)
        archivo.close()
        return cfg
    except:
        return None


def guardarConfiguracion(cfg):
    """
    Funcionalidad: Guarda el objeto de configuracion en memoria secundaria.
    Entrada: cfg (Configuracion): Objeto con la configuracion actual.
    Salida: No retorna valor. Escribe el archivo configuracion.pkl.
    """
    archivo = open(ARCHIVO_CONFIG, "wb")
    pickle.dump(cfg, archivo)
    archivo.close()


def cargarBD():
    """
    Funcionalidad: Carga la lista de objetos Estacionamiento desde memoria secundaria.
    Entrada: No recibe parametros.
    Salida:
    - lista (list): Lista de objetos Estacionamiento.
    - Lista vacia si no existe el archivo.
    """
    try:
        archivo = open(ARCHIVO_BD, "rb")
        lista = pickle.load(archivo)
        archivo.close()
        return lista
    except:
        return []


def guardarBD(lista):
    """
    Funcionalidad: Guarda la lista de objetos Estacionamiento en memoria secundaria.
    Entrada: lista (list): Lista de objetos Estacionamiento a persistir.
    Salida: No retorna valor. Escribe el archivo estacionamientos.pkl.
    """
    archivo = open(ARCHIVO_BD, "wb")
    pickle.dump(lista, archivo)
    archivo.close()


def calcularEspeciales(tamano):
    """
    Funcionalidad: Calcula la cantidad de espacios especiales requeridos por ley. Minimo 2 si el parqueo es pequeno (5% resulta en menos de 2).
    Entrada: tamano (int): Cantidad total de espacios del parqueo.
    Salida: especiales (int): Cantidad de espacios especiales a reservar.
    """
    especiales = int(tamano * 0.05)
    if tamano * 0.05 - especiales > 0:
        especiales += 1
    if especiales < 2:
        especiales = 2
    return especiales


def calcularTopeMaximoMasivo(tamano, tieneElectrico):
    """
    Funcionalidad: Calcula cuantos espacios generales se pueden llenar masivamente,
    respetando especiales, electrico y el 5% libre obligatorio.
    Entrada:-tamano (int): Total de espacios del parqueo.
    -tieneElectrico (bool): Si existe espacio electrico reservado.
    Salida: tope (int): Cantidad maxima de espacios generales a llenar.
    """
    especiales = calcularEspeciales(tamano)
    if tieneElectrico:
        electrico = 1
    else:
        electrico = 0
    porAsignar = tamano - especiales - electrico
    reservaLibre = int(porAsignar * 0.05)
    if porAsignar * 0.05 - reservaLibre > 0:
        reservaLibre += 1
    tope = porAsignar - reservaLibre
    return tope


def generarIdsEspacios(tamano, tieneElectrico):
    """
    Funcionalidad: Genera la lista ordenada de IDs de todos los espacios del parqueo.
    Formato: 'E-01' especiales, 'EL-01' electrico, 'G-01' generales.
    Entrada: -tamano (int): Total de espacios del parqueo.
    -tieneElectrico (bool): Si existe espacio electrico.
    Salida: ids (list): Lista de strings con todos los IDs de espacios.
    """
    especiales = calcularEspeciales(tamano)
    ids = []
    for i in range(1, especiales + 1):
        if i < 10:
            idEspacio = "E-0" + str(i)
        else:
            idEspacio = "E-" + str(i)
        ids.append(idEspacio)
    if tieneElectrico:
        ids.append("EL-01")
        electrico = 1
    else:
        electrico = 0
    generales = tamano - especiales - electrico
    for i in range(1, generales + 1):
        if i < 10:
            idEspacio = "G-0" + str(i)
        else:
            idEspacio = "G-" + str(i)
        ids.append(idEspacio)
    return ids


def generarCodigoQR(datos, nombreArchivo):
    """
    Funcionalidad: Genera un codigo QR con los datos indicados y lo guarda como imagen PNG.
    Entrada:
    - datos (str): Texto a codificar en el QR.
    - nombreArchivo (str): Ruta/nombre del archivo PNG a crear.
    Salida: nombreArchivo (str): Ruta del archivo PNG generado.
    """
    imagen = qrcode.make(datos)
    imagen.save(nombreArchivo)
    return nombreArchivo


def generarNombreVoucher(placa, fechaHoraEntrada):
    """
    Funcionalidad: Construye el nombre del archivo voucher segun el formato del enunciado.
    Entrada:
    - placa (str): Placa del vehiculo.
    - fechaHoraEntrada (str): Fecha y hora de entrada como string.
    Salida: nombre (str): Nombre del archivo con formato voucher_#PLACA_DD-MM-AAAA_HH-mm.pdf
    """
    try:
        dt = datetime.strptime(fechaHoraEntrada, "%Y-%m-%d %H:%M:%S")
        sufijo = dt.strftime("%d-%m-%Y_%H-%M")
    except:
        sufijo = fechaHoraEntrada.replace(":", "-").replace(" ", "_")
    return "voucher_#" + str(placa) + "_" + sufijo


def generarNombreFactura(placa, fechaHoraSalida):
    """
    Funcionalidad: Construye el nombre del archivo factura segun el formato del enunciado.
    Entrada:
    - placa (str): Placa del vehiculo.
    - fechaHoraSalida (str): Fecha y hora de salida como string.
    Salida: nombre (str): Nombre del archivo con formato factura_#PLACA_DD-MM-AAAA_HH-mm.pdf
    """
    try:
        dt = datetime.strptime(fechaHoraSalida, "%Y-%m-%d %H:%M:%S")
        sufijo = dt.strftime("%d-%m-%Y_%H-%M")
    except:
        sufijo = fechaHoraSalida.replace(":", "-").replace(" ", "_")
    return "factura_#" + str(placa) + "_" + sufijo


def crearVoucherPdf(obj):
    """
    Funcionalidad: Genera el voucher PDF de ingreso al parqueo con codigo QR incluido. El archivo se guarda en la carpeta actual con el nombre estandar.
    Entrada: obj (Estacionamiento): Objeto con la informacion del vehiculo.
    Salida: rutaPdf (str): Ruta del archivo PDF generado.
    """
    placa, marca, color, tipo = obj.info
    ubicacion, entrada, salida = obj.estadia
    monto, tipoPago = obj.pago

    placaTexto = str(placa)
    if isinstance(marca, int) and 1 <= marca <= len(MARCAS):
        marcaNombre = MARCAS[marca - 1]
    else:
        marcaNombre = str(marca)
    if isinstance(color, int) and 1 <= color <= len(COLORES):
        colorNombre = COLORES[color - 1]
    else:
        colorNombre = str(color)
    if isinstance(tipo, int) and 1 <= tipo <= len(TIPOS):
        tipoNombre = TIPOS[tipo - 1]
    else:
        tipoNombre = str(tipo)

    datosQr = placaTexto + "-" + marcaNombre + "-" + tipoNombre + "-" + str(entrada)
    nombreBase = generarNombreVoucher(str(placa), str(entrada))
    rutaQr = nombreBase + "_qr.png"
    rutaPdf = nombreBase + ".pdf"

    generarCodigoQR(datosQr, rutaQr)

    pdf = FPDF()
    pdf.add_page()

    pdf.set_fill_color(30, 30, 80)
    pdf.rect(0, 0, 210, 30, 'F')
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 18)
    pdf.set_xy(0, 8)
    pdf.cell(210, 10, "VOUCHER DE INGRESO - PARQUEO TEC", align="C")

    pdf.set_text_color(0, 0, 0)
    pdf.set_xy(15, 38)
    pdf.set_font("Helvetica", "B", 13)
    pdf.cell(0, 8, "Informacion del Vehiculo")
    pdf.ln(12)

    pdf.set_font("Helvetica", "", 11)
    pdf.set_x(15)
    filas = [
        ("Placa:", str(placa)),
        ("Marca:", marcaNombre),
        ("Color:", colorNombre),
        ("Tipo:", tipoNombre),
        ("Ubicacion:", str(ubicacion)),
        ("Hora de Entrada:", str(entrada)),
    ]
    for etiqueta, valor in filas:
        pdf.set_x(15)
        pdf.set_font("Helvetica", "B", 11)
        pdf.cell(55, 9, etiqueta)
        pdf.set_font("Helvetica", "", 11)
        pdf.cell(0, 9, valor)
        pdf.ln()

    if os.path.exists(rutaQr):
        pdf.set_xy(140, 40)
        pdf.image(rutaQr, x=140, y=40, w=55)

    pdf.set_font("Helvetica", "I", 9)
    pdf.set_xy(15, 175)
    pdf.set_text_color(120, 120, 120)
    pdf.cell(0, 6, "Este voucher es su comprobante de ingreso. Conservelo.")

    pdf.output(rutaPdf)

    if os.path.exists(rutaQr):
        os.remove(rutaQr)

    return rutaPdf


def crearFacturaPdf(obj, cfg):
    """
    Funcionalidad: Genera la factura PDF de salida del parqueo con todos los detalles de la estadia y el monto cobrado. Incluye codigo QR.
    Entrada:
    - obj (Estacionamiento): Objeto con la informacion completa del vehiculo.
    - cfg (Configuracion): Configuracion del parqueo (para monto/hora y gracia).
    Salida: rutaPdf (str): Ruta del archivo PDF generado.
    """
    placa, marca, color, tipo = obj.info
    ubicacion, entrada, salida = obj.estadia
    monto, tipoPago = obj.pago

    if isinstance(marca, int) and 1 <= marca <= len(MARCAS):
        marcaNombre = MARCAS[marca - 1]
    else:
        marcaNombre = str(marca)
    if isinstance(color, int) and 1 <= color <= len(COLORES):
        colorNombre = COLORES[color - 1]
    else:
        colorNombre = str(color)
    if isinstance(tipo, int) and 1 <= tipo <= len(TIPOS):
        tipoNombre = TIPOS[tipo - 1]
    else:
        tipoNombre = str(tipo)

    tipoPagoNombre = TIPOS_PAGO.get(tipoPago, str(tipoPago))
    datosQr = str(placa) + "-" + marcaNombre + "-" + tipoNombre + "-" + str(salida)
    nombreBase = generarNombreFactura(str(placa), str(salida))
    rutaQr = nombreBase + "_qr.png"
    rutaPdf = nombreBase + ".pdf"

    generarCodigoQR(datosQr, rutaQr)

    try:
        dtEntrada = datetime.strptime(str(entrada), "%Y-%m-%d %H:%M:%S")
        dtSalida = datetime.strptime(str(salida), "%Y-%m-%d %H:%M:%S")
        minutos = int((dtSalida - dtEntrada).total_seconds() / 60)
        horasFacturadas = max(0, minutos - cfg.tiempoGracia)
        horasFloat = horasFacturadas / 60
    except:
        minutos = 0
        horasFloat = 0

    pdf = FPDF()
    pdf.add_page()

    pdf.set_fill_color(20, 80, 20)
    pdf.rect(0, 0, 210, 30, 'F')
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 18)
    pdf.set_xy(0, 8)
    pdf.cell(210, 10, "FACTURA - PARQUEO TEC", align="C")

    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Helvetica", "B", 13)
    pdf.set_xy(15, 38)
    pdf.cell(0, 8, "Detalle de Estadia")
    pdf.ln(12)

    pdf.set_font("Helvetica", "", 11)
    filas = [
        ("Placa:", str(placa)),
        ("Marca:", marcaNombre),
        ("Color:", colorNombre),
        ("Tipo:", tipoNombre),
        ("Ubicacion:", str(ubicacion)),
        ("Hora de Entrada:", str(entrada)),
        ("Hora de Salida:", str(salida)),
        ("Tiempo total:", str(minutos) + " min"),
        ("Tiempo de gracia:", str(cfg.tiempoGracia) + " min"),
        ("Tiempo facturable:", str(round(horasFloat, 1)) + " h"),
        ("Tarifa por hora:", "₡" + str(cfg.montoHora)),
        ("Tipo de Pago:", tipoPagoNombre),
    ]

    for etiqueta, valor in filas:
        pdf.set_x(15)
        pdf.set_font("Helvetica", "B", 11)
        pdf.cell(60, 9, etiqueta)
        pdf.set_font("Helvetica", "", 11)
        pdf.cell(0, 9, valor)
        pdf.ln()

    pdf.ln(3)
    pdf.set_fill_color(240, 240, 240)
    pdf.set_x(15)
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(175, 12, "TOTAL A PAGAR: ₡" + str(monto), border=1, fill=True)
    pdf.ln()

    if os.path.exists(rutaQr):
        pdf.image(rutaQr, x=140, y=40, w=55)

    pdf.set_font("Helvetica", "I", 9)
    pdf.set_xy(15, 200)
    pdf.set_text_color(120, 120, 120)
    pdf.cell(0, 6, "Gracias por usar nuestro parqueo. Conserve esta factura.")

    pdf.output(rutaPdf)

    if os.path.exists(rutaQr):
        os.remove(rutaQr)

    return rutaPdf


def generarReporteCierreDiarioHtml(lista):
    """
    Funcionalidad:
    Genera el reporte de cierre diario en formato HTML,
    subtotales por tipo de pago y total general. Abre el archivo en el navegador.
    Entrada: lista (list): Lista de objetos Estacionamiento del dia.
    Salida: rutaHtml (str): Ruta del archivo HTML generado.
    """
    hoy = datetime.now().strftime("%d/%m/%Y")
    rutaHtml = "cierre_diario_" + datetime.now().strftime("%d-%m-%Y") + ".html"

    totalesPorTipo = {1: 0.0, 2: 0.0, 3: 0.0}
    totalGeneral = 0.0

    filas = ""
    for obj in lista:
        placa, marca, color, tipo = obj.info
        ubicacion, entrada, salida = obj.estadia
        monto, tipoPago = obj.pago
        if isinstance(marca, int) and 1 <= marca <= len(MARCAS):
            marcaNombre = MARCAS[marca - 1]
        else:
            marcaNombre = str(marca)
        tipoPagoNombre = TIPOS_PAGO.get(tipoPago, str(tipoPago))
        totalesPorTipo[tipoPago] = totalesPorTipo.get(tipoPago, 0) + monto
        totalGeneral += monto
        filas += "<tr>"
        filas += "<td>" + str(ubicacion) + "</td>"
        filas += "<td>" + str(placa) + "</td>"
        filas += "<td>" + str(entrada) + "</td>"
        filas += "<td>" + str(salida) + "</td>"
        filas += "<td>" + tipoPagoNombre + "</td>"
        filas += "<td class='monto'>₡" + str(int(monto)) + "</td>"
        filas += "</tr>\n"

    subtotales = ""
    for tp, nombre in TIPOS_PAGO.items():
        subtotales += "<p><b>" + nombre + ":</b> ₡" + str(int(totalesPorTipo.get(tp, 0))) + "</p>\n"

    html = "<!DOCTYPE html>\n"
    html += "<html lang='es'>\n"
    html += "<head>\n"
    html += "<meta charset='UTF-8'>\n"
    html += "<title>Cierre Diario - " + hoy + "</title>\n"
    html += "<style>\n"
    html += "body { font-family: Arial, sans-serif; background: #f0f4f8; margin: 20px; color: #222; }\n"
    html += "h1 { font-size: 28px; color: #1a3a6b; }\n"
    html += "h2 { font-size: 18px; color: #2e7d32; }\n"
    html += "p { font-size: 13px; color: #888; }\n"
    html += "table { width: 100%; border-collapse: collapse; background: white; }\n"
    html += "thead tr { background: #1a3a6b; color: white; }\n"
    html += "th { padding: 10px; text-align: left; font-size: 13px; }\n"
    html += "td { padding: 8px; font-size: 13px; border-bottom: 1px solid #eee; }\n"
    html += "tr:nth-child(even) { background: #f7f9fc; }\n"
    html += ".monto { color: #2e7d32; font-weight: bold; }\n"
    html += ".total { font-size: 22px; font-weight: bold; color: #f9c74f; background: #1a3a6b; padding: 10px; }\n"
    html += "</style>\n"
    html += "</head>\n"
    html += "<body>\n"
    html += "<h1>Cierre Diario - Parqueo TEC</h1>\n"
    html += "<p>Fecha: " + hoy + " | Generado: " + datetime.now().strftime("%H:%M:%S") + "</p>\n"
    html += "<h2>Detalle de Transacciones</h2>\n"
    html += "<p>Total de registros: " + str(len(lista)) + "</p>\n"
    html += "<table>\n"
    html += "<thead><tr>"
    html += "<th>Ubicacion</th><th>Placa</th><th>Hora Entrada</th>"
    html += "<th>Hora Salida</th><th>Tipo de Pago</th><th>Monto</th>"
    html += "</tr></thead>\n"
    html += "<tbody>\n" + filas + "</tbody>\n"
    html += "</table>\n"
    html += "<h2>Subtotales por tipo de pago</h2>\n"
    html += subtotales
    html += "<p class='total'>Total recaudado del dia: ₡" + str(int(totalGeneral)) + "</p>\n"
    html += "</body>\n</html>"

    archivo = open(rutaHtml, "w", encoding="utf-8")
    archivo.write(html)
    archivo.close()

    webbrowser.open("file:///" + os.path.abspath(rutaHtml))
    return rutaHtml


def generarCierrePorTipoXml(lista):
    """
    Funcionalidad:
    Genera el archivo XML de cierre por tipo de pago con 3 secciones:
    efectivo, sinpe y tarjeta. Almacena informacion completa de cada objeto.
    Entrada: lista (list): Lista de objetos Estacionamiento a exportar.
    Salida: rutaXml (str): Ruta del archivo XML generado.
    """
    rutaXml = "cierre_tipo_pago_" + datetime.now().strftime("%d-%m-%Y") + ".xml"

    grupos = {1: [], 2: [], 3: []}
    for obj in lista:
        tp = obj.pago[1]
        grupos[tp].append(obj)

    def objetoAXml(obj):
        """
        Funcionalidad: Convierte un objeto Estacionamiento a texto XML plano.
        Entrada: obj (Estacionamiento): Objeto a convertir.
        Salida: texto (str): Representacion XML del objeto.
        """
        placa, marca, color, tipo = obj.info
        ubicacion, entrada, salida = obj.estadia
        monto, tipoPago = obj.pago
        if isinstance(marca, int) and 1 <= marca <= len(MARCAS):
            marcaNombre = MARCAS[marca - 1]
        else:
            marcaNombre = str(marca)
        if isinstance(color, int) and 1 <= color <= len(COLORES):
            colorNombre = COLORES[color - 1]
        else:
            colorNombre = str(color)
        if isinstance(tipo, int) and 1 <= tipo <= len(TIPOS):
            tipoNombre = TIPOS[tipo - 1]
        else:
            tipoNombre = str(tipo)
        texto = "        <vehiculo>\n"
        texto += "            <id>" + str(obj.id) + "</id>\n"
        texto += "            <placa>" + str(placa) + "</placa>\n"
        texto += "            <marca>" + marcaNombre + "</marca>\n"
        texto += "            <color>" + colorNombre + "</color>\n"
        texto += "            <tipo>" + tipoNombre + "</tipo>\n"
        texto += "            <ubicacion>" + str(ubicacion) + "</ubicacion>\n"
        texto += "            <entrada>" + str(entrada) + "</entrada>\n"
        texto += "            <salida>" + str(salida) + "</salida>\n"
        texto += "            <monto>" + str(monto) + "</monto>\n"
        texto += "            <tipoPago>" + TIPOS_PAGO.get(tipoPago, str(tipoPago)) + "</tipoPago>\n"
        texto += "        </vehiculo>\n"
        return texto

    contenido = '<?xml version="1.0" encoding="UTF-8"?>\n'
    contenido += "<cierrePorTipoPago>\n"

    contenido += "    <efectivo>\n"
    for obj in grupos[1]:
        contenido += objetoAXml(obj)
    contenido += "    </efectivo>\n"

    contenido += "    <sinpe>\n"
    for obj in grupos[2]:
        contenido += objetoAXml(obj)
    contenido += "    </sinpe>\n"

    contenido += "    <tarjeta>\n"
    for obj in grupos[3]:
        contenido += objetoAXml(obj)
    contenido += "    </tarjeta>\n"

    contenido += "</cierrePorTipoPago>"

    archivo = open(rutaXml, "w", encoding="utf-8")
    archivo.write(contenido)
    archivo.close()

    return rutaXml


def exportarCierroCsv(lista):
    """
    Funcionalidad: Exporta los datos del cierre diario a un archivo CSV sin encabezados, listo para abrir en Excel.
    Columnas: ubicacion, placa, entrada, salida, tipo de pago, monto.
    Entrada: lista (list): Lista de objetos Estacionamiento a exportar.
    Salida: rutaCsv (str): Ruta del archivo CSV generado.
    """
    rutaCsv = "cierre_diario_" + datetime.now().strftime("%d-%m-%Y") + ".csv"

    archivo = open(rutaCsv, "w", newline="", encoding="utf-8")
    escritor = csv.writer(archivo)
    for obj in lista:
        placa, marca, color, tipo = obj.info
        ubicacion, entrada, salida = obj.estadia
        monto, tipoPago = obj.pago
        escritor.writerow([ubicacion, placa, entrada, salida,
                           TIPOS_PAGO.get(tipoPago, str(tipoPago)), monto])
    archivo.close()

    return rutaCsv


def abrirVentanaConfiguracion(ventanaPadre):
    """
    Funcionalidad: Abre la ventana de configuracion del parqueo. Si no existe configuracion,
    obliga al usuario a contestarla. Si ya existe, permite actualizarla
    con confirmacion previa.
    Entrada: ventanaPadre (tk.Tk o tk.Toplevel): Ventana padre de la aplicacion.
    Salida: No retorna valor. Modifica el archivo configuracion.pkl.
    """
    ventana = tk.Toplevel(ventanaPadre)
    ventana.title("Configuracion del Parqueo")
    ventana.geometry("470x320")

    cfgExistente = cargarConfiguracion()

    tk.Label(ventana, text="Configuracion del Parqueo",
             font=("Arial", 14, "bold")).pack(pady=10)

    marco = tk.Frame(ventana)
    marco.pack(padx=20)

    tk.Label(
        marco,
        text="Ingrese la cantidad de espacios del estacionamiento:"
    ).grid(row=0, column=0, sticky="w", pady=5)
    entradaTamano = tk.Entry(marco, width=10)
    entradaTamano.grid(row=0, column=1, padx=10)

    tk.Label(
        marco,
        text="Ingrese el tiempo de gracia (minutos):"
    ).grid(row=1, column=0, sticky="w", pady=5)
    entradaGracia = tk.Entry(marco, width=10)
    entradaGracia.grid(row=1, column=1, padx=10)

    tk.Label(
        marco,
        text="Ingrese el monto por hora (en colones):"
    ).grid(row=2, column=0, sticky="w", pady=5)
    entradaMonto = tk.Entry(marco, width=10)
    entradaMonto.grid(row=2, column=1, padx=10)

    tk.Label(
        marco,
        text="El parqueo tiene espacio para vehiculos electricos?"
    ).grid(row=3, column=0, sticky="w", pady=5)
    varElectrico = tk.BooleanVar()
    tk.Checkbutton(marco, variable=varElectrico).grid(row=3, column=1, sticky="w", padx=10)

    if cfgExistente:
        entradaTamano.insert(0, str(cfgExistente.tamanoParqueo))
        entradaGracia.insert(0, str(cfgExistente.tiempoGracia))
        entradaMonto.insert(0, str(cfgExistente.montoHora))
        varElectrico.set(cfgExistente.tieneElectrico)

    def guardar():
        """
        Funcionalidad: Valida y guarda la configuracion ingresada por el usuario.
        Entrada: No recibe parametros (lee los campos de la ventana).
        Salida: No retorna valor. Cierra la ventana si los datos son validos.
        """
        try:
            tamano = int(entradaTamano.get())
            gracia = int(entradaGracia.get())
            monto = float(entradaMonto.get())
        except ValueError:
            messagebox.showerror("Error", "Tamano y gracia deben ser enteros. Monto puede ser decimal.", parent=ventana)
            return

        if tamano < 1:
            messagebox.showerror("Error", "El tamano debe ser al menos 1.", parent=ventana)
            return

        if cfgExistente:
            confirmado = messagebox.askyesno("Confirmar",
                "Desea actualizar la configuracion del parqueo?\nEsto no elimina los vehiculos actuales.", parent=ventana)
            if not confirmado:
                return

        nuevaCfg = Configuracion(tamano, gracia, monto, varElectrico.get())
        guardarConfiguracion(nuevaCfg)
        messagebox.showinfo("Exito", "Configuracion guardada correctamente.", parent=ventana)
        ventana.destroy()

    tk.Button(ventana, text="Guardar", command=guardar,
              bg="blue", fg="white", font=("Arial", 11, "bold"),
              width=12).pack(pady=18)


def abrirVentanaEspacio(ventanaPadre, espacioId, lista, cfg):
    """
    Funcionalidad:
    Abre la ventana de detalle de un espacio del parqueo.
    Si esta ocupado (rojo): muestra informacion y permite pagar (Facturar).
    Si esta libre (verde): permite estacionar un vehiculo nuevo.
    Entrada:
    - ventanaPadre (tk.Toplevel): Ventana del mapa del parqueo.
    - espacioId (str): ID del espacio seleccionado (ej. 'G-01').
    - lista (list): Lista de objetos Estacionamiento (BD en memoria).
    - cfg (Configuracion): Configuracion actual del parqueo.
    Salida: No retorna valor. Modifica la lista y el archivo pkl si se realizan cambios.
    """
    objEncontrado = None
    for obj in lista:
        ubicacion = obj.estadia[0]
        salida = obj.estadia[2]
        if ubicacion == espacioId and (salida == "" or salida is None):
            objEncontrado = obj
            break

    ventana = tk.Toplevel(ventanaPadre)

    if objEncontrado:
        ventana.title("Espacio Ocupado - " + espacioId)
        ventana.geometry("386x307")

        tk.Label(ventana, text="Espacio: " + espacioId,
                 font=("Arial", 13, "bold"), fg="red").pack(pady=10)

        placa, marca, color, tipo = objEncontrado.info
        if isinstance(marca, int) and 1 <= marca <= len(MARCAS):
            marcaNombre = MARCAS[marca - 1]
        else:
            marcaNombre = str(marca)
        if isinstance(color, int) and 1 <= color <= len(COLORES):
            colorNombre = COLORES[color - 1]
        else:
            colorNombre = str(color)
        entrada = objEncontrado.estadia[1]

        marco = tk.Frame(ventana)
        marco.pack(padx=20)

        campos = [
            ("# Campo:", espacioId),
            ("Placa:", str(placa)),
            ("Marca:", marcaNombre),
            ("Color:", colorNombre),
            ("Hora de Entrada:", str(entrada)),
        ]
        for etiqueta, valor in campos:
            fila = tk.Frame(marco)
            fila.pack(pady=2)
            tk.Label(fila, text=etiqueta, font=("Arial", 10, "bold"), width=18, anchor="w").pack(side="left")
            tk.Label(fila, text=valor, font=("Arial", 10), anchor="w").pack(side="left")

        def pagar():
            """
            Funcionalidad: Registra el pago del espacio: solicita tipo de pago, calcula monto, actualiza el objeto en la lista, guarda la BD y genera la factura PDF.
            Entrada: No recibe parametros (lee datos del objeto encontrado).
            Salida: No retorna valor. Actualiza lista, pkl y genera factura PDF.
            """
            seleccion = simpledialog.askstring(
                "Tipo de Pago",
                "Seleccione tipo de pago:\n1 - Efectivo\n2 - SINPE\n3 - Tarjeta",
                parent=ventana
            )
            if seleccion is None:
                return

            seleccion = seleccion.strip()
            if seleccion not in ["1", "2", "3"]:
                messagebox.showerror("Error", "Opcion invalida. Ingrese 1, 2 o 3.", parent=ventana)
                return

            tipoPago = int(seleccion)
            ahoraMismo = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            monto = calcularMonto(objEncontrado.estadia[1], ahoraMismo, cfg)

            tipoPagoTexto = TIPOS_PAGO[tipoPago]
            confirmado = messagebox.askyesno(
                "Confirmar Pago",
                "Monto a cobrar: ₡" + str(int(monto)) + "\nTipo de pago: " + tipoPagoTexto + "\n\nConfirmar?",
                parent=ventana
            )
            if not confirmado:
                return

            objEncontrado.estadia[2] = ahoraMismo
            objEncontrado.pago = (monto, tipoPago)
            guardarBD(lista)

            rutaPdf = crearFacturaPdf(objEncontrado, cfg)
            messagebox.showinfo("Pago Registrado",
                "Pago exitoso.\nFactura generada:\n" + rutaPdf, parent=ventana)
            ventana.destroy()

        botones = tk.Frame(ventana)
        botones.pack(pady=15)
        tk.Button(botones, text="Pagar", command=pagar,
                  bg="green", fg="white", font=("Arial", 11, "bold"), width=10).pack(side="left", padx=10)
        tk.Button(botones, text="Regresar", command=ventana.destroy,
                  bg="gray", fg="white", font=("Arial", 11, "bold"), width=10).pack(side="left", padx=10)

    else:
        ventana.title("Estacionar Vehiculo - " + espacioId)
        ventana.geometry("420x360")

        tk.Label(ventana, text="Espacio Libre: " + espacioId,
                 font=("Arial", 13, "bold"), fg="green").pack(pady=10)

        marco = tk.Frame(ventana)
        marco.pack(padx=20)

        tk.Label(marco, text="Placa:", anchor="w").grid(row=0, column=0, sticky="w", pady=4)
        entradaPlaca = tk.Entry(marco, width=20)
        entradaPlaca.grid(row=0, column=1, padx=10)

        tk.Label(marco, text="Marca:", anchor="w").grid(row=1, column=0, sticky="w", pady=4)
        varMarca = tk.StringVar()
        comboMarca = ttk.Combobox(marco, textvariable=varMarca, values=MARCAS, state="readonly", width=18)
        comboMarca.grid(row=1, column=1, padx=10)

        tk.Label(marco, text="Color:", anchor="w").grid(row=2, column=0, sticky="w", pady=4)
        varColor = tk.StringVar()
        comboColor = ttk.Combobox(marco, textvariable=varColor, values=COLORES, state="readonly", width=18)
        comboColor.grid(row=2, column=1, padx=10)

        tk.Label(marco, text="Tipo:", anchor="w").grid(row=3, column=0, sticky="w", pady=4)
        varTipo = tk.StringVar()
        comboTipo = ttk.Combobox(marco, textvariable=varTipo, values=TIPOS, state="readonly", width=18)
        comboTipo.grid(row=3, column=1, padx=10)

        tk.Label(marco, text="Hora de Entrada:", anchor="w").grid(row=4, column=0, sticky="w", pady=4)
        entradaHora = tk.Entry(marco, width=20)
        entradaHora.grid(row=4, column=1, padx=10)
        entradaHora.insert(0, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        entradaHora.config(state="readonly")

        tk.Label(marco, text="Tarifa por hora: ₡" + str(cfg.montoHora),
                 font=("Arial", 10)).grid(row=5, column=0, columnspan=2, pady=6)

        def estacionar():
            """
            Funcionalidad: Valida los campos, crea el objeto Estacionamiento, lo agrega a la lista, guarda la BD y genera el voucher PDF de ingreso.
            Entrada: No recibe parametros (lee los campos de la ventana).
            Salida: No retorna valor. Actualiza la lista, el pkl y genera el voucher.
            """
            placa = entradaPlaca.get().strip()
            if not placa:
                messagebox.showerror("Error", "Debe ingresar la placa.", parent=ventana)
                return
            if not varMarca.get():
                messagebox.showerror("Error", "Debe seleccionar la marca.", parent=ventana)
                return
            if not varColor.get():
                messagebox.showerror("Error", "Debe seleccionar el color.", parent=ventana)
                return
            if not varTipo.get():
                messagebox.showerror("Error", "Debe seleccionar el tipo.", parent=ventana)
                return

            confirmado = messagebox.askyesno(
                "Confirmar",
                "Desea estacionar el vehiculo?\nPlaca: " + placa + "\nEspacio: " + espacioId,
                parent=ventana
            )
            if not confirmado:
                return

            horaEntrada = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            marcaIdx = MARCAS.index(varMarca.get()) + 1
            colorIdx = COLORES.index(varColor.get()) + 1
            tipoIdx = TIPOS.index(varTipo.get()) + 1

            nuevoObj = Estacionamiento(
                id=espacioId,
                info=(placa, marcaIdx, colorIdx, tipoIdx),
                estadia=[espacioId, horaEntrada, ""],
                pago=(0, 0)
            )
            lista.append(nuevoObj)
            guardarBD(lista)

            rutaVoucher = crearVoucherPdf(nuevoObj)
            messagebox.showinfo("Vehiculo Estacionado",
                "Vehiculo registrado.\nVoucher generado:\n" + rutaVoucher, parent=ventana)
            ventana.destroy()

        botones = tk.Frame(ventana)
        botones.pack(pady=12)
        tk.Button(botones, text="Estacionar", command=estacionar,
                  bg="blue", fg="white", font=("Arial", 11, "bold"), width=12).pack(side="left", padx=10)
        tk.Button(botones, text="Regresar", command=ventana.destroy,
                  bg="gray", fg="white", font=("Arial", 11, "bold"), width=12).pack(side="left", padx=10)


def abrirVentanaEstacionamiento(ventanaPadre):
    """
    Funcionalidad:
    Abre la ventana grafica del mapa del parqueo con cuadricula interactiva.
    Cada espacio muestra rojo (ocupado) o verde (libre). Al hacer clic
    abre la ventana de detalle del espacio correspondiente.
    Entrada: ventanaPadre (tk.Tk): Ventana principal de la aplicacion.
    Salida: No retorna valor. Abre una ventana Toplevel con la cuadricula.
    """
    cfg = cargarConfiguracion()
    if not cfg:
        messagebox.showwarning("Sin Configuracion",
            "Debe configurar el parqueo primero.", parent=ventanaPadre)
        return

    lista = cargarBD()
    ids = generarIdsEspacios(cfg.tamanoParqueo, cfg.tieneElectrico)

    ocupados = set()
    for obj in lista:
        if obj.estadia[2] == "" or obj.estadia[2] is None:
            ocupados.add(obj.estadia[0])

    ventana = tk.Toplevel(ventanaPadre)
    ventana.title("Ver Estacionamiento")

    columnas = 8
    filas = (len(ids) + columnas - 1) // columnas
    anchoVentana = columnas * 95 + 60
    altoVentana = filas * 75 + 160
    if anchoVentana > 850:
        anchoVentana = 850
    if altoVentana > 700:
        altoVentana = 700
    ventana.geometry(str(anchoVentana) + "x" + str(altoVentana))

    tk.Label(ventana, text="Mapa del Parqueo",
             font=("Arial", 14, "bold")).pack(pady=8)

    leyenda = tk.Frame(ventana)
    leyenda.pack()
    tk.Label(leyenda, text="  ", bg="green", width=3).pack(side="left", padx=4)
    tk.Label(leyenda, text="Libre").pack(side="left")
    tk.Label(leyenda, text="   ", bg="red", width=3).pack(side="left", padx=8)
    tk.Label(leyenda, text="Ocupado").pack(side="left")
    tk.Label(leyenda, text="   ", bg="orange", width=3).pack(side="left", padx=8)
    tk.Label(leyenda, text="Especial/Electrico").pack(side="left")

    frameInternoCuadricula = tk.Frame(ventana)
    frameInternoCuadricula.pack(padx=10, pady=5)

    botonesEspacios = {}

    def hacerClickEspacio(eid):
        """
        Funcionalidad: Maneja el clic sobre un espacio de la cuadricula. Recarga la BD, abre la ventana de detalle y actualiza los colores al cerrarla.
        Entrada: eid (str): ID del espacio clickeado.
        Salida: No retorna valor.
        """
        listaActual = cargarBD()
        abrirVentanaEspacio(ventana, eid, listaActual, cfg)
        actualizarColores()

    def actualizarColores():
        """
        Funcionalidad: Recarga la BD y actualiza el color de cada boton en la cuadricula segun el estado actual (libre/ocupado).
        Entrada: No recibe parametros.
        Salida: No retorna valor. Cambia el color de fondo de los botones.
        """
        listaActual = cargarBD()
        ocupadosActual = set()
        for obj in listaActual:
            if obj.estadia[2] == "" or obj.estadia[2] is None:
                ocupadosActual.add(obj.estadia[0])

        for eid, btn in botonesEspacios.items():
            if eid.startswith("E-") or eid.startswith("EL-"):
                if eid not in ocupadosActual:
                    colorBase = "orange"
                else:
                    colorBase = "red"
            else:
                if eid not in ocupadosActual:
                    colorBase = "green"
                else:
                    colorBase = "red"
            btn.config(bg=colorBase)

    for indice, eid in enumerate(ids):
        fila = indice // columnas
        col = indice % columnas

        if eid.startswith("E-") or eid.startswith("EL-"):
            if eid not in ocupados:
                colorFondo = "orange"
            else:
                colorFondo = "red"
        else:
            if eid not in ocupados:
                colorFondo = "green"
            else:
                colorFondo = "red"

        btn = tk.Button(
            frameInternoCuadricula,
            text=eid,
            bg=colorFondo,
            fg="white",
            font=("Arial", 8, "bold"),
            width=8,
            height=3,
            command=lambda e=eid: hacerClickEspacio(e)
        )
        btn.grid(row=fila, column=col, padx=4, pady=4)
        botonesEspacios[eid] = btn

    filaExtra = filas
    tk.Label(frameInternoCuadricula, text="[CASETILLA]",
             bg="navy", fg="white", font=("Arial", 8, "bold"),
             width=10, height=3).grid(row=filaExtra, column=0, columnspan=2, padx=4, pady=8)
    tk.Label(frameInternoCuadricula, text="[BANO]",
             bg="gray", fg="white", font=("Arial", 8, "bold"),
             width=8, height=3).grid(row=filaExtra, column=2, padx=4, pady=8)

    tk.Button(ventana, text="Cerrar", command=ventana.destroy,
              bg="gray", fg="white", font=("Arial", 10, "bold")).pack(pady=6)


def abrirVentanaReportes(ventanaPadre):
    """
    Funcionalidad: Abre la ventana de reportes con tres opciones: cierre diario (HTML), cierre por tipo de pago (XML) y exportar CSV.
    Entrada: ventanaPadre (tk.Tk): Ventana principal de la aplicacion.
    Salida: No retorna valor. Abre una ventana Toplevel con los botones de reporte.
    """
    ventana = tk.Toplevel(ventanaPadre)
    ventana.title("Reportes")
    ventana.geometry("360x310")

    tk.Label(ventana, text="Reportes del Parqueo",
             font=("Arial", 14, "bold")).pack(pady=14)

    def cierreDiario():
        """
        Funcionalidad: Ejecuta el cierre diario: cierra vehiculos pendientes, genera el reporte HTML y lo abre en el navegador.
        Entrada: No recibe parametros.
        Salida: No retorna valor. Genera el HTML y lo abre en el navegador.
        """
        cfg = cargarConfiguracion()
        if not cfg:
            messagebox.showerror("Error", "No hay configuracion del parqueo.", parent=ventana)
            return

        lista = cargarBD()
        if not lista:
            messagebox.showinfo("Info", "No hay vehiculos registrados.", parent=ventana)
            return

        pendientes = []
        for obj in lista:
            if obj.estadia[2] == "" or obj.estadia[2] is None:
                pendientes.append(obj)

        tiposPago = [1, 2, 3]
        ahoraMismo = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        for obj in pendientes:
            tipoPago = random.choice(tiposPago)
            monto = calcularMonto(obj.estadia[1], ahoraMismo, cfg)
            obj.estadia[2] = ahoraMismo
            obj.pago = (monto, tipoPago)
            crearFacturaPdf(obj, cfg)

        guardarBD(lista)
        rutaHtml = generarReporteCierreDiarioHtml(lista)
        messagebox.showinfo("Cierre Diario",
            "Cierre generado exitosamente.\nArchivo: " + rutaHtml, parent=ventana)

    def cierrePorTipo():
        """
        Funcionalidad: Genera el archivo XML de cierre por tipo de pago (efectivo, SINPE, tarjeta).
        Entrada: No recibe parametros.
        Salida: No retorna valor. Genera el XML en la carpeta actual.
        """
        lista = cargarBD()
        if not lista:
            messagebox.showinfo("Info", "No hay vehiculos registrados.", parent=ventana)
            return

        pagados = []
        for obj in lista:
            if obj.pago[1] != 0:
                pagados.append(obj)

        if not pagados:
            messagebox.showinfo("Info", "No hay vehiculos con pago registrado.", parent=ventana)
            return

        rutaXml = generarCierrePorTipoXml(pagados)
        messagebox.showinfo("Cierre por Tipo de Pago",
            "XML generado:\n" + rutaXml, parent=ventana)

    def exportarCsv():
        """
        Funcionalidad: Exporta el cierre diario completo a un archivo CSV sin encabezados.
        Entrada: No recibe parametros.
        Salida: No retorna valor. Genera el CSV en la carpeta actual.
        """
        lista = cargarBD()
        if not lista:
            messagebox.showinfo("Info", "No hay vehiculos registrados.", parent=ventana)
            return

        rutaCsv = exportarCierroCsv(lista)
        messagebox.showinfo("Exportar CSV",
            "CSV generado exitosamente:\n" + rutaCsv, parent=ventana)

    tk.Button(ventana, text="a. Cierre Diario y Facturacion en Masa",
              command=cierreDiario, bg="blue", fg="white",
              font=("Arial", 10, "bold"), width=32, height=2).pack(pady=8)

    tk.Button(ventana, text="b. Cierre por Tipo de Pago (XML)",
              command=cierrePorTipo, bg="green", fg="white",
              font=("Arial", 10, "bold"), width=32, height=2).pack(pady=8)

    tk.Button(ventana, text="c. Exportar Cierre Diario a CSV",
              command=exportarCsv, bg="orange", fg="white",
              font=("Arial", 10, "bold"), width=32, height=2).pack(pady=8)

    tk.Button(ventana, text="Regresar", command=ventana.destroy,
              bg="gray", fg="white", font=("Arial", 10)).pack(pady=6)


def abrirVentanaAcercaDe(ventanaPadre):
    """
    Funcionalidad: Muestra la ventana 'Acerca de' con la informacion del desarrollador
    y la descripcion del sistema. Incluye boton para regresar al menu principal.
    Entrada: ventanaPadre (tk.Tk): Ventana principal de la aplicacion.
    Salida: No retorna valor. Abre una ventana Toplevel informativa.
    """
    ventana = tk.Toplevel(ventanaPadre)
    ventana.title("Acerca de")
    ventana.geometry("440x380")

    tk.Label(ventana, text="Sistema de Parqueo TEC",
             font=("Arial", 16, "bold")).pack(pady=10)
    tk.Label(ventana, text="Taller de Programacion - I Semestre 2026",
             font=("Arial", 10)).pack()

    cuerpo = tk.Frame(ventana, padx=30, pady=20)
    cuerpo.pack()

    info = [
        ("Version:", "1.0.0"),
        ("Curso:", "Taller de Programacion - TEC"),
        ("Estudiante E2:", "Aaron Sandi"),
        ("Lenguaje:", "Python 3 + Tkinter"),
        ("Persistencia:", "pickle (.pkl)"),
        ("Reportes:", "HTML, XML, CSV, PDF"),
    ]

    for etiqueta, valor in info:
        fila = tk.Frame(cuerpo)
        fila.pack(pady=3)
        tk.Label(fila, text=etiqueta, font=("Arial", 10, "bold"),
                 width=18, anchor="w").pack(side="left")
        tk.Label(fila, text=valor, font=("Arial", 10),
                 anchor="w").pack(side="left")

    tk.Label(cuerpo,
             text="Sistema para la gestion de espacios de estacionamiento\n"
                  "con interfaz grafica, reportes automatizados\n"
                  "y facturacion en PDF con codigo QR.",
             font=("Arial", 9), justify="center").pack(pady=8)

    tk.Button(ventana, text="Regresar al Menu Principal",
              command=ventana.destroy,
              bg="blue", fg="white",
              font=("Arial", 11, "bold"), width=24).pack(pady=10)


def iniciarAplicacion():
    """
    Funcionalidad:
    Crea y lanza la ventana principal de la aplicacion con todos los botones
    del menu. Si no existe configuracion, redirige automaticamente a Configuracion.
    Entrada: No recibe parametros.
    Salida: No retorna valor. Ejecuta el loop principal de tkinter.
    """
    raiz = tk.Tk()
    raiz.title("Sistema de Parqueo - TEC")
    raiz.geometry("380x520")

    tk.Label(raiz, text="PARQUEO TEC",
             font=("Arial", 20, "bold")).pack(pady=10)
    tk.Label(raiz, text="Sistema de Gestion de Estacionamiento",
             font=("Arial", 10)).pack()
    tk.Label(raiz, text="Menu Principal",
             font=("Arial", 12, "bold")).pack(pady=10)

    def abrirE1():
        messagebox.showinfo("Info",
            "Esta funcion es de bran",
            parent=raiz)

    def abrirEstacionamiento():
        abrirVentanaEstacionamiento(raiz)
    def abrirReportes():
        abrirVentanaReportes(raiz)
    def abrirConfiguracion():
        abrirVentanaConfiguracion(raiz)
    def abrirAcercaDe():
        abrirVentanaAcercaDe(raiz)
    tk.Button(raiz, text="1. Obtener Vehiculos y Vouchers",
              bg="blue", fg="white", width=28, height=2,
              command=abrirE1).pack(pady=5)
    tk.Button(raiz, text="2. Ver Estacionamiento",
              bg="green", fg="white", width=28, height=2,
              command=abrirEstacionamiento).pack(pady=5)
    tk.Button(raiz, text="3. Reportes",
              bg="purple", fg="white", width=28, height=2,
              command=abrirReportes).pack(pady=5)
    tk.Button(raiz, text="4. Configuracion",
              bg="orange", fg="white", width=28, height=2,
              command=abrirConfiguracion).pack(pady=5)
    tk.Button(raiz, text="5. Acerca de",
              bg="gray", fg="white", width=28, height=2,
              command=abrirAcercaDe).pack(pady=5)
    tk.Button(raiz, text="Salir",
              bg="red", fg="white", width=28, height=2,
              command=raiz.quit).pack(pady=5)

    cfg = cargarConfiguracion()
    if not cfg:
        abrirVentanaConfiguracion(raiz)

    raiz.mainloop()


if __name__ == "__main__":
    iniciarAplicacion()



def cargarConfiguracion():
    """
    Funcionalidad: Carga la configuración del estacionamiento desde la memoria secundaria.
    Entrada: No recibe parámetros.
    Salida: Objeto de tipo Configuracion si existe.
    None si todavía no se ha creado una configuración.
    """
    try:
        archivo = open("configuracion.pkl","rb")
        configuracion = pickle.load(archivo)
        archivo.close()
        return configuracion
    except:
        return None


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
    Button(ventana, text="Estacionar vehículos masivo", width=30, command=estacionarVehiculosMasivo).pack(pady=5)
    Button(ventana, text="Cierre Diario", width=30, command=crearCierreDiario).pack(pady=5)
    Button(ventana, text="Exportar cierre diario a CSV", width=30, command=exportarCierreCSV).pack(pady=5)
    Button(ventana, text="Configuración", width=30, command=crearConfiguracion).pack(pady=5)
    Button(ventana, text="Cierre por tipo de pago XML", width=30, command=crearCierreXML).pack(pady=5)
    Button(ventana, text="Acerca de", width=30, command=crearAcercaDe).pack(pady=5)
    Button(ventana, text="Salir", width=30, command=ventana.destroy).pack(pady=5)

    ventana.mainloop()

