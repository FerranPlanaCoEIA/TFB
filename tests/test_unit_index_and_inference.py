import os
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import patch

import httpx

from helpers import crear_indice as ci
from helpers import hacer_inferencia as hi
from tests.support import sample_index_data


class CrearIndiceTests(unittest.TestCase):
    def test_process_markdown_extracts_document_summary_and_tokens(self):
        markdown = """# Hoid

| Universo | Cosmere |
| Vinculado con | Roshar |

Hoid es un personaje misterioso del Cosmere que aparece en Roshar.
"""
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = os.path.join(temp_dir, "doc.md")
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(markdown)

            document = ci.process_markdown(file_path, 3, "doc.md")

        self.assertEqual(document["doc_id"], 3)
        self.assertEqual(document["display_name"], "doc")
        self.assertIn("Hoid es un personaje misterioso", document["summary"])
        self.assertIn("hoid", document["tokens"])
        self.assertEqual(document["infobox"]["Universo"], "Cosmere")

    def test_process_markdown_returns_none_for_missing_file(self):
        document = ci.process_markdown("C:\\no-existe.md", 0, "no-existe.md")
        self.assertIsNone(document)

    def test_process_all_markdown_files_reads_only_markdown_sorted(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            with open(os.path.join(temp_dir, "b.md"), "w", encoding="utf-8") as file:
                file.write("# Beta\n\nBeta aparece en Cosmere.")
            with open(os.path.join(temp_dir, "a.md"), "w", encoding="utf-8") as file:
                file.write("# Alfa\n\nAlfa aparece en Roshar.")
            with open(os.path.join(temp_dir, "z.txt"), "w", encoding="utf-8") as file:
                file.write("ignorar")

            documents = ci.process_all_markdown_files(temp_dir)

        self.assertEqual([document["doc_name"] for document in documents], ["a.md", "b.md"])
        self.assertEqual([document["doc_id"] for document in documents], [0, 1])

    def test_build_knowledge_graph_extracts_relations_from_infobox_and_text(self):
        documents = [
            {
                "doc_id": 0,
                "doc_name": "Hoid.md",
                "display_name": "Hoid",
                "summary": "Hoid viaja a Roshar.",
                "text": "Hoid viaja a Roshar y se enfrenta a Odium.",
                "tokens": ["hoid", "roshar", "odium"],
                "infobox": {"Vinculado con": "Roshar"},
            },
            {
                "doc_id": 1,
                "doc_name": "Roshar.md",
                "display_name": "Roshar",
                "summary": "Roshar es un planeta.",
                "text": "Roshar es un planeta.",
                "tokens": ["roshar", "planeta"],
                "infobox": {},
            },
            {
                "doc_id": 2,
                "doc_name": "Odium.md",
                "display_name": "Odium",
                "summary": "Odium es una Esquirla.",
                "text": "Odium es una Esquirla.",
                "tokens": ["odium", "esquirla"],
                "infobox": {},
            },
        ]

        adjacency, metadata = ci.build_knowledge_graph(documents)

        self.assertIn("hoid", metadata["title_to_doc_id"])
        self.assertIn((1, "vinculado_con"), {(edge["target"], edge["relation"]) for edge in adjacency[0]})
        self.assertIn((2, "mencionado_en_texto"), {(edge["target"], edge["relation"]) for edge in adjacency[0]})

    def test_save_and_load_data_round_trip(self):
        documents, adjacency, metadata = sample_index_data()

        with tempfile.TemporaryDirectory() as temp_dir:
            ci.save_data(documents, adjacency, metadata, temp_dir)
            loaded_documents, loaded_adjacency, loaded_metadata = ci.load_data(temp_dir)

        self.assertEqual(loaded_documents, documents)
        self.assertEqual(loaded_adjacency, adjacency)
        self.assertEqual(loaded_metadata, metadata)


class HacerInferenciaTests(unittest.TestCase):
    def test_get_chat_llm_requires_endpoint(self):
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaisesRegex(RuntimeError, "AZURE_OPENAI_ENDPOINT"):
                hi.get_chat_llm("gpt-test")

    def test_get_chat_llm_requires_api_key(self):
        with patch.dict(os.environ, {"AZURE_OPENAI_ENDPOINT": "https://example.test"}, clear=True):
            with self.assertRaisesRegex(RuntimeError, "AZURE_OPENAI_API_KEY"):
                hi.get_chat_llm("gpt-test")

    def test_get_chat_llm_builds_client_with_expected_arguments(self):
        fake_client = object()
        with patch.dict(
            os.environ,
            {
                "AZURE_OPENAI_ENDPOINT": "https://example.test",
                "AZURE_OPENAI_API_KEY": "secret",
            },
            clear=True,
        ):
            with patch("helpers.hacer_inferencia.ChatOpenAI", return_value=fake_client) as mock_chat_openai:
                client = hi.get_chat_llm("gpt-test", temperature=0.3)

        self.assertIs(client, fake_client)
        mock_chat_openai.assert_called_once_with(
            model="gpt-test",
            api_key="secret",
            base_url="https://example.test",
            temperature=0.3,
        )

    def test_get_similar_chunks_prioritizes_direct_entity_matches(self):
        documents, adjacency, metadata = sample_index_data()

        results = hi.get_similar_chunks("Háblame de Hoid", documents, adjacency, metadata, top_n=2)

        self.assertEqual(results[0][0][1], "es.coppermind.net__wiki_Hoid.md")
        self.assertGreaterEqual(results[0][1], results[1][1])

    def test_get_similar_chunks_uses_graph_relations(self):
        documents, adjacency, metadata = sample_index_data()

        results = hi.get_similar_chunks("¿Qué relación hay entre Hoid y Odium?", documents, adjacency, metadata, top_n=1)

        self.assertIn(results[0][0][1], {"es.coppermind.net__wiki_Hoid.md", "es.coppermind.net__wiki_Odium.md"})
        self.assertIn("Relaciones relevantes", results[0][0][3])
        self.assertIn("Odium", results[0][0][3])

    def test_search_knowledge_base_formats_results(self):
        documents, adjacency, metadata = sample_index_data()

        results = hi.search_knowledge_base("Roshar", documents, adjacency, metadata, top_n=1)

        self.assertEqual(results[0]["display_name"], "Roshar")
        self.assertEqual(results[0]["doc_name"], "es.coppermind.net__wiki_Roshar.md")
        self.assertIn("planeta", results[0]["chunk_text"].lower())

    def test_build_knowledge_block_and_serialize_results(self):
        search_results = [
            {
                "display_name": "Hoid",
                "chunk_number": 0,
                "similarity": 0.98765,
                "chunk_text": "Hoid aparece en muchas historias.",
            }
        ]

        knowledge = hi.build_knowledge_block(search_results)
        serialized = hi.serialize_search_results(search_results, max_chars=40)

        self.assertIn("[[Hoid]]: Hoid aparece en muchas historias.", knowledge)
        self.assertTrue(serialized.endswith("..."))

    def test_build_knowledge_block_honors_max_results(self):
        search_results = [
            {"display_name": "Hoid", "chunk_text": "A"},
            {"display_name": "Roshar", "chunk_text": "B"},
        ]

        knowledge = hi.build_knowledge_block(search_results, max_results=1)

        self.assertIn("[[Hoid]]: A", knowledge)
        self.assertNotIn("[[Roshar]]: B", knowledge)

    def test_serialize_search_results_returns_message_for_empty_results(self):
        self.assertEqual(hi.serialize_search_results([]), "Sin resultados recuperados.")

    def test_get_llm_response_supports_string_and_list_blocks(self):
        string_response = SimpleNamespace(content="respuesta plana")
        block_response = SimpleNamespace(content=[{"text": "bloque 1"}, {"text": "bloque 2"}])

        with patch("helpers.hacer_inferencia.get_chat_llm") as mock_get_chat_llm:
            mock_get_chat_llm.return_value.invoke.side_effect = [string_response, block_response]

            first = hi.get_LLM_response("gpt-test", "user", "system")
            second = hi.get_LLM_response("gpt-test", "user", "system")

        self.assertEqual(first, "respuesta plana")
        self.assertEqual(second, "bloque 1bloque 2")
        self.assertEqual(mock_get_chat_llm.return_value.invoke.call_count, 2)

    def test_get_llm_response_returns_error_on_api_failure(self):
        request = httpx.Request("POST", "https://example.test")
        api_error = hi.APIError("boom", request=request, body=None)

        with patch("helpers.hacer_inferencia.get_chat_llm") as mock_get_chat_llm:
            mock_get_chat_llm.return_value.invoke.side_effect = api_error
            result = hi.get_LLM_response("gpt-test", "user", "system")

        self.assertEqual(result, "ERROR")

    def test_get_llm_response_raises_type_error_for_unsupported_content(self):
        unsupported_response = SimpleNamespace(content={"unexpected": "payload"})

        with patch("helpers.hacer_inferencia.get_chat_llm") as mock_get_chat_llm:
            mock_get_chat_llm.return_value.invoke.return_value = unsupported_response

            with self.assertRaises(TypeError):
                hi.get_LLM_response("gpt-test", "user", "system")


if __name__ == "__main__":
    unittest.main()
