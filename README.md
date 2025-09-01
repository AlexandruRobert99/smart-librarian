## Smart Librarian

Smart Librarian este un chatbot AI construit cu Streamlit, OpenAI GPT și ChromaDB, care recomandă cărți pe baza temelor sau intereselor utilizatorului. Sistemul folosește un vector store (RAG) pentru a găsi titluri relevante, iar apoi completează răspunsul cu un rezumat detaliat stocat local.

Funcționalități cheie:

🔎 RAG (Retrieval Augmented Generation): căutare semantică în baza de date de rezumate scurte (book_summaries.json).

💬 Chatbot conversațional: recomandă titluri și explică de ce se potrivesc.

🎙️ Speech-to-Text (STT): transcriere audio cu gpt-4o-mini-transcribe.

🔊 Text-to-Speech (TTS): ascultă recomandările cu gpt-4o-mini-tts.

🖼️ Generare imagini: copertă sugestivă pentru carte cu dall-e-3.

🌐 UI tip ChatGPT: construit în Streamlit, istoric în memorie (se pierde la refresh).

### Setup
1. Crează un fișier `.env` în rădăcina proiectului cu următoarea schemă (înlocuiește `sk-xxx` cu cheia ta OpenAI):

```env
OPENAI_API_KEY=sk-xxx
CHROMA_DIR=./.chroma

# Modele
MODEL_CHAT=gpt-4o-mini
MODEL_EMBED=text-embedding-3-small
MODEL_STT=whisper-1
MODEL_TTS=gpt-4o-mini-tts
MODEL_IMAGE=dall-e-3
```

- `CHROMA_DIR` este directorul local folosit pentru stocarea bazei de date Chroma. Poți modifica calea după preferințe.


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
