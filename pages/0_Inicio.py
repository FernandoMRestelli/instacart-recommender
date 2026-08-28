from base64 import b64encode
from pathlib import Path

import streamlit as st
import plotly.express as px

from src.data import dataset_summary, load_parquet
from src.i18n import is_english, tr
from src.style import apply_style, html_card, next_page_link, style_plotly


# ============================================================
# CONFIGURACIÓN
# ============================================================

st.set_page_config(
    page_title=tr("Anticipando el próximo carrito", "Anticipating the next basket"),
    page_icon="🛒",
    layout="wide"
)

apply_style()


@st.cache_data(show_spinner=False)
def home_header_data_uri(filename: str) -> str:
    image_path = Path(__file__).resolve().parents[1] / "assets" / filename
    encoded = b64encode(image_path.read_bytes()).decode("ascii")
    mime = "image/webp" if image_path.suffix.lower() == ".webp" else "image/png"
    return f"data:{mime};base64,{encoded}"

st.markdown(
    """
    <style>
      .home-showcase {
        display: grid;
        grid-template-columns: minmax(210px, .68fr) minmax(0, 2fr);
        align-items: center;
        gap: 1.25rem;
        margin: -.15rem 0 1.35rem;
      }
      .home-case-column { position: relative; z-index: 2; }
      .home-case-kicker {
        color: #5b45f5;
        font-size: .64rem;
        font-weight: 800;
        letter-spacing: .09em;
        text-transform: uppercase;
      }
      .home-case-title {
        margin: .48rem 0 1rem !important;
        color: #142138;
        font-size: 1.18rem !important;
        line-height: 1.3 !important;
      }
      .home-case-cards { display: flex; flex-direction: column; gap: .7rem; }
      .home-showcase .card { width: 100%; min-height: 92px; margin: 0; padding: .9rem 1rem; }
      .home-showcase .card-value { font-size: .92rem; line-height: 1.35; }
      .home-visual-stage { position: relative; min-width: 0; }
      .home-cover-image {
        overflow: hidden;
        border: 1px solid #243754;
        border-radius: 12px;
        background: #06152b;
        box-shadow: 0 12px 28px rgba(16, 29, 50, .16);
      }
      .home-cover-image img {
        display: block;
        width: 100%;
        height: auto;
      }
      @media (max-width: 900px) {
        .home-showcase { grid-template-columns: 1fr; }
        .home-case-title { max-width: 34rem; }
      }
    </style>
    """,
    unsafe_allow_html=True,
)

header_filename = "instacart_header_en.webp" if is_english() else "instacart_header.webp"
header_alt = tr(
    "Anticipamos el próximo carrito con Machine Learning",
    "We anticipate the next purchase with Machine Learning",
)
st.html(
    f"""
    <section class="home-showcase">
      <div class="home-case-column">
        <div class="home-case-kicker">{tr('Caso de estudio', 'Case study')}</div>
        <h2 class="home-case-title">{tr('Instacart, sus clientes y sus comportamientos de compra.', 'Instacart, its customers, and their purchase behavior.')}</h2>
        <div class="home-case-cards">
          <div class="card accent-violet home-case-card">
            <div class="card-label">Instacart</div>
            <div class="card-value">{tr('Supermercado online con delivery', 'Online grocery delivery')}</div>
          </div>
          <div class="card accent-teal">
            <div class="card-label">{tr('La base', 'The data')}</div>
            <div class="card-value">{tr('Historial de pedidos y productos', 'Order and product history')}</div>
          </div>
          <div class="card soft-violet accent-purple">
            <div class="card-label">{tr('Objetivo', 'Objective')}</div>
            <div class="card-value">{tr('Anticipar el próximo carrito', 'Anticipate the next basket')}</div>
          </div>
        </div>
      </div>
      <div class="home-visual-stage">
        <div class="home-cover-image">
          <img src="{home_header_data_uri(header_filename)}" alt="{header_alt}">
        </div>
      </div>
    </section>
    """
)

# ============================================================
# DATASET
# ============================================================

