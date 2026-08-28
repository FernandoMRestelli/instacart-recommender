from html import escape
from os import getenv

import streamlit as st

from src.data import feature_catalog
from src.i18n import is_english, tr
from src.style import apply_style, hero, next_page_link

st.set_page_config(page_title=tr("Motor predictivo", "Predictive engine"), page_icon="⚙️", layout="wide")
apply_style()
hero(tr("Cómo se predice", "How predictions are made"), tr("Del historial de compra a un ranking cliente-producto, de punta a punta.", "From purchase history to a customer-product ranking, end to end."))

st.markdown(tr("## Flujo del sistema", "## System flow"))
st.markdown(
    f"""
    <div class="chart-intro">
      {tr('El proceso transforma compras históricas en una lista priorizada y explicable para cada cliente. Cada etapa utiliza únicamente la información disponible antes del carrito que se busca predecir.', 'The process transforms historical purchases into a prioritized and explainable list for each customer. Every stage uses only the information available before the basket being predicted.')}
    </div>
    """,
    unsafe_allow_html=True,
)

pipeline_rows = [
    [
        ("01", tr("Datos temporales", "Temporal data"), tr("Ordena compras históricas", "Orders historical purchases"), tr("Preparación", "Preparation")),
        ("02", tr("Split temporal", "Temporal split"), tr("Evita información futura", "Prevents future leakage"), tr("Validación", "Validation")),
        ("03", tr("Candidatos híbridos", "Hybrid candidates"), tr("Historial vecinos popularidad", "History neighbors popularity"), tr("Generación", "Generation")),
        ("04", "KNN coseno", tr("Detecta compradores similares", "Finds similar shoppers"), "Machine Learning"),
        ("05", "Market Basket", tr("Relaciona productos frecuentes", "Links frequent products"), "Data Mining"),
    ],
    [
        ("06", "Feature engineering", tr("Frecuencia recencia cadencia", "Frequency recency cadence"), "Data Science"),
        ("07", "Optuna", tr("Optimiza hiperparámetros NDCG", "Optimizes NDCG parameters"), tr("Optimización", "Optimization")),
        ("08", "LightGBM", tr("Combina señales predictivas", "Combines predictive signals"), tr("Modelo", "Model")),
        ("09", "Ranking Top 20", tr("Prioriza próxima compra", "Prioritizes next purchase"), tr("Recomendación", "Recommendation")),
        ("10", tr("Salida accionable", "Actionable output"), tr("Activa campañas medibles", "Activates measurable campaigns"), tr("Activación", "Activation")),
    ],
]

rows_html = []
for row_number, row in enumerate(pipeline_rows):
    cards = []
    for index, (number, title, phrase, family) in enumerate(row):
        cards.append(
            f"""
            <div class="pipeline-card">
              <div class="pipeline-card-top">
                <span class="pipeline-number">{number}</span>
                <span class="pipeline-family">{family}</span>
              </div>
              <div class="pipeline-title">{title}</div>
              <div class="pipeline-phrase">{phrase}</div>
            </div>
            """
        )
        if index < len(row) - 1:
            cards.append('<div class="pipeline-arrow" aria-hidden="true">→</div>')
    rows_html.append(f'<div class="pipeline-row">{"".join(cards)}</div>')
    if row_number == 0:
        rows_html.append(
            f'<div class="pipeline-turn"><span>{tr("Señales listas", "Signals ready")}</span><b>↓</b></div>'
        )

st.html(f'<div class="pipeline-shell">{"".join(rows_html)}</div>')

st.markdown(tr("## Modelos y técnicas utilizadas", "## Models and techniques used"))
st.markdown(
    f"""
    <div class="chart-intro">
      {tr('Las técnicas cumplen funciones distintas: ampliar candidatos, construir señales, aprender patrones y evaluar el orden del ranking antes de convertirlo en una audiencia accionable.', 'The techniques serve different purposes: expanding candidates, building signals, learning patterns, and evaluating ranking order before turning it into an actionable audience.')}
    </div>
    """,
    unsafe_allow_html=True,
)

