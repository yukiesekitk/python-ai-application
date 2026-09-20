import streamlit as st

from src.ui_helpers import render_output, run_generation

SYSTEM_INSTRUCTION = (
    "あなたはコンテンツマーケティングとコピーライティングの専門家です。"
    "読者の興味を引き、内容を的確に表すタイトル・見出し案を提案してください。"
)

RESULT_KEY = "title_result"


def build_prompt(content, style, count):
    lines = [
        "以下の記事内容に合うタイトル案を考えてください。",
        f"■記事のテーマ・内容:\n{content}",
        f"■スタイル: {style}",
        f"■案の数: {count}個",
        "番号付きリスト形式で、タイトル案のみを出力してください（前置きや説明文は不要です）。",
    ]
    return "\n".join(lines)


def render(client, model):
    st.header("💡 タイトル・見出し案の作成")
    col1, col2 = st.columns(2)

    with col1:
        content = st.text_area(
            "記事のテーマ・内容",
            placeholder="タイトルを付けたい記事の内容やテーマ、要約を入力してください",
            height=300,
            key="title_content",
        )
        style = st.selectbox(
            "スタイル",
            ["SEOを意識した検索されやすいタイトル", "キャッチーで思わずクリックしたくなるタイトル", "シンプルで分かりやすいタイトル", "SNS投稿向けの短いタイトル"],
            key="title_style",
        )
        count = st.slider("案の数", min_value=3, max_value=10, value=5, key="title_count")
        submit = st.button("タイトル案を生成", type="primary", key="title_submit")

        if submit:
            if not content:
                st.warning("記事のテーマ・内容を入力してください。")
            else:
                prompt = build_prompt(content, style, count)
                run_generation(client, model, prompt, SYSTEM_INSTRUCTION, RESULT_KEY)

    with col2:
        st.subheader("生成結果")
        render_output(RESULT_KEY, "タイトル案（コピーしてご利用ください）", height=440)
