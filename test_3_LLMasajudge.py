import os
from dotenv import load_dotenv
import pandas as pd
import re
from helpers.LLM_prompts import LLMs_system_prompts
from helpers.hacer_inferencia import get_LLM_response

load_dotenv()

###### Parámetros
modelo_LLMasajudge="llama-3.3-70b-versatile"
######

script_dir = os.path.dirname(os.path.abspath(__file__)) # Path de este script
ruta_input= os.path.join(script_dir, 'Output Test Automático.xlsx') # Path del input de **este** test (output del anterior)
ruta_output= os.path.join(script_dir, 'Output Test Automático.xlsx') # Path del output del test

df=pd.read_excel(ruta_input)

APIkey_Groq=os.getenv("LLMsAPIkey_Groq")
#APIkey_Groq=os.getenv("LLMsAPIkey_Groq_v2")
#APIkey_Groq=os.getenv("LLMsAPIkey_Groq_v3")

#APIkey_OpenRouter=os.getenv("LLMsAPIkey")
APIkey_OpenRouter=os.getenv("LLMsAPIkey_v2")
#APIkey_OpenRouter=os.getenv("LLMsAPIkey_v3")
#APIkey_OpenRouter=os.getenv("LLMsAPIkey_v4")

PREGUNTA_array=df["PREGUNTA"].tolist()
RESPUESTABEST_array=df["RESPUESTA_BEST"].tolist()
Respuesta_array=df["RESPUESTA"].tolist()
LLMasajudge_array=df["LLMasajudge"].tolist()
LLMasajudge_valoracion_array=df["LLMasajudge_valoracion"].tolist()
LLMasajudge_razonamiento_array=df["LLMasajudge_razonamiento"].tolist()

system_prompt=LLMs_system_prompts("LLMasajudge","","")

contador=0
for k in range(len(Respuesta_array)):
  if LLMasajudge_valoracion_array[k]=="ERROR" or pd.isna(LLMasajudge_valoracion_array[k]):

    user_prompt=f"Pregunta:\n{PREGUNTA_array[k]}\n\nRespuesta_Best:\n{RESPUESTABEST_array[k]}\n\nRespuesta_Generada:\n{Respuesta_array[k]}"
    respuesta_LLM=get_LLM_response("Groq",APIkey_Groq,modelo_LLMasajudge,user_prompt,system_prompt)
    #respuesta_LLM=get_LLM_response("OpenRouter",APIkey_OpenRouter,modelo_LLMasajudge,user_prompt,system_prompt)
    LLMasajudge_array[k]=respuesta_LLM

    if respuesta_LLM=="ERROR":
      print("Rate limit alcanzado")
      break

    if "Valoración: OK" in respuesta_LLM:
      LLMasajudge_valoracion_array[k]="OK"
      LLMasajudge_razonamiento_array[k]=re.sub(r'Valoración: OK','',respuesta_LLM)
    elif "Valoración: KO" in respuesta_LLM:
      LLMasajudge_valoracion_array[k]="KO"
      LLMasajudge_razonamiento_array[k]=re.sub(r'Valoración: KO','',respuesta_LLM)


    contador=contador+1
    print(f"\r{contador}-{LLMasajudge_valoracion_array[k]}",end='',flush=True)


df["LLMasajudge"]=LLMasajudge_array
df["LLMasajudge_valoracion"]=LLMasajudge_valoracion_array
df["LLMasajudge_razonamiento"]=LLMasajudge_razonamiento_array

# Output del Test Automático
df.to_excel(ruta_output,index=False)
print(f'Archivo Excel guardado en: {ruta_output}')
