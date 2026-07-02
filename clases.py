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
    objEncontrado = None  # Buscar si hay vehiculo en ese espacio sin fecha de salida
    for obj in lista:
        ubicacion = obj.estadia[0]
        salida = obj.estadia[2]
        if ubicacion == espacioId and (salida == "" or salida is None):
            objEncontrado = obj
            break

    ventana = tk.Toplevel(ventanaPadre)
    ventana.resizable(False, False)
    ventana.grab_set()

    if objEncontrado:
        ventana.title("Espacio Ocupado - " + espacioId)
        ventana.geometry("386x307")

        tk.Label(ventana, text="Espacio: " + espacioId),
                 font=("Arial", 13, "bold"), fg="#c0392b").pack(pady=10)

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
        marco.pack(padx=20, fill="x")
        campos = [
            ("# Campo:", espacioId),
            ("Placa:", str(placa)),
            ("Marca:", marcaNombre),
            ("Color:", colorNombre),
            ("Hora de Entrada:", str(entrada)),
        ]
        for etiqueta, valor in campos:
            fila = tk.Frame(marco)
            fila.pack(fill="x", pady=2)
            tk.Label(fila, text=etiqueta, font=("Arial", 10, "bold"), width=18, anchor="w").pack(side="left")
            tk.Label(fila, text=valor, font=("Arial", 10), anchor="w").pack(side="left")

        def pagar():
            """
            Funcionalidad: Registra el pago del espacio: solicita tipo de pago, calcula monto, actualiza el objeto en la lista, guarda la BD y genera la factura PDF.
            Entrada: No recibe parametros (lee datos del objeto encontrado).
            Salida: No retorna valor. Actualiza lista, pkl y genera factura PDF.
            """
            opciones = ["1 - Efectivo", "2 - SINPE", "3 - Tarjeta"]
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

            confirmado = messagebox.askyesno(
                "Confirmar Pago",
                "Monto a cobrar: ₡{:,.0f}\nTipo de pago: {}\n\n¿Confirmar?".format(
                    monto, TIPOS_PAGO[tipoPago]),
                parent=ventana
            )
            if not confirmado:
                return

            objEncontrado.estadia[2] = ahoraMismo    # Actualizar objeto en la lista
            objEncontrado.pago = (monto, tipoPago)
            guardarBD(lista)

            rutaPdf = crearFacturaPdf(objEncontrado, cfg)
            messagebox.showinfo("Pago Registrado",
                "Pago exitoso.\nFactura generada:\n{}" + rutaPdf, parent=ventana)
            ventana.destroy()

        botones = tk.Frame(ventana)
        botones.pack(pady=15)
        tk.Button(botones, text="Pagar", command=pagar,
                  bg="#27ae60", fg="white", font=("Arial", 11, "bold"), width=10).pack(side="left", padx=10)
        tk.Button(botones, text="Regresar", command=ventana.destroy,
                  bg="#7f8c8d", fg="white", font=("Arial", 11, "bold"), width=10).pack(side="left", padx=10)

    else:
        ventana.title("Estacionar Vehiculo - {}".format(espacioId))
        ventana.geometry("420x360")

        tk.Label(ventana, text="Espacio Libre: {}".format(espacioId),
                 font=("Arial", 13, "bold"), fg="#27ae60").pack(pady=10)

        marco = tk.Frame(ventana)
        marco.pack(padx=20, fill="x")

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
        entradaHora = tk.Entry(marco, width=20, state="readonly",
                                fg="gray",
                                readonlybackground="#f0f0f0")
        entradaHora.grid(row=4, column=1, padx=10)
        entradaHora.config(state="normal")
        entradaHora.insert(0, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        entradaHora.config(state="readonly")

        tk.Label(marco, text="Tarifa por hora: ₡{:,.0f}".format(cfg.montoHora),
                 font=("Arial", 10, "italic"), fg="#555").grid(row=5, column=0, columnspan=2, pady=6)

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
                "¿Desea estacionar el vehiculo?\nPlaca: {}\nEspacio: {}".format(placa, espacioId),
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
                "Vehiculo registrado.\nVoucher generado:\n{}".format(rutaVoucher), parent=ventana)
            ventana.destroy()

        botones = tk.Frame(ventana)
        botones.pack(pady=12)
        tk.Button(botones, text="Estacionar", command=estacionar,
                  bg="#1a3a6b", fg="white", font=("Arial", 11, "bold"), width=12).pack(side="left", padx=10)
        tk.Button(botones, text="Regresar", command=ventana.destroy,
                  bg="#7f8c8d", fg="white", font=("Arial", 11, "bold"), width=12).pack(side="left", padx=10)

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

    ocupados = set() # IDs ocupados (sin fecha de salida)
    for obj in lista:
        if obj.estadia[2] == "" or obj.estadia[2] is None:
            ocupados.add(obj.estadia[0])

    ventana = tk.Toplevel(ventanaPadre)
    ventana.title("Ver Estacionamiento")
    ventana.grab_set()

    columnas = 8 #calc tama;o venntanas
    filas = (len(ids) + columnas - 1) // columnas
    anchoVentana = min(850, columnas * 95 + 60)
    altoVentana = min(700, filas * 75 + 160)
    ventana.geometry("{}x{}".format(anchoVentana, altoVentana))

    tk.Label(ventana, text="Mapa del Parqueo",
             font=("Arial", 14, "bold")).pack(pady=8)

    leyenda = tk.Frame(ventana)
    leyenda.pack()
    tk.Label(leyenda, text="  ", bg="#27ae60", width=3).pack(side="left", padx=4)
    tk.Label(leyenda, text="Libre").pack(side="left")
    tk.Label(leyenda, text="   ", bg="#e74c3c", width=3).pack(side="left", padx=8)
    tk.Label(leyenda, text="Ocupado").pack(side="left")
    tk.Label(leyenda, text="   ", bg="#f39c12", width=3).pack(side="left", padx=8)
    tk.Label(leyenda, text="Especial/Electrico").pack(side="left")

    marco = tk.Frame(ventana)
    marco.pack(fill="both", expand=True, padx=10, pady=5)

    canvas = tk.Canvas(marco, bg="#ecf0f1")
    scrollY = ttk.Scrollbar(marco, orient="vertical", command=canvas.yview)
    scrollX = ttk.Scrollbar(ventana, orient="horizontal", command=canvas.xview)
    canvas.configure(yscrollcommand=scrollY.set, xscrollcommand=scrollX.set)

    scrollY.pack(side="right", fill="y")
    scrollX.pack(side="bottom", fill="x")
    canvas.pack(side="left", fill="both", expand=True)

    frameInternoCuadricula = tk.Frame(canvas, bg="#ecf0f1")
    canvas.create_window((0, 0), window=frameInternoCuadricula, anchor="nw")

    def actualizarScroll(event):
        canvas.configure(scrollregion=canvas.bbox("all"))

    frameInternoCuadricula.bind("<Configure>", actualizarScroll)

    botonesEspacios = {}

    def hacerClickEspacio(eid):
        """
        Funcionalidad: Maneja el clic sobre un espacio de la cuadricula. Recarga la BD, abre la ventana de detalle y actualiza los colores al cerrarla.
        Entrada: eid (str): ID del espacio clickeado.
        Salida: No retorna valor.
        """

        listaActual = cargarBD()
        abrirVentanaEspacio(ventana, eid, listaActual, cfg)
        ventana.wait_window(ventana.winfo_children()[-1] if ventana.winfo_children() else ventana)
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
                colorBase = "#e67e22" if eid not in ocupadosActual else "#e74c3c"
            else:
                colorBase = "#27ae60" if eid not in ocupadosActual else "#e74c3c"
            btn.config(bg=colorBase)

    for indice, eid in enumerate(ids):  # hacer cuadricula
        fila = indice // columnas
        col = indice % columnas

        if eid.startswith("E-") or eid.startswith("EL-"):
            colorFondo = "#e67e22" if eid not in ocupados else "#e74c3c"
        else:
            colorFondo = "#27ae60" if eid not in ocupados else "#e74c3c"

        btn = tk.Button(
            frameInternoCuadricula,
            text=eid,
            bg=colorFondo,
            fg="white",
            font=("Arial", 8, "bold"),
            width=8,
            height=3,
            relief="raised",
            command=lambda e=eid: hacerClickEspacio(e)
        )
        btn.grid(row=fila, column=col, padx=4, pady=4)
        botonesEspacios[eid] = btn

    filaExtra = filas
    tk.Label(frameInternoCuadricula, text="[CASETILLA]",
             bg="#2c3e50", fg="white", font=("Arial", 8, "bold"),
             width=10, height=3, relief="ridge").grid(
        row=filaExtra, column=0, columnspan=2, padx=4, pady=8)
    tk.Label(frameInternoCuadricula, text="[BANO]",
             bg="#7f8c8d", fg="white", font=("Arial", 8, "bold"),
             width=8, height=3, relief="ridge").grid(
        row=filaExtra, column=2, padx=4, pady=8)

    tk.Button(ventana, text="Cerrar", command=ventana.destroy,
              bg="#7f8c8d", fg="white", font=("Arial", 10, "bold")).pack(pady=6)


