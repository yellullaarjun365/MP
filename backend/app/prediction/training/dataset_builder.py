from __future__ import annotations

from pathlib import Path

import pandas as pd
from sqlalchemy import text
from sqlalchemy.engine import Engine


TARGET = "production_kg"


def build_historical_dataset(
    engine: Engine,
) -> pd.DataFrame:

    query = text(
        """
        SELECT
            h.pond_id,
            h.harvested_at,
            h.quantity_kg AS production_kg,
            h.average_weight_g,
            h.survival_rate,

            p.area_m2 AS pond_area_m2,
            p.depth_m AS pond_depth_m,

            sr.quantity AS stocking_count,
            sr.initial_average_weight_g

        FROM harvest_records h

        LEFT JOIN ponds p
          ON p.id = h.pond_id

        LEFT JOIN LATERAL (
            SELECT
                quantity,
                initial_average_weight_g
            FROM stocking_records
            WHERE pond_id = h.pond_id
              AND stocked_at <= h.harvested_at
            ORDER BY stocked_at DESC
            LIMIT 1
        ) sr
          ON TRUE

        ORDER BY h.harvested_at
        """
    )

    return pd.read_sql(
        query,
        engine,
    )


def save_dataset(
    dataframe: pd.DataFrame,
    destination: str | Path,
) -> Path:

    destination = Path(destination)

    destination.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    dataframe.to_csv(
        destination,
        index=False,
    )

    return destination
