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


def sample_index_data():
    documents = [
        {
            "doc_id": 0,
            "doc_name": "es.coppermind.net__wiki_Hoid.md",
            "display_name": "Hoid",
            "summary": "Hoid es un saltamundos del Cosmere con conexiones con Roshar y Odium.",
            "text": "Hoid es un saltamundos del Cosmere. Hoid se cruza con Roshar y se opone a Odium.",
            "tokens": ["hoid", "saltamundos", "cosmere", "roshar", "odium"],
            "infobox": {"Universo": "Cosmere", "Vinculado con": "Roshar, Odium"},
        },
        {
            "doc_id": 1,
            "doc_name": "es.coppermind.net__wiki_Roshar.md",
            "display_name": "Roshar",
            "summary": "Roshar es un planeta del Cosmere asociado a Honor, Cultivacion y Odium.",
            "text": "Roshar es un planeta del Cosmere. Honor y Cultivacion actuan en Roshar.",
            "tokens": ["roshar", "planeta", "cosmere", "honor", "cultivacion", "odium"],
            "infobox": {"Esquirlas": "Honor, Cultivacion, Odium", "Universo": "Cosmere"},
        },
        {
            "doc_id": 2,
            "doc_name": "es.coppermind.net__wiki_Odium.md",
            "display_name": "Odium",
            "summary": "Odium es una Esquirla de Adonalsium que influye sobre Roshar.",
            "text": "Odium es una Esquirla. Odium influye sobre Roshar y choca con Hoid.",
            "tokens": ["odium", "esquirla", "adonalsium", "roshar", "hoid"],
            "infobox": {"Universo": "Cosmere"},
        },
    ]
    adjacency = {
        0: [
            {"source": 0, "target": 1, "relation": "vinculado_con", "evidence": "Roshar"},
            {"source": 0, "target": 2, "relation": "mencionado_en_texto", "evidence": "Hoid se opone a Odium."},
        ],
        1: [
            {"source": 1, "target": 2, "relation": "esquirlas", "evidence": "Honor, Cultivacion, Odium"},
        ],
        2: [
            {"source": 2, "target": 1, "relation": "mencionado_en_texto", "evidence": "Odium influye sobre Roshar."},
            {"source": 2, "target": 0, "relation": "mencionado_en_texto", "evidence": "Odium choca con Hoid."},
        ],
    }
    metadata = {
        "kind": "knowledge_graph",
        "version": 1,
        "title_to_doc_id": {"hoid": 0, "roshar": 1, "odium": 2},
        "doc_count": 3,
    }
    return documents, adjacency, metadata
