personas={}
def agregar_persona(id,persona):
    global personas
    personas[id]=persona

def obtener_persona(id):
    global personas
    return personas.get(id,False)