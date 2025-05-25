# US Stock Analyzer (Streamlit)

ワンクリックでファンダメンタル＋機械学習テクニカル分析を実行し、Buy / Hold / Sell シグナルを表示するアプリです。

## 使い方 (Streamlit Community Cloud)

1. GitHub にこのリポジトリをプッシュ  
2. https://streamlit.io/cloud で **New App** → リポジトリを選択  
3. **Main file**: `app.py`  
4. **Advanced settings → Secrets** に下記を追加  

```
SEC_API_KEY = "あなたのSEC APIキー"
```

5. **Deploy** ⇒ すぐに公開URLが発行されます

## ローカル動作

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export SEC_API_KEY=xxxxxxxxxxxxxxxx
streamlit run app.py
```

## Docker (任意)

```bash
docker build -t stock-analyzer .
docker run -e SEC_API_KEY=xxxxxxxx -p 8501:8501 stock-analyzer
```