# Instacart Recommender

Aplicación ejecutiva en Streamlit para anticipar el próximo carrito, explicar los drivers de propensión y convertir predicciones cliente-producto en audiencias accionables.

La interfaz está disponible en español e inglés y permite compartir cada idioma mediante el parámetro `?lang=es` o `?lang=en`.

## Contenido

- Inicio y resumen del caso de estudio.
- Ranking personalizado del próximo carrito.
- Drivers de propensión y explicaciones locales.
- Activación de audiencias por producto y categoría.
- Motor predictivo, feature engineering y metodología.
- Performance del modelo, baselines y análisis por deciles.

## Datos

La aplicación utiliza archivos Parquet ya exportados: no entrena ni recalcula modelos durante la ejecución. El caso de estudio parte del [Instacart Market Basket Analysis Dataset](https://www.instacart.com/datasets/grocery-shopping-2017).

`data/recommendations_top20.parquet` se versiona con Git LFS porque supera el límite convencional de tamaño de archivo de GitHub.

## Ejecutar localmente

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
python3 -m streamlit run app.py
```

## Archivos de serving

- `basket_size_by_user.parquet`
- `customer_profiles.parquet`
- `dataset_summary.parquet`
- `feature_catalog.parquet`
- `mba_feature_effectiveness.parquet`
- `mba_pairs.parquet`
- `model_deciles.parquet`
- `model_metrics.parquet`
- `orders_per_user.parquet`
- `product_catalog.parquet`
- `recommendations_top20.parquet`

La explicación SHAP detallada se activa cuando la exportación del notebook genera también `data/local_shap_top20.parquet`.

## Deploy

El punto de entrada es `app.py`. Para desplegar en Streamlit Community Cloud, seleccionar este repositorio, la rama `main` y ese archivo como entrada. El entorno instala las dependencias desde `requirements.txt`.

## Autor

Fernando M. Restelli<br>
[LinkedIn](https://www.linkedin.com/in/fernando-m-restelli/) · [GitHub](https://github.com/FernandoMRestelli) · [Email](mailto:fernandomrestelli@gmail.com)
