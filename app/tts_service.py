import os
from openai import OpenAI

MODEL_TTS = os.getenv("MODEL_TTS", "gpt-4o-mini-tts")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY nu este setat în mediul de execuție!")

client = OpenAI(api_key=OPENAI_API_KEY)

def text_to_speech(text: str) -> bytes:
    """Generează voce (MP3) din text și returnează audio ca bytes."""
    try:
        with client.audio.speech.with_streaming_response.create(
            model=MODEL_TTS,
            voice="alloy",
            input=text
        ) as response:
            return response.read()
    except Exception as e:
        print(f"Eroare la TTS: {e}")
        return b""
