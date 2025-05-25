import yfinance as yf
from sec_api import ExtractorApi, QueryApi
import pandas as pd, os, json

def load_price_data(ticker: str) -> pd.DataFrame:
    df = yf.download(ticker, period="5y", auto_adjust=True, progress=False)
    if df.empty:
        raise FileNotFoundError("株価データなし")
    return df

def _get_last_filing_url(ticker: str, form_type="10-Q"):
    queryApi = QueryApi(api_key=os.getenv("SEC_API_KEY"))

    # 最新ファイリングを 1 件だけ取得（降順ソートを明示）
    query = {
        "query": {
            "query_string": {"query": f"ticker:{ticker} AND formType:{form_type}"}
        },
        "size": 1,
        "sort": [{"filedAt": {"order": "desc"}}]
    }

    res = queryApi.get_filings(query)

    if not res:
        return None

    doc = res[0]
    # 2025-03 以降の新キー
    url = doc.get("filingUrl") \
        or doc.get("linkToFilingDetails") \
        or doc.get("linkToTxt") \
        or doc.get("linkToHtml")

    return url

def load_fundamentals(ticker: str):
    extractor = ExtractorApi(os.getenv("SEC_API_KEY"))
    url = _get_last_filing_url(ticker, "10-Q") or _get_last_filing_url(ticker, "10-K")
    if url is None:
        raise FileNotFoundError("最新10-Q/10-K が見つからない")
    statements = extractor.get_plaintext_filings(url, "financial-statements")
    return json.loads(statements)

def analyse_fundamentals(fs_dict):
    bs = pd.DataFrame(fs_dict["balanceSheet"])
    is_ = pd.DataFrame(fs_dict["incomeStatement"])
    latest = {**bs.iloc[0].to_dict(), **is_.iloc[0].to_dict()}
    pe = latest["netIncome"] and latest["marketCap"] / latest["netIncome"]
    roe = latest["netIncome"] / latest["totalShareholderEquity"]
    debt_equity = latest["totalDebt"] / latest["totalShareholderEquity"]
    metrics = {"P/E": pe, "ROE": roe, "Debt/Equity": debt_equity}
    return pd.Series(metrics).apply(lambda x: round(x, 2)).to_frame("Value")