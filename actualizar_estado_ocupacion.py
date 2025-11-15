import json

with open("sensores_habitaciones.json", "r") as archivo:
    datos = json.load(archivo)

id_habitacion = input("Introduce el id_habitacion: ")
id_habitacion = int(id_habitacion)

longitud = len(datos["habitaciones"]["id_habitacion"])

if id_habitacion <= longitud and id_habitacion > 0:
    for i in range (longitud):
        if datos["habitaciones"]["id_habitacion"][i] == id_habitacion:
            data = datos["habitaciones"]["estado"][i]
            print(f"El estado actual de la sala es: {data}")
            if data == "ocupado":
                nuevo_dato = "libre"
            else:
                nuevo_dato = "ocupado"
            fin = False
            while not fin:
                respuesta = input(f"¿Desea cambiar el estado a {nuevo_dato}? (Si/No)")
                respuesta = str(respuesta)
                if respuesta == "Si":
                    datos["habitaciones"]["estado"][i] = nuevo_dato
                    fin = True
                elif respuesta == "No":
                    datos["habitaciones"]["estado"][i] = data
                    fin = True
                else:
                    print("La respuesta introducida es erronea, debe introducir Si o No.")
            with open("sensores_habitaciones.json", "w") as archivo:
                json.dump(datos, archivo, indent=4)
            print("Datos actualizados correctamente")
            nuevo_data = datos["habitaciones"]["estado"][i]
            print(f"El estado actual de la sala es: {nuevo_data}")
else:
    print(f"La habitación con id {id_habitacion} no existe.")