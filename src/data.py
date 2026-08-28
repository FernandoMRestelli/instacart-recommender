from __future__ import annotations

from pathlib import Path
import duckdb
import pandas as pd
import streamlit as st

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"


def _file(name: str) -> Path:
    p = DATA_DIR / name
    if not p.exists():
        raise FileNotFoundError(
            f"No existe {p.name}. Corré la celda 'EXPORTS PARA STREAMLIT' de la notebook."
        )
    return p


@st.cache_data(show_spinner=False)
def load_parquet(name: str) -> pd.DataFrame:
    return pd.read_parquet(_file(name))


@st.cache_data(show_spinner=False)
def dataset_summary():
    return load_parquet("dataset_summary.parquet").iloc[0]


@st.cache_data(show_spinner=False)
def customer_profiles():
    return load_parquet("customer_profiles.parquet")


@st.cache_data(show_spinner=False)
def product_catalog():
    return load_parquet("product_catalog.parquet")


@st.cache_data(show_spinner=False)
def user_recommendations(user_id: int) -> pd.DataFrame:
    path = str(_file("recommendations_top20.parquet")).replace("'", "''")
    with duckdb.connect() as con:
        df = con.execute(
            f"""
            SELECT *
            FROM read_parquet('{path}')
            WHERE user_id = ?
            ORDER BY rank
            """,
            [int(user_id)],
        ).fetchdf()
    if df.empty:
        return df
    return df.merge(product_catalog(), on="product_id", how="left", validate="many_to_one")


@st.cache_data(show_spinner=False)
def mba_pairs(product_id: int | None = None, limit: int = 20) -> pd.DataFrame:
    path = str(_file("mba_pairs.parquet")).replace("'", "''")
    with duckdb.connect() as con:
        if product_id is None:
            return con.execute(
                f"SELECT * FROM read_parquet('{path}') ORDER BY lift DESC, pair_orders DESC LIMIT ?",
                [limit],
            ).fetchdf()
        return con.execute(
            f"""
            SELECT * FROM read_parquet('{path}')
            WHERE product_a = ? OR product_b = ?
            ORDER BY lift DESC, pair_orders DESC
            LIMIT ?
            """,
            [int(product_id), int(product_id), limit],
        ).fetchdf()


@st.cache_data(show_spinner=False)
def mba_effectiveness():
    return load_parquet("mba_feature_effectiveness.parquet")


@st.cache_data(show_spinner=False)
def model_metrics():
    return load_parquet("model_metrics.parquet")


@st.cache_data(show_spinner=False)
def model_deciles():
    return load_parquet("model_deciles.parquet")


@st.cache_data(show_spinner=False)
def feature_catalog():
    return load_parquet("feature_catalog.parquet")


@st.cache_data(show_spinner=False)
def local_shap(user_id: int, product_id: int) -> pd.DataFrame:
    path = str(_file("local_shap_top20.parquet")).replace("'", "''")
    with duckdb.connect() as con:
        return con.execute(
            f"""
            SELECT *
            FROM read_parquet('{path}')
            WHERE user_id = ? AND product_id = ?
            LIMIT 1
            """,
            [int(user_id), int(product_id)],
        ).fetchdf()
