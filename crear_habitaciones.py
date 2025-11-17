import json
import random

#Realiza la lectura de la informacion del json de habitaciones y sensores
with open("sensores_habitaciones.json", "r") as archivo:
    datos = json.load(archivo)

#Variable para la longitud del array de id_habitaciones del json
longitud = len(datos["habitaciones"]["id_habitacion"])

#Verificación de la respuesta del usuario
terminado = False
while not terminado:
    #Solicita al usuario de la correspondiente información
    resultado = input("¿Deseas añadir una habitación con sus correspondientes sensores? (Si o No)")
    resultado = str(resultado)
    if resultado == "Si":
        id = longitud + 1
        #insercción de ids en el json de sensores y habitaciones
        datos["habitaciones"]["id_habitacion"].append(id)
        datos["sensores"]["id_sensor"].append(id)
        estado = False
        while not estado:
            #Solicita al usuario de la correspondiente información
            respuesta = input("¿Cual quieres que sea el estado de la habitación? (libre o ocupado)")
            respuesta = str(respuesta)
            #Insercción del estado de la habitacion en el json de sensores y habitación
            if respuesta == "libre":
                datos["habitaciones"]["estado"].append("libre")
                estado = True
            if respuesta == "ocupado":
                datos["habitaciones"]["estado"].append("ocupado")
                estado = True
        #Insercción del resto de datos en el json de sensores y habitación
        datos["sensores"]["temperatura"].append(random.randint(20, 35))
        datos["sensores"]["humedad"].append(random.randint(30, 70))
        datos["sensores"]["calidad_aire"]["PM2.5"].append(random.randint(10, 30))
        datos["sensores"]["calidad_aire"]["PM10"].append(random.randint(20, 50))
        datos["sensores"]["calidad_aire"]["CO"].append(random.randint(0, 15))
        datos["sensores"]["calidad_aire"]["NO2"].append(random.randint(0, 50))
        datos["sensores"]["calidad_aire"]["CO2"].append(random.randint(500, 2000))
        datos["sensores"]["calidad_aire"]["TVOC"].append(random.randint(100, 800))
        #Añadir los datos al archivo
        with open("sensores_habitaciones.json", "w") as archivo:
            json.dump(datos, archivo, indent=4)
        #Mensaje de información
        print(f"Se a añadido la habitación y sensores con id {id} y con su correspondiente información.")
        terminado = True
    elif resultado == "No":
        #Mensaje de información
        print("No se ha añadido ninguna información")
        terminado = True
    else:
        #Mensaje de error
        print("Valor erroneo. Intoduzca Si o No")