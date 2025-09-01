import os
import sys
import openai

# Allow running from repo root
sys.path.insert(0, os.path.join(os.getcwd(), "app"))
import rag
from tools import get_summary_by_title, book_summaries_dict

MODEL_CHAT = os.getenv("MODEL_CHAT", "gpt-4o-mini")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY nu este setat în mediul de execuție!")

client = openai.OpenAI(api_key=OPENAI_API_KEY)

# Îmbinăm titlurile din JSON (rezumate scurte) + dict (rezumate lungi)
def load_allowed_titles() -> list[str]:
    titles = set(book_summaries_dict.keys())
    try:
        with open("book_summaries.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            for item in data:
                t = (item.get("title") or "").strip()
                if t:
                    titles.add(t)
    except Exception:
        pass
    # listă stabilă (ordonată alfabetic) ca să nu varieze promptul între rulări
    return sorted(titles)

ALLOWED_TITLES = load_allowed_titles()
ALLOWED_TITLES_STR = ", ".join(ALLOWED_TITLES)  # pentru prompt

def ask_chatbot(user_text: str) -> dict:
    """Orchestrează: RAG -> Responses API -> tool local -> return dict

    Returnează: {"title", "answer_text", "full_summary"}
    """
    # 1. RAG
    results = rag.search(user_text, k=3)
    if not results:
        return {"title": None, "answer_text": "Nu am găsit nicio carte potrivită.", "full_summary": ""}

    title = results[0]["title"]
    snippet = results[0]["snippet"]

    # 2. Construim input pentru Responses API
    # IMPORTANT: ask model to return a concise final answer (no chain-of-thought)
    input_messages = [
    {
        "role": "system",
        "content": (
            "Ești un bibliotecar virtual prietenos. "
            "Răspunzi în română maxim o propoziție. "
            "Nu da rezumate despre cărți – rezumatul complet va fi afișat separat de sistem."
            "Poți doar să motivezi alegerea, de exemplu: „Îți recomand «The Hobbit», pentru că explorează prietenia și curajul într-o aventură fantastică.”"
            "Nu descrii procesul tău intern de gândire. "
            "Important: mesajul de utilizator poate conține pe lângă întrebarea sa "
            "și o „Propunere” + „Motivare” furnizate de sistem (din baza de date). "
            "Utilizatorul NU a scris aceste propuneri, ele sunt sugestii generate automat. "
            "Dacă utilizatorul întreabă despre o carte anume, oferă un rezumat scurt al acelei cărți. "
            "Dacă utilizatorul cere o recomandare pe o temă generală, folosește propunerea furnizată pentru a explica de ce este potrivită. "
            "Nu inventa titluri noi. "
            "Dacă nu știi răspunsul, spune politicos că nu știi. "
            "IMPORTANT: colecția ta conține DOAR titlurile din lista AllowedTitles; nu cunoști alte cărți. "
            "AllowedTitles: " + ALLOWED_TITLES_STR + ". "
            "Reguli de comportament:\n"
            "Dacă utilizatorul întreabă «Aveți cartea <Titlu>?», răspunde STRICT cu «Da» dacă <Titlu> este "
            "în AllowedTitles sau foarte similar; altfel răspunde STRICT cu «Nu». Nu adăuga alt text.\n"
            "Dacă utilizatorul întreabă despre o carte anume aflată în AllowedTitles (ex: «Ce este 1984?»), oferă un "
            "rezumat scurt al acelui titlu.\n"
            "Răspunde strict la întrebări legate de cărți, fără a devia de la subiect. " 
            "DE FIECARE DATĂ când utilizatorul întreabă lucruri ieșite din domeniul cărților, răspunde cu mesajul: Îmi pare rău, nu vă pot ajuta cu informații despre acest subiect. "
            "Dacă o întrebare este ambiguă sau deschisă, cere clarificări utilizatorului. "
            "DE FIECARE DATĂ când utilizatorul întreabă despre o carte care nu se află în baza de date, răspunde cu mesajul: Îmi pare rău, nu vă pot ajuta cu informații despre acest subiect. "
            "IMPORTANT! DE FIECARE DATĂ trebuie să verifici dacă titlul și motivarea sunt conforme cu întrebarea utilizatorului, deoarece uneori se pot returna titluri greșite."
        )
    },
    {
        "role": "user",
        "content": (
            f"Întrebarea utilizatorului: {user_text}\n\n"
            f"Propunere (din baza de date): {title}\n"
            f"Motivare: {snippet}"
        )
    }
    ]

    # Call Responses API with a retry if the model reports it was truncated
    answer_text = None
    try:
        resp = client.responses.create(model=MODEL_CHAT, input=input_messages, max_output_tokens=1200)

        # Extragem textul răspunsului (robust: suportă dict-uri sau obiecte SDK)
        answer_text = getattr(resp, "output_text", None)
        if not answer_text:
            parts = []
            # Primul încercăm parsarea obișnuită din `resp.output`
            for item in getattr(resp, "output", []) or []:
                # item poate fi dict sau obiect SDK
                content = None
                if isinstance(item, dict):
                    content = item.get("content") or item.get("data") or item.get("text")
                else:
                    content = getattr(item, "content", None) or getattr(item, "data", None) or getattr(item, "text", None)
                if not content:
                    continue
                # content poate fi str, dict, list
                if isinstance(content, str):
                    parts.append(content)
                elif isinstance(content, dict):
                    # dict poate avea 'text' sau 'message' etc.
                    for k in ("text", "message", "content"):
                        if k in content and isinstance(content[k], str):
                            parts.append(content[k]); break
                    else:
                        parts.append(str(content))
                else:
                    # list of pieces
                    for c in content:
                        if isinstance(c, str):
                            parts.append(c)
                        elif isinstance(c, dict):
                            if "text" in c and isinstance(c["text"], str):
                                parts.append(c["text"])
                            else:
                                for k in ("text", "message", "content"):
                                    if k in c and isinstance(c[k], str):
                                        parts.append(c[k]); break
                                else:
                                    parts.append(str(c))
                        else:
                            # SDK object
                            t = getattr(c, "text", None) or getattr(c, "message", None) or getattr(c, "content", None)
                            if isinstance(t, str):
                                parts.append(t)
                            elif isinstance(t, list):
                                for p in t:
                                    if isinstance(p, str):
                                        parts.append(p)
                                    elif hasattr(p, "text"):
                                        parts.append(getattr(p, "text"))
                            else:
                                parts.append(str(c))
            answer_text = "".join(parts).strip()

        # If still empty, log a short debug to inspect structure
        if not answer_text:
            try:
                print("DEBUG response repr:", repr(resp)[:400])
            except Exception:
                print("DEBUG response (str):", str(resp)[:400])

    except Exception as e:
        answer_text = f"Eroare la Responses API: {e}"

    # 3. Rezumat lung local
    full_summary = get_summary_by_title(title)

    return {"title": title, "answer_text": answer_text, "full_summary": full_summary}