techniques = [
    (
        "KNN + similitud coseno",
        tr("Descubrimiento colaborativo", "Collaborative discovery"),
        tr("Busca clientes cuyos historiales de compra tienen una orientación similar e incorpora productos comprados por esos vecinos.", "Finds customers whose purchase histories point in a similar direction and adds products purchased by those neighbors."),
        "#168f83",
    ),
    (
        "Market Basket Analysis",
        tr("Asociación entre productos", "Product association"),
        tr("Utiliza support, confidence y lift para medir qué productos suelen aparecer relacionados en los carritos.", "Uses support, confidence, and lift to measure which products tend to appear together in baskets."),
        "#9948e8",
    ),
    (
        "Feature engineering",
        tr("Señales cliente-producto", "Customer-product signals"),
        tr("Construye frecuencia, recencia, cadencia, afinidad colaborativa, popularidad y asociaciones para cada combinación.", "Builds frequency, recency, cadence, collaborative affinity, popularity, and association signals for each pair."),
        "#5b45f5",
    ),
    (
        "Optuna",
        tr("Optimización de hiperparámetros", "Hyperparameter optimization"),
        tr("Explora configuraciones de LightGBM y elige la que obtiene el mejor NDCG@10 sobre el período de validación.", "Explores LightGBM configurations and selects the one with the best NDCG@10 over the validation period."),
        "#c66205",
    ),
    (
        "LightGBM Classifier",
        tr("Modelo de propensión", "Propensity model"),
        tr("Combina todas las señales mediante árboles potenciados y estima un score para cada par cliente-producto.", "Combines all signals through boosted trees and estimates a score for each customer-product pair."),
        "#5b45f5",
    ),
    (
        "Validación temporal",
        tr("Evaluación sin leakage", "Leakage-free evaluation"),
        tr("Separa Train, Validation y Test respetando el orden de compra para evitar utilizar información futura.", "Separates Train, Validation, and Test while preserving purchase order to avoid using future information."),
        "#168f83",
    ),
    (
        "NDCG@10 + métricas Top K",
        tr("Calidad del ranking", "Ranking quality"),
        tr("Evalúa si los productos realmente comprados aparecen y quedan bien posicionados entre las primeras recomendaciones.", "Evaluates whether actually purchased products appear and rank well among the first recommendations."),
        "#c66205",
    ),
]

technique_cards = "".join(
    f"""
    <article class="technique-card" style="--tech-color:{color}">
      <div class="technique-role">{role}</div>
      <div class="technique-title">{title}</div>
      <p>{body}</p>
    </article>
    """
    for title, role, body, color in techniques
)
st.html(f'<div class="technique-grid">{technique_cards}</div>')

st.markdown(tr("## Feature engineering y componentes", "## Feature engineering and components"))
st.markdown(
    f"""
    <div class="chart-intro">
      {tr('Estas variables convierten el comportamiento histórico en señales comparables que LightGBM puede combinar para ordenar productos.', 'These variables turn historical behavior into comparable signals that LightGBM can combine to rank products.')}
    </div>
    """,
    unsafe_allow_html=True,
)
fc = feature_catalog()
component_content = {
    "Fuentes de candidatos": (
        tr("Define por qué un producto ingresa al universo que el modelo debe evaluar.", "Defines why a product enters the candidate universe evaluated by the model."),
        tr("Historial · Vecinos · Popularidad", "History · Neighbors · Popularity"),
        "#5b45f5",
    ),
    "Perfil del cliente": (
        tr("Resume la intensidad, frecuencia y tamaño habitual de sus compras.", "Summarizes purchase intensity, frequency, and typical basket size."),
        tr("Pedidos · Frecuencia · Carrito", "Orders · Frequency · Basket"),
        "#168f83",
    ),
    "Histórico cliente-producto": (
        tr("Mide la relación directa y la cadencia de recompra del producto.", "Measures the direct relationship and repurchase cadence for the product."),
        tr("Frecuencia · Recencia · Cadencia", "Frequency · Recency · Cadence"),
        "#9948e8",
    ),
    "Filtrado colaborativo": (
        tr("Cuantifica el respaldo del producto entre compradores con hábitos similares.", "Quantifies product support among shoppers with similar habits."),
        tr("Vecinos · Afinidad · Similitud", "Neighbors · Affinity · Similarity"),
        "#1475c9",
    ),
    "Popularidad": (
        tr("Aporta cobertura global cuando existe poco historial individual disponible.", "Provides global coverage when little individual history is available."),
        tr("Compradores · Pedidos · Penetración", "Buyers · Orders · Penetration"),
        "#c66205",
    ),
    "Market Basket Analysis": (
        tr("Detecta productos que suelen relacionarse dentro de una misma misión de compra.", "Detects products that tend to be related within the same shopping mission."),
        "Support · Confidence · Lift",
        "#687386",
    ),
}

