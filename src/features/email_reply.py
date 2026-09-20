import streamlit as st

from src.ui_helpers import render_output, run_generation

SYSTEM_INSTRUCTION = (
    "あなたはビジネスメールの作成が得意なアシスタントです。"
    "受け取ったメールの内容を踏まえ、日本語として自然で失礼のない返信メールの本文を作成してください。"
    "宛名・署名を含む完全なメール文面を出力してください。"
)

RESULT_KEY = "email_result"


def build_prompt(original_mail, intent, tone, signature):
    lines = [
        "以下の受信メールに対する返信メールを作成してください。",
        f"■受信メールの内容:\n{original_mail}",
        f"■返信で伝えたい要点・意図:\n{intent}",
        f"■トーン: {tone}",
    ]
    if signature:
        lines.append(f"■署名（メール末尾に使用）:\n{signature}")
    lines.append("返信メールの本文のみを出力してください（前置きや説明文は不要です）。")
    return "\n".join(lines)


def render(client, model):
    st.header("📧 メール返信文の作成")
    col1, col2 = st.columns(2)

    with col1:
        original_mail = st.text_area(
            "受信したメールの本文",
            placeholder="返信したい元のメール内容を貼り付けてください",
            height=200,
            key="email_original",
        )
        intent = st.text_area(
            "返信で伝えたい要点・意図",
            placeholder="例: 提案内容に同意する旨と、来週の打ち合わせ日程の候補を伝えたい",
            height=120,
            key="email_intent",
        )
        tone = st.selectbox(
            "トーン",
            ["丁寧・ビジネス標準", "よりフォーマル・かしこまった", "カジュアル・親しみやすい", "謝罪・お詫び", "丁重にお断り"],
            key="email_tone",
        )
        signature = st.text_area(
            "署名（任意）",
            placeholder="例: 株式会社〇〇 山田太郎",
            height=80,
            key="email_signature",
        )
        submit = st.button("返信文を生成", type="primary", key="email_submit")

        if submit:
            if not original_mail or not intent:
                st.warning("受信メールの本文と、伝えたい要点の両方を入力してください。")
            else:
                prompt = build_prompt(original_mail, intent, tone, signature)
                run_generation(client, model, prompt, SYSTEM_INSTRUCTION, RESULT_KEY)

    with col2:
        st.subheader("生成結果")
        render_output(RESULT_KEY, "生成された返信メール（コピーしてご利用ください）", height=440)
