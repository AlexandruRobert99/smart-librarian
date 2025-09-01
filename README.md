## Smart Librarian

Smart Librarian este un chatbot AI construit cu Streamlit, OpenAI GPT și ChromaDB, care recomandă cărți pe baza temelor sau intereselor utilizatorului. Sistemul folosește un vector store (RAG) pentru a găsi titluri relevante, iar apoi completează răspunsul cu un rezumat detaliat stocat local.

Funcționalități cheie:

🔎 RAG (Retrieval Augmented Generation): căutare semantică în baza de date de rezumate scurte (book_summaries.json).

💬 Chatbot conversațional: recomandă titluri și explică de ce se potrivesc.

📖 Tool get_summary_by_title: atașează rezumatul complet dintr-un dicționar local (tools.py).

🎙️ Speech-to-Text (STT): transcriere audio cu gpt-4o-mini-transcribe.

🔊 Text-to-Speech (TTS): ascultă recomandările cu gpt-4o-mini-tts.

🖼️ Generare imagini (opțional): copertă sugestivă pentru carte cu dall-e-3 sau gpt-image-1.

🌐 UI tip ChatGPT: construit în Streamlit, istoric în memorie (se pierde la refresh).

### Setup
1. Adaugă cheia ta OpenAI în fișierul `.env`:
	```env
	OPENAI_API_KEY=your-openai-key
	```
2. Build & run cu Docker:
	```sh
	docker build -t smart-librarian .
	docker run -p 8501:8501 --env-file .env smart-librarian
	```

### Accesează UI
Deschide [http://localhost:8501](http://localhost:8501) în browser.

### Structură
- `app/` — cod sursă modular
- `book_summaries.json` — dataset folosit pentru RAG
- `requirements.txt` — dependențe
- `Dockerfile` — container build
- `docker-compose.yml` — configurație de dezvoltare
- `.env` — fișier local cu variabile de mediu
- `.gitignore` / `.dockerignore` — fișiere ignorate
- `README.md` — documentație
