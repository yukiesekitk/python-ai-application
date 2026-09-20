# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

個人用のAIライティングツール。Streamlit製のシングルページアプリで、Gemini APIを使った5つのライティング支援機能をタブで切り替えて使う。データベースや認証は使用しない。

## Commands

```bash
# 依存パッケージのインストール
pip install -r requirements.txt

# アプリの起動
streamlit run app.py

# 構文チェック（テストコードは存在しない）
python -m py_compile app.py src/config.py src/gemini_client.py src/ui_helpers.py src/features/*.py
```

起動後、ブラウザ（`http://localhost:8501`）で開き、サイドバーにGemini APIキーを入力する必要がある。APIキーはコードや設定ファイルには保存されず、Streamlitのセッション内でのみ保持される（`.env`などのファイル管理は意図的に廃止済み）。

## Architecture

- `app.py`: エントリーポイント。サイドバーでAPIキー入力のみを行い（モデル選択UIは無い）、`src/config.DEFAULT_MODEL`を固定で使用する。`get_client()`でクライアントを生成して各`src/features/*.py`の`render(client, model)`をタブごとに呼び出す。APIキー未入力時も`client=None`のままタブ自体は表示し、実際の生成実行時にエラーを出す設計（タブが表示されないように見えるUXの問題を過去に修正済み）。
- `src/gemini_client.py`: Gemini API（`google-genai`パッケージ）呼び出しの薄いラッパー。`get_client`は`@st.cache_resource`でキャッシュされ、`generate()`が実際の`generate_content`呼び出しを担う共通関数。
- `src/ui_helpers.py`: 各機能タブ共通のUIロジック。`run_generation()`がGemini呼び出し・例外処理・結果の`st.session_state`保存を担い、`render_output()`が結果表示用のテキストエリア（コピー用）を描画する。
- `src/features/*.py`: 機能ごとのモジュール（`blog.py`, `email_reply.py`, `summarize.py`, `proofread.py`, `title_ideas.py`）。各モジュールは同じパターンに従う: `SYSTEM_INSTRUCTION`定数、`RESULT_KEY`（`st.session_state`のキー）、`build_prompt(...)`（フォーム入力からプロンプト文字列を組み立てる）、`render(client, model)`（左に入力フォーム・右に生成結果を2カラムで配置し、送信ボタンで`run_generation`を呼ぶ）。新機能を追加する場合はこのパターンを踏襲する。

## Adding a new feature tab

1. `src/features/`に新しいモジュールを追加し、既存モジュール（例: `blog.py`）と同じ構成（`SYSTEM_INSTRUCTION` / `RESULT_KEY` / `build_prompt` / `render`）で実装する。
2. `app.py`でモジュールをインポートし、`st.tabs(...)`にラベルを追加して対応する`with tab_xxx:`ブロックで`render(client, model)`を呼ぶ。
3. すべてのwidgetの`key=`とセッション用の`RESULT_KEY`は、機能名のプレフィックス（`blog_*`, `email_*`など）を付けて他モジュールと重複しないようにする（下記「Streamlitの実行モデルに関する注意」を参照）。

## Streamlitの実行モデルに関する注意

`st.tabs()`で作った各タブは、実際に表示されているタブだけでなく**全タブの`render()`が毎回のスクリプト再実行（rerun）で呼ばれる**（非表示のタブも裏で描画される）。そのため：
- 各`features/*.py`のwidgetキー（`key="blog_theme"`など）は全モジュールを通じて一意である必要がある。重複するとStreamlitが例外を出す。
- あるタブでの入力・ボタン操作が原因で発生するrerunでも、他の全タブのコードが実行される（ただし他タブのAPI呼び出しは対応するボタンが押されたときのみ発火するため、意図せずGemini APIが多重に呼ばれることはない）。
- `value=`と`key=`を同時に指定したwidgetは、**2回目以降のrerunで`value`が無視される**（keyがsession_stateに登録された後は、widgetの内部状態が`value`引数より優先されるため）。`ui_helpers.render_output()`が生成結果を表示できなくなるバグの原因になったため、動的に変わる表示専用widgetには`key`を付けない（`src/ui_helpers.py`）。

## Gemini API SDKについて

Google製のGemini用Pythonパッケージには新旧2系統（新: `google-genai`、旧: `google-generativeai`）があり、本プロジェクトは新しい方の`google-genai`を使用している。コードを変更する際は`genai.configure()` / `genai.GenerativeModel(...)`のような旧SDKのAPIではなく、`genai.Client(api_key=...)` → `client.models.generate_content(model=, contents=, config=types.GenerateContentConfig(...))`という新SDKの呼び出し形式（`src/gemini_client.py`）に合わせること。

### モデルの指定方法

`src/config.py`の`DEFAULT_MODEL`に固定モデル名（現在`gemini-3.6-flash`）をハードコードしている。この値を変更するだけでアプリ全体のモデルが切り替わる。

これまでに次の2つの方式を試して、いずれも問題が出たため現在の固定方式に落ち着いた経緯がある:
1. 個別バージョンのハードコード（`gemini-2.5-flash`）→ Googleの提供終了で404 NOT_FOUNDになった。
2. `client.models.list()`から毎回最新バージョンを自動選択する方式 → 選ばれた最新版（`gemini-3.8-flash`）が高負荷で503エラーを頻発させた。「最新」が「安定して使える」とは限らないため撤去した。

新モデルへの切り替えは、`DEFAULT_MODEL`の値を手動で更新する運用とする（自動追従はしない）。

### リトライについて

`generate()`は、`google.genai.errors.ServerError`（5xx。503の高負荷エラーなど）や429（レート制限）を検知した場合、`_MAX_RETRIES`回まで待機を挟んで自動リトライする。404などそれ以外の`ClientError`は即座に例外を投げ、`ui_helpers.run_generation()`側の`try/except`で`st.error`として表示される。リトライ対象を広げる場合は`_RETRYABLE_CLIENT_CODES`にステータスコードを追加する。

## 動作確認について

自動テストは存在しない（UIアプリのため）。ロジックやプロンプトを変更した場合は、`streamlit run app.py`を実際に起動し、対象タブの入力フォームから生成まで一通り動かして確認する。構文エラーのみを素早く確認したい場合は`python -m py_compile`を使う。
