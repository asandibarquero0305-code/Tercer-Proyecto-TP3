#Elaborado por Aaron Sandi y Brandon Coronado
#Ultimo avance: 6-26-2026
#Ultimo avance Brandon Coronado: 6-27-2026
import pickle


class Configuracion:
    """
    Funcionalidad: Guarda la configuración general del estacionamiento.
    Entrada: Tamaño del parqueo, tiempo de gracia,
    monto por hora y existencia de parqueos eléctricos.
    Salida: Objeto de tipo Configuracion.
    """
    def __init__(self,tamanoParqueo,tiempoGracia,montoHora,tieneElectrico):

        self.tamanoParqueo=tamanoParqueo
        self.tiempoGracia=tiempoGracia
        self.montoHora=montoHora
        self.tieneElectrico=tieneElectrico

class Estacionamiento:
    """
    Funcionalidad: Almacena toda la información de un vehículo
    estacionado.
    Entrada: ID, información del vehículo, estadía y pago.
    Salida: Objeto de tipo Estacionamiento.
    """
    def __init__(self, id, info, estadia, pago):
        self.id = id
        self.info = info        # (placa, marca, color, tipo)
        self.estadia = estadia  # [ubicacion, entrada, salida]
        self.pago = pago    

MARCAS = [
    "Toyota", "Hyundai", "Kia", "Honda", "Nissan",
    "Mazda", "Chevrolet", "Ford", "Mitsubishi", "Suzuki"
]
 
COLORES = [
    "Blanco", "Negro", "Gris", "Rojo", "Azul",
    "Verde", "Amarillo", "Plateado", "Cafe", "Naranja"
]
 
TIPOS = ["Sedan", "SUV", "Pickup", "Hatchback", "Van", "Deportivo"]
 
TIPOS_PAGO = {1: "Efectivo", 2: "SINPE", 3: "Tarjeta"}
 
ARCHIVO_BD = "estacionamientos.pkl"
ARCHIVO_CONFIG = "configuracion.pkl"

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
    ventana.resizable(False, False)
    ventana.grab_set()

    cfgExistente = cargarConfiguracion()

    tk.Label(ventana, text="Configuracion del Parqueo",
        font=("Arial", 14, "bold")).pack(pady=10)

    marco = tk.Frame(ventana)
    marco.pack(padx=20, fill="x")

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
        text="Ingrese el monto por hora (en colones ₡):"
    ).grid(row=2, column=0, sticky="w", pady=5)
    entradaMonto = tk.Entry(marco, width=10)
    entradaMonto.grid(row=2, column=1, padx=10)

   tk.Label(
        marco,
        text="¿El parqueo cuenta con espacio para vehículos eléctricos?"
    ).grid(row=3, column=0, sticky="w", pady=5)
    varElectrico = tk.BooleanVar()
    tk.Checkbutton(marco, variable=varElectrico).grid(row=3, column=1, sticky="w", padx=10)

    # Pre-llenar si ya existe configuracion
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
                "¿Desea actualizar la configuracion del parqueo?\n"
                "Esto no elimina los vehiculos actuales.", parent=ventana)
            if not confirmado:
                return

        nuevaCfg = Configuracion(tamano, gracia, monto, varElectrico.get())
        guardarConfiguracion(nuevaCfg)
        messagebox.showinfo("Exito", "Configuracion guardada correctamente.", parent=ventana)
        ventana.destroy()

    tk.Button(ventana, text="Guardar", command=guardar,
              bg="#1a3a6b", fg="white", font=("Arial", 11, "bold"),
              width=12).pack(pady=18)



















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

class Vehiculo:

    """
    Funcionalidad:
    Inicializa un objeto de tipo Vehiculo con sus datos principales.

    Entrada:
    placa: placa del vehículo.
    marca: marca del vehículo.
    color: color del vehículo.

    Salida:
    Crea un objeto Vehiculo.
    """
    def __init__(self, placa, marca, color):
        self.placa = placa
        self.marca = marca
        self.color = color

    """
    Funcionalidad:
    Obtiene los datos principales del vehículo.

    Entrada:
    No recibe parametros.

    Salida:
    Retorna la placa, marca y color del vehículo.
    """
    def obtenerDatosVehiculo(self):
        return self.placa, self.marca, self.color

class Voucher:

    """
    Funcionalidad:
    Inicializa un objeto de tipo Voucher con la placa y hora de entrada.

    Entrada:
    placa: placa del vehículo.
    horaEntrada: hora en que ingresa el vehículo.

    Salida:
    Crea un objeto Voucher.
    """
    def _init_(self, placa, horaEntrada):
        self.placa = placa
        self.horaEntrada = horaEntrada
        self.horaSalida = ""
        self.tipoPago = ""
        self.monto = 0

    """
    Funcionalidad:
    Asigna los datos de salida y pago al voucher.

    Entrada:
    horaSalida: hora en que sale el vehículo.
    tipoPago: forma de pago utilizada.
    monto: monto total a pagar.

    Salida:
    No retorna ningún valor.
    """
    def asignarSalida(self, horaSalida, tipoPago, monto):
        self.horaSalida = horaSalida
        self.tipoPago = tipoPago
        self.monto = monto

    """
    Funcionalidad:
    Obtiene los datos guardados en el voucher.

    Entrada:
    No recibe parámetros.

    Salida:
    Retorna placa, hora de entrada, hora de salida, tipo de pago y monto.
    """
    def obtenerDatosVoucher(self):
        return self.placa, self.horaEntrada, self.horaSalida, self.tipoPago, self.monto
    

class Espacio:

    """
    Funcionalidad:
    Inicializa un objeto de tipo Espacio.

    Entrada:
    numero: número del espacio de parqueo.
    tipo: tipo de espacio.

    Salida:
    Crea un objeto Espacio en estado libre.
    """
    def _init_(self, numero, tipo):
        self.numero = numero
        self.tipo = tipo
        self.estado = "Libre"
        self.vehiculo = None
        self.voucher = None

    """
    Funcionalidad:
    Asigna un vehículo y su voucher al espacio.

    Entrada:
    vehiculo: objeto de tipo Vehiculo.
    voucher: objeto de tipo Voucher.

    Salida:
    No retorna ningún valor.
    """
    def estacionarVehiculo(self, vehiculo, voucher):
        self.vehiculo = vehiculo
        self.voucher = voucher
        self.estado = "Ocupado"

    """
    Funcionalidad:
    Libera el espacio de parqueo.

    Entrada:
    No recibe parámetros.

    Salida:
    El espacio queda libre nuevamente.
    """
    def liberarEspacio(self):
        self.vehiculo = None
        self.voucher = None
        self.estado = "Libre"

    """
    Funcionalidad:
    Obtiene los datos básicos del espacio.

    Entrada:
    No recibe parámetros.

    Salida:
    Retorna número, tipo y estado del espacio.
    """
    def obtenerDatosEspacio(self):
        return self.numero, self.tipo, self.estado
