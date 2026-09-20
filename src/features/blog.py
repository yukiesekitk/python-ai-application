import streamlit as st

from src.ui_helpers import render_output, render_preview, run_generation

SYSTEM_INSTRUCTION = (
    "あなたはSEOに精通したプロのブログライター兼SEOライターです。"
    "読者の検索意図を満たしながら、Google検索でも評価されやすい日本語のブログ記事を執筆してください。"
    "次のSEOのポイントを踏まえて執筆してください。\n"
    "・指定されたキーワードがある場合は、タイトル・導入文・見出し（##）に自然な形で含める"
    "（読みにくくなるような不自然な詰め込みはしない）\n"
    "・記事冒頭の2〜3文で、読者の悩みへの共感と記事を読むメリット（結論の要約）を示す\n"
    "・見出し（##）は読者が検索しそうな疑問・関心に沿った具体的な表現にする\n"
    "・箇条書きや太字を適度に使い、流し読みでも要点が伝わる構成にする\n"
    "・可能であれば具体例や数字を交え、実用的で信頼できる内容にする\n"
    "・記事の最後に「まとめ」の見出しを設け、要点を簡潔に振り返る"
)

RESULT_KEY = "blog_result"


def build_prompt(theme, keywords, tone, length, outline):
    lines = [
        f"以下の条件でブログ記事を執筆してください。",
        f"■テーマ: {theme}",
        f"■文体・トーン: {tone}",
        f"■文章の長さ: {length}",
    ]
    if keywords:
        lines.append(f"■SEOキーワード（タイトル・見出し・導入文に自然に含めること）: {keywords}")
    if outline:
        lines.append(f"■構成メモ・伝えたいポイント:\n{outline}")
    lines.append("記事本文のみを出力してください（前置きや説明文は不要です）。")
    return "\n".join(lines)


def render(client, model):
    st.header("📝 ブログ記事執筆")
    col1, col2 = st.columns(2)

    with col1:
        theme = st.text_input(
            "テーマ・タイトル",
            placeholder="例: 在宅ワークの生産性を上げる5つの方法",
            key="blog_theme",
        )
        keywords = st.text_input(
            "SEOキーワード（任意・カンマ区切り）",
            placeholder="例: 在宅ワーク, 生産性向上, タスク管理",
            key="blog_keywords",
        )
        tone = st.selectbox(
            "文体・トーン",
            ["丁寧・フォーマル", "カジュアル・親しみやすい", "専門的・硬め", "エッセイ風"],
            key="blog_tone",
        )
        length = st.select_slider(
            "文章の長さ",
            options=["短め（500字程度）", "標準（1000字程度）", "長め（2000字程度）"],
            value="標準（1000字程度）",
            key="blog_length",
        )
        outline = st.text_area(
            "構成メモ（任意）",
            placeholder="見出しや伝えたいポイントを箇条書きで",
            height=150,
            key="blog_outline",
        )
        submit = st.button("記事を生成", type="primary", key="blog_submit")

        if submit:
            if not theme:
                st.warning("テーマを入力してください。")
            else:
                prompt = build_prompt(theme, keywords, tone, length, outline)
                run_generation(client, model, prompt, SYSTEM_INSTRUCTION, RESULT_KEY)

        render_preview(RESULT_KEY)

    with col2:
        st.subheader("生成結果")
        render_output(RESULT_KEY, "生成された記事（コピーしてご利用ください）", height=520)
