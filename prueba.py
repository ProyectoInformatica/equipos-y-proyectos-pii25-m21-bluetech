import json

with open("sensores_habitaciones.json", "r") as archivo:
    datos = json.load(archivo)

id_habitacion = input("Introduce el id_habitacion: ")
id_habitacion = int(id_habitacion)

try:
    #Index busca el id en la lista
    indice = datos["habitaciones"]["id_habitacion"].index(id_habitacion)
    estado = input(f"Introduce el estado para la habitacion {id_habitacion}: ")
    # estado = char(estado)

    while len(datos["habitaciones"]["estado"]) <= indice:
        datos["habitaciones"]["estado"].append("")
    
    datos["habitaciones"]["estado"][indice] = estado

    with open("sensores_habitaciones.json", "w") as archivo:
        json.dump(datos, archivo, indent=4)

    print("Datos añadidos correctamente")
    print(datos["habitaciones"]["estado"][indice])

# nuevo_id_habitacion = input("Escribe el id de la habitación: ")
# nuevo_id_sensor = input("Escribe el id del sensor: ")

# nuevo_id_habitacion = int(nuevo_id_habitacion)
# nuevo_id_sensor = int(nuevo_id_sensor)

# datos["id_habitacion"].append(nuevo_id_habitacion)
# datos["id_sensor"].append(nuevo_id_sensor)

# with open("sensores_habitaciones.json", "w") as archivo:
#     json.dump(datos, archivo, indent=4)

except ValueError:
    print(f"La habitación con id {id_habitacion} no existe.")