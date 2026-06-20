#========================================================================
# LIBRARIES
#========================================================================
import requests
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from matplotlib.colors import LinearSegmentedColormap
import numpy as np
import os

#========================================================================
# GENERAL API CALL
#========================================================================
token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJCQ0NSLVNEREUiLCJzdWIiOiJhZHJpYW5icmVuZXNjckBnbWFpbC5jb20iLCJhdWQiOiJTRERFLVNpdGlvRXh0ZXJubyIsImV4cCI6MjUzNDAyMzAwODAwLCJuYmYiOjE3ODAwODEzOTMsImlhdCI6MTc4MDA4MTM5MywianRpIjoiODkyOGViNTctZDA3Ny00ZmQzLWEzNDAtNGRiNjg2OTJkZmM4IiwiZW1haWwiOiJhZHJpYW5icmVuZXNjckBnbWFpbC5jb20ifQ.avWJWJeY4Y_DhpBSxBw5vgI3Lz134U4cCKwJQ68bNX8"

headers = {
    "Authorization": f"Bearer {token}",
    "User-Agent": "Mozilla/5.0"
}

params = {
    "fechaInicio": "1900/01/01",
    "fechaFin": "2100/12/31",
    "idioma": "ES"
}

#========================================================================
# DATA DICTIONARY
#========================================================================
datos = {}

#========================================================================
# SERIES CALL
#========================================================================
# 1. Precio ponderado MONEX
url1 = (
    "https://apim.bccr.fi.cr/SDDE/api/"
    "Bccr.GE.SDDE.Publico.Indicadores.API/"
    "cuadro/219/series"
)

response1 = requests.get(
    url1,
    headers=headers,
    params=params
)

print("STATUS CUADRO 219:", response1.status_code)

data1 = response1.json()

if (
    response1.status_code == 200
    and data1["estado"] is True
    and len(data1["datos"]) > 0
):

    cuadro1 = data1["datos"][0]

    indicador1 = cuadro1["indicadores"][5]

    nombre1 = indicador1["nombreIndicador"]

    for serie in indicador1["series"]:

        fecha = serie["fecha"]

        valor = serie["valorDatoPorPeriodo"]

        if fecha not in datos:
            datos[fecha] = {}

        datos[fecha][nombre1] = valor

else:

    print("Error al importar la primera serie.")
    print(data1)

#------------------------------------------------------------------------
# 2. Cantidad MONEX
url2 = (
    "https://apim.bccr.fi.cr/SDDE/api/"
    "Bccr.GE.SDDE.Publico.Indicadores.API/"
    "cuadro/219/series"
)

response2 = requests.get(
    url2,
    headers=headers,
    params=params
)

print("STATUS CUADRO 219:", response2.status_code)

data2 = response2.json()

if (
    response2.status_code == 200
    and data2["estado"] is True
    and len(data2["datos"]) > 0
):

    cuadro2 = data2["datos"][0]

    indicador2 = cuadro2["indicadores"][10]

    nombre2 = indicador2["nombreIndicador"]

    for serie in indicador2["series"]:

        fecha = serie["fecha"]

        valor = serie["valorDatoPorPeriodo"]

        if fecha not in datos:
            datos[fecha] = {}

        datos[fecha][nombre2] = valor

else:

    print("Error al importar la segunda serie.")
    print(data2)

#========================================================================
# DATA FILTER
#========================================================================
datos_filtrados = {
    fecha: valores
    for fecha, valores in datos.items()
    if nombre1 in valores and valores[nombre1] != 0
}

#========================================================================
# DATAFRAME BUILD
#========================================================================
df = pd.DataFrame.from_dict(datos_filtrados, orient="index")

df.index = pd.to_datetime(df.index)
df = df.sort_index()

# Filter dates
df = df[df.index >= "2026-01-23"]
df = df.sort_index()

#========================================================================
# PLOT DATA
#========================================================================
x = df.index.map(pd.Timestamp.toordinal).to_numpy()
y = df["Promedio ponderado"].to_numpy()
z = df["Monto total negociado en MONEX"].to_numpy()

points = np.array([x, y]).T.reshape(-1, 1, 2)
segments = np.concatenate([points[:-1], points[1:]], axis=1)

cmap = LinearSegmentedColormap.from_list(
    "custom",
    ["white", "lightgray", "red"]
)

lc = LineCollection(segments, cmap=cmap)
lc.set_array(z[:-1])
lc.set_linewidth(2)

#========================================================================
# PLOT
#========================================================================
fig, ax = plt.subplots(figsize=(10, 5))

ax.add_collection(lc)
ax.autoscale()

#========================================================================
# X-AXIS TICKS
#========================================================================
step = max(1, len(x) // 10)

ax.set_xticks(x[::step])
ax.set_xticklabels(
    df.index.strftime("%Y-%m-%d")[::step],
    rotation=45
)

#========================================================================
# LABELS
#========================================================================
plt.title("Fuerza de precio")
plt.colorbar(lc, label="Monto total negociado en MONEX")
plt.ylabel("Promedio ponderado")
plt.xlabel("Fecha")

plt.tight_layout()

#========================================================================
# PLOT SAVE
#========================================================================
output_path = os.path.join(os.path.dirname(__file__), "fuerza_de_precio.png")
plt.savefig(output_path, dpi=150, bbox_inches="tight")

plt.close()