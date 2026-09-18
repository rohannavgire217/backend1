import pandas as pd
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

try:
    from itip_backend.db.models import Detection
except ImportError:  # pragma: no cover
    from db.models import Detection

def ingest_firms_batch(db: Session, records: list[dict]):
    """
    Ingest a batch of FIRMS records.
    Records should be a list of dictionaries parsed from NASA FIRMS API.
    Expects keys: api_source, satellite, observed_at, latitude, longitude, frp, geom, etc.
    """
    if not records:
        return
        
    stmt = insert(Detection).values(records)
    
    # Idempotent deduplication based on natural key
    stmt = stmt.on_conflict_do_nothing(
        index_elements=[
            'api_source', 'observed_at', 'latitude', 'longitude', 'satellite'
        ]
    )
    
    db.execute(stmt)
    db.commit()

def process_csv_and_ingest(db: Session, csv_path: str, api_source: str, satellite: str):
    """
    Helper to process a CSV file from FIRMS and ingest it.
    """
    df = pd.read_csv(csv_path)
    records = []
    for _, row in df.iterrows():
        # This is a simplified parsing, assuming standard FIRMS CSV columns
        # You'd need to convert date/time strings to datetime objects, map confidence, etc.
        # Note: WKT representation for geom
        records.append({
            "api_source": api_source,
            "satellite": satellite,
            "observed_at": f"{row['acq_date']}T{row['acq_time']}Z", # Simplification
            "latitude": float(row['latitude']),
            "longitude": float(row['longitude']),
            "geom": f"SRID=4326;POINT({row['longitude']} {row['latitude']})",
            "frp": float(row.get('frp', 0.0)),
            "brightness": float(row.get('brightness', 0.0)),
            # Add mapping logic for confidence_label...
            "raw_payload": row.to_dict()
        })
    ingest_firms_batch(db, records)
