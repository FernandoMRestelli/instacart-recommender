from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq


def export_local_shap(
    model,
    features: pd.DataFrame,
    identifiers: pd.DataFrame,
    output_path: str | Path,
    chunk_size: int = 50_000,
) -> None:
    """Exporta contribuciones SHAP locales sin conservarlas completas en memoria."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    writer = None

    try:
        for start in range(0, len(features), chunk_size):
            stop = min(start + chunk_size, len(features))
            x_chunk = features.iloc[start:stop]

            if hasattr(model, "booster_"):
                contributions = model.booster_.predict(x_chunk, pred_contrib=True)
            else:
                import shap

                values = shap.TreeExplainer(model)(x_chunk)
                contributions = np.column_stack(
                    [values.values, np.broadcast_to(values.base_values, len(x_chunk))]
                )

            contribution_frame = pd.DataFrame(
                contributions[:, :-1].astype("float32"),
                columns=[f"shap__{name}" for name in features.columns],
            )
            contribution_frame.insert(
                0, "base_value", contributions[:, -1].astype("float32")
            )
            chunk = pd.concat(
                [identifiers.iloc[start:stop].reset_index(drop=True), contribution_frame],
                axis=1,
            )
            table = pa.Table.from_pandas(chunk, preserve_index=False)
            if writer is None:
                writer = pq.ParquetWriter(output_path, table.schema, compression="snappy")
            writer.write_table(table)
    finally:
        if writer is not None:
            writer.close()
