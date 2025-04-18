# TFB - RAG General - Ferrán Plana Caminero

## Pasos para ejecutar este repositorio

### 1. Crear el entorno virtual e instalar los requierements

> :warning: **Aviso**: Este repositorio debe ser ejecutado en python 3.11.11. Hacerlo en otra versión podría producir fallos o errores de dependencias a la hora de instalar los requirements.

## 2. Crear un .env siguiendo lo indicado en el archivo .env_template

Los modelos de _embeddings_ son modelos de _hugging face_ y las llamadas al _LLM_ de elaboración de la respuesta se hacen mediante la librería _litellm_. Si se quiere hacer llamadas a _LLMs_ de forma gratuita, ver los _notebooks_ de la carpeta "Apoyo".

## 3. Subir los documentos de la base de datos

Este repositorio puede procesar documentos con las extensiones .pdf, .docx, .html o .md.  

Se deben subir los documentos a la carpeta "Base de datos RAG general".

## 4. Convertir los documentos a markdown

Ejecutar **python markdown_transformer.py** desde la carpeta "Base de datos RAG general". Este script colocará todos los documentos de la base de datos convertidos a markdown en la carpeta "Base de datos RAG general/Markdowns convertidos"

## 5. Crear el índice de la base de datos

Para hacer los _embeddings_ de la base de datos, ejecutar **python crear_indice.py**. Paciencia, esto puede llevar varios minutos.

## 6. ¡A hacer preguntas!

Cuando haya terminado lo anterior, basta ejecutar **streamlit run interfaz.py** y abrir http://localhost:8501. ¡A hacer preguntas!
