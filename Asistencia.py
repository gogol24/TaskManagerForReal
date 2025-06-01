import datetime
import Datos
# Se asume que las clases Personas, EventoUnidad, la función comprobar_hora y la clase proyectos están definidas.

from typing import Tuple, Union, List


predeterminados={"h":10, "m":20, "p":30, "l":1, "mr":2, "mi":3, "j":4, "v":5, "s":6, "d":7}  # Posibles letras para fechas predeterminadas
mx_tz = datetime.timezone(datetime.timedelta(hours=-6))
def validar_titulo_valor(titulo: str) -> Tuple[bool, Union[str, None]]:
    """
    Valida el título de la tarea.
    
    Si el título es exactamente "mi salchicha", se retorna un mensaje especial.
    De lo contrario, se acepta cualquier cadena no vacía (se puede ampliar la validación).
    
    :param titulo: El título ingresado.
    :return: (strip(titulo), mensaje especial o None) si es válido, o (False, mensaje de error).
    """
    titulo_limpio = titulo.strip()
    if not titulo_limpio:
        return False, "El título no puede estar vacío."
    if titulo_limpio == "mi salchicha":
        return True, "codigo secreto 'mi salchicha'"
    return titulo_limpio, None

def validar_descripcion_valor(descripcion: str) -> Tuple[bool, Union[str, None]]:
    """
    Valida la descripción de la tarea.
    
    Se verifica que no esté vacía (se puede ampliar la lógica si se desea).
    
    :param descripcion: La descripción ingresada.
    :return: (True, None) si es válida, o (False, mensaje de error).
    """
    descripcion_limpia = descripcion.strip()
    if not descripcion_limpia:
        return False, "La descripción no puede estar vacía."
    # Se puede agregar verificación de longitud mínima, si es necesario.
    return descripcion_limpia, None

def validar_dificultad_valor(dificultad: str) -> Tuple[bool, Union[str, None]]:
    """
    Valida la dificultad de la tarea.
    
    Se espera que la dificultad sea un número entero entre 1 y 40.
    
    :param dificultad: Valor ingresado (en formato de cadena).
    :return: (True, None) si es válido, o (False, mensaje de error).
    """
    try:
        valor = int(dificultad)
    except ValueError:
        return False, "La dificultad debe ser un número entero."
    
    if not 1 <= valor <= 40:
        return False, "La dificultad debe estar expresada en horas del 1 al 40."
    
    return True, None

def validar_dificultad_valor(dificultad: str) -> Tuple[bool, Union[str, None]]:
    """
    Valida la dificultad de la tarea.
    
    Se espera que la dificultad sea un número entero entre 1 y 40.
    
    :param dificultad: Valor ingresado (en formato de cadena).
    :return: (True, None) si es válido, o (False, mensaje de error).
    """
    try:
        valor = int(dificultad)
    except ValueError:
        return False, "La dificultad debe ser un número entero."
    
    if not 1 <= valor <= 40:
        return False, "La dificultad debe estar expresada en horas del 1 al 40."
    
    return True, None

