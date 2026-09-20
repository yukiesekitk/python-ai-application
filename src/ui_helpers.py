import logging

import streamlit as st

from src.gemini_client import generate

logger = logging.getLogger(__name__)


def run_generation(client, model, prompt, system_instruction, result_key, spinner_text="生成中..."):
    """Gemini API呼び出しを実行し、結果をsession_stateに保存する。エラー時はst.errorで通知。

    例外の詳細（APIキーがURLに含まれる場合があるなど）はUIに出さず、ログにのみ記録する。
    """
    if client is None:
        st.error("左のサイドバーにGemini APIキーを入力してください。")
        return
    try:
        with st.spinner(spinner_text):
            result = generate(client, model, prompt, system_instruction=system_instruction)
        st.session_state[result_key] = result
    except Exception:
        logger.exception("生成中にエラーが発生しました")
        st.error("生成中にエラーが発生しました。APIキーやネットワーク状況をご確認のうえ、しばらくしてから再度お試しください。")


def render_preview(result_key, title="プレビュー"):
    """生成結果をMarkdownとしてレンダリングしたプレビューを表示する。結果が無ければ何も表示しない。"""
    result = st.session_state.get(result_key, "")
    if not result:
        return
    st.subheader(title)
    with st.container(border=True):
        st.markdown(result)


def render_output(result_key, label, height=400):
    """結果テキストエリアを表示する（コピー用）。

    key引数は付けない: keyを付けるとStreamlitはwidgetの内部状態を優先し、
    生成完了後にvalueを更新しても画面に反映されなくなるため。
    """
    result = st.session_state.get(result_key, "")
    st.text_area(label, value=result, height=height)
    if not result:
        st.caption("左のフォームを入力して生成ボタンを押してください。")
