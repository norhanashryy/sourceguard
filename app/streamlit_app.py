import streamlit as st
import time

from main import app


st.set_page_config(
    page_title="Grounded Documentation Assistant",
    layout="wide",
)


st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Source+Serif+4:opsz,wght@8..60,500;8..60,600&family=Inter:wght@400;500&family=JetBrains+Mono:wght@400;500&display=swap');

    :root {
        --bg: #10181A;
        --surface: #182225;
        --surface-raised: #1E2A2D;
        --border: #2C393D;
        --text: #E4E9E7;
        --text-muted: #8B9A9D;
        --accent: #D9A441;
        --accent-dim: #8A6B2E;
        --stamp-approved: #7CA36B;
        --stamp-rejected: #C1614A;
        --font-display: 'Source Serif 4', Georgia, serif;
        --font-body: 'Inter', sans-serif;
        --font-mono: 'JetBrains Mono', monospace;
    }

    html, body, [class*="css"] {
        font-family: var(--font-body);
    }

    .stApp {
        background-color: var(--bg);
        color: var(--text);
    }

    h1 {
        font-family: var(--font-display);
        color: var(--text);
        font-weight: 600;
        letter-spacing: 0.01em;
    }

    h2, h3 {
        font-family: var(--font-display);
        color: var(--text);
        font-weight: 600;
    }

    .subtitle {
        color: var(--text-muted);
        font-size: 0.95rem;
        font-style: italic;
        margin-top: -8px;
        margin-bottom: 28px;
        padding-bottom: 14px;
        border-bottom: 1px solid var(--border);
    }

    .section-label {
        font-family: var(--font-mono);
        font-size: 0.72rem;
        font-weight: 500;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        color: var(--accent);
        margin: 22px 0 10px 0;
    }

    .section-label::before {
        content: "§ ";
        color: var(--accent-dim);
    }

    .answer-card {
        background-color: var(--surface);
        border: 1px solid var(--border);
        border-left: 3px solid var(--accent);
        border-radius: 3px;
        padding: 22px 24px;
        margin-bottom: 12px;
        line-height: 1.7;
        font-size: 1.02rem;
        color: var(--text);
    }

    /* Sources styled as numbered footnotes/index cards rather than a plain box */
    .source-card, .source {
        background-color: var(--surface);
        border: 1px solid var(--border);
        border-radius: 4px;
        padding: 10px 16px 10px 44px;
        margin: 6px 0;
        position: relative;
        counter-increment: source-count;
    }

    .source-card::before, .source::before {
        content: counter(source-count);
        position: absolute;
        left: 0;
        top: 0;
        bottom: 0;
        width: 32px;
        display: flex;
        align-items: center;
        justify-content: center;
        background-color: var(--surface-raised);
        color: var(--accent);
        font-family: var(--font-mono);
        font-size: 0.75rem;
        border-right: 1px solid var(--border);
    }

    .source-url {
        font-family: var(--font-mono);
        font-size: 0.85rem;
        color: var(--text-muted);
        word-break: break-all;
    }

    /* Reviewer verdict rendered as an ink stamp - this is a verification
       step, so it reads like one rather than a generic status pill */
    .pass, .fail {
        display: inline-block;
        font-family: var(--font-mono);
        font-size: 0.95rem;
        font-weight: 500;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        padding: 10px 20px;
        border-radius: 3px;
        border: 2px solid;
        transform: rotate(-1.5deg);
        background-color: transparent;
    }

    .pass {
        color: var(--stamp-approved);
        border-color: var(--stamp-approved);
        box-shadow: 0 0 0 1px var(--stamp-approved) inset;
    }

    .fail {
        color: var(--stamp-rejected);
        border-color: var(--stamp-rejected);
        box-shadow: 0 0 0 1px var(--stamp-rejected) inset;
        transform: rotate(1.5deg);
    }

    .workflow {
        background-color: var(--surface);
        border: 1px solid var(--border);
        border-radius: 4px;
        padding: 18px 20px;
        color: var(--text);
        line-height: 1.9;
        font-family: var(--font-mono);
        font-size: 0.9rem;
    }

    /* Widget label ("Ask a question") was invisible - it inherits a color
       that isn't set anywhere for a dark background. Set it explicitly. */
    .stTextInput label, .stTextInput label p {
        color: var(--text) !important;
        font-weight: 500;
    }

    .stTextInput input {
        background-color: var(--surface);
        color: var(--text);
        border: 1px solid var(--border);
        border-radius: 4px;
        font-family: var(--font-mono);
    }

    .stTextInput input::placeholder {
        color: var(--text-muted);
        opacity: 0.7;
    }

    .stTextInput input:focus {
        border-color: var(--accent);
        box-shadow: 0 0 0 1px var(--accent);
    }

    /* Default Streamlit body text (st.write, st.caption, expander contents) */
    p, li, .stMarkdown, .stCaption, [data-testid="stCaptionContainer"] {
        color: var(--text);
    }

    [data-testid="stCaptionContainer"] {
        color: var(--text-muted) !important;
        font-family: var(--font-mono) !important;
        font-size: 0.8rem !important;
    }

    hr {
        border-color: var(--border);
    }

    .stButton button {
        background-color: var(--accent);
        color: var(--bg);
        border-radius: 4px;
        border: none;
        padding: 8px 24px;
        font-weight: 600;
        font-family: var(--font-mono);
        letter-spacing: 0.03em;
        transition: background-color 0.15s ease;
    }

    .stButton button:hover {
        background-color: var(--stamp-approved);
        color: var(--bg);
    }

    [data-testid="stExpander"] {
        background-color: var(--surface);
        border: 1px solid var(--border);
        border-radius: 4px;
    }
