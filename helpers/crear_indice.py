import os
import pickle
import re

from unidecode import unidecode


LEGACY_CHUNKS_FILE = "chunks_with_ids.pkl"
LEGACY_EMBEDDINGS_FILE = "embeddings.pkl"
LEGACY_MODEL_FILE = "model.pkl"
MAX_SUMMARY_CHARS = 900
MAX_EVIDENCE_CHARS = 220


def _normalize_text(text):
    normalized = unidecode(str(text or "")).lower()
    return " ".join(normalized.split())


def _tokenize(text):
    return re.findall(r"[a-z0-9]+", _normalize_text(text))


def _extract_display_name(doc_name):
    if not doc_name.endswith(".md"):
        return doc_name
    return doc_name[:-3].replace("es.coppermind.net__wiki_", "").replace("_", " ")


def _clean_markdown_text(text):
    cleaned = re.sub(r"!\[[^\]]*\]\([^)]+\)", " ", text)
    cleaned = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", cleaned)
    cleaned = re.sub(r"`([^`]*)`", r"\1", cleaned)
    cleaned = re.sub(r"\*\*([^*]+)\*\*", r"\1", cleaned)
    cleaned = re.sub(r"\*([^*]+)\*", r"\1", cleaned)
    cleaned = re.sub(r"#+\s*", "", cleaned)
    cleaned = cleaned.replace("|", " ")
    return " ".join(cleaned.split())


def _is_noise_paragraph(paragraph):
    normalized = _normalize_text(paragraph)
    if not normalized:
        return True
    if normalized.startswith("por "):
        return True
    if normalized.startswith("para mas informacion"):
        return True
    if normalized.startswith("esta pagina o seccion usa informacion basada"):
        return True
    if normalized.startswith("este articulo esta en proceso de traduccion"):
        return True
    if normalized.startswith("vease "):
        return True
    return False


def _split_markdown_sections(text):
    lines = text.splitlines()
    sections = []
    current_lines = []

    for line in lines:
        stripped = line.strip()
        if not stripped:
            if current_lines:
                current_lines.append("")
            continue

        if stripped.startswith("|"):
            continue

        if stripped.startswith("#"):
            if current_lines:
                sections.append("\n".join(current_lines))
                current_lines = []
            current_lines.append(stripped)
            continue

        current_lines.append(stripped)

    if current_lines:
        sections.append("\n".join(current_lines))

    cleaned_sections = []
    for section in sections:
        paragraphs = []
        for paragraph in section.split("\n\n"):
            cleaned_paragraph = _clean_markdown_text(paragraph.strip())
            if _is_noise_paragraph(cleaned_paragraph):
                continue
            paragraphs.append(cleaned_paragraph)
        if paragraphs:
            cleaned_sections.append(paragraphs)

    return cleaned_sections


def _extract_summary(section_groups, fallback_title):
    for group in section_groups:
        for paragraph in group:
            if len(paragraph) < 30:
                continue
            return paragraph[:MAX_SUMMARY_CHARS]
    return fallback_title


def _extract_infobox(lines):
    infobox = {}
    for line in lines:
        stripped = line.strip()
        if not stripped.startswith("|") or stripped == "| --- | --- |":
            continue

        cells = [cell.strip() for cell in stripped.split("|")[1:-1]]
        if len(cells) != 2:
            continue

        key, value = cells
        if not key or not value or key == "---" or value == "---":
            continue

        infobox[_clean_markdown_text(key)] = _clean_markdown_text(value)

    return infobox


def process_markdown(file_path, doc_id, doc_name, chunk_size=None, chunk_overlap=None):
    del chunk_size, chunk_overlap

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            text = file.read()
    except Exception as error:
        print(f"Error al procesar el Markdown {doc_name}: {error}")
        return None

    display_name = _extract_display_name(doc_name)
    section_groups = _split_markdown_sections(text)
    summary = _extract_summary(section_groups, display_name)
    cleaned_text = " ".join(
        paragraph
        for group in section_groups
        for paragraph in group
    )

    return {
        "doc_id": doc_id,
        "doc_name": doc_name,
        "display_name": display_name,
        "summary": summary,
        "text": cleaned_text,
        "tokens": sorted(set(_tokenize(f"{display_name} {cleaned_text}"))),
        "infobox": _extract_infobox(text.splitlines()),
    }


