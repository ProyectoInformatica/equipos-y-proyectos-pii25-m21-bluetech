import json

#Se realiza la lectura del json de habitaciones y sensores
with open("sensores_habitaciones.json", "r") as archivo:
    datos = json.load(archivo)

#Solicita al usuario el id_habitación
id_habitacion = input("Introduce el id_habitacion: ")
id_habitacion = int(id_habitacion)

#Variable para la longitud del array de id_habitaciones del json
longitud = len(datos["habitaciones"]["id_habitacion"])

#verifica que el id sea mayor que 0 y este en el array ya que van en orden
if id_habitacion <= longitud and id_habitacion > 0:
    #recorre el array de id_habitacion
    for i in range (longitud):
        #verifica que uno de ellos coincida
        if datos["habitaciones"]["id_habitacion"][i] == id_habitacion:
            #Muestra el estado actual de la sala
            data = datos["habitaciones"]["estado"][i]
            print(f"El estado actual de la sala {id_habitacion} es: {data}")
else:
    #Error al encontrar el id
    print(f"La habitación con id {id_habitacion} no existe.")