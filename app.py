import streamlit as st

from src.i18n import language_selector, tr
from src.style import mobile_top_navigation, sidebar_footer


language_selector()
sidebar_footer()
mobile_top_navigation()


pages = [
    st.Page("pages/0_Inicio.py", title=tr("Inicio", "Home"), icon="🏠", default=True),
    st.Page(
        "pages/1_Proximo_Carrito.py",
        title=tr("Próximo carrito", "Next basket"),
        icon="🛒",
    ),
    st.Page("pages/2_Factores.py", title=tr("Drivers de propensión", "Propensity drivers"), icon="🔎"),
    st.Page("pages/3_Audiencias.py", title=tr("Activación de audiencias", "Audience activation"), icon="👥"),
    st.Page("pages/5_Como_Se_Predice.py", title=tr("Motor predictivo", "Predictive engine"), icon="⚙️"),
    st.Page("pages/6_Metricas.py", title=tr("Performance del modelo", "Model performance"), icon="📈"),
]

navigation = st.navigation(pages)
navigation.run()
