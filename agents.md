# agents.md

Guía breve para agentes que trabajen en este repositorio.

## 1. Qué es este proyecto

Repositorio de un **chatbot RAG agéntico sobre el Cosmere** con:

- indexación local de documentos Markdown en `Base de datos_Cosmere\`
- recuperación semántica sobre embeddings serializados en `Indice\`
- generación de respuesta con `langchain-openai`
- interfaz web en Streamlit
- pipeline de evaluación automática basado en Excel

La versión de Python esperada es **3.11.11**.

## 2. Mapa rápido del repositorio

- `crear_indice.py`: reconstruye el índice vectorial.
- `hacer_inferencia.py`: prueba rápida por terminal.
- `inferencia_interfaz.py`: puente entre la UI y el orquestador.
- `interfaz.py`: app Streamlit.
- `helpers\crear_indice.py`: chunking, embeddings y serialización.
- `helpers\hacer_inferencia.py`: retrieval, cliente LLM y utilidades.
- `helpers\agentic_chatbot_orchestrator.py`: flujo agéntico con tool calling.
- `helpers\chat_memory.py`: historial reciente y resumen conversacional.
- `GS_0_retrieval.py` a `GS_3_LLMasajudge.py`: evaluación incremental.

## 3. Contratos que no conviene romper

1. `helpers\agentic_chatbot_orchestrator.py::generate_agentic_chatbot_response(...)` debe seguir devolviendo un `dict` con estas claves:
   - `assistant_content`
   - `assistant_display_content`
   - `conversation_summary`
2. Las referencias documentales se manejan en formato `[[Referencia]]` y luego `interfaz.py` / el orquestador las transforman en enlaces visibles.
3. El índice local esperado está en `Indice\` con estos ficheros:
   - `chunks_with_ids.pkl`
   - `embeddings.pkl`
   - `model.pkl`
4. `search_knowledge_base_tool(query: str)` es la tool que el agente usa para consultar la base; si cambias su salida, revisa el flujo completo del orquestador.
5. Los tests de evaluación esperan archivos Excel concretos:
   - entrada inicial: `Input Test Automático.xlsx`
   - salida encadenada: `Output Test Automático.xlsx`

## 4. Variables de entorno

Crear `.env` en la raíz con:

```env
AZURE_OPENAI_ENDPOINT=...
AZURE_OPENAI_API_KEY=...
```

No hardcodear secretos ni rutas personales.

## 5. Comandos de trabajo

Instalación:

```powershell
pip install -r requirements.txt
```

Reconstruir índice:

```powershell
python crear_indice.py
```

Inferencia rápida:

```powershell
python hacer_inferencia.py
```

Levantar interfaz:

```powershell
streamlit run interfaz.py
```

Pipeline de evaluación:

```powershell
python GS_0_retrieval.py
python GS_1_respuesta.py
python GS_2_fuentes.py
python GS_3_LLMasajudge.py
```

## 6. Cómo tocar el código sin romper el proyecto

- Si cambias lógica de chunking, embeddings o carga de datos, asume que hay que **regenerar `Indice\`**.
- Si cambias el formato de respuesta del orquestador, revisa `inferencia_interfaz.py` e `interfaz.py`.
- Si cambias retrieval o citación, revisa también `GS_0_retrieval.py` y `GS_2_fuentes.py`.
- Si cambias prompts o decisiones del agente, mira `helpers\LLM_prompts.py` y el límite de iteraciones del orquestador.
- Mantén los mensajes, variables y nombres en español cuando el código ya siga ese patrón.

## 7. Convenciones útiles

- Preferir cambios pequeños y trazables.
- No editar manualmente los `.pkl` de `Indice\`; regenerarlos.
- No subir `.env`, claves ni artefactos temporales.
- No asumir que la evaluación automática funciona sin el Excel de entrada.
- Si trabajas en Windows, ejecuta los comandos desde la raíz del repo para evitar problemas de rutas relativas.

## 8. Orden recomendado de diagnóstico

1. Verificar que existe `Indice\`.
2. Verificar `.env`.
3. Probar `python hacer_inferencia.py`.
4. Probar `streamlit run interfaz.py`.
5. Ejecutar el bloque de tests que corresponda al área modificada.

## 9. Qué debe incluir una buena modificación

- mantener el flujo: pregunta -> retrieval -> respuesta -> referencias -> renderizado
- respetar el contrato del orquestador
- actualizar la documentación si cambia el modo de uso
- validar con el script o test más cercano al área tocada
