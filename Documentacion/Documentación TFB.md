<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="author" content="Ferrán Plana Caminero">
    <style>
        .titulo {
            font-size: 2em;
            font-weight: bold;
            color: #333;
            text-align: center;
            margin-top: 2em;
        }
        .autor {
            font-size: 1.5em;
            font-weight: normal;
            color: #555;
            text-align: center;
            margin-top: 1em;
        }
    </style>
    <title>
        RAG de la Coppermind, una Wikipedia del Cosmere
    </title>
</head>

# Introducción  

# Objetivos  

# Desarrollo

## I. Creación de la base de datos 

<p style="text-align: justify;">
En primer lugar, he elegido la lista de entradas de la <i>wikipedia</i> que quiero utilizar como base de datos. Me he decantado por centrarme no en una saga en concreto, sino en los conceptos que son comunes a toda saga, a todo el universo del <i>Cosmere</i>.  
</p>

<p style="text-align: justify;">
Adjunto la [_lista_](https://drive.google.com/file/d/1-2jTNQljoHThvsco3jfIMhAOamoCOCqM/view?usp=sharing) con las urls de las entradas elegidas. He hecho un script que descarga el html a partir de la lista de urls. La descarga de cada entrada, al ser de una web, ha sido en formato html.   
<span style="color: red;">(Script en Creación de base de datos-TFB.ipynb en local)</span>
</p>
  
### I.II. Tratamiento de los htmls  

<p style="text-align: justify;">
Para optimizar el RAG he convertido los htmls en markdown. Además, he hecho cierto procesamiento para eliminar varias cosas:  

* Eliminación de vínculos a otras entradas de la <i>wikipedia</i>.  
* Eliminación de citas.  
* Eliminación de imágenes.  
* Eliminación de la sección de notas en adelante (sección donde se ponen todas las referencias, no aporta valor).  

<p style="text-align: justify;">
De momento no voy a hacer más tratamiento al texto. Más adelante, con la ayuda del Test Automático, estudiaré si sería conveniente.
</p>

<span style="color: red;">(Script en html_to_markdown.ipynb en local, luego subir markdowns al drive)</span>  
</p>

### I.III. Embeddings  

<p style="text-align: justify;">
Una vez procesado el contenido de cada entrada, he dividido el texto completo de la base de datos en <i>chunks</i> con un <i>overlap</i> del 20% (el tamaño del <i>chunk</i> está por ver, a estudiar con el Test Automático). He hecho los <i>embeddings</i> con el modelo <i>paraphrase-MiniLM-L6-v2</i>, un modelo de transformers que es relativamente compacto y eficiente cuya principal aplicaciión es la búsqueda semántica. He obtenido el modelo de <i>Hugging Face</i>.  
</p>

<p style="text-align: justify;">
El código divide el texto en <i>chunks</i>, hace los <i>embeddings</i> de cada <i>chunk</i> y guarda en <i>Google Drive</i> cada <i>chunk</i> y <i>embedding</i> con varios metadatos asociados: el número de <i>chunk</i> (entre todos los <i>chunks</i> del documento), el número de documento o <i>DOCID</i> (número de entrada de las totales) y su nombre (la <i>url</i> asociada, o algo similar).  
</p>

<span style="color: red;">(Script en Creación de la base de datos.ipynb, Google Colab)</span>

## II. Funcionamiento del <i>RAG</i>

<p style="text-align: justify;">
Un modelo <i>RAG</i> (<i>Retrieval-Augmented Generation</i>) consiste en dos partes principales: búsqueda semántica y generación de la respuesta. La búsqueda semántica consiste en hallar un cierto número de <i>chunks</i> de la base de datos que tienen mayor similitud con la pregunta del usuario. Una vez hallados, se le pide a un <i>LLM</i> componer una respuesta en base a esa pregunta y los chunks encontrados.  
</p>

### II.I. Búsqueda semántica  

<p style="text-align: justify;">
Una vez hechos y guardados los <i>embeddings</i>, podemos acceder a ellos mediante <i>Google Drive</i>. Al hacer una pregunta, se hace el <i>embedding</i> de esa pregunta y se calcula la similitud entre esa pregunta y todos los <i>embeddings</i> de la base de datos. Otro de los hiperparámetros, junto con el tamaño de <i>chunk</i> y el <i>overlap</i>, es <i>top-n</i>, el número de chunks con más similitud que nos quedamos. El valor óptimo de este hiperparámetro también lo decidiremos con la ayuda del Test Automático.  
</p>

<p style="text-align: justify;">
Al hacer una pregunta, obtenemos los <i>chunks</i> con mayor similitud, el número de <i>chunk</i>, el <i>DOCID</i>, su nombre y la similitud entre ese <i>chunk</i> y la pregunta. Quedaría esto:
</p>

> Question: ¿Se puede leer algún libro del Cosmere sin haber leído otras sagas?
> The 3 chunks most similar to your question are:  
>
> 1. DOCID: 12 | Document Name: https://es.coppermind.net/wiki/Cosmere | Chunk number: 3 | Similarity: 0.6855  
> subyacentes, apareciendo algunos personajes en otros mundos ajenos al suyo. A pesar de las conexiones, Brandon ha dejado claro que uno no necesita ningún conocimiento del Cosmere en general para leer, entender, o disfrutar de los libros que tienen lugar en él. Las secuencia principal del Cosmere consistirá en la saga *Dragonsteel*"), la trilogía de *Elantris*, al menos cuatro eras de la saga *Nacidos de la bruma*") y *El archivo de las tormentas*. La historia del Cosmere no incluye ningún libro que haga referencia a la Tierra, puesto que la tierra no está en el Cosmere. Para una lista completa
> 
> 2. DOCID: 19 | Document Name: https://es.coppermind.net/wiki/Esquirla del Amanecer | Chunk number: 49 | Similarity: 0.6744  
no se refiera a Sigzil. En *Viento y verdad*, se confirmó que Hoid tuvo en su poder la Esquirla del Amanecer Existe durante los sucesos de los libros 1-5 de *El archivo de las tormentas*. ## Notes 1. ↑ a b c d e f g h i j k l m n o p q r s t u *Esquirla del Amanecer (novella)* capítulo 19")Summary: Esquirla del Amanecer (novella)/Chapter\_19/Chapter 19 (la página no existe)")#/Chapter 19") 2. ↑ a b General Reddit 2022 — Arcanum - 2022-12-02Cite: Arcanum-15961# 3. ↑ a b c Dawnshard Annotations Reddit Q&A — Arcanum -
>
> 3. DOCID: 24 | Document Name: https://es.coppermind.net/wiki/Hoid | Chunk number: 184 | Similarity: 0.6562  
qué libro fue eso respondió *Brazales de Duelo")*. * La misión de Hoid quizás sea: «hacer aquello que una vez fue». * Hoid no está impresionado por los Sangre Espectral. * Hoid detesta al Grupo, y los miembros de este último que le conocen también le detestan. * Aunque una vez le dijo a Kaladin (bastante acertado) que su vida comenzó como palabras en una página, este hecho no tenía la intención de romper la cuarta pared. * Hoid se ha travestido en el pasado, «muchas veces». * Antes de los eventos de *Palabras Radiantes*, a Hoid no le habían