</style>
""", unsafe_allow_html=True)

st.title("Grounded Documentation Assistant")

st.markdown(
    '<div class="subtitle">'
    "Two-agent question answering over LangChain, LangGraph, and Qdrant documentation."
    "</div>",
    unsafe_allow_html=True,
)


query = st.text_input(
    "Ask a question",
    placeholder="e.g. What is Qdrant?",
)


if st.button("Ask") and query.strip():

    start_time = time.time()

    with st.spinner("Researching and verifying..."):

        result = app.invoke(
            {
                "question": query,
                "answer": "",
                "original_answer": "",
                "documentation": "",
                "chunks": [],
                "review": "",
                "revised": False,
            }
        )

    latency = time.time() - start_time

    # -------------------------
    # Final answer
    # -------------------------

    st.markdown(
        '<div class="section-label">Final Answer</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        f'<div class="answer-card">{result["answer"]}</div>',
        unsafe_allow_html=True,
    )

    # -------------------------
    # Sources
    # -------------------------

    st.markdown(
        '<div class="section-label">Sources</div>',
        unsafe_allow_html=True,
    )

    sources = []

    for chunk in result.get("chunks", []):
        source = chunk.get("source")

        if source and source not in sources:
            sources.append(source)

    if sources:

        st.markdown(
            '<div style="counter-reset: source-count;"></div>',
            unsafe_allow_html=True,
        )

        for source in sources:
            st.markdown(
                f"""
                <div class="source">
                    <div class="source-url">{source}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    else:
        st.write("No supporting sources were retrieved.")

    # -------------------------
    # Reviewer verdict
    # -------------------------

    st.markdown(
        '<div class="section-label">Reviewer Verdict</div>',
        unsafe_allow_html=True,
    )

    review = result.get("review", "")

    if review.startswith("PASS"):

        st.markdown(
            '<div class="pass">PASS — The final answer is supported by the retrieved documentation.</div>',
            unsafe_allow_html=True,
        )

    else:

        st.markdown(
            '<div class="fail">FAIL — The answer could not be fully grounded in the retrieved documentation.</div>',
            unsafe_allow_html=True,
        )

    # -------------------------
    # Retrieved documentation
    # -------------------------

    with st.expander("Retrieved Documentation"):

        chunks = result.get("chunks", [])

        if chunks:

            for i, chunk in enumerate(chunks, 1):

                st.markdown(f"**Result {i}**")

                st.caption(
                    f"Source: {chunk.get('source', 'Unknown source')}"
                )

                st.write(chunk.get("text", ""))

                if i < len(chunks):
                    st.divider()

        else:
            st.write("No documentation was retrieved.")

    # -------------------------
    # Workflow details
    # -------------------------

    with st.expander("Workflow Details"):

        revision_status = (
            "Researcher → Reviewer → Final"
            if not result.get("revised")
            else
            "Researcher → Reviewer → Revision → Reviewer"
        )

        st.markdown(
            f"""
            <div class="workflow">

            <b>Workflow:</b> {revision_status}<br><br>

            <b>Revision performed:</b>
            {"Yes" if result.get("revised") else "No"}<br><br>

            <b>Latency:</b> {latency:.2f} seconds

            </div>
            """,
            unsafe_allow_html=True,
        )



# import streamlit as st
# import time

# from main import app


# st.set_page_config(
#     page_title="Grounded Documentation Assistant",
#     page_icon=None,
#     layout="wide",
# )


# st.markdown("""
# <style>
#     .stApp {
#         background-color: #E9EDF3;
#         color: #182235;
#     }