st.markdown(tr("### Descripción:", "### Description:"))

try:

    s = dataset_summary()

    cols = st.columns(5)

    cards = [
        (
            tr("Clientes", "Customers"),
            f"{int(s['clients']):,}",
            tr("usuarios", "users"),
            "accent-violet",
        ),
        (
            tr("Pedidos", "Orders"),
            f"{int(s['orders']):,}",
            tr("órdenes", "orders"),
            "accent-teal",
        ),
        (
            tr("Productos", "Products"),
            f"{int(s['products']):,}",
            "SKU",
            "accent-purple",
        ),
        (
            tr("Departamentos", "Departments"),
            f"{int(s['departments']):,}",
            tr("categorías macro", "macro categories"),
            "accent-orange",
        ),
        (
            tr("Pasillos", "Aisles"),
            f"{int(s['aisles']):,}",
            "aisles",
            "accent-slate",
        ),
    ]

    for col, (label, value, note, css) in zip(cols, cards):

        with col:
            html_card(
                label,
                value,
                note,
                css,
            )


    # ========================================================
    # TAMAÑO DEL CARRITO
    # ========================================================

    st.markdown(tr("### ¿Cómo son los carritos de compra?", "### What do shopping baskets look like?"))

    st.write(
        tr("Distribución del tamaño habitual del carrito de cada cliente, medido como la cantidad promedio de productos por pedido.", "Distribution of each customer's typical basket size, measured as the average number of products per order.")
    )


    # Cargar tabla previamente generada en la notebook

    basket = load_parquet(
        "basket_size_by_user.parquet"
    )


    # ========================================================
    # ESTADÍSTICAS
    # ========================================================

    x = basket["avg_products_per_order"]

    avg_basket = x.mean()
    median_basket = x.median()
    q1_basket = x.quantile(0.25)
    q3_basket = x.quantile(0.75)


    # Cards ejecutivas

    m1, m2, m3, m4 = st.columns(4)

    with m1:
        html_card(
            tr("Promedio", "Average"),
            f"{avg_basket:.1f}",
            tr("productos por pedido", "products per order"),
            "accent-orange",
        )

    with m2:
        html_card(
            tr("Mediana", "Median"),
            f"{median_basket:.1f}",
            tr("productos por pedido", "products per order"),
            "accent-violet",
        )

    with m3:
        html_card(
            "Q1",
            f"{q1_basket:.1f}",
            tr("25% de los clientes", "25% of customers"),
            "accent-teal",
        )

    with m4:
        html_card(
            "Q3",
            f"{q3_basket:.1f}",
            tr("75% de los clientes", "75% of customers"),
            "accent-purple",
        )


    # ========================================================
    # HISTOGRAMA + BOXPLOT
    # ========================================================

    fig = px.histogram(
    basket,
    x="avg_products_per_order",
    nbins=45,
    )

    # Estilo general
    style_plotly(fig)


    # Barras
    fig.update_traces(
        marker=dict(
            color="#635BFF",
            line=dict(
                color="white",
                width=1
            )
        ),
        opacity=0.82,
        hovertemplate=(
            tr("<b>%{x:.1f} productos</b><br>Clientes: %{y:,}", "<b>%{x:.1f} products</b><br>Customers: %{y:,}")
            + "<extra></extra>"
        )
    )


    # Línea de mediana
    fig.add_vline(
        x=median_basket,
        line_width=2,
        line_dash="dot",
        line_color="#171C2C"
    )


    # Etiqueta de mediana
    fig.add_annotation(
        x=median_basket,
        y=0.96,
        yref="paper",
        text=f"<b>{tr('Mediana', 'Median')} · {median_basket:.1f}</b>",
        showarrow=False,
        xanchor="left",
        xshift=8,
        bgcolor="#F0EEFF",
        bordercolor="#D8D3FF",
        borderwidth=1,
        borderpad=6,
        font=dict(
            size=12,
            color="#4C3ED9"
        )
    )


    # Layout
    fig.update_layout(
        height=420,
        title=None,
        margin=dict(
            l=20,
            r=20,
            t=25,
            b=20
        ),
        plot_bgcolor="white",
        paper_bgcolor="rgba(0,0,0,0)",
        bargap=0.04,
        showlegend=False,
        font=dict(
            family="Inter, Arial, sans-serif",
            color="#5B6475",
            size=12
        )
    )


    # Eje X
    fig.update_xaxes(
        title=dict(
            text=tr("Productos promedio por pedido", "Average products per order"),
            font=dict(
                size=13,
                color="#8791A5"
            )
        ),
        tickfont=dict(
            size=11,
            color="#667085"
        ),
        showgrid=False,
        zeroline=False,
        showline=True,
        linecolor="#E5E9F0",
        linewidth=1,
        ticks=""
    )


    # Eje Y
    fig.update_yaxes(
        title=dict(
            text=tr("Cantidad de clientes", "Number of customers"),
            font=dict(
                size=13,
                color="#8791A5"
            )
        ),
        tickfont=dict(
            size=11,
            color="#667085"
        ),
        gridcolor="#EEF1F6",
        gridwidth=1,
        zeroline=False,
        showline=False,
        ticks=""
    )


    st.markdown("<div class='section-gap'></div>", unsafe_allow_html=True)
    chart_col, insight_col = st.columns([3, 1.15], gap="medium")

    with chart_col:
        st.plotly_chart(
            fig,
            use_container_width=True,
            config={
                "displayModeBar": False
            }
        )

    with insight_col:
        st.markdown(
            f"""
            <div class="insight-card">
              <h3>{tr('Qué aporta la base', 'What the data provides')}</h3>
              <ul>
                <li>{tr('Pedidos históricos del cliente', 'Customer order history')}</li>
                <li>{tr('Productos por pedido', 'Products per order')}</li>
                <li>{tr('Días entre pedidos', 'Days between orders')}</li>
                <li>{tr('Historial cliente-producto', 'Customer-product history')}</li>
                <li>{tr('Productos del último carrito', 'Products in the latest basket')}</li>
                <li>{tr('Frecuencia y recencia de recompra', 'Repurchase frequency and recency')}</li>
              </ul>
              <div class="insight-card-note">{tr('Se muestran únicamente las señales utilizadas por el modelo.', 'Only signals used by the model are shown.')}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )




except FileNotFoundError as e:

    st.info(str(e))


# ============================================================
# STORYTELLING
# ============================================================

st.markdown(tr("### Resumen", "### Summary"))

st.write(
    tr("La base permite observar cómo compran los clientes de Instacart: cuántos pedidos realizan, qué tamaño tienen sus carritos y con qué frecuencia vuelven a comprar. Esta información constituye el punto de partida para entender sus hábitos y avanzar hacia una estimación personalizada del próximo carrito.", "The data reveals how Instacart customers shop: how many orders they place, how large their baskets are, and how frequently they return. This information is the starting point for understanding their habits and building a personalized estimate of the next basket.")
)

st.markdown(
        f"""
        <div class="decision-callout">
          {tr('De millones de interacciones históricas a una decisión simple: qué producto priorizar para cada cliente en su próxima compra.', 'From millions of historical interactions to one simple decision: which product to prioritize for each customer in their next purchase.')}
        </div>
        """,
        unsafe_allow_html=True,
    )

st.html(
    f"""
    <div class="project-link-banner project-link-dataset">
      <div>
        <span>{tr('Fuente de datos', 'Data source')}</span>
        <strong>Instacart Market Basket Analysis</strong>
        <p>{tr('Dataset público con pedidos, productos y secuencias históricas de compra.', 'Public dataset containing orders, products, and historical purchase sequences.')}</p>
      </div>
      <a href="https://www.kaggle.com/c/instacart-market-basket-analysis/data" target="_blank" rel="noopener noreferrer">{tr('Ver dataset', 'View dataset')} ↗</a>
    </div>
    """
)

next_page_link("Proximo_Carrito", "Próximo carrito", "Next basket")
