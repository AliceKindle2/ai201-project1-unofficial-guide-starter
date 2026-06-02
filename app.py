"""
app.py  —  Milestone 5: Generation + Gradio Interface
======================================================
Full RAG pipeline using Groq's llama-3.3-70b-versatile (free tier).
API key is loaded from a .env file — no hardcoding needed.

Run:
    python app.py

Dependencies (install once):
    pip install gradio groq python-dotenv sentence-transformers chromadb
"""

import os
import re
import gradio as gr
from groq import Groq
from dotenv import load_dotenv
from retrieve import retrieve

# ── LOAD API KEY FROM .env ────────────────────────────────────────────────────
# Create a file called .env in the same folder as this script with:
#   GROQ_API_KEY=your_key_here
load_dotenv()

# ── CONFIG ────────────────────────────────────────────────────────────────────
TOP_K       = 5
MIN_SCORE   = 0.25
MODEL       = "llama-3.3-70b-versatile"

# ── PROMPT TEMPLATE ───────────────────────────────────────────────────────────
SYSTEM_PROMPT = (
    "You are a helpful assistant for University of Texas at Dallas students. "
    "Answer the question using only the information in the provided documents. "
    "If the documents don't contain enough information to answer, say "
    "'I don't have enough information on that.' "
    "Cite each source by referring to it as [Source N] after every claim you make."
)

# ── SOURCE ICONS ──────────────────────────────────────────────────────────────
SOURCE_ICONS = {
    "Rate My Professor": "⭐",
    "UTD Grades":        "📊",
    "UTD CourseBook":    "📚",
    "Coursicle":         "🗓️",
    "Niche":             "🎓",
    "Collegedunia":      "🌐",
    "AcademicJobs RMP":  "🏫",
    "r/utdallas":        "💬",
}

def icon(source):
    return SOURCE_ICONS.get(source, "📌")


# ── CONTEXT BUILDER ───────────────────────────────────────────────────────────

def build_context(chunks: list[dict]) -> str:
    lines = []
    for i, c in enumerate(chunks, start=1):
        meta = f"Source: {c['source']}"
        if c.get("professor"):
            meta += f" | Professor: {c['professor']}"
        if c.get("course"):
            meta += f" | Course: {c['course']}"
        lines.append(f"[Source {i}] {meta}\n{c['text']}")
    return "\n\n".join(lines)


def build_sources_panel(chunks: list[dict]) -> str:
    lines = ["**Sources used:**\n"]
    for i, c in enumerate(chunks, start=1):
        parts = [f"**[Source {i}]** {icon(c['source'])} {c['source']}"]
        if c.get("professor"):
            parts.append(f"— {c['professor']}")
        if c.get("course"):
            parts.append(f"(*{c['course']}*)")
        parts.append(f"*(relevance: {c['score']:.2f})*")
        lines.append(" ".join(parts))
        lines.append(f"> {c['text'][:180]}{'...' if len(c['text']) > 180 else ''}")
        lines.append("")
    return "\n".join(lines)


# ── GENERATION ────────────────────────────────────────────────────────────────

def generate_response(question: str) -> tuple[str, str]:
    # Step 1 — retrieve and filter
    chunks = retrieve(question, top_k=TOP_K)
    chunks = [c for c in chunks if c["score"] >= MIN_SCORE]

    if not chunks:
        return (
            "❌ I don't have enough information on that. "
            "Try searching Rate My Professor or UTDgrades directly.",
            "*(No relevant sources found)*"
        )

    # Step 2 — build context block for the prompt
    context = build_context(chunks)

    user_message = (
        f"Documents:\n{context}\n\n"
        f"Question: {question}"
    )

    # Step 3 — call Groq
    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": user_message},
        ],
        max_tokens=512,
        temperature=0.2,   # low temp = more factual, less creative
    )

    answer = response.choices[0].message.content.strip()

    # Step 4 — guarantee attribution fallback
    if not re.search(r"\[Source\s+\d+\]", answer):
        names = list(dict.fromkeys(c["source"] for c in chunks))
        answer += f"\n\n*(Based on: {', '.join(names)})*"

    return answer, build_sources_panel(chunks)


# ── GRADIO UI ─────────────────────────────────────────────────────────────────

def gradio_query(question: str) -> tuple[str, str]:
    question = question.strip()
    if not question:
        return "Please enter a question.", ""
    try:
        return generate_response(question)
    except Exception as e:
        return f"Error: {str(e)}", ""


EXAMPLES = [
    ["Who is the worst professor for Operating Systems?"],
    ["What are the prerequisites for Calculus II?"],
    ["How many professors are teaching Pre-Calc?"],
    ["How does one sign up for EPICS?"],
    ["Who are the top teachers for CS 2305?"],
    ["What do students say about Jeyakesavan Veerasamy's class?"],
    ["Is CS 2337 a hard course?"],
    ["What is CS 2305 about?"],
    ["Who teaches introductory financial accounting?"],
    ["What do students say about marketing professors at UTD?"],
]

with gr.Blocks(title="UTD Unofficial Course Guide", theme=gr.themes.Soft()) as demo:

    gr.Markdown("""
    # 🎓 UTD Unofficial Course Guide
    Ask anything about **University of Texas at Dallas** professors and courses.
    Answers are grounded exclusively in student reviews and course data.
    """)

    with gr.Row():
        with gr.Column(scale=3):
            question_box = gr.Textbox(
                label="Your Question",
                placeholder="e.g. Who is the easiest CS professor at UTD?",
                lines=2,
            )
            submit_btn = gr.Button("🔍 Ask", variant="primary", size="lg")

        with gr.Column(scale=1):
            gr.Markdown("**Try an example:**")
            gr.Examples(examples=EXAMPLES, inputs=question_box, label="")

    with gr.Row():
        with gr.Column(scale=2):
            answer_box = gr.Markdown(
                value="*Ask a question above to get started.*"
            )
        with gr.Column(scale=1):
            sources_box = gr.Markdown(value="")

    submit_btn.click(fn=gradio_query, inputs=question_box,
                     outputs=[answer_box, sources_box])
    question_box.submit(fn=gradio_query, inputs=question_box,
                        outputs=[answer_box, sources_box])

    gr.Markdown("""
    ---
    *Data from: ⭐ Rate My Professor · 📊 UTDgrades · 📚 UTD CourseBook ·
    🗓️ Coursicle · 🎓 Niche · 🌐 Collegedunia · 🏫 AcademicJobs RMP · 💬 r/utdallas*
    """)

if __name__ == "__main__":
    demo.launch()