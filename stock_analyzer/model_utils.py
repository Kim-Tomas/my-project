import pandas as pd, numpy as np
from ta import add_all_ta_features
from xgboost import XGBRegressor
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import mean_absolute_error

def build_features(df: pd.DataFrame, horizon: int = 5):
    df_feat = df.copy()
    df_feat = add_all_ta_features(df_feat, open="Open", high="High", low="Low", close="Close", volume="Volume")
    df_feat["fwd_return"] = df_feat["Close"].shift(-horizon) / df_feat["Close"] - 1
    df_feat.dropna(inplace=True)
    y = df_feat.pop("fwd_return")
    X = df_feat
    latest_feats = X.iloc[[-1]]
    return X.iloc[:-1], y.iloc[:-1], latest_feats

def train_predict(X, y, latest_feats):
    tss = TimeSeriesSplit(n_splits=5)
    preds, trues = [], []
    for train, test in tss.split(X):
        model = XGBRegressor(n_estimators=200, max_depth=4, subsample=0.8,
                             learning_rate=0.05, objective="reg:squarederror",
                             n_jobs=-1, random_state=42)
        model.fit(X.iloc[train], y.iloc[train])
        preds.extend(model.predict(X.iloc[test]))
        trues.extend(y.iloc[test])
    mae = mean_absolute_error(trues, preds)
    final_model = XGBRegressor(n_estimators=200, max_depth=4, subsample=0.8,
                               learning_rate=0.05, objective="reg:squarederror",
                               n_jobs=-1, random_state=42)
    final_model.fit(X, y)
    pred_latest = float(final_model.predict(latest_feats)[0])
    return pred_latest, mae