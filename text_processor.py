# text_processor.py
# ------------------------------------------------------------
# Interactive Text Processor (Streamlit)
# - Covers Task 1–4 + bonus items (validation, history, warnings)
# - Fully commented so you can see what each part does
# ------------------------------------------------------------

import streamlit as st
from datetime import datetime

# ---------- Page setup ----------
st.set_page_config(page_title="Interactive Text Processor", page_icon="📝", layout="wide")

st.title("Interactive Text Processor")
st.caption("Paste text, choose a processing option in the sidebar, and see results update instantly.")

# ---------- Session state (for bonus: history) ----------
# Store the last few operations across reruns.
if "history" not in st.session_state:
    st.session_state.history = []   # list of dicts: {"time":..., "op":..., "preview":...}

# ---------- Sidebar (Task 1) ----------
with st.sidebar:
    st.header("⚙️ Configuration")

    # Processing type (Task 2)
    op = st.selectbox(
        "Processing type",
        ["Word Count", "Character Count", "Reverse Text", "Uppercase", "Title Case"],
        help="Pick the operation to apply to your text."
    )

    # Character limit control (Task 2)
    limit = st.number_input(
        "Character limit",
        min_value=10, max_value=500, value=100, step=10,
        help="We’ll warn you when input length goes over this limit."
    )

    # Show processing steps (Task 2)
    show_steps = st.checkbox("Show processing steps", value=True)

    # Bonus: Minimum text length validation threshold
    min_len = st.number_input("Minimum text length (validation)", min_value=0, max_value=200, value=0)

# ---------- Input area (Task 2) ----------
# Provide a default example so the app does something immediately.
default_text = "Streamlit makes building data and AI apps super quick. Try processing this text!"
text = st.text_area("Input Text", value=default_text, height=180, placeholder="Type or paste text here…")

# ---------- Input validation (Bonus 1) ----------
if not text.strip():
    st.warning("Please enter some text to process.")
    st.stop()

if len(text) < min_len:
    st.warning(f"Input is shorter than the minimum required length ({min_len} characters).")
    st.stop()

# ---------- Character limit warning (Bonus 3) ----------
if len(text) > limit:
    st.warning(f"Your input has {len(text)} characters, which exceeds the limit of {limit}.")

# ---------- Processing functions (Task 3) ----------
def word_count(t: str):
    """Return a human-readable report string and steps list."""
    words = [w for w in t.split() if w.strip()]
    report = f"Word count: {len(words)}"
    steps = [
        "Split text on whitespace.",
        "Filter out empty tokens.",
        "Count remaining tokens."
    ]
    return report, steps

def character_count(t: str):
    """Return a report string (with & without spaces) and steps."""
    with_spaces = len(t)
    without_spaces = len(t.replace(" ", ""))
    report = f"Character count — with spaces: {with_spaces}, without spaces: {without_spaces}"
    steps = [
        "Count all characters (including spaces).",
        "Create a copy without spaces and count again."
    ]
    return report, steps

def reverse_text(t: str):
    """Reverse entire text."""
    out = t[::-1]
    steps = ["Reverse the string using slicing: t[::-1]."]
    return out, steps

def to_upper(t: str):
    """Uppercase conversion."""
    out = t.upper()
    steps = ["Convert all characters to uppercase with str.upper()."]
    return out, steps

def to_title(t: str):
    """Title case conversion."""
    out = t.title()
    steps = ["Convert to title case with str.title()."]
    return out, steps

# Map operation name to function and a style (Bonus 4: simple styling)
OP_FUNCS = {
    "Word Count": (word_count, "info"),
    "Character Count": (character_count, "info"),
    "Reverse Text": (reverse_text, "warning"),
    "Uppercase": (to_upper, "success"),
    "Title Case": (to_title, "success"),
}

# ---------- Run the selected processing (Task 3) ----------
func, style = OP_FUNCS[op]
processed_text, steps = func(text)

# ---------- Dynamic display (Task 4) ----------
# Two-column layout so users can compare input vs output
left, right = st.columns(2)

with left:
    st.subheader("Original")
    st.code(text, language="text")

with right:
    st.subheader("Processed")
    # Styled container: use Streamlit message types for simple color coding
    if style == "info":
        st.info(processed_text)
    elif style == "success":
        st.success(processed_text)
    elif style == "warning":
        st.warning(processed_text)
    else:
        st.write(processed_text)

# Optional: show processing steps (Task 4)
if show_steps:
    with st.expander("Processing steps"):
        for i, s in enumerate(steps, start=1):
            st.write(f"{i}. {s}")

# Success message after processing is complete (Task 4)
st.success("✅ Processing complete.")

# Download button for the processed result (Task 4)
# For count operations, you still download the human-readable report string.
st.download_button(
    label="⬇️ Download result",
    data=str(processed_text).encode("utf-8"),
    file_name="processed.txt",
    mime="text/plain",
)

# ---------- Bonus: processing history (last 3 ops) ----------
# Save a tiny preview (first 60 chars) to keep the history compact.
preview = processed_text if isinstance(processed_text, str) else str(processed_text)
st.session_state.history.append(
    {"time": datetime.now().strftime("%H:%M:%S"), "op": op, "preview": preview[:60] + ("…" if len(preview) > 60 else "")}
)
# Keep only the last 3
st.session_state.history = st.session_state.history[-5:]

with st.sidebar:
    st.divider()
    st.subheader("🕘 Recent operations")
    if st.session_state.history:
        for h in reversed(st.session_state.history):
            st.caption(f"[{h['time']}] {h['op']}: {h['preview']}")
    else:
        st.caption("No history yet.")

# ---------- Debug helper (hint mentions this) ----------
# Uncomment for quick debugging prints in the app:
# st.write({"len(text)": len(text), "limit": limit, "op": op})
