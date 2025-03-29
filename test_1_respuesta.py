import os
from dotenv import load_dotenv
import pandas as pd
from helpers.LLM_prompts import LLMs_system_prompts
from helpers.hacer_inferencia import get_LLM_response

load_dotenv()

###### Parámetros
modelo_respuesta="google/gemini-2.0-flash-thinking-exp:free"
######


APIkey=[os.getenv("LLMsAPIkey"),os.getenv("LLMsAPIkey_v2"),os.getenv("LLMsAPIkey_v3"),os.getenv("LLMsAPIkey_v4")]

script_dir = os.path.dirname(os.path.abspath(__file__)) # Path de este script
ruta_input= os.path.join(script_dir, 'Output Test Automático.xlsx') # Path del input de **este** test (output del anterior)
ruta_output= os.path.join(script_dir, 'Output Test Automático.xlsx') # Path del output del test

for niter_APIkey in range(len(APIkey)):
  APIkey_OpenRouter=APIkey[niter_APIkey]

  df=pd.read_excel(ruta_input)

  #APIkey_Groq=os.getenv("LLMsAPIkey_Groq")
  APIkey_Groq=os.getenv("LLMsAPIkey_Groq_v2")

  Respuesta_userprompt_array=df["RESPUESTA_USERPROMPT"].tolist()
  Respuesta_array=df["RESPUESTA"].tolist()

  system_prompt=LLMs_system_prompts("elaborate_responses","","")

  for k in range(len(Respuesta_userprompt_array)):
    if Respuesta_array[k]=="ERROR" or pd.isna(Respuesta_array[k]):
      user_prompt=Respuesta_userprompt_array[k]
      respuesta_LLM=get_LLM_response("OpenRouter",APIkey_OpenRouter,modelo_respuesta,user_prompt,system_prompt)
      #respuesta_LLM=get_LLM_response("Groq",APIkey_Groq,"llama-3.3-70b-versatile",user_prompt,system_prompt)
      print(respuesta_LLM)
      Respuesta_array[k]=respuesta_LLM
      if respuesta_LLM=="ERROR":
        print("Rate limit alcanzado")
        break


  df["RESPUESTA"]=Respuesta_array


  # Output del Test Automático
  df.to_excel(ruta_output,index=False)
  print(f'Archivo Excel guardado en: {ruta_output}')



