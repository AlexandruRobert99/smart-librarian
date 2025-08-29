## Smart Librarian POC

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
- `requirements.txt` — dependențe
- `Dockerfile` — build container
- `.env` — cheie OpenAI
