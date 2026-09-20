import streamlit as st

from src.ui_helpers import render_output, run_generation

SYSTEM_INSTRUCTION = (
    "あなたは文章要約の専門家です。与えられた文章の要点を漏らさず、"
    "簡潔で分かりやすい日本語に要約してください。"
)

RESULT_KEY = "summarize_result"


def build_prompt(text, length, format_style):
    lines = [
        "以下の文章を要約してください。",
        f"■要約の長さ: {length}",
        f"■出力形式: {format_style}",
        f"■元の文章:\n{text}",
        "要約結果のみを出力してください（前置きや説明文は不要です）。",
    ]
    return "\n".join(lines)


def render(client, model):
    st.header("📄 文章の要約")
    col1, col2 = st.columns(2)

    with col1:
        text = st.text_area(
            "要約したい文章",
            placeholder="ここに要約したい文章を貼り付けてください",
            height=350,
            key="summarize_text",
        )
        length = st.select_slider(
            "要約の長さ",
            options=["一言で（1文）", "短め（3行程度）", "標準（5〜7行程度）", "詳しめ（要点を細かく列挙）"],
            value="標準（5〜7行程度）",
            key="summarize_length",
        )
        format_style = st.selectbox(
            "出力形式",
            ["箇条書き", "段落形式の文章"],
            key="summarize_format",
        )
        submit = st.button("要約を生成", type="primary", key="summarize_submit")

        if submit:
            if not text:
                st.warning("要約したい文章を入力してください。")
            else:
                prompt = build_prompt(text, length, format_style)
                run_generation(client, model, prompt, SYSTEM_INSTRUCTION, RESULT_KEY)

    with col2:
        st.subheader("生成結果")
        render_output(RESULT_KEY, "要約結果（コピーしてご利用ください）", height=440)