def calcular_fecha_predeterminada(diaisoE: int, base_date: datetime.date) -> Tuple[bool, datetime.date]:
    """
    Calcula la fecha de entrega usando valores predeterminados basados en el día ISO.
    
    :param diaisoE: Valor numérico (por ejemplo, 10, 20 o 30) que se usará para ajustar el día ISO.
    :param base_date: Fecha base (usualmente la fecha actual) que se usa para calcular la fecha de entrega.
    :return: (True, fecha_calculada) o (False, mensaje de error) si fuera necesario.
    """
    año_base = base_date.year
    # Determinar cuántas semanas tiene el año
    try:
        datetime.date.fromisocalendar(año_base, 53, 7)
        semanas_totales = 53
    except ValueError:
        semanas_totales = 52

    # Obtener la información ISO de la fecha base
    iso_year, iso_week, iso_day = base_date.isocalendar()

    # Hoy=10
    # Mañana=20
    # Pasado=30
    # l=1
    # mr=2
    # mi=3
    # j=4
    # v=5
    # s=6
    # d=7

    # Cálculo según el valor de diaisoE
    # Si es hoy mañana o pasado
    
    if diaisoE // 10 in [1, 2, 3]:
        dia_calculado = iso_day + (diaisoE // 10) - 1
        if dia_calculado > 7:
            dia_calculado -= 7
            semana_calculada = iso_week + 1
        else:
            semana_calculada = iso_week
    elif diaisoE == iso_day or diaisoE < iso_day:
        semana_calculada = iso_week + 1
        dia_calculado = diaisoE
    else:
        semana_calculada = iso_week
        dia_calculado = diaisoE
    if semana_calculada > semanas_totales:
        iso_year += 1
        semana_calculada = 1

    fecha_calculada = datetime.date.fromisocalendar(iso_year, semana_calculada, dia_calculado)
    return fecha_calculada,False

def formatear_componente_fecha(componente: Union[str, int]) -> str:
    """
    Asegura que un componente de la fecha (día o mes) tenga dos dígitos.
    
    :param componente: El valor (cadena o número) a formatear.
    :return: Cadena con dos dígitos.
    """
    componente_str = str(componente)
    if len(componente_str) == 1:
        return f"0{componente_str}"
    return componente_str

def validar_componentes_fecha(
    dia: str, 
    mes: Union[str, None] = None, 
    año: Union[str, None] = None, 
    base_date: Union[datetime.date, None] = None
) -> Tuple[bool, Union[bool, List[str], str]]:
    """
    Valida que los componentes de la fecha sean coherentes y correctos.
    
    :param dia: Día en formato string.
    :param mes: Mes en formato string; si no se proporciona, se usa el mes de base_date.
    :param año: Año en formato string; si no se proporciona, se usa el año de base_date.
    :param base_date: Fecha base para la comparación; si no se proporciona, se usa la fecha actual.
    :return: (True, False) si es válida, o (False, errores) con lista de componentes erróneos 
             o un mensaje si no se pudo validar.
    """

    if base_date is None:
        base_date = datetime.date.today()
    if mes is None:
        mes = base_date.strftime("%m")
    if año is None:
        año = base_date.strftime("%Y")

    #hacer entero de la fecha base 
    current_year = int(base_date.strftime("%Y"))
    current_month = int(base_date.strftime("%m"))
    current_day = int(base_date.strftime("%d"))

    errores = []
    error_año = False
    error_mes = False
    error_dia = False

    try:
        #intentar hacer las fechas numeros
        dia_int = int(dia)
        mes_int = int(mes)
        año_int = int(año)
    except ValueError:
        return False, "Los componentes de la fecha deben ser numéricos."



    #si el año es menor al año actualo se pasa por 10 años
    if año_int < current_year or año_int > current_year + 10:
        error_año = True
    #meses fuer adel rango
    if mes_int < 1 or mes_int > 12:
        error_mes = True
    #dis fuera del rango
    if dia_int < 1 or dia_int > 31:
        error_dia = True
    #si la fecha y el mes son menores o iguales a aldia aactua y el año es igual o menor kue el actual, (una fecha pasada)
    if dia_int < current_day and mes_int <= current_month and año_int <= current_year:
        error_dia = True
        error_mes = True

    #si hay cauklkier error
    if error_año or error_mes or error_dia:
        if error_año:
            errores.append("año")
        if error_mes:
            errores.append("mes")
        if error_dia:
            errores.append("día")
        #añadir el error y devolver los errores
        return False, errores

    try:
        # Verifica que se pueda formar una fecha válida
        datetime.date.fromisoformat(f"{año}-{mes}-{dia}")
    except ValueError:
        return False, "La fecha ingresada no puede ser aceptada"
    #si no hay error, treu falso
    return True, False

def crear_fecha_de_entrega(
    fecha_str: str, 
    base_date: Union[datetime.date, None] = None
) -> Tuple[bool, Union[datetime.date, str, List[str]]]:
    """
    Crea una fecha de entrega a partir de una cadena de entrada.
    
    La función acepta:
      - Códigos predeterminados (por ejemplo, "h" para hoy, "m" para mañana, etc.), 
      - Formato 'dd/mm' (usando el año actual), o
      - Formato 'dd/mm/aaaa'.

    :param fecha_str: Cadena ingresada por el usuario.
    :param predeterminados: Diccionario con códigos predeterminados (por ejemplo, {"h": 10, ...}).
    :param base_date: Fecha base para el cálculo; si no se proporciona, se usa la fecha actual.
    :return: (True, fecha) si se pudo crear la fecha, o (False, mensaje de error o lista de errores).
    """
    global predeterminados
    if base_date is None:
        base_date = datetime.date.today()
    current_year = base_date.year
    current_month = base_date.month
    current_day = base_date.day

    #Si la fecha tiene longitu 1 o 2, es un dia o es una fecha predeterminada
    if len(fecha_str) in [1, 2]:
    
        fecha_str_lower = fecha_str.lower()
        #Si la fecha es un predeterminado
        if fecha_str_lower in predeterminados:
            # Se usa la función para calcular la fecha predeterminada
            return calcular_fecha_predeterminada(predeterminados[fecha_str_lower], base_date)
        else:
            #si no es predetermianda, fromateral para agregar 0 si no tiene
            try:
                diaE = formatear_componente_fecha(fecha_str)
            except ValueError:
                return False, "El día debe ser un número entre 1 y 31."
            if int(diaE) < current_day:
                #si es meno kue el dia de hoy, es el proximo mes
                mesE = current_month + 1
                #si el mes se pasa de 12, entonces es el proximo año
                if mesE == 13:
                    añoE = current_year + 1
                    mesE=1
                    mesE_str = formatear_componente_fecha(mesE)
                    añoE_str = str(añoE)

                else:
                    #si no es el proxim oaño, pues dejarlo normal
                    mesE_str = formatear_componente_fecha(mesE)
                    añoE_str = str(current_year)
            else:
                #Si no es menor, es el mes actual
                mesE_str = formatear_componente_fecha(current_month)
                añoE_str = str(current_year)
            
            valid, error = validar_componentes_fecha(diaE, mesE_str, añoE_str, base_date)
            if not valid:
                return False, error
            fecha_de_entrega = datetime.date.fromisoformat(f"{añoE_str}-{mesE_str}-{diaE}")
            return fecha_de_entrega,False
    elif len(fecha_str) == 5 and "/" in fecha_str:
        diaE = fecha_str[0:2]
        mesE = fecha_str[3:5]
        añoE = str(current_year)
        valid, error = validar_componentes_fecha(diaE, mesE, añoE, base_date)
        if not valid:
            return False, error
        fecha_de_entrega = datetime.date.fromisoformat(f"{añoE}-{mesE}-{diaE}")
        return fecha_de_entrega,False
    elif len(fecha_str) == 10 and "/" in fecha_str:
        diaE = fecha_str[0:2]
        mesE = fecha_str[3:5]
        añoE = fecha_str[6:]
        valid, error = validar_componentes_fecha(diaE, mesE, añoE, base_date)
        if not valid:
            return False, error
        fecha_de_entrega = datetime.date.fromisoformat(f"{añoE}-{mesE}-{diaE}")
        return fecha_de_entrega,False
    else:
        return False, ("Formato de fecha incorrecto. Usa:\n"
                       "• Códigos: h para hoy, m para mañana, p para pasado mañana, "
                       "l para lunes, mr para martes, mi para miércoles, j para jueves, "
                       "v para viernes, s para sábado, d para domingo\n"
                       "• o dd/mm o dd/mm/aaaa")

def validar_hora(tiempo):
        '''
        Valida una hora en fromato string y devuelve su equivalente en objeto datetime

        :param fecha: hora en formato string, si es "n" la hora devuelta sera 23:59

        '''
        tiempo=tiempo.lower()
        if tiempo=="n":
            hora=23
            minutos=59
            return datetime.time(hora,minutos), False
        
        elif (len(tiempo)!=5 or ":" not in tiempo) and len(tiempo)!=2:
            return False, "La hora debe estar en formato hh:mm o hh ej: 07, 23, 18:10"
    
        try: 
            h=False
            m=False
            if len(tiempo)==2:
                h=True
                hora=tiempo
                minutos=0
                hora=int(hora)
                h=False
            else:
                h=True
                m=True
                hora, minutos=tiempo.split(":")
                hora,minutos=(map(int,(hora,minutos)))
                h=False
                m=False

            if not (0 <= hora < 24):
                h=True
            if not (0 <= minutos < 60):
                m=True
            if h or m:
                raise ValueError

        except ValueError:
            if h and m:
                e=f"[{hora}\n{minutos}]"
            elif h:
                e=f"La hora debe ser un numero entre 00 y 23, escribiste '{hora}'"
            elif m:
                e=f"Los minutos deben ser un numero netre 00 y 59, escribiste '{minutos}'"

            return False, e

        horaE=datetime.time(hora,minutos,tzinfo=mx_tz)

        return horaE, False

class Personas():
    listadepersonas=[]
    def __init__(self,id):
        Personas.listadepersonas.append(self)
        self.id=id
        #HACER UN ARCHIVO CSV POR CADA USUARIO
        #ESTO DA IGUAL POR AHORA, PRIMERO VAMOS A HACER LO DE FORMA INDIVIDUAL
        #EL CSV SE TIENE KE ACTUALZIAR CADA VEZ
        #cuando un usuairo llama al bot el bot tiene ke administrar el hecho de ke la tarea ke se esta creando correpsonde a ese usuraio, esot es, la tarea recien creada debe agregarse al bot(id correspondiente).
        self.lista_tareas=[]
        self.lista_recordatorios=[]
        self.lista_fechas_limite=[]

        self.dict_eventos={Tarea:self.lista_tareas,Recordatorio:self.lista_recordatorios,FechaLimite:self.lista_fechas_limite} 
        self.lista_tareas_completas=[]

        self.lista_recordatorios_copmpletos=[]

        self.lista_fechas_limite_completas=[]

        self.dict_eventos_completados={Tarea:self.lista_tareas_completas,Recordatorio:self.lista_recordatorios_copmpletos,FechaLimite:self.lista_fechas_limite_completas}

        proyectog=proyectos("general",id)
        self.dicsproyectos={proyectog.nombre:proyectog}
        
        self.contador_de_eventos=0#####CAMBIARESTO CUADNO BORRE LA TAREA FAKEEEEE
        self.contador_de_proyectos=0
        self.agregar_evento(Tarea.from_dict(self.id,{0:"TareaFake",3:datetime.datetime.now(mx_tz)+datetime.timedelta(days=1)}))

    
#    def tarea(self, id ):


    @classmethod
    def porid(cls,id):
            
        """
        Devuelve la persona segun el id ingreado

        Args: 
            ID (int), id de la persona que se desea buscar

        Returns:
            Persona: Instancia de la persona con ese ID 
            Bool: False si no encuentra la persona 
        """ 

        for persona in cls.listadepersonas:
            if id==persona.id:
                return persona
        persona=Personas(id)
        return persona
    
    def agregar_evento(self,evento):

        evento.id=int(f"{self.id}{self.contador_de_eventos}")
        self.dict_eventos[type(evento)].append(evento)
        self.dict_eventos[type(evento)].sort(key=lambda t: t.fecha_de_entrega_completa)
        self.contador_de_eventos+=1
        
    def agregar_proyecto(self,proyecto):
        proyecto.id=int(f"{self.id}{self.contador_de_proyectos}")
        self.dicsproyectos[proyecto.nombre]=proyecto
        self.contador_de_proyectos+=1

    def consultar_lista_tareas(self):
        return self.lista_tareas
    
    def consultar_lista_proyectos(self):
        return self.dicsproyectos

    def completartarea(self,tarea):
        '''
        completar la tarea
        '''
        tarea.complete=True
        self.lista_tareas.remove(tarea)
        self.lista_tareas_completas.append(tarea)   
        
class proyectos(Personas):
    #AGERGAR MAESTROS A LAS proyectos Y TAL VEZ UNA DESCRIPCION 
#    listadeproyectos=[]
        
    
    def __repr__(self):
        return f"Proyecto(id:{self.id!r}, nombre={self.nombre!r})"
    
    
    def __str__(self):
        return self.nombre
    
    def __init__(self,nombre,id):

        self.nombre=nombre
        self.dueño_id=id
        self.id=False
        self.profesores=False

 #       proyectos.listadeproyectos.append(self
    def nombrarproyecto(self,nombre):
        self.nombre=nombre
    
    def agregarprofesor(self,maestro):
        self.profesores=maestro

class EventoUnidad:
    def __init__(self, dueño_id,titulo: str, fecha_de_entrega: datetime.date, hora: datetime.time):
        self.dueño_id=dueño_id
        self.id=False
        self.titulo = titulo
        self.fecha_de_entrega = fecha_de_entrega
        if not fecha_de_entrega:
            self.fecha_de_entrega=datetime.date.today()+datetime.timedelta(5)
        else:
            self.fecha_de_entrega=fecha_de_entrega
        if not hora:
            self.hora=datetime.time(0,0,tzinfo=mx_tz)
        else:
            self.hora = hora
        self.fecha_de_entrega_completa=datetime.datetime.combine(self.fecha_de_entrega,self.hora) 
        self.complete=False



    def __str__(self):
        return (f"EventoUnidad(titulo={self.titulo}, "
                f"fecha_de_entrega={self.fecha_de_entrega}, hora={self.hora})")

    @classmethod
    def from_dict(cls, data: dict):
        """
        Crea una instancia de EventoUnidad a partir de un diccionario.
        Se utilizan las llaves:
          0: título, 3: fecha_de_entrega, 4: hora
        """
        dueño_id=data.get(0)
        titulo = data.get(1)
        fecha_de_entrega = data.get(2)
        hora = data.get(3)
        return cls(dueño_id,titulo, fecha_de_entrega, hora)

class Tarea(EventoUnidad):
    def __init__(self, dueño_id, titulo: str, fecha_de_entrega: datetime.date, hora: datetime.time, 
                 descripcion: str, dificultad: int, proyecto: str):
        super().__init__(dueño_id,titulo, fecha_de_entrega, hora)
        self.descripcion = descripcion
        self.dificultad = dificultad
        self.proyecto = proyecto

    def __str__(self):
        return (f"Tarea(titulo={self.titulo}, fecha_de_entrega={self.fecha_de_entrega}, "
                f"hora={self.hora}, descripcion={self.descripcion}, "
                f"dificultad={self.dificultad}, proyecto={self.proyecto})")

    @classmethod
    def from_dict(cls, dueño_id, data: dict):
        """
        Crea una instancia de Tarea a partir de un diccionario.
        Se utilizan las llaves:
          0: título, 1: descripción, 2: proyecto,
          3: fecha_de_entrega, 4: hora, 5: dificultad.
        """
        titulo = data.get(0,None)
        descripcion = data.get(1,None)
        proyecto = data.get(2,None)
        fecha_de_entrega = data.get(3,None)
        hora = data.get(4,None)
        dificultad = data.get(5,None)
        return cls(dueño_id,titulo, fecha_de_entrega, hora, descripcion, dificultad, proyecto)
    
    def diccionario_estandar(self):
        return {0:self.titulo,1:self.descripcion,2:self.proyecto,3:self.fecha_de_entrega,4:self.hora,5:self.dificultad}

class Recordatorio(EventoUnidad):
    def __init__(self, titulo: str, fecha_de_entrega: datetime.date, hora: datetime.time, descripcion: str):
        super().__init__(titulo, fecha_de_entrega, hora)
        self.descripcion = descripcion

    def __str__(self):
        return (f"Recordatorio(titulo={self.titulo}, fecha_de_entrega={self.fecha_de_entrega}, "
                f"hora={self.hora}, descripcion={self.descripcion})")

    @classmethod
    def from_dict(cls, id,data: dict):
        """
        Crea una instancia de Recordatorio a partir de un diccionario.
        Se utilizan las llaves:
          0: título, 1: descripción, 3: fecha_de_entrega, 4: hora.
        """
        titulo = data.get(0)
        descripcion = data.get(1)
        fecha_de_entrega = data.get(3)
        hora = data.get(4)
        return cls(id,titulo, fecha_de_entrega, hora, descripcion)

class FechaLimite(Tarea):
    def __init__(self, titulo: str, fecha_de_entrega: datetime.date, hora: datetime.time, 
                 descripcion: str, dificultad: int, proyecto: str):
        super().__init__(titulo, fecha_de_entrega, hora, descripcion, dificultad, proyecto)
        self.tipo = "FechaLimite"

    def __str__(self):
        return (f"FechaLimite(titulo={self.titulo}, fecha_de_entrega={self.fecha_de_entrega}, "
                f"hora={self.hora}, descripcion={self.descripcion}, "
                f"dificultad={self.dificultad}, proyecto={self.proyecto})")

    @classmethod
    def from_dict(cls, data: dict):
        """
        Crea una instancia de FechaLimite a partir de un diccionario.
        Se utilizan las llaves:
          0: título, 1: descripción, 2: proyecto,
          3: fecha_de_entrega, 4: hora, 5: dificultad.
        """
        titulo = data.get(0)
        descripcion = data.get(1)
        proyecto = data.get(2)
        fecha_de_entrega = data.get(3)
        hora = data.get(4)
        dificultad = data.get(5)
        return cls(titulo, fecha_de_entrega, hora, descripcion, dificultad, proyecto)

def validar_proyecto_valor(name_proyecto: str, id:int) -> Tuple[bool, Union[str, None]]:
    """
    Valida el proyecto asociado a la tarea.
    
    Se asume que 'lista_proyectos' es la lista (o conjunto) de nombres de proyectos válidos.
    Si el valor ingresado coincide con el estado de creación pendiente (estado_creacion),
    se considera una confirmación para crear el proyecto.
    Si no, se verifica que el proyecto exista en la lista.
    
    :param proyecto: El nombre del proyecto ingresado.
    :param lista_proyectos: La lista de proyectos disponibles.
    :param estado_creacion: Valor que indica si se está en proceso de creación.
    :return: (True, None) si es válido, o (False, mensaje de error).
    """

    proyecto_limpio = name_proyecto.strip()
    if not proyecto_limpio:
        return False, "Huh?"
    nombres_proyectos:Personas=Datos.obtener_persona(id).consultar_lista_proyectos().keys()
    if proyecto_limpio in nombres_proyectos:
        return False, "Ya existe un proyecto con ese nombre"
    else:
        proyecto=proyectos(name_proyecto, id)

        return proyecto, False

nombres_evento_dict = {"tarea":Tarea.from_dict, "recordatorio":Recordatorio.from_dict, "fecha_limite":FechaLimite.from_dict}


def consultar_proyectos(id):
    '''
    Devuelve el diccionario de proyectos {nombre:proyecto} del id
    '''
    persona=Datos.obtener_persona(id)
    if persona:
        return persona.dicsproyectos
    else:
        return False, "No se encontro a la persona con ese id"

def agregar_proyecto_a_persona(proyecto,id):
    '''
    Agrega el proyecto al id
    '''
    persona:Personas=Datos.obtener_persona(id)
    persona.agregar_proyecto(proyecto)
    return

def crear_y_agregar_evento_a_persona(evento,dicc,id):
    '''Crea el objeto tarea y lo agerga al id'''
    
    desdediccionario=nombres_evento_dict[evento]

    E=desdediccionario(id,dicc)

    Datos.obtener_persona(id).agregar_evento(E)
    print(E.id)
    return E

def consulta_tareas(id,rekisitos:list=[0,1,3],lim=None):

    #ORDENAR  LAS TAREAS POR FECHA DE ENTREGA O LO KUE NO SPIDAN
    print(Datos.personas)
    persona:Personas=Datos.obtener_persona(id)
    Tareas=persona.consultar_lista_tareas()
    consulta={}
    for tarea in Tareas[:lim]:
        taread=tarea.diccionario_estandar()
        datosdetarea={}
        for rekisito in rekisitos:
            datosdetarea[rekisito]=taread[rekisito]
        consulta[tarea]=datosdetarea
    return consulta


# Ejemplo de uso:



#class Tarea(Personas, EventoUnidad):
#     zonahoraria = datetime.timezone(datetime.timedelta(hours=-6))
#     preguntas = ["titulo", "descripcion", "fecha", "proyecto", "dficultad", "importancia"]

#     def __init__(self, user):
#         self.id = user
#         self.hoy = datetime.date.today()  # FECHA DE HOY QUE SE USARÁ EN EL PROGRAMA
#         self.añoh = f"{self.hoy:%Y}"       # AÑO
#         self.mesh = f"{self.hoy:%m}"       # MES
#         self.diah = f"{self.hoy:%d}"       # DÍA
#         self.pred = {"h":10, "m":20, "p":30, "l":1, "mr":2, "mi":3, "j":4, "v":5, "s":6, "d":7}  # Posibles letras para fechas predeterminadas
#         self.diasiso = [0, 1, 2, 3, 4, 5, 6]

#         self.creandoproyecto = False  # Para manejo de proyectos

#         self.añadir_objeto()
#         # Inicialmente los atributos se establecen en False para indicar que no han sido asignados
#         self.titulo = False
#         self.descripcion = False
#         self.fecha = False
#         self.semifecha = False
#         self.proyecto = False
#         self.dificultad = False
#         self.asignando = False

#         # Inicializamos las listas y diccionarios de seguimiento
#         self.atributos = [self.titulo, self.descripcion, self.fecha, self.proyecto, self.dificultad]
#         self.nombres = {
#             "el titulo": self.titulo,
#             "la descripcion": self.descripcion,
#             "la fecha": self.fecha,
#             "el proyecto": self.proyecto,
#             "la dificultad": self.dificultad
#         }
#         self.funcionesPorAtributo = {
#             self.titular: self.titulo,
#             self.describir: self.descripcion,
#             self.fechar: self.fecha,
#             self.proyectar: self.proyecto,
#             self.dificultadear: self.dificultad
#         }

#     def _actualizar_diccionarios(self):
#         """Actualiza las listas y diccionarios que reflejan el estado actual de la tarea."""
#         self.atributos = [self.titulo, self.descripcion, self.fecha, self.proyecto, self.dificultad]
#         self.nombres = {
#             "el titulo": self.titulo,
#             "la descripcion": self.descripcion,
#             "la fecha": self.fecha,
#             "el proyecto": self.proyecto,
#             "la dificultad": self.dificultad
#         }
#         self.funcionesPorAtributo = {
#             self.titular: self.titulo,
#             self.describir: self.descripcion,
#             self.fechar: self.fecha,
#             self.proyectar: self.proyecto,
#             self.dificultadear: self.dificultad
#         }

#     @classmethod
#     def tareaporid(cls, id):
#         for tarea in cls.listadeobjetos:
#             if tarea.id == id:
#                 return tarea

#     def titular(self, titulo):
#         print("asignando titulo")
#         if titulo == "mi salchicha":
#             self.titulo = "mi salchicha"
#             self._actualizar_diccionarios()
#             return True, "codigo secreto 'mi salchicha'"
#         self.titulo = titulo
#         print("titulo asignado")
#         self.asignando = False
#         print("dejando de asignar")
#         self._actualizar_diccionarios()
#         return True, False
    
#     def describir(self, valor):
#         print("asignando descripcion")
#         self.descripcion = valor  # Asigna dato
#         self.asignando = False  # Deja de asignar
#         print("descripcion asignada")
#         self._actualizar_diccionarios()
#         return True, False  # Retorna estado y posible mensaje
    
#     def porpred(self, diaisoE):
#         # ASIGNAR FECHA POR VALORES PREDETERMINADOS
#         fechafeultimasemana = datetime.date(int(self.añoh), 12, 31)
#         try:
#             datetime.date.fromisocalendar(int(self.añoh), 53, 7)
#             semisof = 53
#         except ValueError:
#             semisof = 52
#         añoisof = int(self.añoh)
#         diaisof = 7
        
#         ultimafechadesemanacompleta = datetime.date.fromisocalendar(añoisof, semisof, diaisof)
#         añoisoh, semisoh, disoh = self.hoy.isocalendar()
        
#         if diaisoE // 10 in [1, 2, 3]:
#             diaisoE = disoh + (diaisoE // 10) - 1
#             if diaisoE > 7:
#                 diaisoE = diaisoE - 7
#                 semisoE = semisoh + 1
#             else:
#                 semisoE = semisoh
#         elif diaisoE == disoh or diaisoE < disoh:
#             semisoE = semisoh + 1
#         else:
#             semisoE = semisoh

#         if semisoE > semisof:
#             añoisoE = añoisoh + 1
#             semisoE = 1
#         else:
#             añoisoE = añoisoh

#         FechaDeE = datetime.date.fromisocalendar(añoisoE, semisoE, diaisoE)
#         return True, FechaDeE

#     def formatoutil(self, fecha):
#         # Convierte la fecha a string y agrega un 0 si es de un solo caracter
#         fecha = str(fecha)
#         if len(fecha) == 1:
#             nfecha = f"0{fecha}"
#         else:
#             nfecha = str(fecha)
#         return nfecha   
            
#     def comprobarfecha(self, diaor, mesor=0, añoor=0):
#         if not mesor:
#             mesor = self.mesh
#             añoor = self.añoh
#         try:
#             errores = []
#             año = False
#             mes = False
#             dia = False
#             if int(añoor) < int(self.añoh) or int(añoor) > int(self.añoh) + 2:
#                 año = True
#             if int(mesor) < 1 or int(mesor) > 12:
#                 mes = True
#             if int(diaor) < 1 or int(diaor) > 31:
#                 dia = True
#             if int(diaor) < int(self.diah) and int(mesor) <= int(self.mesh) and añoor <= self.añoh:
#                 dia = True
#                 mes = True
            
#             conj = {"año": año, "mes": mes, "dia": dia} 
#             for e in conj.values():
#                 if e:
#                     raise ValueError
#             datetime.date.fromisoformat(f"{añoor}-{mesor}-{diaor}")
#         except ValueError:
#             conj = {"año": año, "mes": mes, "dia": dia} 
#             for d, e in conj.items():
#                 if e:
#                     errores.append(d)
#             if len(errores):
#                 return False, errores
#             else:
#                 return False, "La fecha ingresada no puede ser aceptada"
#         return True, False

#     def crearFechaDeEntrega(self, fechaE: str):
#         print("creando fecha")
#         print(fechaE)
#         if len(fechaE) == 2 or len(fechaE) == 1:
#             fechaE = fechaE.lower()
#             if fechaE in self.pred.keys():
#                 return self.porpred(self.pred[fechaE])
#             else:
#                 diaE = self.formatoutil(fechaE)
#                 if diaE < self.diah:
#                     mesE = int(self.mesh) + 1
#                     if mesE == 13:
#                         añoE = int(self.añoh) + 1
#                         mesE = 1
#                         mesE = self.formatoutil(mesE)
#                         añoE = self.formatoutil(añoh)
#                     else:
#                         mesE = self.formatoutil(mesE)
#                         añoE = self.añoh
#                 else:
#                     mesE = self.mesh
#                     añoE = self.añoh
#                 evFecha = self.comprobarfecha(diaE, mesE, añoE)
#         elif len(fechaE) == 5 and "/" in fechaE:
#             diaE = fechaE[0:2]
#             mesE = fechaE[3:5]
#             añoE = self.añoh
#             evFecha = self.comprobarfecha(diaE, mesE, añoE)
#         elif len(fechaE) == 10 and "/" in fechaE:
#             diaE = fechaE[0:2]
#             mesE = fechaE[3:5]
#             añoE = fechaE[6:]
#             evFecha = self.comprobarfecha(diaE, mesE, añoE)
#         else:
#             return False, "formato de fecha incorrecto usa h para hoy, m para mañana, p para pasado mañana, l para lunes, mr para martes, mi para miercoles, j para jueves, v para viernes, s para sabado, d para domingo o dd/mm o dd/mm/aaaa"

#         if not evFecha[0]:
#             return evFecha
        
#         fechaDeEntrega = datetime.date.fromisoformat(f"{añoE}-{mesE}-{diaE}")
#         return True, fechaDeEntrega

#     def fechar(self, fecha):
#         print("asignando fecha")
#         if not self.semifecha:
#             print("no hay fecha, creando fecha a partir del texto")
#             Parcial = self.crearFechaDeEntrega(fecha)
#             if Parcial[0]:
#                 self.semifecha = Parcial[1]
#                 print("fecha asignada")
#                 self._actualizar_diccionarios()
#                 return True, False
#             else:
#                 print("error en la fecha, dejando de asignar")
#                 self.asignando = False
#                 if isinstance(Parcial[1], list):
#                     Parcial = list(Parcial)
#                     Parcial[1] = f"Existe un error en los siguientes datos: " + " ".join(Parcial[1])
#                     self._actualizar_diccionarios()
#                     return Parcial
#                 else:
#                     self._actualizar_diccionarios()
#                     return Parcial
#         else:
#             print("Asignando hora")    
#             comp = comprobar_hora(fecha)
#             if comp[0]:
#                 print("hora aprovada, asignando fecha completa y dejando de asignar")
#                 self.fecha = datetime.datetime.combine(self.semifecha, comp[0])
#                 self.asignando = False
#                 self._actualizar_diccionarios()
#                 return True, False
#             else:
#                 print("error en la hora, dejando de asignar")
#                 self.asignando = False
#                 self._actualizar_diccionarios()
#                 return comp


#     def proyectar(self, proyecto=False):
#         print("asignando proyecto")
#         persona: Personas = Personas.porid(self.id)
#         if not proyecto and len(persona.listaproyectos) == 0:
#             self._actualizar_diccionarios()
#             return True, False
#         elif not proyecto:
#             self._actualizar_diccionarios()
#             return "proyecto", list(persona.listaproyectos.keys())

#         if self.creandoproyecto == proyecto:
#             print("Nombre del proyecto confirmado, agregando proyecto")
#             l = proyectos(proyecto, self.id)
#             nomb = proyectos.por_nombre(proyecto)
#             if nomb:
#                 self.proyecto = nomb
#             else:
#                 self.creandoproyecto = False
#                 self.asignando = False
#                 self._actualizar_diccionarios()
#                 return False, "Hubo un error, llama al desarrollador inmediatamente"
#             self.creandoproyecto = False
#             self.asignando = False
        
#         elif proyecto in persona.listaproyectos.keys():
#             print("proyecto seleccionada")
#             self.proyecto = persona.listaproyectos[proyecto]
#         else:
#             self.creandoproyecto = proyecto
#             self._actualizar_diccionarios()
#             return False, f"El proyecto '{proyecto}' no existe, si kieres crearla ingresa el nombre de nuevo, si no selecciona un proyecto valido:\n" + "\n".join(proyectos.nombres())
        
#         print("proyecto asignado")
#         self.asignando = False
#         self._actualizar_diccionarios()
#         return True, False

#     def dificultadear(self, dificultad):
#         print("asignando dificultad")
#         try: 
#             Dif = int(dificultad)
#             if Dif not in range(1, 41):
#                 raise ValueError
#         except ValueError:
#             print("error en la dificultad, dejando de asignar")
#             self._actualizar_diccionarios()
#             return False, "La dificultas debe estar expresada en horas del 1 al 40"

#         self.dificultad = Dif
#         self.asignando = False
#         print("dificultad asignada")
#         self._actualizar_diccionarios()
#         return True, False     
      
#     def funcionTareaCompleta(self):
#         print("actualizando listas y diccionarios de la tarea")
#         self._actualizar_diccionarios()
#         for n, a in self.nombres.items():
#             if not a:
#                 print(n, "no esta asignado, asigando ahora")
#                 self.asignando = True
#                 if a == self.fecha and self.semifecha:
#                     print("El atributo actual es la hora de entrega")
#                     return f"Ingresa la hora de entrega", False
                
#                 if a == self.proyecto:
#                     proyectos_list = Personas.porid(self.id).consultar_lista_proyectos()
#                     if len(proyectos_list) == 0:
#                         return "materia", False
#                     else:
#                         return "materia", list(proyectos_list.keys())
                     
#                 return f"Ingresa {n}", False
#         print("Agregando la tarea a la lista de tareas de la persona")    
#         persona: Personas = Personas.porid(self.id)
#         persona.agregarTarea(self)
#         Tarea.listadeobjetos.remove(self)
#         return False, False

#     def directorio(self, valor):
#         print("actualizando listas y diccionarios de la tarea")
#         self._actualizar_diccionarios()
#         print("llamando a la funcion correspondiente")
#         for f, atributo in self.funcionesPorAtributo.items():
#             if not atributo:
#                 return f(valor)


def main():
    print(crear_fecha_de_entrega("m"))
if __name__ == '__main__':

    main()