component_cards = []
component_labels = {
    "Fuentes de candidatos": tr("Fuentes de candidatos", "Candidate sources"),
    "Perfil del cliente": tr("Perfil del cliente", "Customer profile"),
    "Histórico cliente-producto": tr("Histórico cliente-producto", "Customer-product history"),
    "Filtrado colaborativo": tr("Filtrado colaborativo", "Collaborative filtering"),
    "Popularidad": tr("Popularidad", "Popularity"),
    "Market Basket Analysis": "Market Basket Analysis",
}
for position, (category, group) in enumerate(fc.groupby("category", sort=False), start=1):
    description, keywords, color = component_content[category]
    component_cards.append(
        f"""
        <article class="feature-component-card" style="--component-color:{color}">
          <div class="feature-component-top">
            <span class="feature-component-number">{position:02d}</span>
            <span class="feature-component-count">{len(group)} {tr('señales', 'signals')}</span>
          </div>
          <div class="feature-component-title">{component_labels[category]}</div>
          <p>{description}</p>
          <div class="feature-component-keywords">{keywords}</div>
        </article>
        """
    )
st.html(f'<div class="feature-component-grid">{"".join(component_cards)}</div>')

st.markdown(tr("### Explorar las variables", "### Explore variables"))
selected_component = st.selectbox(
    tr("Componente", "Component"),
    fc["category"].drop_duplicates().tolist(),
    label_visibility="collapsed",
    format_func=component_labels.get,
)
selected_group = fc.loc[fc["category"].eq(selected_component)].copy()
description, keywords, color = component_content[selected_component]
st.html(
    f"""
    <div class="feature-explorer-intro" style="--component-color:{color}">
      <div>
        <span>{tr('Componente seleccionado', 'Selected component')}</span>
        <strong>{component_labels[selected_component]}</strong>
      </div>
      <p>{description} <b>{keywords}</b></p>
    </div>
    """
)
feature_descriptions_en = {
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
if is_english():
    selected_group["business_description"] = selected_group.apply(
        lambda row: feature_descriptions_en.get(row["feature"], row["business_description"]), axis=1
    )
selected_group = selected_group[["feature", "business_description"]].rename(
    columns={
        "feature": tr("Variable del modelo", "Model variable"),
        "business_description": tr("Qué representa", "What it represents"),
    }
)
st.dataframe(selected_group, width="stretch", hide_index=True)

st.markdown(tr("## Código y reproducibilidad", "## Code and reproducibility"))
st.markdown(
    f"""
    <div class="chart-intro">
      {tr('El repositorio reúne la notebook de modelado, el código de la aplicación y la lógica utilizada para generar los archivos de serving.', 'The repository contains the modeling notebook, application code, and the logic used to generate serving files.')}
    </div>
    """,
    unsafe_allow_html=True,
)
github_repository_url = getenv(
    "GITHUB_REPOSITORY_URL",
    "https://github.com/FernandoMRestelli/instacart-recommender",
).strip()
if github_repository_url:
    safe_github_url = escape(github_repository_url, quote=True)
    st.html(
        f"""
        <div class="project-link-banner project-link-github">
          <div><span>{tr('Repositorio del proyecto', 'Project repository')}</span><strong>{tr('Código completo en GitHub', 'Full code on GitHub')}</strong><p>{tr('Notebook, aplicación Streamlit y documentación técnica.', 'Notebook, Streamlit application, and technical documentation.')}</p></div>
          <a href="{safe_github_url}" target="_blank" rel="noopener noreferrer">{tr('Ver código', 'View code')} ↗</a>
        </div>
        """
    )

else:
    st.html(
        f"""
        <div class="project-link-banner project-link-github project-link-pending">
          <div><span>{tr('Repositorio del proyecto', 'Project repository')}</span><strong>{tr('Código completo en GitHub', 'Full code on GitHub')}</strong><p>{tr('El bloque está listo; falta incorporar la URL definitiva del repositorio.', 'This block is ready; the final repository URL still needs to be added.')}</p></div>
          <span class="project-link-status">{tr('Enlace pendiente', 'Link pending')}</span>
        </div>
        """
    )

next_page_link("Metricas", "Performance del modelo", "Model performance")