def calcularMonto(entrada, salida, cfg):
    """
    Funcionalidad: Calcula el monto a cobrar segun la duracion de la estadia y el tiempo de gracia configurado.
    Entrada:
    - entrada (str): Fecha y hora de entrada en formato '%Y-%m-%d %H:%M:%S'.
    - salida (str): Fecha y hora de salida en formato '%Y-%m-%d %H:%M:%S'.
    - cfg (Configuracion): Objeto con montoHora y tiempoGracia.
    Salida:
    - monto (float): Monto total en colones a cobrar.
    """
    dtEntrada = datetime.strptime(str(entrada), "%Y-%m-%d %H:%M:%S")
    dtSalida = datetime.strptime(str(salida), "%Y-%m-%d %H:%M:%S")
    minutos = (dtSalida - dtEntrada).total_seconds() / 60
    minutosFacturables = max(0, minutos - cfg.tiempoGracia)
    horas = minutosFacturables / 60
    return round(horas * cfg.montoHora, 0)


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

    placaTexto = str(placa) # Datos del QR
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

    if os.path.exists(rutaQr): # QR
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
        dtEntrada = datetime.strptime(str(entrada), "%Y-%m-%d %H:%M:%S") # Calculo horas
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

    if os.path.exists(rutaQr):  #QR
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
        filas += """
        <tr>
            <td>{}</td>
            <td>{}</td>
            <td>{}</td>
            <td>{}</td>
            <td>{}</td>
            <td class="monto">₡{:,.0f}</td>
        </tr>""".format(ubicacion, placa, entrada, salida, tipoPagoNombre, monto)

    subtotales = ""
    for tp, nombre in TIPOS_PAGO.items():
        subtotales += """
        <div class="subtotal-bloque">
            <span class="subtotal-etiqueta">{}</span>
            <span class="subtotal-valor">₡{:,.0f}</span>
        </div>""".format(nombre, totalesPorTipo.get(tp, 0))

    html = """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Cierre Diario - {fecha}</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            background: #f0f4f8;
            margin: 0;
            padding: 20px;
            color: #222;
        }}
        /* --- 3 tamanos de letra --- */
        h1 {{ font-size: 28px; color: #1a3a6b; }}  /* grande / azul */
        h2 {{ font-size: 18px; color: #2e7d32; }}  /* mediano / verde */
        p.fecha {{ font-size: 13px; color: #888; }} /* pequeno / gris */

        header {{
            background: #1a3a6b;
            color: white;
            padding: 18px 28px;
            border-radius: 8px;
            margin-bottom: 24px;
        }}
        header h1 {{ color: white; margin: 0; }}
        header p {{ margin: 4px 0 0; font-size: 14px; opacity: 0.85; }}

        table {{
            width: 100%;
            border-collapse: collapse;
            background: white;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        }}
        thead tr {{
            background: #1a3a6b;  /* azul - color 1 */
            color: white;
        }}
        th {{ padding: 11px 14px; text-align: left; font-size: 13px; }}
        td {{ padding: 9px 14px; font-size: 13px; border-bottom: 1px solid #eee; }}
        tr:nth-child(even) {{ background: #f7f9fc; }}
        .monto {{ color: #2e7d32; font-weight: bold; }} /* verde - color 2 */

        .resumen {{
            margin-top: 28px;
            display: flex;
            gap: 20px;
            flex-wrap: wrap;
        }}
        .subtotal-bloque {{
            background: white;
            border-left: 5px solid #2e7d32;
            padding: 12px 20px;
            border-radius: 6px;
            box-shadow: 0 2px 6px rgba(0,0,0,0.07);
            min-width: 200px;
        }}
        .subtotal-etiqueta {{ display: block; font-size: 13px; color: #555; }}
        .subtotal-valor {{ display: block; font-size: 20px; font-weight: bold; color: #1a3a6b; }}

        .total-general {{
            margin-top: 18px;
            background: #1a3a6b;
            color: white;
            padding: 14px 24px;
            border-radius: 8px;
            display: inline-block;
        }}
        .total-general span {{
            font-size: 22px;   /* tercer tamano de letra */
            font-weight: bold;
            color: #f9c74f;    /* amarillo - color 3 */
        }}
    </style>
</head>
<body>
    <header>
        <h1>Cierre Diario - Parqueo TEC</h1>
        <p>Fecha: {fecha} &nbsp;|&nbsp; Generado: {hora}</p>
    </header>

    <h2>Detalle de Transacciones</h2>
    <p class="fecha">Total de registros: {cantidad}</p>

    <table>
        <thead>
            <tr>
                <th>Ubicacion</th>
                <th>Placa</th>
                <th>Hora Entrada</th>
                <th>Hora Salida</th>
                <th>Tipo de Pago</th>
                <th>Monto</th>
            </tr>
        </thead>
        <tbody>
            {filas}
        </tbody>
    </table>

    <div class="resumen">
        {subtotales}
    </div>

    <div class="total-general">
        Total recaudado del dia: <span>₡{total:,.0f}</span>
    </div>
</body>
</html>""".format(
        fecha=hoy,
        hora=datetime.now().strftime("%H:%M:%S"),
        cantidad=len(lista),
        filas=filas,
        subtotales=subtotales,
        total=totalGeneral
    )

    with open(rutaHtml, "w", encoding="utf-8") as f:
        f.write(html)

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

    def objetoAXml(obj, indent="        "):
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
        return (
            "{}<vehiculo>\n"
            "{}    <id>{}</id>\n"
            "{}    <placa>{}</placa>\n"
            "{}    <marca>{}</marca>\n"
            "{}    <color>{}</color>\n"
            "{}    <tipo>{}</tipo>\n"
            "{}    <ubicacion>{}</ubicacion>\n"
            "{}    <entrada>{}</entrada>\n"
            "{}    <salida>{}</salida>\n"
            "{}    <monto>{}</monto>\n"
            "{}    <tipoPago>{}</tipoPago>\n"
            "{}</vehiculo>\n"
        ).format(
            indent, indent, obj.id,
            indent, placa, indent, marcaNombre,
            indent, colorNombre, indent, tipoNombre,
            indent, ubicacion, indent, entrada,
            indent, salida, indent, monto,
            indent, TIPOS_PAGO.get(tipoPago, str(tipoPago)),
            indent
        )

    lineas = ['<?xml version="1.0" encoding="UTF-8"?>', "<cierrePorTipoPago>"]

    for nombreSeccion, claveNum in [("efectivo", 1), ("sinpe", 2), ("tarjeta", 3)]:
        lineas.append("    <{}>".format(nombreSeccion))
        for obj in grupos[claveNum]:
            lineas.append(objetoAXml(obj))
        lineas.append("    </{}>".format(nombreSeccion))

    lineas.append("</cierrePorTipoPago>")

    with open(rutaXml, "w", encoding="utf-8") as f:
        f.write("\n".join(lineas))

    return rutaXml