def process_all_markdown_files(carpeta_path, chunk_size=None, chunk_overlap=None):
    files = os.listdir(carpeta_path)
    files_array = sorted(
        file
        for file in files
        if os.path.isfile(os.path.join(carpeta_path, file)) and file.endswith(".md")
    )
    documents = []

    for doc_id, file in enumerate(files_array):
        file_path = os.path.join(carpeta_path, file)
        document = process_markdown(file_path, doc_id, file, chunk_size, chunk_overlap)
        if document is not None:
            documents.append(document)

    return documents


def _extract_evidence(doc_text, target_name):
    target_normalized = _normalize_text(target_name)
    for sentence in re.split(r"(?<=[.!?])\s+", doc_text):
        if target_normalized and target_normalized in _normalize_text(sentence):
            return sentence[:MAX_EVIDENCE_CHARS]
    return doc_text[:MAX_EVIDENCE_CHARS]


def _relation_label_from_field(field_name):
    label = _normalize_text(field_name).replace(" ", "_")
    return label or "relacionado_con"


def _find_related_documents(text, normalized_titles):
    normalized_text = _normalize_text(text)
    related_doc_ids = set()

    for normalized_title, doc_id in normalized_titles.items():
        if not normalized_title:
            continue
        if normalized_title in normalized_text:
            related_doc_ids.add(doc_id)

    return related_doc_ids


def build_knowledge_graph(documents):
    normalized_titles = {
        _normalize_text(document["display_name"]): document["doc_id"]
        for document in documents
    }
    documents_by_id = {document["doc_id"]: document for document in documents}
    adjacency = {document["doc_id"]: [] for document in documents}

    for document in documents:
        seen_edges = set()

        for field_name, field_value in document["infobox"].items():
            for target_id in _find_related_documents(field_value, normalized_titles):
                if target_id == document["doc_id"]:
                    continue

                relation = _relation_label_from_field(field_name)
                edge_key = (target_id, relation)
                if edge_key in seen_edges:
                    continue

                seen_edges.add(edge_key)
                adjacency[document["doc_id"]].append(
                    {
                        "source": document["doc_id"],
                        "target": target_id,
                        "relation": relation,
                        "evidence": field_value[:MAX_EVIDENCE_CHARS],
                    }
                )

        for target_id in _find_related_documents(document["text"], normalized_titles):
            if target_id == document["doc_id"]:
                continue

            edge_key = (target_id, "mencionado_en_texto")
            if edge_key in seen_edges:
                continue

            seen_edges.add(edge_key)
            target_name = documents_by_id[target_id]["display_name"]
            adjacency[document["doc_id"]].append(
                {
                    "source": document["doc_id"],
                    "target": target_id,
                    "relation": "mencionado_en_texto",
                    "evidence": _extract_evidence(document["text"], target_name),
                }
            )

    metadata = {
        "kind": "knowledge_graph",
        "version": 1,
        "title_to_doc_id": normalized_titles,
        "doc_count": len(documents),
    }
    return adjacency, metadata


def create_embeddings(documents, model_embeddings=None):
    del model_embeddings
    return build_knowledge_graph(documents)


def save_data(chunks, embeddings, model, save_folder):
    os.makedirs(save_folder, exist_ok=True)
    with open(os.path.join(save_folder, LEGACY_CHUNKS_FILE), "wb") as file:
        pickle.dump(chunks, file)
    with open(os.path.join(save_folder, LEGACY_EMBEDDINGS_FILE), "wb") as file:
        pickle.dump(embeddings, file)
    with open(os.path.join(save_folder, LEGACY_MODEL_FILE), "wb") as file:
        pickle.dump(model, file)


def load_data(save_folder):
    with open(os.path.join(save_folder, LEGACY_CHUNKS_FILE), "rb") as file:
        chunks = pickle.load(file)
    with open(os.path.join(save_folder, LEGACY_EMBEDDINGS_FILE), "rb") as file:
        embeddings = pickle.load(file)
    with open(os.path.join(save_folder, LEGACY_MODEL_FILE), "rb") as file:
        model = pickle.load(file)
    return chunks, embeddings, model
