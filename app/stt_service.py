import os
from typing import BinaryIO
from openai import OpenAI

MODEL_STT = os.getenv("MODEL_STT", "gpt-4o-mini-transcribe")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY nu este setat în mediul de execuție!")

client = OpenAI(api_key=OPENAI_API_KEY)

def transcribe_audio(file_like: BinaryIO) -> str:
    """Transcrie un fișier audio și returnează textul.

    Exemplu:
        with open("sample.wav","rb") as f:
            text = transcribe_audio(f)
    """
    try:
        file_like.seek(0)
        resp = client.audio.transcriptions.create(
            model=MODEL_STT,
            file=file_like,
        )
        return resp.text.strip()
    except Exception as e:
        return f"Eroare la transcriere: {e}"