def exportarCierroCsv(lista):
    """
    Funcionalidad: Exporta los datos del cierre diario a un archivo CSV sin encabezados, listo para abrir en Excel. 
    Columnas: ubicacion, placa, entrada, salida, tipo de pago, monto.
    Entrada: lista (list): Lista de objetos Estacionamiento a exportar.
    Salida: rutaCsv (str): Ruta del archivo CSV generado.
    """
    rutaCsv = "cierre_diario_" + datetime.now().strftime("%d-%m-%Y") + ".csv"

    with open(rutaCsv, "w", newline="", encoding="utf-8") as f:
        escritor = csv.writer(f)
        for obj in lista:
            placa, marca, color, tipo = obj.info
            ubicacion, entrada, salida = obj.estadia
            monto, tipoPago = obj.pago
            escritor.writerow([ubicacion, placa, entrada, salida,
                                TIPOS_PAGO.get(tipoPago, str(tipoPago)), monto])

    return rutaCsv

def abrirVentanaReportes(ventanaPadre):
    """
    Funcionalidad: Abre la ventana de reportes con tres opciones: cierre diario (HTML), cierre por tipo de pago (XML) y exportar CSV.
    Entrada: ventanaPadre (tk.Tk): Ventana principal de la aplicacion.
    Salida: No retorna valor. Abre una ventana Toplevel con los botones de reporte.
    """
    ventana = tk.Toplevel(ventanaPadre)
    ventana.title("Reportes")
    ventana.geometry("360x310")
    ventana.resizable(False, False)
    ventana.grab_set()

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

        pendientes = [o for o in lista if o.estadia[2] == "" or o.estadia[2] is None]
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
            "Cierre generado exitosamente.\nArchivo: {}".format(rutaHtml), parent=ventana)

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

        pagados = [o for o in lista if o.pago[1] != 0]
        if not pagados:
            messagebox.showinfo("Info", "No hay vehiculos con pago registrado.", parent=ventana)
            return

        rutaXml = generarCierrePorTipoXml(pagados)
        messagebox.showinfo("Cierre por Tipo de Pago",
            "XML generado:\n{}".format(rutaXml), parent=ventana)

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
            "CSV generado exitosamente:\n{}".format(rutaCsv), parent=ventana)

    tk.Button(ventana, text="a. Cierre Diario y Facturacion en Masa",
              command=cierreDiario, bg="#1a3a6b", fg="white",
              font=("Arial", 10, "bold"), width=32, height=2).pack(pady=8)

    tk.Button(ventana, text="b. Cierre por Tipo de Pago (XML)",
              command=cierrePorTipo, bg="#27ae60", fg="white",
              font=("Arial", 10, "bold"), width=32, height=2).pack(pady=8)

    tk.Button(ventana, text="c. Exportar Cierre Diario a CSV",
              command=exportarCsv, bg="#e67e22", fg="white",
              font=("Arial", 10, "bold"), width=32, height=2).pack(pady=8)

    tk.Button(ventana, text="Regresar", command=ventana.destroy,
              bg="#7f8c8d", fg="white", font=("Arial", 10)).pack(pady=6)


























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
