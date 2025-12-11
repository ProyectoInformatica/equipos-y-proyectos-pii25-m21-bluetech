#Es mucho mejor y mas visual hacerlo con Flet por lo que he mirado (este es un boceto en pyhton pero se hará en Flet)
import json

#Realiza la lectura de la informacion del json de habitaciones y sensores
with open("sensores_habitaciones.json", "r") as archivo:
    datos = json.load(archivo)

#Variable para la longitud del array de id_habitaciones del json
longitud = len(datos["habitaciones"]["id_habitacion"])

# Crear mapa. Recorre e array de ids de habitaciones para mostrar todas las habitaciones que hay
for i in range(longitud):
    #Variables que almacenan los datos correspondientes sacandolos del fichero json de habitaciones y sensores
    id_hab = datos["habitaciones"]["id_habitacion"][i]
    temperatura = datos["sensores"]["temperatura"][i]
    humedad = datos["sensores"]["humedad"][i]
    pm2 = datos["sensores"]["calidad_aire"]["PM2.5"][i]
    pm10 = datos["sensores"]["calidad_aire"]["PM10"][i]
    co = datos["sensores"]["calidad_aire"]["CO"][i]
    no2 = datos["sensores"]["calidad_aire"]["NO2"][i]
    co2 = datos["sensores"]["calidad_aire"]["CO2"][i]
    tvoc = datos["sensores"]["calidad_aire"]["TVOC"][i]

    #Imprimir todos los datos por pantalla
    print("+" + "-"*40)
    print(f"| Habitación {id_hab}")
    print(f"| Temperatura: {temperatura}°C")
    print(f"| Humedad: {humedad}%")
    print("| Calidad del aire: ")
    print(f"| \tPM2: {pm2} µg/m³")
    print(f"| \tPM10: {pm10} µg/m³")
    print(f"| \tCO: {co} ppm")
    print(f"| \tNO2: {no2} ppb")
    print(f"| \tCO2: {co2} ppm")
    print(f"| \tTVOC: {tvoc} ppb")
    print("+" + "-"*40 + "\n")