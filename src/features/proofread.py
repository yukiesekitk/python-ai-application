import streamlit as st

from src.ui_helpers import render_output, run_generation

SYSTEM_INSTRUCTION = (
    "あなたは日本語文章の校正・リライトの専門家です。"
    "文意を変えずに、指定された方向性に沿って文章を改善してください。"
)

RESULT_KEY = "proofread_result"

DIRECTION_INSTRUCTIONS = {
    "誤字脱字・文法チェックのみ": "誤字脱字や文法上の誤りのみを修正してください。文体や表現は元の文章をできるだけ維持してください。",
    "分かりやすく言い換え": "専門用語や回りくどい表現を減らし、誰が読んでも分かりやすい文章に言い換えてください。",
    "より丁寧に": "全体をより丁寧で、敬意のこもった表現に書き直してください。",
    "より簡潔に": "冗長な表現を削り、要点を保ったまま簡潔な文章に書き直してください。",
    "ビジネス文書らしく": "ビジネスシーンにふさわしい、フォーマルで整った文章に書き直してください。",
}


def build_prompt(text, direction):
    instruction = DIRECTION_INSTRUCTIONS[direction]
    lines = [
        "以下の文章を校正・リライトしてください。",
        f"■方向性: {direction}（{instruction}）",
        f"■元の文章:\n{text}",
        "修正後の文章のみを出力してください（前置きや説明文、変更点の解説は不要です）。",
    ]
    return "\n".join(lines)


def render(client, model):
    st.header("✏️ 文章校正・リライト")
    col1, col2 = st.columns(2)

    with col1:
        text = st.text_area(
            "校正・リライトしたい文章",
            placeholder="ここに元の文章を貼り付けてください",
            height=350,
            key="proofread_text",
        )
        direction = st.selectbox(
            "校正の方向性",
            list(DIRECTION_INSTRUCTIONS.keys()),
            key="proofread_direction",
        )
        submit = st.button("校正・リライトを実行", type="primary", key="proofread_submit")

        if submit:
            if not text:
                st.warning("文章を入力してください。")
            else:
                prompt = build_prompt(text, direction)
                run_generation(client, model, prompt, SYSTEM_INSTRUCTION, RESULT_KEY)

    with col2:
        st.subheader("生成結果")
        render_output(RESULT_KEY, "校正・リライト後の文章（コピーしてご利用ください）", height=440)
