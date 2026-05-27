import os
import pandas as pd
from unidecode import unidecode

script_dir = os.path.dirname(os.path.abspath(__file__)) # Path de este script
ruta_input= os.path.join(script_dir, 'Output Test Automático.xlsx') # Path del input de **este** test (output del anterior)
ruta_output= os.path.join(script_dir, 'Output Test Automático.xlsx') # Path del output del test

df=pd.read_excel(ruta_input)

Respuesta_array=df["RESPUESTA"].tolist()
DOCSBEST_array=df["DOCS_BEST"].tolist()
Test_fuentes_array=df["TEST_FUENTES"].tolist()

for k in range(len(Respuesta_array)):
  Test_fuentes_array[k]="KO"
  for j in DOCSBEST_array[k].split(','):
    buscar=f"[[{unidecode(j)}]]"
    #print(buscar)
    if buscar in unidecode(Respuesta_array[k]):
      Test_fuentes_array[k]="OK"
      break

df["TEST_FUENTES"]=Test_fuentes_array

# Output del Test Automático
df.to_excel(ruta_output,index=False)

