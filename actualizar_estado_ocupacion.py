import json

#Se realiza la lectura del json de habitaciones y sensores
with open("sensores_habitaciones.json", "r") as archivo:
    datos = json.load(archivo)

#Introduce el usuario el id_habitación
id_habitacion = input("Introduce el id_habitacion: ")
id_habitacion = int(id_habitacion)

#Variable para la longitud del array de id_habitaciones del json
longitud = len(datos["habitaciones"]["id_habitacion"])

#verifica que el id sea mayor que 0 y este en el array
if id_habitacion <= longitud and id_habitacion > 0:
    #recorre el array de id_habitacion
    for i in range (longitud):
        #verifica que uno de ellos coincida
        if datos["habitaciones"]["id_habitacion"][i] == id_habitacion:
            #Muestra el estado actual de la sala
            data = datos["habitaciones"]["estado"][i]
            print(f"El estado actual de la sala {id_habitacion} es: {data}")
            #En caso de estar ocupado el nuevo dato sera libre y a la inversa en caso contrario
            if data == "ocupado":
                nuevo_dato = "libre"
            else:
                nuevo_dato = "ocupado"
            fin = False
            #Se ejecuta siempre que no se cumpla la respuesta del usuario con lo solicitado
            while not fin:
                #Almacena en una variable la respuesta del usuario a la pregunta solicitada
                respuesta = input(f"¿Desea cambiar el estado a {nuevo_dato}? (Si/No)")
                respuesta = str(respuesta)
                #En caso de que la respuesta sea Si cambia el estado en caso contrario lo deja igual
                if respuesta == "Si":
                    datos["habitaciones"]["estado"][i] = nuevo_dato
                    fin = True
                elif respuesta == "No":
                    datos["habitaciones"]["estado"][i] = data
                    fin = True
                #En caso de respuesta erronea salta error y vuelve a solicitar una respuesta
                else:
                    print("La respuesta introducida es erronea, debe introducir Si o No.")
            #Sobreescribe el archivo json de habitaciones y sensores con las modificaciones correspondientes
            with open("sensores_habitaciones.json", "w") as archivo:
                json.dump(datos, archivo, indent=4)
            #Confirma que los datos se han actualizado y le vueleve a mostrar el resultado actualizado del estado
            print("Datos actualizados correctamente")
            nuevo_data = datos["habitaciones"]["estado"][i]
            print(f"El estado actual de la sala {id_habitacion} es: {nuevo_data}")
        else:
            #Error al encontrar el id
            print (f"La habitación con id {id_habitacion} no existe.")
else:
    #Error al encontrar el id
    print(f"La habitación con id {id_habitacion} no existe.")