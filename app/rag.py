import os
import json
from typing import List, Dict
import chromadb
from chromadb.utils import embedding_functions

# Config
CHROMA_DIR = os.getenv("CHROMA_DIR", "./.chroma")
MODEL_EMBED = os.getenv("MODEL_EMBED", "text-embedding-3-small")

client = chromadb.PersistentClient(path=CHROMA_DIR)


def ensure_collection():
	"""Returnează colecția Chroma 'books', creând-o dacă nu există."""
	return client.get_or_create_collection(
		name="books",
		embedding_function=embedding_functions.OpenAIEmbeddingFunction(
			api_key=os.getenv("OPENAI_API_KEY"),
			model_name=MODEL_EMBED,
		),
	)


def load_json(path: str) -> List[Dict]:
	"""Încarcă lista de cărți dintr-un fișier JSON."""
	with open(path, encoding="utf-8") as f:
		return json.load(f)


def ingest_documents(docs: List[Dict]):
	"""Ingest documents în colecția 'books'.

	docs: list de dicturi cu cel puțin cheile 'title' și 'summary_short'.
	Dacă colecția are deja același număr de itemi, nu face ingest.
	"""
	col = ensure_collection()
	# numărul curent de itemi (fallback la 0 dacă nu există)
	try:
		existing_ids = col.get(ids=None)["ids"]
		existing_count = len(existing_ids)
	except Exception:
		existing_count = 0

	if existing_count == len(docs) and existing_count > 0:
		print("Colecția există deja, ingest ignorat.")
		return

	# Adăugăm fiecare document; id-ul folosit este titlul
	for doc in docs:
		text = f"{doc.get('title','')} {doc.get('summary_short','')}"
		col.add(
			documents=[text],
			ids=[doc.get("title")],
			metadatas=[{"title": doc.get("title"), "snippet": doc.get("summary_short")}],
		)
	print(f"Ingestat {len(docs)} cărți în colecție.")


def build_collection_if_needed(json_path: str = "book_summaries.json"):
	"""Convenience: încarcă JSON și face ingest dacă este necesar."""
	docs = load_json(json_path)
	ingest_documents(docs)


def search(query: str, k: int = 3) -> List[Dict]:
	"""Caută semantic în colecția 'books' și returnează o listă de dicturi:

	[{"title": str, "snippet": str, "score": float}, ...]
	"""
	col = ensure_collection()
	try:
		results = col.query(query_texts=[query], n_results=k)
	except Exception:
		return []

	out: List[Dict] = []
	# results may have shape with lists inside
	ids_list = results.get("ids", [])
	metadatas_list = results.get("metadatas", [])
	distances_list = results.get("distances", [])

	# safety checks
	if not ids_list or not metadatas_list:
		return out

	ids = ids_list[0]
	metadatas = metadatas_list[0]
	distances = distances_list[0] if distances_list else [None] * len(ids)

	for i, _id in enumerate(ids):
		meta = metadatas[i] if i < len(metadatas) else {}
		snippet = meta.get("snippet") if isinstance(meta, dict) else None
		out.append({"title": _id, "snippet": snippet or "", "score": distances[i] if i < len(distances) else None})

	return out

