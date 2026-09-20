# AIライティングツール

Gemini APIを使った個人用のAIライティングツールです。以下の5機能をタブで切り替えて使えます。

- 📝 ブログ執筆
- 📧 メール返信文の作成
- 📄 文章の要約
- ✏️ 文章の校正・リライト
- 💡 タイトル・見出し案の作成

## セットアップ

依存パッケージをインストールします。

```bash
pip install -r requirements.txt
```

## 起動方法

```bash
streamlit run app.py
```

ブラウザで `http://localhost:8501` が開いたら、左のサイドバーにGemini APIキーを入力してください。
APIキーは [Google AI Studio](https://aistudio.google.com/apikey) から取得できます。

APIキーはファイルに保存されず、ブラウザのセッション内でのみ使用されます（ページを再読み込みすると再入力が必要です）。
使用するモデルは選択式ではなく、`gemini-3.6-flash`に固定しています（`src/config.py`の`DEFAULT_MODEL`で変更できます）。
