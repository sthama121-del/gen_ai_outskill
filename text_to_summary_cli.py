# text_to_summary_cli.py — paste article in terminal, get summary back

# Prefer .safetensors globally (must be before any transformers import)
import os
os.environ["TRANSFORMERS_PREFER_SAFETENSORS"] = "1"

import sys
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline

# ==== Model choice ====
# Small, summarization-tuned model (good balance on CPU)
MODEL_NAME = "sshleifer/distilbart-cnn-12-6"
# If you must use a Meta-only baseline (lower summarization quality), uncomment:
# MODEL_NAME = "facebook/bart-base"

# ==== Load tokenizer & model (force safe tensors) ====
tok = AutoTokenizer.from_pretrained(MODEL_NAME, use_fast=True)
model = AutoModelForSeq2SeqLM.from_pretrained(
    MODEL_NAME,
    use_safetensors=True,    # ✅ force safe weights, avoid .bin + CVE gate
    low_cpu_mem_usage=True,  # friendlier RAM usage
    dtype="auto",            # modern arg (replaces torch_dtype)
)

summarizer = pipeline(
    task="summarization",
    model=model,
    tokenizer=tok,
    device_map="auto",       # CPU on your iMac (GPU if available)
)

# ---- helpers ----
def chunk_text(text: str, max_chars: int = 1200):
    """Split long text into ~1200-char chunks (paragraph-aware)."""
    text = text.strip()
    if len(text) <= max_chars:
        return [text]
    chunks, curr, curr_len = [], [], 0
    for para in text.split("\n"):
        p = para.strip()
        if not p:
            continue
        if curr_len + len(p) + 1 > max_chars:
            chunks.append("\n".join(curr))
            curr, curr_len = [p], len(p)
        else:
            curr.append(p)
            curr_len += len(p) + 1
    if curr:
        chunks.append("\n".join(curr))
    return chunks

def summarize(article_text: str, min_len: int = 60, max_len: int = 160, beams: int = 4) -> str:
    """Summarize possibly-long text via chunking + optional second-pass merge."""
    if not article_text or not article_text.strip():
        return "No article text received."

    chunks = chunk_text(article_text, max_chars=1200)

    partial = []
    for c in chunks:
        out = summarizer(
            c,
            max_length=int(max_len),
            min_length=int(min_len),
            num_beams=int(beams),
            do_sample=False,
        )[0]["summary_text"]
        partial.append(out)

    combined = "\n".join(partial)
    if len(chunks) > 1:
        # second pass: summarize the summaries
        final = summarizer(
            combined,
            max_length=int(max_len),
            min_length=int(min_len),
            num_beams=int(beams),
            do_sample=False,
        )[0]["summary_text"]
    else:
        final = combined

    # Make quick bullet points
    sentences = [s.strip() for s in final.replace("\n", " ").split(".") if s.strip()]
    bullets = "\n".join([f"- {s}." for s in sentences[:5]])  # up to 5 bullets

    return f"\n=== SUMMARY ===\n{final}\n\n=== KEY POINTS ===\n{bullets}\n"

def read_article_from_stdin() -> str:
    """Prompt user and read multi-line article from stdin until EOF (Ctrl+D on macOS)."""
    print("Paste your article below. When finished, press Ctrl+D (macOS/Linux) or Ctrl+Z then Enter (Windows).")
    print("-" * 72)
    try:
        data = sys.stdin.read()
    except KeyboardInterrupt:
        data = ""
    print("-" * 72)
    return data

if __name__ == "__main__":
    # If user piped a file: `cat my.txt | python text_to_summary_cli.py`
    # we’ll just read from stdin; otherwise we prompt interactively.
    if sys.stdin.isatty():
        # interactive
        article = read_article_from_stdin()
    else:
        # piped input
        article = sys.stdin.read()

    result = summarize(article, min_len=60, max_len=160, beams=4)
    print(result)
