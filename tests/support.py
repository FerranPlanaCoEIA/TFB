import numpy as np


class FakeResponse:
    def __init__(self, content, tool_calls=None):
        self.content = content
        self.tool_calls = tool_calls or []


class SequenceLLM:
    def __init__(self, responses):
        self._responses = list(responses)
        self.bound_tools = []

    def bind_tools(self, tools):
        self.bound_tools = list(tools)
        return self

    def invoke(self, messages):
        if not self._responses:
            raise AssertionError("No quedan respuestas falsas configuradas para el LLM.")
        return self._responses.pop(0)


class KeywordEmbeddingModel:
    def encode(self, texts):
        vectors = []
        for text in texts:
            normalized = text.lower()
            if "hoid" in normalized:
                vectors.append([1.0, 0.0])
            elif "roshar" in normalized:
                vectors.append([0.0, 1.0])
            else:
                vectors.append([0.5, 0.5])
        return np.array(vectors, dtype=float)


def sample_index_data():
    chunks = [
        (0, "es.coppermind.net__wiki_Hoid.md", 0, "Hoid es un personaje misterioso del Cosmere."),
        (1, "es.coppermind.net__wiki_Roshar.md", 0, "Roshar es un planeta azotado por altas tormentas."),
    ]
    embeddings = np.array([[1.0, 0.0], [0.0, 1.0]], dtype=float)
    return chunks, embeddings, KeywordEmbeddingModel()
