import os
import smtplib
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import streamlit as st

# When executed directly via `python app.py` or editor play button, automatically launch Streamlit
try:
    from streamlit.runtime import exists as _runtime_exists

    if not _runtime_exists():
        import sys
        from streamlit.web import cli as stcli

        sys.argv = ["streamlit", "run", __file__]
        sys.exit(stcli.main())
except ImportError:
    pass

from google import genai
from google.genai import types

from prompts import SUMMARY_REQUEST_PROMPT, SYSTEM_PROMPT, WELCOME_MESSAGE_TEMPLATE

# --- Application Configuration ---
st.set_page_config(
    page_title="Snap & Learn — AI Study Buddy",
    page_icon="📚",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# Custom Styling for modern, premium study experience
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    
    .stApp {
        background: radial-gradient(circle at top right, rgba(99, 102, 241, 0.04), transparent 40%),
                    radial-gradient(circle at bottom left, rgba(168, 85, 247, 0.04), transparent 40%);
    }
    
    /* Header & Badges */
    .hero-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.12), rgba(168, 85, 247, 0.12));
        color: #6366f1;
        padding: 4px 12px;
        border-radius: 9999px;
        font-size: 0.85rem;
        font-weight: 600;
        margin-bottom: 8px;
        border: 1px solid rgba(99, 102, 241, 0.2);
    }
    
    /* Button enhancements */
    .stButton > button {
        border-radius: 10px;
        font-weight: 600;
        transition: all 0.2s ease;
    }
    
    /* Email action button */
    div[data-testid="stButton"] > button[kind="primary"] {
        background: linear-gradient(135deg, #4f46e5, #7c3aed);
        border: none;
        color: white;
    }
    
    /* Input styling */
    .stChatInputContainer {
        border-radius: 16px !important;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.04);
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- Configuration & Secrets Handling ---
MODEL_NAME = st.secrets.get("GEMINI_MODEL", "gemini-3.8-flash")


# Helper to retrieve secret or environment variable
def get_secret(key, default=""):
    try:
        val = st.secrets.get(key, "")
        if val and not val.startswith("your-"):
            return val
    except Exception:
        pass
    return os.environ.get(key, default)


GEMINI_API_KEY = get_secret("GEMINI_API_KEY", "")
GMAIL_ADDRESS = get_secret("GMAIL_ADDRESS", "")
GMAIL_APP_PASSWORD = get_secret("GMAIL_APP_PASSWORD", "")


@st.cache_resource
def get_gemini_client(api_key: str) -> genai.Client:
    """Initializes and caches the Gemini client to avoid connection resets."""
    clean_key = api_key if api_key and not api_key.startswith("your-") else "unconfigured_key"
    return genai.Client(api_key=clean_key)


def is_valid_email(email: str) -> bool:
    """Basic sanity check for email format."""
    return "@" in email and "." in email.split("@")[-1] and len(email) > 5


def send_email(to_address: str, user_name: str, summary: str):
    """Sends the study revision notes via Gmail SMTP SSL with both plain text and styled HTML."""
    gmail_sender = get_secret("GMAIL_ADDRESS", "") or st.session_state.get("custom_gmail_address", "")
    gmail_password = get_secret("GMAIL_APP_PASSWORD", "") or st.session_state.get("custom_gmail_password", "")

    if not gmail_sender or not gmail_password or "your-" in gmail_sender:
        return False, "Gmail credentials not configured. Please add GMAIL_ADDRESS and GMAIL_APP_PASSWORD in .streamlit/secrets.toml."

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"📚 Snap & Learn: Study Revision Notes for {user_name}"
        msg["From"] = f"Snap & Learn <{gmail_sender}>"
        msg["To"] = to_address

        # Plain text fallback
        plain_body = (
            f"Hi {user_name},\n\n"
            f"Here are your revision notes from your Snap & Learn study session:\n\n"
            f"{summary}\n\n"
            f"Keep up the great work!\n"
            f"— Your Snap & Learn AI Study Buddy"
        )

        # Beautiful HTML email
        html_formatted_summary = summary.replace("\n", "<br>")
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
          <meta charset="utf-8">
          <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; line-height: 1.6; color: #1e293b; background-color: #f8fafc; margin: 0; padding: 20px; }}
            .card {{ max-width: 600px; margin: 0 auto; background: #ffffff; border-radius: 14px; border: 1px solid #e2e8f0; overflow: hidden; box-shadow: 0 4px 12px rgba(0,0,0,0.05); }}
            .header {{ background: linear-gradient(135deg, #4f46e5, #7c3aed); padding: 28px 24px; text-align: center; color: #ffffff; }}
            .header h1 {{ margin: 0; font-size: 24px; letter-spacing: -0.5px; }}
            .header p {{ margin: 6px 0 0; opacity: 0.9; font-size: 14px; }}
            .content {{ padding: 28px 24px; }}
            .notes-box {{ background: #f1f5f9; border-left: 4px solid #6366f1; border-radius: 8px; padding: 18px; font-family: 'Courier New', Courier, monospace; font-size: 13.5px; line-height: 1.5; color: #0f172a; margin: 20px 0; }}
            .footer {{ background: #f8fafc; border-top: 1px solid #e2e8f0; padding: 16px 24px; text-align: center; font-size: 13px; color: #64748b; }}
          </style>
        </head>
        <body>
          <div class="card">
            <div class="header">
              <h1>📚 Snap & Learn</h1>
              <p>Your Personal Study Revision Guide</p>
            </div>
            <div class="content">
              <p>Hi <strong>{user_name}</strong>,</p>
              <p>Awesome job studying today! Here is the complete breakdown and revision notes from your recent session:</p>
              <div class="notes-box">
                {html_formatted_summary}
              </div>
              <p>Review these takeaways before your next exam or quiz. You've got this! 🚀</p>
            </div>
            <div class="footer">
              Generated with ❤️ by <strong>Snap & Learn</strong> · Keep exploring and learning!
            </div>
          </div>
        </body>
        </html>
        """

        msg.attach(MIMEText(plain_body, "plain"))
        msg.attach(MIMEText(html_body, "html"))

        # Clean spaces from 16-character App Password (e.g. "abcd efgh ijkl mnop")
        clean_password = gmail_password.replace(" ", "")

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(gmail_sender, clean_password)
            server.send_message(msg)

        return True, "Email sent successfully!"
    except Exception as error:
        return False, str(error)


# --- Sidebar Navigation & Settings ---
with st.sidebar:
    st.markdown("### 📚 About Snap & Learn")
    st.markdown(
        "Snap & Learn is your 24/7 AI study buddy powered by Google Gemini Vision and Gmail automation. "
        "Photograph homework problems, diagrams, or lecture notes to get instant, step-by-step guidance."
    )

    st.markdown("---")
    st.markdown("#### 💡 What you can snap:")
    st.markdown("• 📐 **Math & Physics**: Equations, derivations, graphs")
    st.markdown("• 🧪 **Chemistry & Biology**: Reactions, cell diagrams, cycles")
    st.markdown("• 📝 **Handwritten Notes**: Summaries, unclear handwriting")
    st.markdown("• 💻 **Code & Algorithms**: Debugging, flowchart explanations")

    st.markdown("---")
    # API Key & Credential Status Indicator
    st.markdown("#### ⚙️ Service Status")
    if GEMINI_API_KEY:
        st.success("Gemini API: Configured ✅")
    else:
        st.warning("Gemini API: Key Needed ⚠️")
        gemini_input = st.text_input("Enter Gemini API Key", type="password")
        if gemini_input:
            GEMINI_API_KEY = gemini_input
            st.session_state.custom_gemini_key = gemini_input

    if GMAIL_ADDRESS and GMAIL_APP_PASSWORD:
        st.success("Gmail SMTP: Configured ✅")
    else:
        st.info("Gmail SMTP: Add in secrets.toml to enable emailing")

    if st.session_state.get("onboarded", False):
        st.markdown("---")
        if st.button("🔄 Start New Study Session", use_container_width=True):
            for key in ["onboarded", "name", "recipient_email", "chat", "messages"]:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()


# --- Step 1: Onboarding Screen ---
if "onboarded" not in st.session_state:
    st.markdown('<div class="hero-badge">✨ AI Vision Study Assistant</div>', unsafe_allow_html=True)
    st.title("📚 Snap & Learn")
    st.markdown(
        "**Snap it. Learn it. Email yourself the study notes.**\n\n"
        "Snap a photo of any problem, textbook page, or diagram you're stuck on. "
        "Ask questions in natural language, and receive instant explanations and emailed revision notes."
    )

    if not GEMINI_API_KEY and not st.session_state.get("custom_gemini_key"):
        st.warning(
            "⚠️ **Gemini API Key Required**:\n"
            "Please paste your free Google Gemini API key below, or configure it in `.streamlit/secrets.toml`. "
            "[Get a free key from Google AI Studio](https://aistudio.google.com)."
        )

    with st.form("onboarding_form"):
        name = st.text_input("Your Name", placeholder="e.g. Alex", help="What should Snap & Learn call you?")
        recipient_email = st.text_input(
            "Your Email Address",
            placeholder="e.g. student@gmail.com",
            help="Snap & Learn will email your complete study revision sheet to this address.",
        )
        
        # In case the user hasn't set secrets.toml yet, allow entering it directly in form
        api_key_field = ""
        if not GEMINI_API_KEY and not st.session_state.get("custom_gemini_key"):
            api_key_field = st.text_input(
                "Gemini API Key (free from aistudio.google.com)",
                type="password",
                placeholder="AIzaSy...",
            )

        submitted = st.form_submit_button("Start Studying 🚀", use_container_width=True)

    if submitted:
        active_key = GEMINI_API_KEY or st.session_state.get("custom_gemini_key") or api_key_field.strip()
        
        if not name.strip() or not recipient_email.strip():
            st.warning("Please fill in both your name and email address.")
        elif not is_valid_email(recipient_email.strip()):
            st.warning("Please enter a valid email address (e.g., student@gmail.com).")
        elif not active_key:
            st.error("Please enter a valid Gemini API Key to proceed.")
        else:
            try:
                gemini_client = get_gemini_client(active_key)
                st.session_state.active_gemini_key = active_key
                st.session_state.name = name.strip()
                st.session_state.recipient_email = recipient_email.strip()
                
                # Create the chat session with the specialized study tutor system prompt
                st.session_state.chat = gemini_client.chats.create(
                    model=MODEL_NAME,
                    config=types.GenerateContentConfig(system_instruction=SYSTEM_PROMPT),
                )
                st.session_state.messages = []
                st.session_state.onboarded = True
                st.rerun()
            except Exception as err:
                st.error(f"Failed to initialize Gemini session: {err}")

    st.stop()


# --- Step 2: Main Study Chat Interface ---

# Retrieve active Gemini client
active_key = st.session_state.get("active_gemini_key") or GEMINI_API_KEY
gemini_client = get_gemini_client(active_key)


def render_message(message):
    """Renders a single message in the chat stream (text or image)."""
    with st.chat_message(message["role"]):
        if message["kind"] == "text":
            st.markdown(message["content"])
        elif message["kind"] == "image":
            st.image(message["content"], caption="📸 Uploaded Study Material", use_container_width=True)


def add_message(role, kind, content):
    """Appends message to session state and displays it immediately."""
    st.session_state.messages.append({"role": role, "kind": kind, "content": content})
    render_message(st.session_state.messages[-1])


def ask_gemini(parts):
    """Sends text and/or image parts with automatic retry and model failover for 503 high demand and 404 errors."""
    candidate_models = ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash"]
    current_model = getattr(st.session_state, "active_model", MODEL_NAME)

    if current_model in candidate_models:
        candidate_models.remove(current_model)
    candidate_models.insert(0, current_model)

    last_error = None

    # Step 1: Try current active chat session with brief backoff if 503 / high demand
    for attempt in range(2):
        try:
            response = st.session_state.chat.send_message(parts)
            return response.text
        except Exception as error:
            last_error = error
            err_str = str(error).lower()
            # If 503 high demand or 429 rate limit, wait briefly before retrying
            if ("503" in err_str or "unavailable" in err_str or "high demand" in err_str or "429" in err_str) and attempt == 0:
                time.sleep(1.5)
                continue
            break

    # Step 2: Failover to alternative Flash models if primary model is unavailable
    for fallback_model in candidate_models:
        if fallback_model == current_model:
            continue
        try:
            time.sleep(0.5)
            fallback_chat = gemini_client.chats.create(
                model=fallback_model,
                config=types.GenerateContentConfig(system_instruction=SYSTEM_PROMPT),
            )
            res = fallback_chat.send_message(parts)
            st.session_state.chat = fallback_chat
            st.session_state.active_model = fallback_model
            return f"*(Switched to `{fallback_model}` due to high traffic on `{current_model}`)*\n\n{res.text}"
        except Exception as fallback_err:
            last_error = fallback_err
            continue

    # Step 3: Polite, user-friendly notice if all endpoints are temporarily saturated
    error_msg = str(last_error) if last_error else "Service temporarily busy"
    if "503" in error_msg or "unavailable" in error_msg.lower() or "high demand" in error_msg.lower():
        return (
            "⏳ **Google Gemini servers are currently experiencing high demand.**\n\n"
            "This traffic spike is temporary. Please wait 5–10 seconds and resend your question."
        )
    return f"Sorry, something went wrong while analyzing: {error_msg}"


# App Header with Title and Email Summary Action
header_col, action_col = st.columns([5, 2], vertical_alignment="center")

with header_col:
    st.title("📚 Snap & Learn")

with action_col:
    # Button is disabled until at least one exchange (beyond welcome message) has occurred
    curr_messages = st.session_state.get("messages", [])
    send_disabled = len(curr_messages) <= 2
    if st.button("📧 Email Study Notes", disabled=send_disabled, use_container_width=True, type="primary"):
        with st.spinner("Compiling high-yield revision sheet..."):
            summary = ask_gemini([SUMMARY_REQUEST_PROMPT])
        
        user_email = st.session_state.get("recipient_email", "")
        user_name = st.session_state.get("name", "Student")
        with st.spinner(f"Sending study notes to {user_email}..."):
            success, info = send_email(
                user_email,
                user_name,
                summary,
            )

        if success:
            st.success("Study notes sent! Check your inbox / spam folder 📬")
            with st.expander("👀 View Generated Revision Sheet"):
                st.markdown(summary)
        else:
            st.error(f"Could not send email: {info}")
            with st.expander("👀 View Generated Revision Sheet (Copy Notes Here)"):
                st.markdown(summary)

user_name = st.session_state.get("name", "Student")
user_email = st.session_state.get("recipient_email", "")
st.caption(f"👤 Studying as **{user_name}** · Notes will be delivered to **{user_email}**")

# Display Conversation History
if "messages" not in st.session_state:
    st.session_state.messages = []

if not st.session_state.messages:
    add_message("assistant", "text", WELCOME_MESSAGE_TEMPLATE.format(name=user_name))
else:
    for message in st.session_state.messages:
        render_message(message)

# Unified Chat & Vision Input Box
user_input = st.chat_input(
    "Ask a question or snap/upload a photo of notes, diagrams, or problems...",
    accept_file=True,
    file_type=["jpg", "jpeg", "png"],
)

if user_input:
    photo = user_input.files[0] if user_input.files else None
    text = user_input.text
    parts = []

    if photo is not None:
        photo_bytes = photo.getvalue()
        add_message("user", "image", photo_bytes)
        parts.append(types.Part.from_bytes(data=photo_bytes, mime_type=photo.type))

    if text:
        add_message("user", "text", text)
        parts.append(text)
    elif photo is not None:
        # Default prompt if photo attached without caption
        default_caption = "Please analyze this study material or problem step-by-step, highlighting key concepts, definitions, or formulas."
        parts.append(default_caption)

    with st.spinner("Analyzing study material & breaking down concepts..."):
        answer = ask_gemini(parts)

    add_message("assistant", "text", answer)
