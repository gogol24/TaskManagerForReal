#!/usr/bin/env python3
import logging
import Asistencia
from telegram import Update, ReplyKeyboardMarkup,InlineKeyboardMarkup,InlineKeyboardButton,ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler,CallbackQueryHandler
import Datos
import datetime
import os
from decouple import config


BOT_TOKEN=config("BOT_TOKEN")


if not BOT_TOKEN:
    raise RuntimeError("Falta la variable TELEGRAM_TOKEN")

# Configuración del logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)


TITULO, DESCRIPCION, PROYECTO, FECHA, HORA, DIFICULTAD, SELECCIONANDOPROYECTO, CREANDOPROYECTO = range(8)

PREGUNTANDOHR, RECIBIENDOHR=range(2)

SELECCIONCOMPLETANDOTAREA=range(0)
listanombres=["Titulo","Descripcion","Proyecto","Fecha","Hora","Dificultad"]
#0,1,2,3,4
textoestado={TITULO:"Ingresa el titulo de la tarea:",
                DESCRIPCION:"Descripcion:",
                PROYECTO:"Proyecto al que pertenece:",
                FECHA:"Fecha de entrega:",
                HORA:"Hora de entrega:",
                DIFICULTAD:"Dificultad:"}

#DECORADOREEEES
def decorador_conversaciontarea(funcion):#es el decorador, es la funcion que se va a llamar para construir la nueva funcion en llugar de la funcion
        async def envoltura(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:#Una funcion que hace algo extra

            user_id = context._user_id
            
            f=await funcion(update,context)#si se tiene que entrar a un estado  como seleccionar un pryecto o crearlo
            if f:#devolver el estado correspondiente, eso es por si uno de los estados de la conversacion tiene kue devolver otro estado kue no esta contemplado dentro de los estados para crear la tarea,por ejemplo un estado para crear un proyetco
                return f#se devuelve el estado para crear el proyetco provocando kue la siguiente update entre en ese estado 
            
            data=context.user_data["tarea"]
            print(f"Se llamo a una funcion de estados, {data}")
            progreso=(f"{data[0]} \n" if data[0] else f"Nueva tarea \n") +"\n".join(f"{listanombres[atributo]}: {data[atributo]}" if  data[atributo] and atributo!=0 else f"{listanombres[atributo]}: '' ''" for atributo in list(data.keys())[1:])
            await context.bot.send_message(chat_id=user_id,text=progreso)


            accion=siguiente_tareass(context.user_data["tarea"],context)
            if accion==ConversationHandler.END:
                Asistencia.crear_y_agregar_tarea_a_persona(context.user_data["tarea"],user_id)

                print(Datos.obtener_persona(user_id).consultar_lista_proyectos())
                context.user_data["tarea"]=False

                await context.bot.send_message(chat_id=user_id,text="Tarea creada")
                if context.user_data["RecordatorioDiario"]=="R":
                    await context.bot.send_message(chat_id=user_id,text="No tienes un recordatorio diario para tus tareas")
                    teclado=[[InlineKeyboardButton ("Si",callback_data="tareaRSi")],[InlineKeyboardButton("No",callback_data="tareaRNo")],[InlineKeyboardButton("Recuerdame más tarde",callback_data="tareaRTarde")]]
                    inlinerecordatorio=InlineKeyboardMarkup(teclado)
                    await context.bot.send_message(chat_id=user_id,
                                                   text="Deseas agregarlo?",
                                                   reply_markup=inlinerecordatorio)

                    sustetas=[["/Rdiario (Si)","No","recuerdame más tarde"]]
                    await context.bot.send_message(chat_id=user_id,text="O selecciona del teclado:",
                    reply_markup=ReplyKeyboardMarkup(sustetas, one_time_keyboard=True, resize_keyboard=True)
                )
                context.user_data["CreandoTareaR"]=True
                return accion
            
            print(f"se esta preguntando por {accion[0]}")
            await context.bot.send_message(chat_id=user_id,text=accion[0]) if accion[0] else None

            print(accion)
            await accion[1](update,context) if accion[1] else None

            #si no hay algo especial kue llamar, llamemos al siguiente estado
            return accion[2]#esta nueva funcion devuelve el nuevo estado a determinar, en base a si se asigno o no el atributo

        return envoltura #es la neuva funcion 



def decorador_started(funcion):
    async def envoltura(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        if context.user_data is None:
            data=context.job.data["contextogenerico"].user_data
        else:
            data=context.user_data

        if not data.get("init",False):
            await start(update,context)
        return await funcion(update,context)
    return envoltura



#PRINCIPALES HANDLERS
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:

    if not update:
            user_id=context._user_id  
    else:
        user_id = update.message.from_user.id
        if not user_id:
            user_id=update.callback_query.from_user.id

    usuario=Asistencia.Personas(user_id)
    Datos.agregar_persona(user_id,usuario)
    context.user_data["tarea"]=False
    context.user_data["RecordatorioDiario"]="R"
    context.user_data["init"]=True



@decorador_started
async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:

    if update.message and update.message.text:
        await update.message.reply_text(update.message.text)



@decorador_started
async def consulta_tareas(update:Update,context:ContextTypes.DEFAULT_TYPE): 
    print("haciendo consutlta")
    user_id=context._user_id
    if not user_id:
        user_id=context.job.chat_id

    consulta:dict=Asistencia.consulta_tareas(user_id)

    if len(consulta)==0:
        await context.bot.send_message(chat_id=user_id,text="sin tareas ... por ahora")
        return

    await context.bot.send_message(chat_id=user_id,text="ola mamabicho estas son tus tareas")
    n=1
    for tarea,datos in consulta.items():
        await context.bot.send_message(chat_id=user_id,text=(f"Tarea {n}\n")+"\n".join(f"{listanombres[clave]}: {valor}"for clave,valor in datos.items()))
        n+=1



@decorador_started
@decorador_conversaciontarea  
async def start_tarea(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    
    user_id = update.message.from_user.id
    #POR AHORA VAMOS A CREAR LA PERSONA PERO DEBERIAMOS FIJARNOS SI EXISTE NE LA CASE DE DATOS Y CARGAR SUS DATOS, ESTO ES POR SI SE APAGA EL BOT
    if context.user_data["tarea"]:
        await update.message.reply_text("Ya estas creando una tarea")

    else:
        context.user_data["tarea"]={TITULO:False,HORA:False,PROYECTO:False}
        data=context.user_data["tarea"]
        await update.message.reply_text(
            "Iniciando creación de tarea.",
            parse_mode="Markdown")
    

@decorador_started
async def completar_tarea(update:Update,context:ContextTypes.DEFAULT_TYPE):
    user_id=update.message.from_user.id
    persona:Asistencia.Personas=Datos.obtener_persona(user_id)
    tareas=persona.consultar_lista_tareas()

    await context.bot.send_message(chat_id=user_id,text="Primera fasse completada")
    if not len(tareas):
        await update.message.reply_text("No tienes tareas, yei")
        return

    keyboard = [
        [InlineKeyboardButton(t.titulo, callback_data=f"tarea_{t.id}")] for t in tareas
    ]#si los titulos de las tareas son iguales añadir otra caracteristica, kue las diferencie

    reply_markup = InlineKeyboardMarkup(keyboard)    
    
    if context.args:
        await update.message.reply_text("Argumento")
        #ninhguna tarea con el nombre tal, te referias a tal?
        
    else:
        pass
        
    
async def eliminar_tarea(update:Update,context:ContextTypes.DEFAULT_TYPE):
    pass



#HANDLERS SECUNDARIOS


#FUNCIONES

async def preguntar(update: Update,context:ContextTypes.DEFAULT_TYPE):
    print("ojoooo")
    return await asignar_fecha_recordatorio_diario(update,context)

async def mensaje_diario (context: ContextTypes.DEFAULT_TYPE):
    await consulta_tareas(False,context)



#   TAREA
def siguiente_tareass(estados_tarea,context=None):
        global funcionesestado
        for atributo,estado in estados_tarea.items():
            if not estado:
                return textoestado[atributo],funcionesestado.get(atributo,False),atributo
        return ConversationHandler.END



#FUNCIONES DE ESTADOS DE TAREA
@decorador_conversaciontarea      
async def titulo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    
    titulo,detalle=Asistencia.validar_titulo_valor(update.message.text)
    data=context.user_data["tarea"]
    if titulo:
        context.user_data["tarea"][TITULO] = update.message.text
        await update.message.reply_text(detalle) if detalle is not None else await update.message.reply_text("Titulo asignado")
    else:
        await update.message.reply_text(detalle) if detalle is not None else await update.message.reply_text("Como hiciste para obtener un titulo invalido cabron")
    


@decorador_conversaciontarea
async def descripcion_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    
    user_id = update.message.from_user.id

    data=context.user_data["tarea"]
    Descripcion,detalle=Asistencia.validar_descripcion_valor(update.message.text)
    if Descripcion:
        context.user_data["tarea"][DESCRIPCION] = update.message.text
        await update.message.reply_text(detalle) if detalle is not None else await update.message.reply_text("Descripcion asignada")
    else:
        await update.message.reply_text("Descripcion invalida, por favor intenta de nuevo")
        return



async def proyecto_starter(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

    user_id = context._user_id

    # obtener la persona y sus proyetcos 
    
    proyectos=Asistencia.consultar_proyectos(user_id)

    #respuesta con opciones
    #MOSTRAR KEYBOARD CON PROYECTOS O LA OPCIOND EC REAR UNO
    keyboardproyectos=[]
    for nombre_proyecto in proyectos.keys():
        keyboardproyectos.append([InlineKeyboardButton(nombre_proyecto,callback_data=f"PR{nombre_proyecto}")])
    keyboardproyectos.append([InlineKeyboardButton("Crear nuevo proyecto", callback_data="PRcrear")])
    replyamarkup=InlineKeyboardMarkup(keyboardproyectos)

    #respesta con teclado
    listaproyectos=list(proyectos.keys())
    listaproyectos.append("Crear nuevo proyecto")
    reply_keyboard=[listaproyectos]


    await update.message.reply_text("Selecciona un proyecto ",reply_markup=replyamarkup)
    await update.message.reply_text(
        "O selecciona del teclado",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True)
    )
    # await update.message.reply_text("Por último, ingresa la *dificultad* (un número entre 1 y 40).")
    return
    #KERBOARD CON SI O NO
    #context.user_data["tarea"][PROYECTO] = update.message.text



@decorador_conversaciontarea
async def proyecto_handler_por_boton(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Maneja la respuesta del usuario al pulsar alguno de los botones inline.
    Si se pulsa "Crear nuevo proyecto", se cambia el estado para solicitar el nombre.
    Si se pulsa un proyecto existente, se guarda y se finaliza la conversación.
    """
    print("Estamos en el manejadore de proyectos, el proyecto ya se inicio ")

    user_id=update.callback_query.from_user.id
    query = update.callback_query
    await query.answer()  # Responde al callback para quitar la rueda de carga
    seleccion = query.data[2:]
    
    if seleccion == "crear":
        # Se solicita el nombre del nuevo proyecto.
        await query.edit_message_text(f"Se selecciono '{seleccion}'")
        await context.bot.send_message(chat_id=user_id,text="Ingresa el nombre del nuevo proyecto", reply_markup=ReplyKeyboardRemove())
        return CREANDOPROYECTO
    else:
        proyectos=Asistencia.consultar_proyectos(user_id)
        if seleccion in proyectos.keys():
            context.user_data["tarea"][PROYECTO] = proyectos[seleccion]
            await query.edit_message_text(f"Has seleccionado el proyecto: {seleccion}")
            
        else:
            await query.edit_message_text("Opción no válida, inténtalo de nuevo.")
            return 



@decorador_conversaciontarea
async def proyecto_handler_por_texto(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Maneja la respuesta del usuario al pulsar alguno de los botones inline.
    Si se pulsa "Crear nuevo proyecto", se cambia el estado para solicitar el nombre.
    Si se pulsa un proyecto existente, se guarda y se finaliza la conversación.
    """
    print("Estamos en el manejadore de proyectos, el proyecto ya se inicio ")

    user_id=context._user_id
    seleccion = update.message.text.strip()
    proyectos=Asistencia.consultar_proyectos(user_id)

    if seleccion == "Crear nuevo proyecto":
        # Se activará el modo de creación de proyecto
        await update.message.reply_text(
            "Iniciando creación de nuevo proyecto.\n\nPor favor, ingresa el nombre del nuevo proyecto:",
            reply_markup=ReplyKeyboardRemove()
        )
        return CREANDOPROYECTO
    
    elif seleccion in proyectos.keys():
        # Se guarda el proyecto seleccionado
        context.user_data["tarea"][PROYECTO] = proyectos[seleccion]
        await update.message.reply_text(
            f"Has seleccionado el proyecto: '{seleccion}'",
            reply_markup=ReplyKeyboardRemove()
        )
        return 
    else:
        await update.message.reply_text("Opción inválida, por favor selecciona un proyecto del menú.")
        return 



@decorador_conversaciontarea
async def crear_proyecto(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Crea un nuevo proyecto a partir del nombre ingresado por el usuario, lo guarda
    y lo marca como seleccionado.
    """
    user_id = update.message.from_user.id
    proyecto,detalle=Asistencia.validar_proyecto_valor(update.message.text,user_id)
    # Asignamos un nuevo id de manera sencilla.
    if proyecto:
        Datos.obtener_persona(user_id).agregar_proyecto(proyecto)
        context.user_data["tarea"][PROYECTO]=proyecto
        await update.message.reply_text(
            f"Nuevo proyecto '{proyecto.nombre}' creado y seleccionado.",
            reply_markup=ReplyKeyboardRemove()
        )
        return
    
    else:
        await update.message.reply_text(detalle)
        return CREANDOPROYECTO



# Estado para capturar la fecha
@decorador_conversaciontarea
async def fecha_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    fecha,detalle=Asistencia.crear_fecha_de_entrega(update.message.text)
    if fecha:
        context.user_data["tarea"][FECHA] = fecha
    else:
        await update.message.reply_text(detalle)
        return



@decorador_conversaciontarea
async def hora_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    tiempo,detalle=Asistencia.validar_hora(update.message.text)    
    if tiempo:
        context.user_data["tarea"][HORA] = update.message.text
    else:
        await update.message.reply_text(detalle)



@decorador_conversaciontarea
async def dificultad_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["tarea"][DIFICULTAD] = update.message.text
    tarea = context.user_data["tarea"]
    # resumen = (
    #     "Tarea creada:\n"
    #     f"• Título: {tarea.get('titulo')}\n"
    #     f"• Descripción: {tarea.get('descripcion')}\n"
    #     f"• Fecha: {tarea.get('fecha')}\n"
    #     f"• Proyecto: {tarea.get('proyecto')}\n"
    #     f"• Dificultad: {tarea.get('dificultad')}"
    # )
    # await update.message.reply_text(resumen)



funcionesestado={PROYECTO:proyecto_starter}


#FUNCIONES DE ESTADOS DE RECORDATORIO DIARIO

#ENTRY
#setermina si se asiganra unr ecordatorio diario a partir del callback del boton
async def determinar_recordatorio_diario(update: Update, context: ContextTypes.DEFAULT_TYPE):
    modo_callback=False
    if update.callback_query:
        modo_callback=True
    if modo_callback:
        user_id=update.callback_query.from_user.id
        query = update.callback_query
        await query.answer()  # Responde al callback para quitar la rueda de carga
        seleccion = query.data[6:]
    else:
        user_id=context._user_id
        seleccion=update.message.text
 
    if seleccion=="Si":
        if modo_callback:
            await update.callback_query.edit_message_text(f"Se selecciono '{seleccion}'")
            await context.bot.send_message(chat_id=user_id,text="Comenzando creacio de recordatorio diario")

        return await asignar_fecha_recordatorio_diario(update,context)

    elif seleccion=="No":
        context.user_data["RecordatorioDiario"]=False
        if modo_callback:
            await update.callback_query.edit_message_text(f"Se selecciono '{seleccion}' ")
        await context.bot.send_message(chat_id=user_id,text="De acuerdo, si kuieres accitvarlo usa /Rdiario")

    else:
        if modo_callback:
            await update.callback_query.edit_message_text(f"Se selecciono '{seleccion}'")
        await context.bot.send_message(chat_id=user_id,text="Okey")

#  ENTRY PREGUNTANDOHR  

@decorador_started
async def asignar_fecha_recordatorio_diario(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=context._user_id,text="Ingresa la hora, en formado 24 horas, HH o HH:MM Ej. 22, 10:00, 09:12, 06",reply_markup=ReplyKeyboardRemove())
    return RECIBIENDOHR



#   RECIBIENDOHR
async def evaluar_recordatorio_diario(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id=context._user_id

    tiempo,detalle=Asistencia.validar_hora(update.message.text)
    if tiempo:

        #HOARA MEXICO A UTC
        horaajustada=tiempo.hour+6 if tiempo.hour+6<24 else tiempo.hour-18

        tiempo=datetime.time(hour=horaajustada,minute=tiempo.minute)
        context.user_data["RecordatorioDiario"]=tiempo
        job_name = f"{user_id}_daily_message"
        current_jobs = context.job_queue.get_jobs_by_name(job_name)
        for job in current_jobs:
            job.schedule_removal()

        # Programar el nuevo mensaje diario
        context.job_queue.run_daily(
        mensaje_diario,
        time=context.user_data["RecordatorioDiario"],
        chat_id=user_id,
        name=job_name,
        data={"contextogenerico":context}
    )

        await update.message.reply_text(f"Tu mensaje diario se enviará a las {tiempo.strftime('%H:%M')}")
        context.user_data["CreandoTareaR"]=False
        return ConversationHandler.END
    else:
        await update.message.reply_text(f"{detalle}, vuelve a intentarlo")
        return RECIBIENDOHR



async def cancel(update,context):
    print("m")



def main() -> None:

    # Crear la aplicación con el token de tu bot
    application = Application.builder().token(BOT_TOKEN).get_updates_connect_timeout(120).get_updates_read_timeout(120).get_updates_write_timeout(120).get_updates_pool_timeout(120).pool_timeout(120).read_timeout(120).write_timeout(120).connect_timeout(120).build()
    
    # Añadir el handler para /start
    application.add_handler(CommandHandler("start", start))
    # Añadir el handler para el comando /tarea

    conversacion_tarea = ConversationHandler(
    entry_points=[CommandHandler("tarea", start_tarea)],
    states={
        TITULO: [MessageHandler(filters.TEXT & ~filters.COMMAND, titulo_handler)],
        DESCRIPCION: [MessageHandler(filters.TEXT & ~filters.COMMAND, descripcion_handler)],
        PROYECTO: [MessageHandler(filters.TEXT & ~filters.COMMAND, proyecto_handler_por_texto),
                   CallbackQueryHandler(proyecto_handler_por_boton)],
        FECHA: [MessageHandler(filters.TEXT & ~filters.COMMAND, fecha_handler)],
        HORA: [MessageHandler(filters.TEXT & ~filters.COMMAND, hora_handler)],
        DIFICULTAD: [MessageHandler(filters.TEXT & ~filters.COMMAND, dificultad_handler)],
        CREANDOPROYECTO:[MessageHandler(filters.TEXT & ~filters.COMMAND, crear_proyecto)]
    },
    fallbacks=[CommandHandler("cancelar", cancel)],
    )


    conversacion_recordatorios_diarios = ConversationHandler(
    entry_points=[CommandHandler("Rdiario", asignar_fecha_recordatorio_diario),
                  CallbackQueryHandler(determinar_recordatorio_diario,pattern=r"^tareaR")],
    states={
        PREGUNTANDOHR:[MessageHandler(filters.TEXT & ~filters.COMMAND, asignar_fecha_recordatorio_diario)],
        RECIBIENDOHR:[MessageHandler(filters.TEXT & ~filters.COMMAND, evaluar_recordatorio_diario)]
    },
    fallbacks=[CommandHandler("cancelar", cancel)]
    )
    
    

    application.add_handler(conversacion_tarea)
    application.add_handler(conversacion_recordatorios_diarios) 
    
    application.add_handler(CommandHandler("consultar_tareas", consulta_tareas))
    application.add_handler(CommandHandler("completar_tarea", completar_tarea))
    # Añadir el handler para mensajes de texto (excluyendo comandos)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

   

    # Iniciar el bot en modo polling
    application.run_polling()

if __name__ == '__main__':

    main()
