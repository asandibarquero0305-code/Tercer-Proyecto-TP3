from tkinter import *
from tkinter import messagebox, simpledialog
from clases import Vehiculo, Voucher, Espacio
from datetime import datetime
import urllib.request
import json

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

