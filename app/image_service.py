import base64
import os
from typing import Optional
from openai import OpenAI
import urllib.request
import ssl

# dacă nu ai org „verified” pentru gpt-image-1, mergi pe dall-e-3
MODEL_IMAGE = os.getenv("MODEL_IMAGE", "dall-e-3")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    # allow client to be created without explicit key if environment or runtime already provides it
    client = OpenAI()
else:
    client = OpenAI(api_key=OPENAI_API_KEY)


def _find_b64_in_response(res) -> Optional[str]:
    # common new SDK shape: res.data[0].b64_json
    data = getattr(res, "data", None)
    if data and len(data) > 0:
        first = data[0]
        if isinstance(first, dict):
            return first.get("b64_json") or first.get("b64")
        else:
            return getattr(first, "b64_json", None) or getattr(first, "b64", None)

    # older/alternate shapes: try output -> content -> image
    for out in getattr(res, "output", []) or []:
        content = None
        if isinstance(out, dict):
            content = out.get("content")
        else:
            content = getattr(out, "content", None)
        if not content:
            continue
        # content may be list
        items = content if isinstance(content, list) else [content]
        for itm in items:
            if isinstance(itm, dict):
                # {"image": {"b64_json": ...}}
                img = itm.get("image") or itm.get("data") or itm.get("result")
                if isinstance(img, dict):
                    b = img.get("b64_json") or img.get("b64")
                    if b:
                        return b
    return None


def generate_book_image(title: str, themes: str = "") -> str:
    """Generează o imagine sugestivă pentru o carte cu Images API.
    Returnează path-ul fișierului PNG salvat local.
    """
    prompt = f"Book cover illustration for '{title}'. Themes: {themes}. Clean composition, no text."
    image_b64: Optional[str] = None

    try:
        res = client.images.generate(model=MODEL_IMAGE, prompt=prompt, size="1024x1024", timeout=60)
        image_b64 = _find_b64_in_response(res)
    except Exception as e:
        # bubble up after attempting to inspect response
        raise RuntimeError(f"Error calling Images API: {e}")

    if not image_b64:
        # If API returned a URL (common for DALL·E), try to download it
        # Look for data[0].url
        data = getattr(res, "data", None) or []
        img_url = None
        if data and len(data) > 0:
            first = data[0]
            if isinstance(first, dict):
                img_url = first.get("url") or first.get("image_url")
            else:
                img_url = getattr(first, "url", None) or getattr(first, "image_url", None)

        if img_url:
            try:
                # allow downloading from self-signed etc. if needed
                ctx = ssl.create_default_context()
                with urllib.request.urlopen(img_url, context=ctx, timeout=30) as resp:
                    img_bytes = resp.read()
            except Exception as e:
                raise RuntimeError(f"Nu am primit base64 pentru imagine și descărcarea URL-ului a eșuat: {e}")
        else:
            # include a short repr to help debugging (avoid huge dumps)
            try:
                snippet = repr(res)[:1000]
            except Exception:
                snippet = "(unable to repr response)"
            raise RuntimeError(f"Nu am primit base64 pentru imagine din API și nu am găsit URL. Response snippet: {snippet}")

    if image_b64:
        try:
            img_bytes = base64.b64decode(image_b64)
        except Exception as e:
            raise RuntimeError(f"Eroare la decodarea base64 a imaginii: {e}")

    safe_title = title.replace(" ", "_").replace("'", "")
    file_path = f"cover_{safe_title}.png"
    with open(file_path, "wb") as f:
        f.write(img_bytes)
    return file_path
