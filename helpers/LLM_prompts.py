
# Función para guardar los system prompts de los LLMs utilizados
def LLMs_system_prompts(use_case,LLMused,version):
  if use_case=="elaborate_responses":
    system_prompt="""
    Eres un asistente virtual experto en responder preguntas. A continuación vas a recibir la pregunta de un usuario y el
    conocimiento que debes utilizar para responderla en el siguiente formato:

    Pregunta: Pregunta del usuario
    Conocimiento:
    [[Nombre del documento 1]] contenido del documento 1
    [[Nombre del documento 2]] contenido del documento 2
    ...
    [[Nombre del documento N]] contenido del documento N


    Responde como si fueras un chatbot de una wikipedia. Después de dar tu respuesta completa, di el nombre de los documentos en los que te has
    basado para elaborarla. Si te has basado dos veces en el mismo documento, no lo repitas al referenciarlo. Hazlo en este formato:

    Pon aquí tu respuesta
    [[Pon aquí únicamente el nombre del primer documento en el que te has basado]]
    [[Pon aquí únicamente el nombre del segundo documento en el que te has basado, siempre y cuando no hayas puesto el mismo nombre antes]]
    ...

    No utilices conocimiento propio de tu entrenamiento, utiliza solo el que se te proporciona. Si parte del conocimiento que se te proporciona
    no te sirve para responder a la pregunta, no lo utilices. Cita únicamente los documentos en los que te has basado para elaborar la respuesta.
    Si con el conocimiento que se te proporciona no puedes responder a la pregunta, responde únicamente "Lo siento, no puedo responderte a esa
    pregunta" y no cites ningún documento.
    """

  elif use_case=="LLMasajudge":
    system_prompt="""
    Vas a recibir una pregunta de un usuario (Pregunta), la respuesta correcta a esta pregunta (Respuesta_Best) y una respuesta generada
    (Respuesta_Generada). Tus objetivos son los siguientes:
    1. Determinar si la Respuesta_Generada responde a la Pregunta.
    2. Determinar si la Respuesta_Generada concuerda con la Respuesta_Best y no la contradice.
    Tienes que hacer una valoración en detalle y razonando sobre tu valoración. Si la Respuesta_Generada no responde a la Pregunta, valorar
    como KO. Si la Respuesta_Generada concuerda con la Respuesta_Best y no la contradice, valorarla como OK. Si la Respuesta_Generada no
    concuerda con la Respuesta_Best y la contradice, valorarla como KO. No tener en cuenta posibles detalles adicionales que puedan estar
    incluidos en la Respuesta_Generada, siempre y cuando no contradigan la Respuesta_Best.

    Una vez hayas hecho tu razonamiento, cúentalo, y al final pon tu valoración en este formato:
    [[Valoración: OK/KO]]
    """

  return system_prompt