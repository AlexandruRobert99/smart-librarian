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

# Inject a nicer font and message-style CSS (WhatsApp-like alignment)
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    html, body, [class*="css"]  { font-family: 'Inter', system-ui, -apple-system, 'Segoe UI', Roboto, 'Helvetica Neue', Arial !important; }
    .message-row { display: flex; margin: 8px 0; }
    .message-row.user { justify-content: flex-end; }
    .message-row.assistant { justify-content: flex-start; }
    .message-frame { max-width: 85%; }
    .bubble { padding: 12px; border-radius: 14px; line-height: 1.35; box-shadow: 0 1px 0 rgba(0,0,0,0.04); }
    .bubble.user { background: #dcf8c6; color: #062006; border-bottom-right-radius: 4px; }
    .bubble.assistant { background: #f1f3f4; color: #111; border-bottom-left-radius: 4px; }
    .label { font-weight: 700; margin-bottom: 6px; font-size: 14px; }
    .label.user { text-align: right; color: #0b57d0; }
    .label.assistant { text-align: left; color: #c80815; }
    /* make the expander content align left as assistant replies */
    .stExpander > .stMarkdown, .stExpanderContent { text-align: left; }
    </style>
    """,
    unsafe_allow_html=True,
)


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
    # store generated media so they survive reruns
    if "generated_audio" not in st.session_state:
        st.session_state.generated_audio = None
    if "generated_image" not in st.session_state:
        st.session_state.generated_image = None


ensure_state()


def render_messages():
    for msg in st.session_state.messages:
        role = msg.get("role")
        text = msg.get("text", "")
        # Build safe HTML fragments and use CSS classes to control alignment
        safe = escape_html(text)
        if role == "user":
            # user: align right, 'Tu' label on the right
            html_snippet = (
                "<div class='message-row user'>"
                "  <div class='message-frame'>"
                "    <div class='label user'>Tu</div>"
                "    <div class='bubble user'>" + safe + "</div>"
                "  </div>"
                "</div>"
            )
            st.markdown(html_snippet, unsafe_allow_html=True)
        else:
            # assistant: align left
            if text.startswith("Rezumat detaliat"):
                with st.expander("Rezumat detaliat"):
                    st.write(text.replace("Rezumat detaliat:\n", ""))
            else:
                html_snippet = (
                    "<div class='message-row assistant'>"
                    "  <div class='message-frame'>"
                    "    <div class='label assistant'>Librarian</div>"
                    "    <div class='bubble assistant'>" + safe + "</div>"
                    "  </div>"
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


st.markdown("<h1 style='text-align:center; margin-bottom: 0.4rem'>📚 Smart Librarian</h1>", unsafe_allow_html=True)

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
    # Decide whether this response is a valid recommendation
    apology = "Îmi pare rău, nu vă pot ajuta cu informații despre acest subiect."
    has_title = bool(title)
    has_answer = bool(answer_text)
    is_apology = apology in (answer_text or "")

    if not has_title or not has_answer:
        # No useful recommendation returned
        st.session_state.messages.append({"role": "assistant", "text": "Nu am o recomandare relevantă pentru această temă. Încearcă să reformulezi."})
    elif is_apology:
        # Model explicitly refused — show refusal but do NOT update last_* so buttons keep previous valid reply
        st.session_state.messages.append({"role": "assistant", "text": answer_text})
    else:
        # Valid recommendation: update the 'last' fields and show answer + detailed summary
        st.session_state.last_title = title
        st.session_state.last_full_summary = full_summary
        st.session_state.last_answer_text = answer_text
        st.session_state.messages.append({"role": "assistant", "text": answer_text})
        if full_summary:
            st.session_state.messages.append({"role": "assistant", "text": "Rezumat detaliat:\n" + full_summary})

# Inline audio uploader (placed BEFORE the text area so we can send immediately)
# Action buttons (listen / generate cover) placed above the audio uploader
last_title = st.session_state.get("last_title")
last_answer_text = st.session_state.get("last_answer_text")
last_full = st.session_state.get("last_full_summary")
# Buttons: when clicked, store generated media in session_state so both can coexist
if last_title and last_answer_text:
    act_cols = st.columns([1, 1])
    with act_cols[0]:
        if st.button("🔊 Ascultă", key="audio_top"):
            combined = last_answer_text + "\n\n" + (last_full or "")
            audio = text_to_speech(combined)
            # store result (bytes or path) in session state
            st.session_state.generated_audio = audio

    with act_cols[1]:
        if HAS_IMAGE and st.button("🖼️ Generează coperta", key="image_top"):
            try:
                img = generate_book_image(last_title)
                st.session_state.generated_image = img
            except Exception as e:
                st.warning(f"Eroare la generarea imaginii: {e}")

    st.markdown("---")

    # render stored media so they persist across reruns
    media_cols = st.columns([1, 1])
    with media_cols[0]:
        ga = st.session_state.get("generated_audio")
        if ga:
            if isinstance(ga, (bytes, bytearray)):
                st.audio(ga, format="audio/mp3")
            elif isinstance(ga, str) and os.path.exists(ga):
                with open(ga, "rb") as f:
                    st.audio(f.read(), format="audio/mp3")
    with media_cols[1]:
        gi = st.session_state.get("generated_image")
        if gi:
            if isinstance(gi, (bytes, bytearray)):
                st.image(io.BytesIO(gi))
            elif isinstance(gi, str) and os.path.exists(gi):
                st.image(gi)

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

def handle_send():
    send_text(st.session_state.user_input)

# Full-width send button matching the conversation column
st.button("Trimite", use_container_width=True, on_click=handle_send)
    

