# text_to_summary.py — safe-tensors only, CLI smoke test

# 0) Prefer .safetensors globally (must be BEFORE any transformers import)
import os
os.environ["TRANSFORMERS_PREFER_SAFETENSORS"] = "1"

# 1) Imports
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline

# 2) Model choice (small, summarization-tuned)
MODEL_NAME = "sshleifer/distilbart-cnn-12-6"
# If you must use a Meta-only baseline (lower summarization quality):
# MODEL_NAME = "facebook/bart-base"

# 3) Load tokenizer (fast) and model with safetensors enforced
tok = AutoTokenizer.from_pretrained(MODEL_NAME, use_fast=True)

model = AutoModelForSeq2SeqLM.from_pretrained(
    MODEL_NAME,
    use_safetensors=True,    # ✅ force safe weights (no .bin)
    low_cpu_mem_usage=True,  # friendlier RAM usage
    dtype="auto",            # (new arg) let HF pick a reasonable dtype
)

# 4) Build pipeline from the objects (DO NOT pass model name strings)
summarizer = pipeline(
    task="summarization",
    model=model,
    tokenizer=tok,
    device_map="auto",       # CPU on iMac unless you have a GPU
)

def summarize_text(text: str, min_len: int = 40, max_len: int = 120, beams: int = 2) -> str:
    """Summarize a short paragraph."""
    if not text or not text.strip():
        return ""
    return summarizer(
        text,
        max_length=int(max_len),
        min_length=int(min_len),
        num_beams=int(beams),
        do_sample=False,
    )[0]["summary_text"]

if __name__ == "__main__":
    sample = (
        "AI is changing healthcare, education, and productivity, "
        "but raises ethical issues and job concerns."
    )
    print(summarize_text(sample))
