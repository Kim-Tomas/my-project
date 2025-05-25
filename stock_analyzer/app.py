import streamlit as st
import os
from finance_utils import load_price_data, load_fundamentals, analyse_fundamentals
from model_utils import build_features, train_predict

st.set_page_config(page_title="US Stock Analyzer", layout="wide")
st.title("📈 US Stock Fundamental + ML Technical Analyzer")

# -- API KEY handling --
SEC_API_KEY = os.getenv("SEC_API_KEY")
if not SEC_API_KEY:
    SEC_API_KEY = st.text_input("SEC_API_KEY (SEC EDGAR API)", type="password")
    if SEC_API_KEY:
        os.environ["SEC_API_KEY"] = SEC_API_KEY

ticker = st.text_input("Ticker (e.g. AAPL)", value="AAPL").upper()

if st.button("解析開始") and ticker:
    try:
        with st.spinner("📥 データ収集中…"):
            price_df = load_price_data(ticker)
            fs_dict   = load_fundamentals(ticker)
        with st.spinner("🔍 ファンダメンタルズ解析…"):
            funda_summary = analyse_fundamentals(fs_dict)
        with st.spinner("🤖 機械学習モデル学習＆予測…"):
            X, y, latest_feats = build_features(price_df)
            pred, mae = train_predict(X, y, latest_feats)

        signal = "Buy" if pred > 0.03 else ("Sell" if pred < -0.03 else "Hold")
        st.subheader(f"最終シグナル: **{signal}**")
        col1, col2 = st.columns(2)
        col1.metric(label="予測5日後騰落率", value=f"{pred*100:.2f}%")
        col2.metric(label="モデルMAE(検証)", value=f"{mae*100:.2f}%")
        st.write("### バリュエーション指標")
        st.dataframe(funda_summary)
        st.line_chart(price_df["Close"].tail(250))
    except FileNotFoundError as e:
        st.error(f"必要資料が取得できませんでした: {e}\n手動で10-K/10-Q XBRLファイルをアップロードしてください。")