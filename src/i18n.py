from __future__ import annotations

import streamlit as st


LANGUAGE_KEY = "app_language"
LANGUAGE_SELECTOR_KEY = "app_language_selector"
LANGUAGE_QUERY_PARAMETER = "lang"

FEATURE_DESCRIPTIONS_EN = {
    "source_previous": "The customer purchased the product before.",
    "source_similar_users": "The product appears among customers with similar purchasing behavior.",
    "source_global_popular": "The product enters through global popularity.",
    "Cant_de_pedidos": "Number of historical orders available.",
    "avg_products_per_order_user": "The customer's average basket size.",
    "avg_days_between_orders": "Average frequency between orders.",
    "std_days_between_orders": "Variability in purchase frequency.",
    "user_product_orders": "Number of orders in which the customer purchased the product.",
    "user_product_order_share": "Share of the customer's orders containing the product.",
    "days_since_user_product": "Days since the product was last purchased.",
    "avg_days_between_product": "Average repurchase cadence for the product.",
    "reorder_due_ratio": "Compares current recency with the historical repurchase cadence.",
    "neighbor_buyers": "Number of similar neighbors who purchased the product.",
    "neighbor_similarity_sum": "Sum of similarity among buyer neighbors.",
    "neighbor_similarity_max": "Highest observed similarity among buyer neighbors.",
    "neighbor_similarity_mean": "Average similarity among buyer neighbors.",
    "global_unique_buyers": "Number of unique buyers of the product.",
    "global_purchase_count": "Number of historical orders that included the product.",
    "global_product_penetration": "Product penetration across the customer base.",
    "max_lift_last_basket": "Highest lift between the candidate and products in the latest basket.",
    "mean_lift_last_basket": "Average lift versus products in the latest basket.",
    "max_confidence_last_basket": "Highest association confidence with the latest basket.",
    "count_last_basket_products": "Number of latest-basket products associated with the candidate.",
    "max_lift_core_products": "Highest lift versus the customer's characteristic products.",
    "mean_lift_core_products": "Average lift versus the customer's characteristic products.",
    "sum_weighted_lift_core_products": "Sum of lift weighted by the historical relevance of core products.",
    "count_lift_core_products": "Number of core products associated with the candidate.",
}


def language() -> str:
    return st.session_state.get(LANGUAGE_KEY, "es")


def is_english() -> bool:
    return language() == "en"


def tr(spanish: str, english: str) -> str:
    return english if is_english() else spanish


def feature_description(feature: str, spanish_description: str) -> str:
    if not is_english():
        return spanish_description
    return FEATURE_DESCRIPTIONS_EN.get(feature, spanish_description)


def language_selector() -> str:
    query_language = st.query_params.get(LANGUAGE_QUERY_PARAMETER)
    if query_language not in {"es", "en"}:
        query_language = None

    if LANGUAGE_KEY not in st.session_state:
        st.session_state[LANGUAGE_KEY] = query_language or "es"
    if LANGUAGE_SELECTOR_KEY not in st.session_state:
        st.session_state[LANGUAGE_SELECTOR_KEY] = (
            "English" if st.session_state[LANGUAGE_KEY] == "en" else "Español"
        )
    selected = st.sidebar.selectbox(
        "Idioma / Language",
        ["Español", "English"],
        key=LANGUAGE_SELECTOR_KEY,
    )
    st.session_state[LANGUAGE_KEY] = "en" if selected == "English" else "es"
    if st.query_params.get(LANGUAGE_QUERY_PARAMETER) != st.session_state[LANGUAGE_KEY]:
        st.query_params[LANGUAGE_QUERY_PARAMETER] = st.session_state[LANGUAGE_KEY]
    return st.session_state[LANGUAGE_KEY]