Además, se puede obtener una gráfica interesante: el histograma de la similitud entre cada <i>chunk</i> de la base de datos y la pregunta.  

::: center
![Distribución de _chunks_ con mayor similitud respecto a una pregunta dada.](Images/distribucion-similitudes.png){ width=50%, align=center }
:::

<span style="color: red;">(Script en Creación de la base de datos.ipynb, Google Colab)</span>
</p>

## II.II. Generación de la respuesta

<p style="text-align: justify;">
Esos <i>chunks</i> con mayor similitud con la pregunta se le pasan, junto con la pregunta del usuario, a un <i>LLM</i>, pidiéndole que responda a la pregunta del usuario en base a los <i>chunks</i> encontrados. 
</p>

<p style="text-align: justify;">
El modelo seleecionado se decidirá más adelante a raíz de una serie de tests. Para esta y posteriores llamadas a <i>LLMs</i> se utilizarán varios proveedores que permiten hacer llamadas gratis vía API (ver [_LLMs_free_API_keys.ipynb_](https://drive.google.com/file/d/1F9DaZLL1n1gUDcGtaeGBuQ-fTJLYN5xE/view?usp=sharing) para más detalles).  
</p>

El <i>system prompt</i> es el siguiente:  

> Eres un asistente virtual experto en responder preguntas. A continuación vas a recibir la pregunta de un usuario y el conocimiento que debes utilizar para responderla en el siguiente formato:
> 
> Pregunta: Pregunta del usuario
> Conocimiento:
> Nombre del documento 1: contenido del documento 1
> Nombre del documento 2: contenido del documento 2
> ...
> Nombre del documento N: contenido del documento N
> 
> Responde como si fueras un chatbot de una wikipedia. Después de dar tu respuesta completa, di el nombre de los documentos en los que te has basado para elaborarla. Si te has basado dos veces en el mismo documento, no lo repitas al referenciarlo. Hazlo en este formato:
> 
> Pon aquí tu respuesta
> [[Pon aquí únicamente el nombre del primer documento en el que te has basado]]
> [[Pon aquí únicamente el nombre del segundo documento en el que te has basado, siempre y cuando no hayas puesto el mismo nombre antes]]
> ...
> 
> No utilices conocimiento propio de tu entrenamiento, utiliza solo el que se te proporciona. Si parte del conocimiento que se te proporciona no te sirve para responder a la pregunta, no lo utilices. Cita únicamente los documentos en los que te has basado para elaborar la respuesta. Si con el conocimiento que se te proporciona no puedes responder a la pregunta, responde únicamente "Lo siento, no puedo responderte a esa pregunta" y no cites ningún documento.

El <i>user prompt</i> es el siguiente:  

> Pregunta: {Pregunta del usuario}  
> 
> Conocimiento:  
> {Nombre del documento del chunk}: {contenido del chunk}

<p style="text-align: justify;">
Como se puede observar, no solo se le pide al <i>LLM</i> que componga la respuesta, sino que cite sus fuentes. De esta forma el usuario puede, con solo pinchar en el nombre de la referencia, acceder a dicha entrada de la <i>wikipedia</i> mediante la <i>url</i>.
</p>

## III. Test Automático  

<p style="text-align: justify;">
Con el objetivo de poder valorar si los cambios tienen un impacto positivo en el modelo, he creado un test de regresión, al que llamaré Test Automático. Este test consiste en 137 preguntas de las que sé la respuesta correcta, a la que llamaré respuesta <i>best</i>, y la entrada (o entradas) de la wikipedia donde se responde a esa pregunta, que llamaré documento <i>best</i>. El test consistirá en 3 subtests:  
</p>

<p style="text-align: justify;">
* OK RAG: Porcentaje de preguntas en las que el documento/s <i>best</i> se encuentra entre los encontrados por la búsqueda semántica.  
</p>

<p style="text-align: justify;">
* OK FUENTES: Porcentaje de preguntas en las que el documento/s <i>best</i> se encuentra entre los elegidos y referenciados por el <i>LLM</i> para redactar la respuesta.  
</p>

<p style="text-align: justify;">
* OK RESPUESTA: Porcentaje de preguntas en las que un segundo <i>LLM</i> valora si la respuesta del primero se ajusta a la respuesta <i>best</i>. El <i>LLM</i> elegido para el test de <i>LLM as a judge</i> ha sido el <i>Llama 3.3 70B versatile</i>, ya que es un <i>LLM</i> grande, la útima versión de los modelos <i>LLama</i> (hasta el lanzamiento del <i>Llama 4</i>) y apto para gran variedad de tareas.   
</p>

<span style="color: red;">(Script en Test Automático.ipynb, Google Colab)</span>

El <i>system prompt</i> es el siguiente:  

> Vas a recibir una pregunta de un usuario (Pregunta), la respuesta correcta a esta pregunta (Respuesta_Best) y una respuesta generada (Respuesta_Generada). Tus objetivos son los siguientes:
> 1. Determinar si la Respuesta_Generada responde a la Pregunta.
> 2. Determinar si la Respuesta_Generada concuerda con la Respuesta_Best y no la contradice.
> Tienes que hacer una valoración en detalle y razonando sobre tu valoración. Si la Respuesta_Generada no responde a la Pregunta, valorar como KO. Si la Respuesta_Generada concuerda con la Respuesta_Best y no la contradice, valorarla como OK. Si la Respuesta_Generada no concuerda con la Respuesta_Best y la contradice, valorarla como KO. No tener en cuenta posibles detalles adicionales que puedan estar incluidos en la Respuesta_Generada, siempre y cuando no contradigan la Respuesta_Best.
> 
> Una vez hayas hecho tu razonamiento, cúentalo, y al final pon tu valoración en este formato:
> [[Valoración: OK/KO]]

El <i>user prompt</i> es el siguiente:  

> Pregunta:  
> {Pregunta del usuario}  
> 
> Respuesta_Best:  
> {Respuesta marcada como correcta}  
> 
> Respuesta_Generada:  
> {Respuesta generada por el <i>LLM</i>}

<p style="text-align: justify;">
Las preguntas, documento/s <i>best</i> y respuestas <i>best</i> se pueden ver aquí: [_Input Test Automático.xlsx_](https://docs.google.com/spreadsheets/d/1gs--ymPUeTYjbyf6AwcPHpowz6-6ehQb/edit?usp=sharing&ouid=117815217117454739708&rtpof=true&sd=true). El registro de todos los tests se puede ver aquí: PONER
</p>

### III.I. <i>chunk size</i>, <i>overlap</i> y <i>top n</i>

<p style="text-align: justify;">
El primer objetivo de este test es determinar el tamaño óptimo de los <i>chunks</i> de la base de datos. Para eso se ha ejecutado el test con varios <i>chunk size</i> distintos, así como para varios <i>top n</i> (el número de <i>chunks</i> pasados al <i>LLM</i> para redactar la respuesta). En este caso se ha fijado el <i>LLM</i> de elaboración de la respuesta y varios de sus parámetros. El <i>LLM</i> ha sido <i>Google Gemini 2.0 pro experimental</i>, aunque más adelante se comaprarán varios modelos y se eligirá el mejor. La temperatura se ha fijado a 0 para aumentar la reproducibilidad de los tests y reducir su variabilidad. Además, se ha fijado la <i>repetition penalty</i> a 0 para intentar producir respuestas concisas. Por último, el <i>chunk overlap</i> se ha fijado por defecto al 20%.  
</p>

<p style="text-align: justify;">
Se han hecho estas pruebas para un <i>chunk size</i> de 50, 75, 100 y 200 tokens, y <i>top n</i> de 3, 5, 10 y 15 <i>chunks</i>.  
</p>

| Chunk_size (tokens) | top_n (chunks) | OK RAG (%) | OK FUENTES (%) | OK RESPUESTA (%) |
|---------------------|----------------|------------|----------------|------------------|
| 50                  | 3              | 68,38      | 55,15          | 47,06            |
|                     | 5              | 78,68      | 61,76          | 55,15            |
|                     | 10             | 87,50      | 72,79          | 66,18            |
|                     | 15             | 90,44      | 74,26          | 69,85            |
| 75                  | 3              | 63,97      | 48,53          | 42,22            |
|                     | 5              | 72,79      | 55,88          | 55,88            |
|                     | 10             | 83,09      | 63,97          | 63,97            |
|                     | 15             | 86,76      | 69,12          | 69,85            |
| **100**             | 3              | 66,18      | 51,47          | 44,85            |
|                     | 5              | 75,74      | 60,29          | 52,94            |
|                     | **10**         | **84,56**  | **66,91**      | **66,18**      |
|                     | 15             | 88,24      | 69,85          | 72,79            |
| 200                 | 3              | 61,03      | 47,06          | 44,12            |
|                     | 5              | 65,44      | 53,68          | 52,21            |
|                     | 10             | 74,26      | 53,68          | 56,62            |
|                     | 15             | 79,41      | 58,09          | 59,56            |

::: center
![Valor de las métricas OR RAG, FUENTES y RESPUESTA en función del _chunk size_ y _top n_, con _chunk overlap_ del 20% del _chunk size_, modelo de _embeddings_ _paraphrase-MiniLM-L6-v2_ y modelo de elaboración de la respuesta _Google-Gemini 2.0 pro exp 02/05_ (temperatura y _repetition penalty_ a 0).](Images/chunksize-topn.jpg){ width=50%, align=center }
:::

<p style="text-align: justify;">
A raíz de estos resultados se utilizará un <i>chunk size</i> de 100 <i>tokens</i> (por tanto, un <i>chunk overlap</i> de 20 <i>tokens</i>) y un <i>top n</i> de 10 <i>chunks</i>. Se escoge esto por varias razones. En primer lugar, es el que mayor porcentaje de OK arroja en OK de la respuesta para <i>top n</i> de 10, junto a un <i>chunk size</i> de 50. Se elige sobre este porque, para resultados iguales, un <i>chunk size</i> de 100 ofrece más contexto. No se escoge <i>chunk size</i> de 100 y <i>top n</i> de 15 porque la mejora en esta métrica no es demasiada. Además, hay que tener en cuenta el tiempo de respuesta del modelo, una métrica que en este caso no se ha evaludao, pero que es fundamental, ya que esta aplicación de IA es un <i>chatbot</i>. En resumen, los parámetros elegidos han sido <b><i>chunk size</i> = 100 <i>tokens</i>, <i>chunk overlap</i> = 20 <i>tokens</i>, <i>top n</i> = 10 <i>chunks</i></b>.  
</p>

<p style="text-align: justify;">
Por otro lado, como más adelante se va a analizar el <i>LLM</i> a utilizar para responder a las preguntas, así como su temperatura, cabría preguntarse si este análisis fijando el <i>LLM</i> es válido para otros. La realidad es que no, pero se ha hecho así para reducir el número de pruebas a hacer. Aunque los resultados del análisis del <i>chunk size</i>, <i>overlap</i> y <i>top n</i> probablemente cambien de un <i>LLM</i> a otro, se ha supuesto que no serán cambios significativos.  
</p>

### III.II. Modelo de <i>embeddings</i>  

<p style="text-align: justify;">
En el momento que se hicieron los tests III.I pensaba que el modelo de <i>embeddings</i> que estaba utilizando, <i>paraphrase-MiniLM-L6-v2</i>, era el mejor. Sin embargo, en una de las clases me hicieron saber que este modelo no está entrenado en español, por lo que es fundamental encontrar uno que funcione mejor entrenado específicamente en español.  
</p>

<p style="text-align: justify;">
Lo ideal sería hacer primero este test y después el III.I, ya que es más determinante el modelo de <i>embeddings</i> utilizado. Sin embargo, como el test III.I consume mucho tiempo, asumiremos el error producido por hacerlo en este orden.  
</p>

Los modelos de <i>embeddings</i> que vamos a comparar son los siguientes:  

* <i>paraphrase-MiniLM-L6-v2</i> (as-is, entrenado solo en inglés)
* <i>paraphrase-multilingual-MiniLM-L12-v2</i>
* <i>paraphrase-multilingual-mpnet-base-v2</i>
* <i>distiluse-base-multilingual-cased-v2</i>
* <i>stsb-xlm-r-multilingual</i>
* <i>Shaharyar6/finetuned_sentence_similarity_spanish</i>

<p style="text-align: justify;">
Por desgracia, y debido a las limitaciones de tener que usar llamadas gratis via API a <i>LLMs</i> ofrecidos por distintos proveedores, el <i>LLM</i> de elaboración de la respuesta que usé en el test III.I, <i>Google: Gemini Pro 2.0 Experimental (free)</i>, ya no está disponible. Debido a esto voy a tener que utilizar otro, <i>Google: Gemini 2.0 Flash Thinking Experimental 01-21 (free)</i>. Aún así, esto no invalida las conclusiones de este test.
</p>  

Los resultados de este test son los siguientes:  

| Modelo de embeddings                                    | OK RAG (%)  | OK FUENTES (%) | OK RESPUESTA (%) |
|---------------------------------------------------------|---------|------------|--------------|
| paraphrase-MiniLM-L6-v2 (inglés)                                | 84,56  | 66,18     | 61,03       |
| paraphrase-multilingual-MiniLM-L12-v2                 | 88,97  | 77,21     | 80,74       |
| paraphrase-multilingual-mpnet-base-v2                 | 89,71  | 76,47     | 78,68       |
| **distiluse-base-multilingual-cased-v2**                  | **88,24**  | **77,94**     | **82,35**       |
| stsb-xlm-r-multilingual                               | 67,65  | 47,06     | 56,62       |
| Shaharyar6/finetuned_sentence_similarity_spanish      | 92,65  | 82,35     | 83,82       |

::: center
![Valor de las métricas OR RAG, FUENTES y RESPUESTA en función del modelo de _embeddings_, con _chunk size_ de 100 _tokens_, _chunk overlap_ de 20 _tokens_, _top n_ de 10 _chunks_ y modelo de elaboración de la respuesta _Google: Gemini 2.0 Flash Thinking Experimental 01-21_ (temperatura y _repetition penalty_ a 0).](Images/modelo-embeddings.jpg){ width=50%, align=center }
:::

<p style="text-align: justify;">
Podemos observar que, aunque OK RAG del modelo entrenado en inglés es similar al resto (entrenados en español), en las otras dos métricas es muy inferior. Es decir, los modelos de <i>embeddings</i> entrenados en español están encontrando chunks mucho más útiles para elaborar la respuesta.
</p>

<p style="text-align: justify;">
Que haya más OK RESPUESTA que OK FUENTES se explica por la naturaleza de la base de datos: como es una <i>wikipedia</i> tiene mucha información redundante, así que es probable que para alguna pregunta haya más documento/s <i>best</i> de los que he puesto en el test automático.  
</p>

<p style="text-align: justify;">
Sin embargo, lo que más llama la atención son los pésimos resultados del modelo <i>stsb-xlm-r-multilingual</i>.
EXPLICAR ESTO
</p>

<p style="text-align: justify;">
Como los resultados de los modelos entrenados en español (quitando el mencionado anteriormente) son similares, vamos a elegir basándonos también en el tiempo de inferencia de cada modelo. Aunque no está implementado el cálculo del tiempo de ejecución de cada pregunta del test, podemos estimar el tiempo de otra forma. Como el número de <i>chunks</i> y <i>tokens</i> de la base de datos es fijo, podemos medir el tiempo que tarda cada modelo en crear el índice. Esto nos dará una idea de qué modelos tardan menos en hacer una inferencia.  
</p>

| Modelo de embeddings                                    | Tiempo de creación del índice (s) |
|---------------------------------------------------------|-----------------------------------|
| paraphrase-MiniLM-L6-v2                                | 85                                |
| paraphrase-multilingual-MiniLM-L12-v2                 | 154                               |
| paraphrase-multilingual-mpnet-base-v2                 | 531                               |
| **distiluse-base-multilingual-cased-v2**                  | **260**                               |
| stsb-xlm-r-multilingual                               | 365                               |
| Shaharyar6/finetuned_sentence_similarity_spanish      | 447                               |

::: center
![Tiempo de creación del índice de la base de documentos en función del modelo de _embeddings_, con _chunk size_ y _overlap_ de 100 y 20 _tokens_ respectivamente.](Images/modelo-embeddings-tiempos.jpg){ width=50%, align=center }
:::

<p style="text-align: justify;">
Con estos resultados, el modelo de <i>embeddings</i> que vamos a utilizar es <b><i>distiluse-base-multilingual-cased-v2</i></b>, el segundo que mejor OK RESPUESTA da y el tercero más rápido, además del más rápido de los modelos por encima del 70% de OK RESPUESTA.
</p>

### III.III. <i>LLM</i> de generación de la respuesta  

<p style="text-align: justify;">
A continuación, se evaluará qué <i>LLM</i> se utilizará para generar la respuesta a partir del conocimiento encontrado.
</p>

Los modelos que vamos a evaluar son:  

* google/gemini-2.0-flash-thinking-exp:free
* google/gemini-2.5-pro-exp-03-25:free
* meta-llama/llama-3.3-70b-instruct:free
* deepseek/deepseek-chat:free (V3)
* deepseek/deepseek-r1-zero:free
* qwen/qwen-2.5-72b-instruct:free
* microsoft/phi-3-medium-128k-instruct:free
* mistralai/mistral-7b-instruct:free
* gpt-4o-mini
* meta-llama/llama-4-maverick:free
* meta-llama/llama-4-scout:free

<p style="text-align: justify;">
Los resultados han sido los siguientes (recordemos que la métrica OK RAG tiene un valor de 88,24%, que no cambiará con el <i>LLM</i> de elaboración de la respuesta, por lo que no incluiremos esta métrica aquí):
</p>

| Modelo de respuesta                               | OK FUENTES (%) | OK RESPUESTA (%) |
|---------------------------------------------------|----------------|------------------|
| google/gemini-2.0-flash-thinking-exp:free         | 77,94          | 82,35            |
| google/gemini-2.5-pro-exp-03-25:free              | 80,88          | 83,09            |
| meta-llama/llama-3.3-70b-instruct:free            | 82,35          | 80,15            |
| deepseek/deepseek-chat:free (V3)                  | 79,41          | 82,35            |
| deepseek/deepseek-r1-zero:free                    | 75,00          | 83,09            |
| qwen/qwen-2.5-72b-instruct:free                   | 77,21          | 79,41            |
| microsoft/phi-3-medium-128k-instruct:free         | 0,00           | 66,91            |
| mistralai/mistral-7b-instruct:free                | 73,53          | 73,53            |
| gpt-4o-mini                                       | 79,41          | 76,47            |
| **meta-llama/llama-4-maverick:free**                  | **86,76**          | **83,82**            |
| meta-llama/llama-4-scout:free                     | 83,09          | 77,94            |

::: center
![Valor de las métricas OK FUENTES y RESPUESTA en función del modelo de elaboración de la respuesta (temperatura y _repetition penalty_ a 0), con _distiluse-base-multilingual-cased-v2_ como modelo de _embeddings_, _chunk size_ de 100 _tokens_, _chunk overlap_ de 20 _tokens_ y _top n_ de 10 _chunks_.](Images/modelo-respuesta.jpg){ width=50%, align=center }
:::

<p style="text-align: justify;">
A la vista de estos resultados se aprecia que el mejor modelo de elaboración de la respuesta es <b><i>meta-llama/llama-4-maverick:free</i></b>, de reciente lanzamiento el 5/04/2025. Se puede apreciar que en la métrica OK RESPUESTA está cerca de otros, como los <i>gemini</i> o <i>deepseek</i>, pero parece que hay más diferencia al referenciar las fuentes.
</p>

# Puesta en producción

# Conclusiones

# Posibles mejoras

<p style="text-align: justify;">
En esta sección voy a detallar las posibles mejoras que hacer a este trabajo. Son ideas que han salido durante la realización del mismo o gracias a las clases recibidas, que no se alejan demasiado de los objetivos del trabajo, pero que o bien son demasiado ambiciosas o bien no ha dado tiempo a hacerlas. 
</p> 

## 1. <i>LLms</i> de pago

<p style="text-align: justify;">
Si ha habido algo que haya lastrado este trabajo es la limitación que teníamos de utilizar llamdas gratis via <i>API</i> a <i>LLMs</i> ofrecidos por distintos proveedores. Esto ha hecho que estemos restringidos en cuanto a los modelos que utilizar, tengamos que crear varias cuentas por proveedor para poder sortear esos <i>rate limit</i>, no podamos automatizar del todo los test automáticos, etc. Además, los mejores <i>LLMs</i> no se ofrecen gratis, por lo que contratar alguno puede aumentar también el desempeño del <i>RAG</i>, además de probablemente reducir los tiempos de inferencia.
</p>  

<p style="text-align: justify;">
Usar <i>LLMs</i> de pago me permitiría además aplicar <i>Structured Outputs</i> para que en la elaboración de la respuesta y el <i>LLM as a judge</i> den, respectivamente, las referencias separadas de la respuesta y la valoración del razonamiento.
</p>

<p style="text-align: justify;">
Por otro lado, utilizar el modelo de <i>embeddings</i> de <i>OpenAI</i> mejoraría significativamente los resultados de la parte del <i>restrieval</i>, ya que es un modelo grande pero que no necesita ser alojado en local, por lo que además es rápido. En clases y prácticas anteriores hemos discutido y comprobado la mejora notable por utilizar este modelo.  
</p>

## 2. <i>Prompts</i>  

<p style="text-align: justify;">
En cuanto a los <i>prompts</i>, el prompt que utilizo en este trabajo, tanto para la elaboración de la respuesta como para la parte del <i>LLM as a judge</i> del test automático, son los que han funcionado para el modelo <i>Google: Gemini Pro 2.0 Experimental (free)</i>. Que funcionaran bien con ese modelo no implica que funcionen también con el resto, por lo que una posible mejora podría ser encontrar el <i>prompt</i> ideal para cada <i>LLM</i> utilizado. Además, se podría haber aplicado la técnica <i>Few-Shot Prompting</i> para incluir algún ejemplo de cómo elaborar la respuesta y referenciar los documentos adecuados.  
</p>

<p style="text-align: justify;">
Otra cosa que me gustaría haber hecho mejor es la gestión de los prompts. En el repositorio del código están incluidas en un <i>script</i> de <i>python</i>, pero deben poder guardarse y tratar las versiones con alguna herramienta externa que sea más idónea.  
</p>

## 3. Test Automático  

<p style="text-align: justify;">
Una mejora clara en esta parte es incluir el tiempo de inferencia medio de cada test. Esta es una métrica funcamental para soluciones tipo <i>RAG</i>. Esta es además una métrica que, de poner esta solución en producción, mejoraría mucho, ya que los <i>LLMs</i> y modelos de <i>embeddings</i> de pago son mucho más rápidos.  
</p>

<p style="text-align: justify;">
Por otro lado, el test puede no ser todo lo representativo que pretende, ya que el número de preguntas de cada documento no lo he decidido de forma rigurosa. Podría hacerse que el porcentaje de preguntas sobre cada documento dependa de la longitud de cada documento de la base de datos. Además, por supuesto, las preguntas pueden estar hechas de forma sesgada, ya que he sido yo mismo el que las ha diseñado. Una manera de hacerlo menos sesgado es quizás pasarle fragmentos del documento a un <i>LLM</i> y pedirle que elaborara una pregunta que fuera respondida con algo de ese fragmento.  
</p>

<p style="text-align: justify;">
A su vez, los resultados de cada test se han enviado a un <i>Excel</i>, cosa que no es ni muy limpia ni muy escalable. Lo que podría hacerse es enviar los resultados y parámetros de cada test a <i>MLflow</i>.
</p>

## 4. Métricas de <i>Ragas</i> y <i>Groundedness</i> de <i>Microsoft</i> 

<p style="text-align: justify;">
Una mejora que sería muy buena es utilizar <i>Ragas</i>, una herramienta de código abierto diseñada para evaluar sistemas <i>RAG</i>. En la carpeta de Apoyo dejo un notebook donde hago un análisis de las distintas métricas que ofrece, además de poder usarse de soporte para elaborar métricas propias.  
</p>  

<p style="text-align: justify;">
Además de estas métricas, podría calcularse la métrica <i>Groundedness</i> de <i>Microsoft</i>. Esta métrica mide lo desviada que está la respuesta de un sistema <i>RAG</i> respecto del contexto que se le pasa. Es al fin y al cabo una forma de medir las alucinaciones, o lo que añade el <i>LLM</i> que elabora la respuesta al contexto recibido. Esta es una métrica que se calcula via <i>API</i> y en la que no se utiliza un <i>LLM</i> para calcularla, por lo que es muy rápida (unos 300 ms). Es por esto que podría incluso utilizarse para avisar al usuario de lo fiable que puede ser la respuesta, pintándola por ejemplo en una escala de color del rojo al verde.
</p>

## 5. Llamadas a <i>LLMs</i> con <i>LiteLLM</i>  

<p style="text-align: justify;">
En el código de este trabajo hago las llamadas a los <i>LLMs</i> de los distintos proveedores de forma algo sucia; cada uno necesita una estructura diferente. <i>LiteLLM</i> es una librería de código abierto que actúa como una interfaz unificada para hacer estas llamadas, de forma que lo hace mucho más escalable (es más fácil añadir otros proveedores) y limpia. En la carpeta de Apoyo dejo un pequeño tutorial de cómo se haría.
</p>

<p style="text-align: justify;">
Esto finalmente me ha dado tiempo a incluirlo.
</p>

# Líneas a futuro

<p style="text-align: justify;">
En esta sección voy a detallar las líneas a futuro que surgen de este trabajo. Son ideas que han salido durante la realización del mismo o gracias a las clases recibidas, como las de la sección de posibles mejoras, pero estas suponen cambios grandes en el funcionamiento de la solución actual y podrían formar parte de un nuevo trabajo por sí mismas. 
</p> 

## 1. Implementación de un <i>chatbot</i>  

<p style="text-align: justify;">
Actualmente este <i>RAG</i> funciona sin poder hacer varias iteraciones sobre las mismas preguntas; únicamente recibe una <i>query</i> de entrada a la que da respuesta. En un primer momento se pretendía que se pudiera <i>chatear</i>, pero esto supone un gran cambio en la lógica, como el manejo del historial de la conversación, una búsqueda más dinámica en el <i>RAG</i>, etc. Una de las piezas nuevas que habría que pensar en incluir es un detector de <i>chit-chat</i> que, si uno de los mensajes del usuario no tiene intención de realizar una búsqueda en el <i>RAG</i>, sepa manejarlo y no haga la búsqueda.
</p>

## 2. Implementación de un agente

<p style="text-align: justify;">
La solución actual es muy rígida por construcción: para cada <i>query</i> obtiene un número fijo de <i>chunks</i>, con los que tiene que elaborar la respuesta. Si ahí no está la respuesta no puede hacerse nada. Todos los hiperparámetros de esta solución son fijos, aunque puedan no ser los más idóneos para alguna pregunta. Un ejemplo de pregunta para la que esta solución no es idónea es si se le pidiera hacer una lista de características de varios elementos: lo ideal sería que buscara cada elemento por separado, pero tal y como está planteada la solución actualmente hace una única búsqueda, pudiendo no encontrar toda la información.
</p>

<p style="text-align: justify;">
En este sentido, sería muy interesante elaborar una solución en la que sea un agente el que gestione las búsquedas en la base de datos y la elaboración de la respuesta. De esta forma, el agente puede adaptar la <i>query</i> del usuario y hacer búsquedas con <i>querys</i> más adecuadas, no hacer solamente una, decidir si tiene que hacer más porque aún no tiene la respuesta o modificar hiperparámetros como <i>top_n</i>.
</p>

## 3. Mejoras en las <i>querys</i> del <i>RAG</i>

<p style="text-align: justify;">
Una técnica muy habitual en <i>RAGs</i> productivos es <i>RAG-fusión</i>. <i>RAG-fusión</i> consiste en, con la ayuda de un <i>LLM</i>, generar más <i>querys</i> a partir de la inicial, hacer varias búsquedas para cada <i>query</i>, reordenar los <i>chunks</i> encontrados y generar la respuesta con todos ellos. Esta solución aporta mayor cobertura, precisión y respuestas más robustas a las soluciones de <i>RAG</i>.
</p>

## 4. Mejoras en la creación del índice

<p style="text-align: justify;">
Una de las limitaciones de este <i>RAG</i> es que en la creación del índice se hacen <i>embeddings</i> directamente sobre el contenido de la base de datos, pero este contenido no tiene por qué ser muy similar a las preguntas que hacen los usuarios. Otra opción es hacer los <i>embeddings</i> sobre las preguntas que podría responder cada <i>chunk</i> de la base de datos, generando estas preguntas con la ayuda de un <i>LLM</i>.
</p>

<p style="text-align: justify;">
Otra de las posibles mejoras en la cración del índice de este tipo de sooluciones es incluir un pequeño resumen de cada documento como metadato de los <i>chunks</i> que lo conforman. De esta forma, el <i>LLM</i> que elabora la respuesta tiene más contexto y puede responder mejor. Estos resúmenes pueden crearse con otro <i>LLM</i>.
</p>

