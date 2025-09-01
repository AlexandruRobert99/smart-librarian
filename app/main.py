import os
import io
import sys
import os
import html
import streamlit as st

# import sibling modules (main.py runs from the `app/` folder)
sys.path.insert(0, os.path.dirname(__file__))
from chat_service import ask_chatbot, client
from stt_service import transcribe_audio
from streamlit_mic_recorder import mic_recorder
from tts_service import text_to_speech

try:
    from image_service import generate_book_image
    HAS_IMAGE = True
except Exception:
    HAS_IMAGE = False

# px constant for textarea and mic size
# Start textarea at a minimal practical height (px).
# Assumption: 40px is a reasonable minimal starting height for a single-line textarea.
TEXTAREA_HEIGHT = 40  # px – poți schimba oricând
st.set_page_config(page_title="Smart Librarian", page_icon="📚", layout="centered")

# Inject a nicer font and message-style CSS (WhatsApp-like alignment)
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    html, body, [class*="css"]  { font-family: 'Inter', system-ui, -apple-system, 'Segoe UI', Roboto, 'Helvetica Neue', Arial !important; }
    .message-row { display: flex; margin: 4px 0 !important; }
    .message-row.user { justify-content: flex-end; }
    .message-row.assistant { justify-content: flex-start; }
    .message-frame { max-width: 85%; margin-bottom: 4px !important; }
    .bubble { padding: 12px; border-radius: 14px; line-height: 1.35; box-shadow: 0 1px 0 rgba(0,0,0,0.04); }
    .bubble.user { background: #dcf8c6; color: #062006; border-bottom-right-radius: 4px; }
    .bubble.assistant { background: #f1f3f4; color: #111; border-bottom-left-radius: 4px; }
    .label { font-weight: 700; margin-bottom: 6px; font-size: 14px; }
    .label.user { text-align: right; color: #0b57d0; font-size: 24px; }
    .label.assistant { text-align: left; color: #c80815; font-size: 24px; }
    /* make the expander content align left as assistant replies */
    .stExpander > .stMarkdown, .stExpanderContent { text-align: left; }
    /* mic recorder wrapper button styling: make the mic a circular button matching the
       textarea height (100px). Target common nested patterns used by recorder components
       and Streamlit so the visible element is a single circular control. */
        #mic-wrapper { display: flex; align-items: center; justify-content: center; height: 100%; }
    /* Make the mic the same height as the textarea and a circle; use the
       CSS variable --mic-size so changing TEXTAREA_HEIGHT updates everything. */
    #mic-wrapper button,
    #mic-wrapper .stButton>button,
    #mic-wrapper .stButton>div>button,
    #mic-wrapper [role="button"] { 
        width: var(--mic-size) !important;
        height: var(--mic-size) !important;
        min-width: var(--mic-size) !important;
        min-height: var(--mic-size) !important;
        padding: 0 !important;
        border-radius: 50% !important; /* perfect circle */
        background: #0b57d0 !important;
        color: #fff !important;
        border: none !important;
        box-shadow: 0 6px 16px rgba(11,87,208,0.24) !important;
        font-size: calc(var(--mic-size) * 0.18) !important;
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
        outline: none !important;
    }
    /* ensure SVG/icon size */
    #mic-wrapper button svg, #mic-wrapper .stButton>button svg { width: calc(var(--mic-size) * 0.26) !important; height: calc(var(--mic-size) * 0.26) !important; }
    #mic-wrapper button:active, #mic-wrapper .stButton>button:active { transform: scale(0.96); }
    /* normalize outer containers that some recorder versions render */
    #mic-wrapper > div, #mic-wrapper > div > div, #mic-wrapper .stButton, #mic-wrapper .stButton > div { background: transparent !important; padding: 0 !important; margin: 0 !important; box-shadow: none !important; border: none !important; }
    /* capture cases where the component nests the real clickable inside divs */
    #mic-wrapper .stButton > div > button, #mic-wrapper .stButton > div > div > button { padding:0 !important; margin:0 !important; }
    /* force the clickable element to be the circular button */
    #mic-wrapper [role="button"], #mic-wrapper .stButton>button, #mic-wrapper > div > button { width: var(--mic-size) !important; height: var(--mic-size) !important; min-width:var(--mic-size) !important; min-height:var(--mic-size) !important; border-radius:50% !important; padding:0 !important; display:flex !important; align-items:center !important; justify-content:center !important; background:#0b57d0 !important; color:#fff !important; box-shadow: 0 6px 16px rgba(11,87,208,0.24) !important; }
    /* specifically target recorder's custom button class (seen in your snippet) */
    #mic-wrapper .myButton, #mic-wrapper button.myButton {
        width: 100% !important;
        height: 100% !important;
        min-width: 100% !important;
        min-height: 100% !important;
        padding: 0 !important; /* keep center alignment */
        border-radius: 50% !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        background: #0b57d0 !important; /* override inline bg */
        color: #fff !important; /* override inline color */
        border: none !important; /* override inline border-color */
        box-shadow: 0 6px 16px rgba(11,87,208,0.24) !important;
        font-size: calc(var(--mic-size) * 0.45) !important; /* make the emoji large */
        line-height: 1 !important;
    }
    /* hide extraneous small squares, borders and backgrounds */
    #mic-wrapper div[style], #mic-wrapper .small-square, #mic-wrapper .square { background: transparent !important; border: none !important; box-shadow: none !important; }
    /* additional fallbacks: keep wrappers flexible and only size the real button */
    #mic-wrapper > div { background: transparent !important; padding: 0 !important; margin: 0 !important; display: flex !important; align-items: center !important; justify-content: center !important; }
    /* the actual clickable button inside whatever wrapper the component renders */
    #mic-wrapper > div > button { background: #0b57d0 !important; color: #fff !important; width: var(--mic-size) !important; height: var(--mic-size) !important; border-radius: 50% !important; display:flex !important; align-items:center !important; justify-content:center !important; padding:0 !important; border:none !important; }
    #mic-wrapper .stButton, #mic-wrapper .stButton>div { background: transparent !important; padding: 0 !important; margin: 0 !important; box-shadow: none !important; }
    /* hide any inner small square elements that some versions render; keep the svg/icon visible */
    #mic-wrapper .recorder-icon, #mic-wrapper .icon, #mic-wrapper .small-square { background: transparent !important; width: auto !important; height: auto !important; }
    /* explicitly neutralize Streamlit button wrapper and component containers around the recorder */
    #mic-wrapper .stButton, #mic-wrapper .stButton>div, #mic-wrapper .streamlit-expanderHeader { background: transparent !important; border: none !important; box-shadow: none !important; padding: 0 !important; margin: 0 !important; }
    /* make sure Streamlit wrapper doesn't force a different shape; keep it flexible */
    #mic-wrapper .stButton { border-radius: 0 !important; display:flex !important; align-items:center !important; justify-content:center !important; }
    /* Sidebar specific: fundal #181818 și text deschis */
    section[data-testid="stSidebar"], div[data-testid="stSidebar"], .stSidebar {
        background-color: #181818 !important;
        color: #e0e0e0 !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Ensure the mic button matches the textarea height defined above. We use a CSS variable
# so changing TEXTAREA_HEIGHT updates both textarea and recorder button.
st.markdown(f"""
<style>
/* default fallback mic size — use the TEXTAREA_HEIGHT so mic starts equal to textarea */
:root {{ --mic-size: {TEXTAREA_HEIGHT}px; }}

/* Make the mic-wrapper an exact square and center its contents. The real
   clickable element should fill the wrapper so nested wrappers don't change size. */
#mic-wrapper {{
    width: var(--mic-size) !important;
    height: var(--mic-size) !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    margin: 0 !important; padding: 0 !important; overflow: visible !important;
}}

/* The button (or any element with role=button) should fill the wrapper */
#mic-wrapper button, #mic-wrapper [role="button"] {{
    width: 100% !important;
    height: 100% !important;
    border-radius: 50% !important;
    padding: 0 !important;
    background: #0b57d0 !important;
    color: #fff !important;
    display: flex !important; align-items: center !important; justify-content: center !important;
    box-shadow: 0 6px 16px rgba(11,87,208,0.24) !important;
}}

/* Icon scaling */
#mic-wrapper svg {{ width: calc(var(--mic-size) * 0.32) !important; height: calc(var(--mic-size) * 0.32) !important; }}

</style>
""", unsafe_allow_html=True)


def ensure_state():
    if "messages" not in st.session_state:
        st.session_state.messages = []
        # initial assistant greeting
        st.session_state.messages.append({"role": "assistant", "text": "Salut! Cu ce te pot ajuta?"})
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
    if "recorder_last_id" not in st.session_state:
        st.session_state.recorder_last_id = 0


ensure_state()


def is_moderation_flagged(text: str) -> tuple[bool, dict]:
    """Use OpenAI Moderation API to check text. Returns (flagged, details).

    If the moderation call fails we return (False, {}) to avoid blocking on
    infra problems; you can change this behavior to fail-closed if desired.
    """
    try:
        if not text:
            return False, {}
        resp = client.moderations.create(model="omni-moderation-latest", input=text)
        # SDK may return an object with .results or a dict
        results = None
        if isinstance(resp, dict):
            results = resp.get("results")
        else:
            results = getattr(resp, "results", None)
        if not results:
            return False, {}
        first = results[0]
        flagged = False
        if isinstance(first, dict):
            flagged = bool(first.get("flagged"))
        else:
            flagged = bool(getattr(first, "flagged", False))
        return flagged, first
    except Exception:
        # Do not block on moderation API errors by default
        return False, {}


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
    st.header("Smart Librarian")
    st.markdown("""
    **Funcții principale:**
    - Pune întrebări despre cărți și autori
    - Primește recomandări personalizate
    - Ascultă răspunsurile generate (Text-to-Speech)
    - Generează coperta unei cărți
    - Transcrie mesaje audio (Speech-to-Text)
    """)

    st.markdown("---")
    st.markdown("**Modele folosite:**")
    st.write("chat: gpt-4o-mini")
    st.write("embeddings: text-embedding-3-small")
    st.write("tts: gpt-4o-mini-tts")
    st.write("stt: gpt-4o-mini-transcribe")
    st.write("image: dall-e-3")
    st.caption("Istoricul conversației se pierde la refresh (session-only).")


st.markdown("<h1 style='text-align:center; margin-bottom: 0.4rem'>📚 Smart Librarian</h1>", unsafe_allow_html=True)

# Process any recorder output stored by the component (key + '_output') so that
# messages created from the recording appear in the same run before rendering.
RECORDER_KEY = 'browser_recorder'
rec_out_key = RECORDER_KEY + '_output'
if rec_out_key in st.session_state and st.session_state.get(rec_out_key):
    audio_dict = st.session_state.get(rec_out_key)
    try:
        rid = int(audio_dict.get('id', 0))
    except Exception:
        rid = 0
    if rid and rid > st.session_state.recorder_last_id:
        st.session_state.recorder_last_id = rid
        audio_bytes = audio_dict.get('bytes')
        if audio_bytes:
            try:
                audio_io = io.BytesIO(audio_bytes)
                audio_io.name = 'recording.wav'
                res = transcribe_audio(audio_io)
            except Exception as e:
                st.session_state.messages.append({"role": "assistant", "text": f"Eroare STT: {e}"})
                res = None

            if isinstance(res, str) and res.startswith("Eroare"):
                st.session_state.messages.append({"role": "assistant", "text": res})
            elif res:
                user_text = res
                # Moderation check on transcribed text
                flagged, _ = is_moderation_flagged(user_text)
                if flagged:
                    st.session_state.messages.append({"role": "user", "text": user_text})
                    st.session_state.messages.append({"role": "assistant", "text": "Îmi pare, nu pot procesa mesaje care conțin limbaj ofensator. Te rog reformulează."})
                    st.rerun()
                st.session_state.messages.append({"role": "user", "text": user_text})
                placeholder_text = "Generare răspuns..."
                st.session_state.messages.append({"role": "assistant", "text": placeholder_text})
                placeholder_idx = len(st.session_state.messages) - 1
                try:
                    out = ask_chatbot(user_text)
                except Exception as e:
                    st.session_state.messages[placeholder_idx] = {"role": "assistant", "text": f"Eroare la generare: {e}"}
                    out = None

                if out:
                    title = out.get("title")
                    answer_text = out.get("answer_text", "")
                    full_summary = out.get("full_summary", "")
                    apology = "Îmi pare rău, nu vă pot ajuta cu informații despre acest subiect."
                    has_title = bool(title)
                    has_answer = bool(answer_text)
                    is_apology = apology in (answer_text or "")

                    if not has_title or not has_answer:
                        st.session_state.messages[placeholder_idx] = {"role": "assistant", "text": "Nu am o recomandare relevantă pentru această temă. Încearcă să reformulezi."}
                    elif is_apology:
                        # If the model refused, show only the canonical apology text (avoid extra descriptions)
                        st.session_state.messages[placeholder_idx] = {"role": "assistant", "text": apology}
                    else:
                        st.session_state.last_title = title
                        st.session_state.last_full_summary = full_summary
                        st.session_state.last_answer_text = answer_text
                        st.session_state.messages[placeholder_idx] = {"role": "assistant", "text": answer_text}
                        if full_summary:
                            st.session_state.messages.insert(placeholder_idx + 1, {"role": "assistant", "text": "Rezumat detaliat:\n" + full_summary})
                        # Force an immediate rerun so the newly appended messages render now
                        st.rerun()


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
    # Moderation check before sending to the LLM
    flagged, _ = is_moderation_flagged(text)
    if flagged:
        st.session_state.messages.append({"role": "assistant", "text": "Îmi pare, nu pot procesa mesaje care conțin limbaj ofensator. Te rog reformulează."})
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
        # Model explicitly refused — show only the canonical refusal text and do NOT update last_*
        st.session_state.messages.append({"role": "assistant", "text": apology})
    else:
        # Valid recommendation: update the 'last' fields and show answer + detailed summary
        st.session_state.last_title = title
        st.session_state.last_full_summary = full_summary
        st.session_state.last_answer_text = answer_text
        st.session_state.messages.append({"role": "assistant", "text": answer_text})
        if full_summary:
            st.session_state.messages.append({"role": "assistant", "text": "Rezumat detaliat:\n" + full_summary})
    # Force immediate rerun so typed messages show now
    st.rerun()

# Now render messages so any new items appended above (e.g., by recorder processing)
# are visible immediately in this run.
render_messages()

# removed one horizontal divider here to reduce vertical gaps

# ---------- Acțiuni secundare pentru ultimul răspuns (audio/cover) ----------
last_title = st.session_state.get("last_title")
last_answer_text = st.session_state.get("last_answer_text")
last_full = st.session_state.get("last_full_summary")

# Render the buttons only after we have a valid assistant reply (title + answer_text).
action_placeholder = st.empty()
can_show_actions = bool(last_title and last_answer_text)
if can_show_actions:
    cols = action_placeholder.columns([1, 1])
    with cols[0]:
        def _handle_play():
            if last_title and last_answer_text:
                combined = last_answer_text + "\n\n" + (last_full or "")
                audio = text_to_speech(combined)
                st.session_state.generated_audio = audio
        st.button("🔊 Ascultă", key="audio_top", on_click=_handle_play)

    with cols[1]:
        def _handle_image():
            if last_title:
                try:
                    img = generate_book_image(last_title)
                    st.session_state.generated_image = img
                except Exception as e:
                    st.warning(f"Eroare la generarea imaginii: {e}")
        if HAS_IMAGE:
            st.button("🖼️ Generează coperta", key="image_top", on_click=_handle_image)
        else:
            # Keep layout consistent when image generation isn't available
            st.button("🖼️ Generează coperta", key="image_top", disabled=True)

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

    

# Input area with recorder on the right (simple in-browser recorder)
col1, col2 = st.columns([5, 1], vertical_alignment="center")
with col1:
    user_input = st.text_area("Mesaj", value=st.session_state.user_input, key="user_input", placeholder="Scrie aici…", height=TEXTAREA_HEIGHT, label_visibility="visible")
with col2:
    # Wrap the recorder so we can target the internal button with CSS and
    # ensure the wrapper uses the same height as the textarea constant.
    st.markdown("<div id='mic-wrapper' style='display:flex; align-items:center; justify-content:center;'>", unsafe_allow_html=True)
    # Capture the immediate return value so the first start/stop can be handled
    # disable use_container_width so the recorder doesn't stretch the wrapper
    rec_audio = mic_recorder(start_prompt="🎤", stop_prompt="🛑", key=RECORDER_KEY, use_container_width=False, just_once=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Inject JS: use ResizeObserver to keep --mic-size synced to the textarea height
    # This is more robust than a one-time measurement and handles user resizes.
    st.markdown(
        """
        <script>
        (function(){
            function setMicSizeFromTextarea(ta){
                try{
                    if(!ta) return;
                    const rect = ta.getBoundingClientRect();
                    const h = Math.ceil(rect.height);
                    document.documentElement.style.setProperty('--mic-size', h + 'px');
                }catch(e){ console && console.warn && console.warn('setMicSizeFromTextarea failed', e); }
            }

            function initObserver(){
                const ta = document.querySelector('textarea');
                if(!ta) return false;
                // initial set
                setMicSizeFromTextarea(ta);
                // observe height changes
                try{
                    const ro = new ResizeObserver(entries => {
                        for(const ent of entries){
                            setMicSizeFromTextarea(ent.target);
                        }
                    });
                    ro.observe(ta);
                }catch(e){ /* ResizeObserver may not be available in old browsers */ }
                // also update on window resize as a fallback
                window.addEventListener('resize', function(){ setMicSizeFromTextarea(ta); });
                return true;
            }

            function readyInit(){
                if(!initObserver()){
                    // retry shortly if textarea not yet present
                    setTimeout(readyInit, 250);
                }
            }

            if(document.readyState === 'complete' || document.readyState === 'interactive'){
                readyInit();
            } else {
                window.addEventListener('DOMContentLoaded', readyInit);
            }
        })();
        </script>
        """,
        unsafe_allow_html=True,
    )

def handle_send():
    send_text(st.session_state.user_input)

# Full-width send button matching the conversation column
st.button("Trimite", use_container_width=True, on_click=handle_send)
    
# -------------------- PROCESS IMMEDIATE RECORDER RETURN --------------------
if 'rec_audio' in locals() and rec_audio:
    try:
        rid = int(rec_audio.get('id', 0))
    except Exception:
        rid = 0
    if rid and rid > st.session_state.recorder_last_id:
        st.session_state.recorder_last_id = rid
        audio_bytes = rec_audio.get('bytes')
        if audio_bytes:
            try:
                audio_io = io.BytesIO(audio_bytes)
                audio_io.name = 'recording.wav'
                res = transcribe_audio(audio_io)
            except Exception as e:
                st.session_state.messages.append({"role": "assistant", "text": f"Eroare STT: {e}"})
                res = None

            if isinstance(res, str) and res.startswith("Eroare"):
                st.session_state.messages.append({"role": "assistant", "text": res})
            elif res:
                user_text = res
                # Moderation check on immediate transcription
                flagged, _ = is_moderation_flagged(user_text)
                if flagged:
                    st.session_state.messages.append({"role": "user", "text": user_text})
                    st.session_state.messages.append({"role": "assistant", "text": "Îmi pare, nu pot procesa mesaje care conțin limbaj ofensator. Te rog reformulează."})
                    st.rerun()
                st.session_state.messages.append({"role": "user", "text": user_text})
                placeholder_text = "Generare răspuns..."
                st.session_state.messages.append({"role": "assistant", "text": placeholder_text})
                placeholder_idx = len(st.session_state.messages) - 1
                try:
                    out = ask_chatbot(user_text)
                except Exception as e:
                    st.session_state.messages[placeholder_idx] = {"role": "assistant", "text": f"Eroare la generare: {e}"}
                    out = None

                if out:
                    title = out.get("title")
                    answer_text = out.get("answer_text", "")
                    full_summary = out.get("full_summary", "")
                    apology = "Îmi pare rău, nu vă pot ajuta cu informații despre acest subiect."
                    has_title = bool(title)
                    has_answer = bool(answer_text)
                    is_apology = apology in (answer_text or "")

                    if not has_title or not has_answer:
                        st.session_state.messages[placeholder_idx] = {"role": "assistant", "text": "Nu am o recomandare relevantă pentru această temă. Încearcă să reformulezi."}
                    elif is_apology:
                        # If the model refused, show only the canonical apology text (avoid extra descriptions)
                        st.session_state.messages[placeholder_idx] = {"role": "assistant", "text": apology}
                    else:
                        st.session_state.last_title = title
                        st.session_state.last_full_summary = full_summary
                        st.session_state.last_answer_text = answer_text
                        st.session_state.messages[placeholder_idx] = {"role": "assistant", "text": answer_text}
                        if full_summary:
                            st.session_state.messages.insert(placeholder_idx + 1, {"role": "assistant", "text": "Rezumat detaliat:\n" + full_summary})

                # Force immediate rerun to show transcript and response
                st.rerun()
