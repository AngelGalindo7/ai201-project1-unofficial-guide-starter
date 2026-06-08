"""
app.py — Gradio web UI for the Unofficial UCI Professor Guide.
Run: python app.py  ->  open http://localhost:7860
"""

import gradio as gr

from query import ask


def handle_query(question):
    question = (question or "").strip()
    if not question:
        return "Please enter a question.", ""
    result = ask(question)
    sources = "\n".join(f"• {s}" for s in result["sources"]) or "(no sources)"
    return result["answer"], sources


with gr.Blocks(title="Unofficial UCI Professor Guide") as demo:
    gr.Markdown(
        "# Unofficial UCI Professor Guide\n"
        "Ask about UCI ICS/CS professors and courses. Answers come **only** from "
        "collected Reddit and RateMyProfessors posts — sources are listed below each answer."
    )
    inp = gr.Textbox(label="Your question")
    btn = gr.Button("Ask", variant="primary")
    answer = gr.Textbox(label="Answer", lines=8)
    sources = gr.Textbox(label="Retrieved from", lines=4)

    btn.click(handle_query, inputs=inp, outputs=[answer, sources])
    inp.submit(handle_query, inputs=inp, outputs=[answer, sources])


if __name__ == "__main__":
    demo.launch()
