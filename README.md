## Smart Librarian

Un POC care recomandă cărți pe baza temelor tale, folosind un index semantic local (Chroma) și OpenAI pentru generare de răspunsuri, transcriere și sinteză audio. Interfață simplă în Streamlit, istoric de sesiune (fără persistență). 

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
