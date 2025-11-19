import json
import random

#Realiza la lectura de la informacion de los json de habitaciones y sensores
with open("sensores_temperatura.json", "r") as archivo:
    datos1 = json.load(archivo)
with open("sensores_humedad.json", "r") as archivo:
    datos2 = json.load(archivo)
with open("sensores_calidad_aire.json", "r") as archivo:
    datos3 = json.load(archivo)
with open("habitacion.json", "r") as archivo:
    datos4 = json.load(archivo)


#Variable para la longitud del array de id_habitaciones del json
longitud = len(datos4["habitaciones"]["id_habitacion"])

#Verificación de la respuesta del usuario
terminado = False
while not terminado:
    #Solicita al usuario de la correspondiente información
    resultado = input("¿Deseas añadir una habitación con sus correspondientes sensores? (Si o No)")
    resultado = str(resultado)
    if resultado == "Si":
        id = longitud + 1
        id_sensor = (id * 10)
        #insercción de ids en el json de sensores y habitaciones
        datos4["habitaciones"]["id_habitacion"].append(id)
        datos1["sensores_temp"]["id_sensor"].append(id_sensor+1)
        datos2["sensores_hum"]["id_sensor"].append(id_sensor+2)
        datos3["sensores_cali_aire"]["id_sensor"].append(id_sensor+3)
        estado = False
        while not estado:
            #Solicita al usuario de la correspondiente información
            respuesta = input("¿Cual quieres que sea el estado de la habitación? (libre o ocupado)")
            respuesta = str(respuesta)
            #Insercción del estado de la habitacion en el json de sensores y habitación
            if respuesta == "libre":
                datos4["habitaciones"]["estado"].append("libre")
                estado = True
            if respuesta == "ocupado":
                datos4["habitaciones"]["estado"].append("ocupado")
                estado = True
        #Insercción del resto de datos en el json de sensores y habitación
        datos1["sensores_temp"]["temperatura"].append(random.randint(20, 35))
        datos2["sensores_hum"]["humedad"].append(random.randint(30, 70))
        datos3["sensores_cali_aire"]["calidad_aire"]["PM2.5"].append(random.randint(10, 30))
        datos3["sensores_cali_aire"]["calidad_aire"]["PM10"].append(random.randint(20, 50))
        datos3["sensores_cali_aire"]["calidad_aire"]["CO"].append(random.randint(0, 15))
        datos3["sensores_cali_aire"]["calidad_aire"]["NO2"].append(random.randint(0, 50))
        datos3["sensores_cali_aire"]["calidad_aire"]["CO2"].append(random.randint(500, 2000))
        datos3["sensores_cali_aire"]["calidad_aire"]["TVOC"].append(random.randint(100, 800))
        #Añadir los datos al archivo
        with open("sensores_temperatura.json", "w") as archivo:
            json.dump(datos1, archivo, indent=4)
        with open("sensores_humedad.json", "w") as archivo:
            json.dump(datos2, archivo, indent=4)
        with open("sensores_calidad_aire.json", "w") as archivo:
            json.dump(datos3, archivo, indent=4)
        with open("habitacion.json", "w") as archivo:
            json.dump(datos4, archivo, indent=4)
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