import requests
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns





## OBTENCIÓN DE LOS DATOS

response = requests.get('https://l2h237eh53.execute-api.us-east-1.amazonaws.com/dev/precios?start_date=2024-03-15&end_date=2024-04-14')

# Verificación de solicitud exitosa
if response.status_code == 200:
    datos_energia = response.json()

# Eestructura API:
# Cada fecha es la clave de un diccionario cuyo valor es un diccionario
# Los diccionarios valores de las fecha tienen como clave las horas y como valores presuntamente los valores de consumo en esa hora de ese día de energía.





## PROCESAMIENTO DE LOS DATOS

# Lista para las fechas:
lista_fechas = [] 

# Sacar lista de fechas:
lista_fechas = list(datos_energia['data'].keys()) # Toma todas las fechas y las pone en una lista
 
# Creación de dataframe para organizar la información del consumo diario de energía por hora sin las fechas:
df_precios_energia = pd.DataFrame()

# Ciclo para agregar como nuevas filas los valores por hora asociados al diccionario cuya clave es la fecha (esto puede ser una función)
for fecha in lista_fechas: # Recorre cada fecha de la lista de fechas
    
    for fechas_datos in datos_energia['data']: # Recorre cada fecha del diccionario de la información de la API
        if fecha == fechas_datos: # Compara los valores de las fechas tomados en los ciclos, si son iguales procede a operar
            df_fila_nueva_sinFecha = pd.DataFrame([datos_energia['data'][fechas_datos]]) # Dataframe de la fila de horas y sus valores/precios de energía por fecha
            
            df_fecha = pd.DataFrame([{'Fecha': fecha}]) # Dataframe de la fecha 
            
            df_fila_nueva = pd.concat([df_fecha, df_fila_nueva_sinFecha], axis=1) # Adición de la fecha como columna nueva al dataframe de las horas correspondientes
            df_precios_energia = pd.concat([df_precios_energia, df_fila_nueva], ignore_index=True) # Adición al dataframe principal de la fila completa de la fecha con sus horas y valores asociados a energía correspondientes


# Cambiar el nombre de la una columna de 24:00 a 00:00
df_precios_energia = df_precios_energia.rename(columns={'24:00': '00:00'}) # Renombra la columnas '24:00' por '00:00'

# Ordenar el dataframe: poner la columna de 00:00h al inicio:
columnas = list(df_precios_energia.columns.values) # Crea una lista de los nombre de las columnas del dataframe
columnas.insert(1, columnas[-1])  # Pone la última fila (00:00) en la segunda posición de la lista de las columnas
columnas.pop()  # Quita el último elemento de la lista porque ya está en la segunda posición
df_precios_energia = df_precios_energia[columnas] # Asigna las columnas organizadas al dataframe
print('Marco de datos con todos los datos obtenidos de la API:\n')
print(df_precios_energia,'\n')

# Exportar los datos a CSV para ver valores nulos: 
#df_precios_energia.to_csv("info_clima.csv", index=False)





## TRATAMIENTO DE DATOS FALTANTES

# Ciclo para llenar las celdas vacías de dataframe
for col in df_precios_energia: # Recorre el dataframe por columnas
    
    for precio in range(len(df_precios_energia[col])): # Recorre cada dato de la columna indicada del dataframe
        if pd.isna(df_precios_energia[col][precio]): # Se asegura de que el valor sea nulo y en caso de que sí
            df_precios_energia[col][precio] = df_precios_energia[col][precio-1] # Asinga al campo nulo el valo inmediatamente anterior en índice, por eso el -1

print('Marco de datos sin datos nulos: \n')
print(df_precios_energia,'\n') 





## CÁLCULO DE PROMEDIOS

# Calculo del promedio de precio diario:
df_copia_precios_energia = df_precios_energia.copy() # Hacer una copia del dataframe
df_copia_precios_energia = df_copia_precios_energia.drop(columns='Fecha') # Quitar la columna de la fecha del dataframe para poder sacar los promedios por fila

df_promedios_diarios = pd.DataFrame({'Precio promedio': df_copia_precios_energia.mean(axis=1)}) # Sacar los promedio de las filas (días)

df_fecha_sola = pd.DataFrame({'Fecha': lista_fechas}) # Data drame de las fechas en orden, agrega el nombre de la columna como 'Fecha'

df_promedios_precios_diario = pd.concat([df_fecha_sola, df_promedios_diarios], axis=1) # Dataframe de las fechas con sus precios promedios teniendo en cuenta las 24 horas del día
print('Precio promedio por día: \n')
print(df_promedios_precios_diario,'\n')

# Cálculo del promedio movil de 7 días
df_promedios_precios_diario['Promedio movil de 7 días'] = df_promedios_precios_diario['Precio promedio'].rolling(window=7).mean() # Adición de la columna del promedio movil de 7 días al dataframe de las fechas con sus promedios
print('Precio promedio por día con promedio móvil de 7 días: \n')
print(df_promedios_precios_diario, '\n')





## VISUALIZACIÓN

eje_x = df_promedios_precios_diario['Fecha'] # Definición del eje x como la fecha (tiempo)
eje_y1 = df_promedios_precios_diario['Precio promedio'] # Definición de una de las series del eje y como el promedio aritmético
eje_y2 = df_promedios_precios_diario['Promedio movil de 7 días'] # Definición de la serie del eje y del promedio móvil de 7 días

fig, ax = plt.subplots()
ax.plot(eje_x, eje_y1, marker = "o", label = "Promedio de precios") 
ax.plot(eje_x, eje_y2, marker = "o", label = "Promedio movil de 7 días del precio")
ax.legend()

ax.set(xlabel='Días', ylabel='Precio')
ax.set_title('Promedio aritmético y promedio móvil de 7 días de los precios diarios de energía entre 15/03/2024 y 14/04/2024', fontdict={'fontsize': 16, 'fontweight': 'bold'})
ax.grid()

fig.savefig("test.png")
plt.show()
























