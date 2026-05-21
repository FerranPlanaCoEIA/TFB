# TFB

Chatbot RAG de la Coppermind (Cosmere) con:

- Construcción de índice vectorial desde documentos Markdown.
- Recuperación semántica de chunks relevantes.
- Generación de respuesta con LLMs vía LiteLLM.
- Interfaz web en Streamlit.
- Pipeline de evaluación automática (retrieval, fuentes y LLM-as-a-judge).

> :warning: **Aviso**: Este repositorio debe ser ejecutado en Python 3.11.11. Hacerlo en otra versión podría producir fallos o errores de dependencias al instalar requirements.

## RAG General

Para acceder al RAG General, cambia a la rama `feature/general-RAG`.

## Tabla de contenidos

- [Descripción funcional](#descripción-funcional)
- [Arquitectura](#arquitectura)
- [Estructura del repositorio](#estructura-del-repositorio)
- [Requisitos](#requisitos)
- [Instalación](#instalación)
- [Configuración de entorno](#configuración-de-entorno)
- [Cómo usar el proyecto](#cómo-usar-el-proyecto)
- [Pipeline de tests y evaluación](#pipeline-de-tests-y-evaluación)
- [Detalles de implementación](#detalles-de-implementación)
- [Problemas frecuentes](#problemas-frecuentes)
- [Recursos de apoyo](#recursos-de-apoyo)

## Descripción funcional

El proyecto implementa un sistema RAG para responder preguntas sobre el Cosmere usando contenido de la Coppermind en español.

Flujo general:

1. Se procesan documentos `.md` y se dividen en chunks.
2. Se generan embeddings de esos chunks.
3. Se guarda un índice local serializado (`Indice/`).
4. Ante una pregunta, se recuperan los chunks más similares por similitud coseno.
5. Se construye un prompt con conocimiento recuperado.
6. Se consulta un LLM (OpenRouter, Groq u OpenAI vía LiteLLM).
7. Se devuelve una respuesta con referencias.

## Arquitectura

Componentes principales:

- **Indexación**: `crear_indice.py` (usa funciones en `helpers/crear_indice.py`).
- **Inferencia por script**: `hacer_inferencia.py`.
- **Inferencia para UI**: `inferencia_interfaz.py`.
- **Interfaz web**: `interfaz.py` (Streamlit).
- **Prompts del sistema**: `helpers/LLM_prompts.py`.
- **LLM client + retrieval**: `helpers/hacer_inferencia.py`.
- **Evaluación automática**: `test_0_retrieval.py`, `test_1_respuesta.py`, `test_2_fuentes.py`, `test_3_LLMasajudge.py`.

## Estructura del repositorio

```text
TFB/
├─ Base de datos_Cosmere/
│  ├─ 0_documentos_base_datos.txt
│  └─ html_to_markdown.ipynb
├─ helpers/
│  ├─ crear_indice.py
│  ├─ hacer_inferencia.py
│  └─ LLM_prompts.py
├─ Apoyo/
│  ├─ Entendiendo Ragas.ipynb
│  ├─ LiteLLM_Tutorial.ipynb
│  ├─ LLMs_free_API_keys.ipynb
│  └─ PruebasAPIOpenAI.ipynb
├─ Interfaz-Images/
├─ Documentacion/
│  ├─ Documentación TFB.pdf
│  └─ Images/
├─ crear_indice.py
├─ hacer_inferencia.py
├─ inferencia_interfaz.py
├─ interfaz.py
├─ test_0_retrieval.py
├─ test_1_respuesta.py
├─ test_2_fuentes.py
├─ test_3_LLMasajudge.py
├─ requirements.txt
├─ requirements_mac.txt
└─ freeze_GoogleColab.txt
```

## Requisitos

- Python 3.11.11
- Pip actualizado
- Acceso a APIs LLM (según proveedor elegido)

Dependencias principales (ver `requirements.txt`):

- `sentence-transformers`
- `scikit-learn`
- `numpy`
- `pandas`
- `openpyxl`
- `python-dotenv`/`dotenv`
- `requests`
- `litellm`
- `streamlit`

## Instalación

1. Clona el repositorio.
2. Crea y activa un entorno virtual con Python 3.11.11.
3. Instala dependencias:

```bash
pip install -r requirements.txt
```

Para Mac existe un listado alternativo en `requirements_mac.txt`.

## Configuración de entorno

Este proyecto usa variables de entorno para API keys. Crea un archivo `.env` en la raíz del proyecto.

Variables observadas en el código:

- `LLMsAPIkey`
- `LLMsAPIkey_v2`
- `LLMsAPIkey_v3`
- `LLMsAPIkey_v4`
- `LLMsAPIkey_v5`
- `LLMsAPIkey_v6`
- `LLMsAPIkey_v7`
- `LLMsAPIkey_Groq`
- `LLMsAPIkey_Groq_v2`
- `LLMsAPIkey_Groq_v3`
- `LLMsAPIkey_OpenAI`
- `LLMsAPIkey_OpenAI_v2`
- `LLMsAPIkey_OpenAI_v3`
- `LLMsAPIkey_OpenAI_v4`
- `LLMsAPIkey_OpenAI_v5`

Ejemplo:

```env
LLMsAPIkey=...
LLMsAPIkey_v2=...
LLMsAPIkey_v3=...
LLMsAPIkey_v4=...
LLMsAPIkey_v5=...
LLMsAPIkey_v6=...
LLMsAPIkey_v7=...

LLMsAPIkey_Groq=...
LLMsAPIkey_Groq_v2=...
LLMsAPIkey_Groq_v3=...

LLMsAPIkey_OpenAI=...
LLMsAPIkey_OpenAI_v2=...
LLMsAPIkey_OpenAI_v3=...
LLMsAPIkey_OpenAI_v4=...
LLMsAPIkey_OpenAI_v5=...
```

## Cómo usar el proyecto

### 1) Crear índice vectorial

Genera chunks + embeddings y guarda artefactos en `Indice/`.

```bash
python crear_indice.py
```

Parámetros relevantes en `crear_indice.py`:

- `chunk_size=100`
- `chunk_overlap=20`
- `model_embeddings="distiluse-base-multilingual-cased-v2"`

### 2) Inferencia por terminal (rápida)

Ejecuta una pregunta de prueba desde script.

```bash
python hacer_inferencia.py
```

Parámetros editables en `hacer_inferencia.py`:

- `question`
- `top_n`
- modelo de respuesta y proveedor

### 3) Interfaz web (Streamlit)

Lanza la app:

```bash
streamlit run interfaz.py
```

Detalles:

- Usa `inferencia_interfaz.py` para resolver preguntas.
- Carga una imagen de fondo desde `Interfaz-Images/Image1.webp`.
- Tema configurado en `.streamlit/config.toml`.

## Pipeline de tests y evaluación

El proyecto plantea una evaluación incremental usando Excel de entrada/salida.

Archivo esperado:

- `Input Test Automático.xlsx` con columnas como `PREGUNTA`, `DOCS_BEST`, `RESPUESTA_BEST`.

Secuencia recomendada:

1. Retrieval:

```bash
python test_0_retrieval.py
```

Genera/actualiza en `Output Test Automático.xlsx`:

- `RESULTADO_RAG`
- `DOCS_RAG`
- `TEST_RAG`
- `RESPUESTA_USERPROMPT`

2. Generación de respuesta:

```bash
python test_1_respuesta.py
```

Actualiza columna:

- `RESPUESTA`

3. Validación de fuentes citadas:

```bash
python test_2_fuentes.py
```

Actualiza columna:

- `TEST_FUENTES`

4. Evaluación LLM-as-a-judge:

```bash
python test_3_LLMasajudge.py
```

Actualiza columnas:

- `LLMasajudge`
- `LLMasajudge_valoracion`
- `LLMasajudge_razonamiento`

## Detalles de implementación

- El índice se serializa con `pickle` en:
  - `Indice/chunks_with_ids.pkl`
  - `Indice/embeddings.pkl`
  - `Indice/model.pkl`
- Recuperación por similitud coseno (`sklearn.metrics.pairwise.cosine_similarity`).
- Cliente LLM unificado con `litellm.completion`.
- El prompt del modo `elaborate_responses` fuerza uso exclusivo del contexto recuperado.
- En la interfaz, las referencias `[[...]]` devueltas por el LLM se convierten a enlaces HTML de la wiki.

## Problemas frecuentes

1. **Error al cargar índice**
	- Causa probable: no existe carpeta `Indice/` o faltan `.pkl`.
	- Solución: ejecuta primero `python crear_indice.py`.

2. **Respuestas con `ERROR`**
	- Causa probable: API key inválida, rate limit o proveedor no disponible.
	- Solución: revisa `.env` y alterna entre claves/versiones de key configuradas.

3. **Dependencias fallan al instalar**
	- Causa probable: versión de Python distinta a 3.11.11.
	- Solución: recrea el entorno con la versión indicada.

4. **No aparece fondo/recursos en Streamlit**
	- Causa probable: ruta incorrecta de imagen o ejecución fuera de la raíz.
	- Solución: ejecuta `streamlit run interfaz.py` desde la carpeta raíz del repo.

## Recursos de apoyo

- `Documentacion/Documentación TFB.pdf`
- `Documentacion/Images/`
- Notebooks en `Apoyo/` para experimentación y aprendizaje.
- `Base de datos_Cosmere/0_documentos_base_datos.txt` con inventario de documentos de la base.
