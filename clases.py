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