#     h1, h2, h3 {
#         color: #182235;
#     }

#     .answer-card {
#         background-color: #FFFFFF;
#         border: 1px solid #B8C2D0;
#         border-radius: 10px;
#         padding: 20px;
#         margin-bottom: 20px;
#     }

#     .source-card {
#         background-color: #FFFFFF;
#         border-left: 4px solid #315A85;
#         padding: 12px 16px;
#         margin: 8px 0;
#         border-radius: 6px;
#     }

#     .review-card {
#         background-color: #FFFFFF;
#         border: 1px solid #B8C2D0;
#         border-radius: 10px;
#         padding: 16px;
#         margin-top: 15px;
#     }

#     .stTextInput input {
#         background-color: #FFFFFF;
#         color: #182235;
#         border: 1px solid #8F9CAF;
#     }

#     .stButton button {
#         background-color: #315A85;
#         color: #FFFFFF;
#         border-radius: 7px;
#         border: none;
#         padding: 8px 20px;
#     }
# </style>
# """, unsafe_allow_html=True)

# st.title("Grounded Documentation Assistant")

# st.markdown(
#     '<div class="subtitle">'
#     "Two-agent question answering over LangChain, LangGraph, and Qdrant documentation."
#     "</div>",
#     unsafe_allow_html=True,
# )


# query = st.text_input(
#     "Ask a question",
#     placeholder="e.g. What is Qdrant?",
# )


# if st.button("Ask") and query.strip():

#     start_time = time.time()

#     with st.spinner("Researching and verifying..."):

#         result = app.invoke(
#             {
#                 "question": query,
#                 "answer": "",
#                 "original_answer": "",
#                 "documentation": "",
#                 "chunks": [],
#                 "review": "",
#                 "revised": False,
#             }
#         )

#     latency = time.time() - start_time

#     # -------------------------
#     # Final answer
#     # -------------------------

#     st.markdown(
#         '<div class="section-label">Final Answer</div>',
#         unsafe_allow_html=True,
#     )

#     st.markdown(
#         f'<div class="answer-card">{result["answer"]}</div>',
#         unsafe_allow_html=True,
#     )

#     # -------------------------
#     # Sources
#     # -------------------------

#     st.markdown(
#         '<div class="section-label">Sources</div>',
#         unsafe_allow_html=True,
#     )

#     sources = []

#     for chunk in result.get("chunks", []):
#         source = chunk.get("source")

#         if source and source not in sources:
#             sources.append(source)

#     if sources:

#         for source in sources:
#             st.markdown(
#                 f"""
#                 <div class="source">
#                     <div class="source-url">{source}</div>
#                 </div>
#                 """,
#                 unsafe_allow_html=True,
#             )

#     else:
#         st.write("No supporting sources were retrieved.")

#     # -------------------------
#     # Reviewer verdict
#     # -------------------------

#     st.markdown(
#         '<div class="section-label">Reviewer Verdict</div>',
#         unsafe_allow_html=True,
#     )

#     review = result.get("review", "")

#     if review.startswith("PASS"):

#         st.markdown(
#             '<div class="pass">PASS; The final answer is supported by the retrieved documentation.</div>',
#             unsafe_allow_html=True,
#         )

#     else:

#         st.markdown(
#             '<div class="fail">FAIL; The answer could not be fully grounded in the retrieved documentation.</div>',
#             unsafe_allow_html=True,
#         )

#     # -------------------------
#     # Retrieved documentation
#     # -------------------------

#     with st.expander("Retrieved Documentation"):

#         chunks = result.get("chunks", [])

#         if chunks:

#             for i, chunk in enumerate(chunks, 1):

#                 st.markdown(f"**Result {i}**")

#                 st.caption(
#                     f"Source: {chunk.get('source', 'Unknown source')}"
#                 )

#                 st.write(chunk.get("text", ""))

#                 if i < len(chunks):
#                     st.divider()

#         else:
#             st.write("No documentation was retrieved.")

#     # -------------------------
#     # Workflow details
#     # -------------------------

#     with st.expander("Workflow Details"):

#         revision_status = (
#             "Researcher → Reviewer → Final"
#             if not result.get("revised")
#             else
#             "Researcher → Reviewer → Revision → Reviewer"
#         )

#         st.markdown(
#             f"""
#             <div class="workflow">

#             <b>Workflow:</b> {revision_status}<br><br>

#             <b>Revision performed:</b>
#             {"Yes" if result.get("revised") else "No"}<br><br>

#             <b>Latency:</b> {latency:.2f} seconds

#             </div>
#             """,
#             unsafe_allow_html=True,
#         )