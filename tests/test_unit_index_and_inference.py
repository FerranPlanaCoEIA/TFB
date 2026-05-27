import os
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

import httpx
import numpy as np

from helpers import crear_indice as ci
from helpers import hacer_inferencia as hi
from tests.support import sample_index_data


class CrearIndiceTests(unittest.TestCase):
    def test_process_markdown_creates_overlapping_chunks(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = os.path.join(temp_dir, "doc.md")
            with open(file_path, "w", encoding="utf-8") as file:
                file.write("uno dos tres cuatro cinco seis siete ocho")

            chunks = ci.process_markdown(file_path, 3, "doc.md", 3, 1)

        expected = [
            (3, "doc.md", 0, "uno dos tres"),
            (3, "doc.md", 1, "tres cuatro cinco"),
            (3, "doc.md", 2, "cinco seis siete"),
            (3, "doc.md", 3, "siete ocho"),
        ]
        self.assertEqual(chunks, expected)

    def test_process_markdown_returns_empty_for_missing_file(self):
        chunks = ci.process_markdown("C:\\no-existe.md", 0, "no-existe.md", 10, 2)
        self.assertEqual(chunks, [])

    def test_process_all_markdown_files_reads_only_markdown_sorted(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            with open(os.path.join(temp_dir, "b.md"), "w", encoding="utf-8") as file:
                file.write("beta uno dos")
            with open(os.path.join(temp_dir, "a.md"), "w", encoding="utf-8") as file:
                file.write("alfa uno dos")
            with open(os.path.join(temp_dir, "z.txt"), "w", encoding="utf-8") as file:
                file.write("ignorar")

            chunks = ci.process_all_markdown_files(temp_dir, 10, 1)

        self.assertEqual([chunk[1] for chunk in chunks], ["a.md", "b.md"])
        self.assertEqual([chunk[0] for chunk in chunks], [0, 1])

    def test_save_and_load_data_round_trip(self):
        chunks = [(0, "doc.md", 0, "texto")]
        embeddings = np.array([[1.0, 2.0]])
        model = {"name": "fake-model"}

        with tempfile.TemporaryDirectory() as temp_dir:
            ci.save_data(chunks, embeddings, model, temp_dir)
            loaded_chunks, loaded_embeddings, loaded_model = ci.load_data(temp_dir)

        self.assertEqual(loaded_chunks, chunks)
        self.assertTrue(np.array_equal(loaded_embeddings, embeddings))
        self.assertEqual(loaded_model, model)


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

    def test_patch_transformer_config_adds_missing_flags(self):
        config = SimpleNamespace(_output_attentions=True, _output_hidden_states=False)
        auto_model = SimpleNamespace(config=config)
        model = SimpleNamespace(_modules={"layer": SimpleNamespace(auto_model=auto_model)})

        patched = hi._patch_transformer_config(model)

        self.assertIs(patched, model)
        self.assertTrue(config.output_attentions)
        self.assertFalse(config.output_hidden_states)
        self.assertFalse(auto_model._use_flash_attention_2)
        self.assertFalse(auto_model._use_sdpa)

    def test_encode_question_uses_fallback_model_when_original_model_keeps_failing(self):
        class BrokenModel:
            def encode(self, _texts):
                raise AttributeError("broken")

        fallback_model = Mock()
        fallback_model.encode.return_value = np.array([[0.2, 0.8]])

        with patch("helpers.hacer_inferencia.SentenceTransformer", return_value=fallback_model):
            embedding, resolved_model = hi._encode_question("Roshar", BrokenModel())

        self.assertTrue(np.array_equal(embedding, np.array([[0.2, 0.8]])))
        self.assertIs(resolved_model, fallback_model)

    def test_get_similar_chunks_returns_results_sorted_by_similarity(self):
        chunks, embeddings, model = sample_index_data()

        results = hi.get_similar_chunks("Háblame de Hoid", chunks, embeddings, model, top_n=2)

        self.assertEqual(results[0][0][1], "es.coppermind.net__wiki_Hoid.md")
        self.assertGreaterEqual(results[0][1], results[1][1])

    def test_search_knowledge_base_formats_results(self):
        chunks, embeddings, model = sample_index_data()

        results = hi.search_knowledge_base("Roshar", chunks, embeddings, model, top_n=1)

        self.assertEqual(results[0]["display_name"], "Roshar")
        self.assertEqual(results[0]["doc_name"], "es.coppermind.net__wiki_Roshar.md")
        self.assertIn("planeta", results[0]["chunk_text"])

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

    def test_serialize_search_results_returns_message_for_empty_results(self):
        self.assertEqual(hi.serialize_search_results([]), "Sin resultados recuperados.")

    def test_get_llm_response_supports_string_and_list_blocks(self):
        request = httpx.Request("POST", "https://example.test")
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


if __name__ == "__main__":
    unittest.main()
