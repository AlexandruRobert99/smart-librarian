import os
import io
import sys
import os
import html
import streamlit as st

# import sibling modules (main.py runs from the `app/` folder)
sys.path.insert(0, os.path.dirname(__file__))
from chat_service import ask_chatbot
from stt_service import transcribe_audio
from tts_service import text_to_speech

try:
    from image_service import generate_book_image
    HAS_IMAGE = True
except Exception:
    HAS_IMAGE = False


st.set_page_config(page_title="Smart Librarian", page_icon="📚", layout="centered")


def ensure_state():
    if "messages" not in st.session_state:
        st.session_state.messages = []
        # initial assistant greeting
        st.session_state.messages.append({"role": "assistant", "text": "Salut! Spune-mi ce temă te interesează și îți recomand o carte."})
    if "pending_audio" not in st.session_state:
        st.session_state.pending_audio = None
    if "user_input" not in st.session_state:
        st.session_state.user_input = ""
    if "just_sent" not in st.session_state:
        st.session_state.just_sent = False


ensure_state()


def render_messages():
    for msg in st.session_state.messages:
        role = msg.get("role")
        text = msg.get("text", "")
        if role == "user":
            safe = escape_html(text)
            # user bubble: name above, green bubble
            html_snippet = (
                "<div style='margin:8px 0'>"
                "<div style='font-size:12px;font-weight:600;margin-bottom:4px;color:#145214'>Tu</div>"
                "<div style='background:#d6f5d6;color:#062006;padding:12px;border-radius:12px;margin:0;max-width:85%'>" + safe + "</div>"
                "</div>"
            )
            st.markdown(html_snippet, unsafe_allow_html=True)
        else:
            # assistant
            if text.startswith("Rezumat detaliat"):
                with st.expander("Rezumat detaliat"):
                    st.write(text.replace("Rezumat detaliat:\n", ""))
            else:
                safe = escape_html(text)
                # assistant bubble: name above, grey bubble
                html_snippet = (
                    "<div style='margin:8px 0'>"
                    "<div style='font-size:12px;font-weight:600;margin-bottom:4px;color:#333'>Librarian</div>"
                    "<div style='background:#cbd2d9;color:#111;padding:12px;border-radius:12px;margin:0;max-width:85%'>" + safe + "</div>"
                    "</div>"
                )
                st.markdown(html_snippet, unsafe_allow_html=True)


def escape_html(s: str) -> str:
    """Escape text for safe insertion into an HTML snippet in Streamlit."""
    if s is None:
        return ""
    return html.escape(s).replace('\n', '<br/>')


with st.sidebar:
    st.header("Audio (STT)")
    st.markdown("Pentru transcriere, încarcă un fișier audio sau folosește butonul de înregistrare (dacă este disponibil).")

    st.markdown("---")
    st.markdown("**Modele folosite:**")
    st.write("chat: gpt-4o-mini")
    st.write("embeddings: text-embedding-3-small")
    st.write("tts: gpt-4o-mini-tts")
    st.write("stt: gpt-4o-mini-transcribe")
    st.write("image: dall-e-3")
    st.caption("Istoricul conversației se pierde la refresh (session-only).")


st.title("📚 Smart Librarian — RAG + Tool")

render_messages()

st.markdown("---")

# If we just sent a message in the previous run, clear the input before creating the widget
if st.session_state.get("just_sent"):
    st.session_state.user_input = ""
    st.session_state.just_sent = False

# Reusable send function so uploader can call it before widgets are created
def send_text(text: str):
    text = (text or "").strip()
    if not text:
        st.session_state.messages.append({"role": "assistant", "text": "Te rog introdu un mesaj."})
        return
    st.session_state.messages.append({"role": "user", "text": text})
    st.session_state.user_input = ""
    out = ask_chatbot(text)
    title = out.get("title")
    answer_text = out.get("answer_text", "")
    full_summary = out.get("full_summary", "")
    st.session_state.last_title = title
    st.session_state.last_full_summary = full_summary
    st.session_state.last_answer_text = answer_text
    if not title or not answer_text:
        st.session_state.messages.append({"role": "assistant", "text": "Nu am o recomandare relevantă pentru această temă. Încearcă să reformulezi."})
    else:
        st.session_state.messages.append({"role": "assistant", "text": answer_text})
        st.session_state.messages.append({"role": "assistant", "text": "Rezumat detaliat:\n" + full_summary})

# Inline audio uploader (placed BEFORE the text area so we can send immediately)
st.markdown("**Audio:** Încarcă un fișier pentru transcriere")
uploaded_inline = st.file_uploader("Încarcă audio pentru transcriere", type=["wav", "mp3", "m4a", "ogg", "flac"], key="uploader_inline")
if uploaded_inline is not None:
    # define a callback that will run before Streamlit reruns the script
    def _transcribe_and_send(f):
        res = transcribe_audio(f)
        if isinstance(res, str) and res.startswith("Eroare"):
            # append an assistant-style error so user sees it immediately on rerun
            st.session_state.messages.append({"role": "assistant", "text": res})
        else:
            send_text(res)

    st.button("Transcrie și trimite ca mesaj", key="transcribe_inline", on_click=_transcribe_and_send, args=(uploaded_inline,))

# Input area with recorder on the right (simple in-browser recorder)
user_input = st.text_area("Mesaj", value=st.session_state.user_input, key="user_input", placeholder="Scrie aici…", height=100, label_visibility="visible")

col1, col2 = st.columns([8, 1])
with col1:
    def handle_send():
        send_text(st.session_state.user_input)

    send = st.button("Trimite", use_container_width=True, on_click=handle_send)
with col2:
    # small placeholder column (reserved for icons / future recorder)
    st.write("")
    

# After messages are rendered, show action buttons for the last assistant reply if available
last_title = st.session_state.get("last_title")
last_answer_text = st.session_state.get("last_answer_text")
last_full = st.session_state.get("last_full_summary")
if last_title and last_answer_text:
    act_cols = st.columns([1, 1])
    with act_cols[0]:
        if st.button("🔊 Ascultă"):
            combined = last_answer_text + "\n\n" + (last_full or "")
            audio = text_to_speech(combined)
            if isinstance(audio, (bytes, bytearray)):
                st.audio(audio, format="audio/mp3")
            elif isinstance(audio, str) and os.path.exists(audio):
                with open(audio, "rb") as f:
                    st.audio(f.read(), format="audio/mp3")
            else:
                st.warning("Nu am putut genera audio.")

    with act_cols[1]:
        if HAS_IMAGE and st.button("🖼️ Generează coperta"):
            try:
                img = generate_book_image(last_title)
                if isinstance(img, (bytes, bytearray)):
                    st.image(io.BytesIO(img))
                elif isinstance(img, str) and os.path.exists(img):
                    st.image(img)
                else:
                    st.warning("Imaginea a fost generată, dar nu am putut afișa rezultatul.")
            except Exception as e:
                st.warning(f"Eroare la generarea imaginii: {e}")

    st.markdown("---")
