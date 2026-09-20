# `app.py`を10分で理解する — Streamlitアプリの「司令塔」を読み解く

## この記事で分かること

このAIライティングツールの`app.py`は、アプリ全体の入り口（エントリーポイント）です。ファイル自体は46行しかありませんが、「サイドバー」「タブ」「各機能への橋渡し」という3つの役割を担っています。順番に見ていきましょう。

## 1. 必要な部品を持ってくる（1〜5行目）

```python
import streamlit as st

from src.config import DEFAULT_MODEL
from src.features import blog, email_reply, proofread, summarize, title_ideas
from src.gemini_client import get_client
```

- `streamlit`: 画面（UI）を作るためのライブラリです。`st.〇〇`という形でボタンやテキスト欄を出します。
- `src.config`の`DEFAULT_MODEL`: 使用するGeminiモデル名（今は`"gemini-3.6-flash"`に固定）が書かれた設定値です。
- `src.features`の5つのモジュール: `blog.py`や`email_reply.py`など、各タブの中身（入力フォームと生成処理）を書いたファイルです。
- `src.gemini_client`の`get_client`: APIキーからGemini APIに接続するための「クライアント」を作る関数です。

**ポイント**: `app.py`自体には「ブログ記事の書き方」のような具体的なロジックは一切書かれていません。各機能は`features/`フォルダの担当ファイルに任せ、`app.py`はそれらを呼び出す「司令塔」に徹しています。

## 2. ページの基本設定（7行目）

```python
st.set_page_config(page_title="AIライティングツール", page_icon="✍️", layout="wide")
```

ブラウザのタブに表示されるタイトルやアイコン、画面幅を設定しています。`layout="wide"`にすることで、画面をめいっぱい使えるようにしています。

## 3. サイドバーでAPIキーを受け取る（9〜18行目）

```python
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
```

`with st.sidebar:`のブロック内に書いたものは、すべて画面左のサイドバーに表示されます。

`st.text_input(type="password")`で、入力した文字が「●●●●」のように伏字になるパスワード欄を作っています。ここで入力されたAPIキーは、ファイルに保存されず、ブラウザを開いている間だけメモリ上に保持されます（このアプリが「サーバーにキーを保存しない」設計にしている理由です）。

## 4. モデルとクライアントの準備（20〜21行目）

```python
model = DEFAULT_MODEL
client = get_client(api_key) if api_key else None
```

ここが少し重要なポイントです。

- `model`には、設定ファイルで固定した`"gemini-3.6-flash"`が入ります。
- `client`は「もしAPIキーが入力されていれば、`get_client()`でGemini APIに繋がるクライアントを作る。入力されていなければ`None`（何もない状態）にする」という条件分岐です。

**なぜ`None`を許すのか？** これは、APIキーが未入力でもアプリの画面（5つのタブ）自体は表示させたいからです。以前、このアプリでは「キーが無いと画面がまるごと止まってしまい、機能が実装されていないように見える」というバグがありました。今の設計では、`client`が`None`のまま各タブに渡され、実際に生成ボタンを押した瞬間にだけ「APIキーを入力してください」とエラー表示する仕組みになっています。

## 5. タイトルと警告表示（23〜27行目）

```python
st.title("✍️ AIライティングツール")
st.caption(f"Powered by Gemini API（model: {model}）")

if not api_key:
    st.warning("左のサイドバーにGemini APIキーを入力すると、各機能が使えるようになります。")
```

画面上部にタイトルと、今使っているモデル名を表示します。APIキーが未入力の場合だけ、黄色い警告メッセージを出します（アプリが壊れているのではなく、「キーを入れてね」という案内です）。

## 6. 5つのタブを作る（29〜31行目）

```python
tab_blog, tab_email, tab_summary, tab_proofread, tab_title = st.tabs(
    ["📝 ブログ執筆", "📧 メール返信", "📄 要約", "✏️ 校正・リライト", "💡 タイトル案"]
)
```

`st.tabs()`にラベルのリストを渡すと、その数だけタブが横並びで作られ、それぞれの「タブの中身を書く場所（コンテナ）」が返ってきます。5つのラベルに対応して、5つの変数（`tab_blog`など）を受け取っています。

## 7. 各タブに機能をはめ込む（33〜46行目）

```python
with tab_blog:
    blog.render(client, model)

with tab_email:
    email_reply.render(client, model)

# ...（以下同様に summarize, proofread, title_ideas）
```

各タブの中で、対応するモジュールの`render(client, model)`関数を呼び出しています。つまり、

- 「ブログ執筆」タブの見た目や動きは、すべて`src/features/blog.py`の`render()`関数の中身が決めている
- `app.py`は「このタブにはこの機能を表示してね」と橋渡ししているだけ

という役割分担です。`client`（Gemini APIへの接続）と`model`（使うモデル名）を、5つの機能すべてに同じものを渡すことで、どのタブでも同じAPIキー・同じモデルで動くようになっています。

## まとめ：`app.py`の全体像

| 行 | やっていること |
|---|---|
| 1〜5行目 | 部品（ライブラリ・他ファイルの関数）を読み込む |
| 7行目 | ページの基本設定 |
| 9〜18行目 | サイドバーにAPIキー入力欄を作る |
| 20〜21行目 | モデルとAPIクライアントを準備（キー無しなら`client=None`） |
| 23〜27行目 | タイトル表示・キー未入力時の警告 |
| 29〜31行目 | 5つのタブを作る |
| 33〜46行目 | 各タブに、対応する機能ファイルの`render()`を呼び出す |

`app.py`自体は「画面の骨組みを組み立てて、各パーツ（機能）を配置する」だけに専念していて、実際の生成ロジックは一切書いていません。この「司令塔と実務担当を分ける」作りのおかげで、新しい機能タブを追加したいときも、`src/features/`に新しいファイルを1つ足して、`app.py`に数行追記するだけで済むようになっています。
