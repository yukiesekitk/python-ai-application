import streamlit as st

from src.config import DEFAULT_MODEL
from src.features import blog, email_reply, proofread, summarize, title_ideas
from src.gemini_client import get_client

st.set_page_config(page_title="AIライティングツール", page_icon="✍️", layout="wide")

with st.sidebar:
    st.header("⚙️ 設定")
    api_key = st.text_input(
        "Gemini APIキー",
        type="password",
        key="gemini_api_key",
        placeholder="AIza...",
        help="このセッション内でのみ使用され、保存されません。",
    )
    st.caption("APIキーは [Google AI Studio](https://aistudio.google.com/apikey) から取得できます。")

model = DEFAULT_MODEL
client = get_client(api_key) if api_key else None

st.title("✍️ AIライティングツール")
st.caption(f"Powered by Gemini API（model: {model}）")

if not api_key:
    st.warning("左のサイドバーにGemini APIキーを入力すると、各機能が使えるようになります。")

tab_blog, tab_email, tab_summary, tab_proofread, tab_title = st.tabs(
    ["📝 ブログ執筆", "📧 メール返信", "📄 要約", "✏️ 校正・リライト", "💡 タイトル案"]
)

with tab_blog:
    blog.render(client, model)

with tab_email:
    email_reply.render(client, model)

with tab_summary:
    summarize.render(client, model)

with tab_proofread:
    proofread.render(client, model)

with tab_title:
    title_ideas.render(client, model)
