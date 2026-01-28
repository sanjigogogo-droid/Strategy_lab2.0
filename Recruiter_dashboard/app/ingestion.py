# app/ingestion.py
import pandas as pd
from pathlib import Path

SOURCE_DIR = Path("data/sources")


def ingest_source(file_path: Path, source_name: str):
    try:
        df = pd.read_csv(file_path)

        if df.empty or len(df.columns) == 0:
            print(f"⚠️ Skipping empty file: {file_path.name}")
            return None

        df["source_system"] = source_name
        return df

    except pd.errors.EmptyDataError:
        print(f"⚠️ EmptyDataError in: {file_path.name}")
        return None

    except Exception as e:
        print(f"❌ Failed to read {file_path.name}: {e}")
        return None


def ingest_all_sources():
    frames = []

    for path in SOURCE_DIR.glob("*.csv"):
        df = ingest_source(path, path.stem)
        if df is not None:
            frames.append(df)

    if not frames:
        raise RuntimeError("❌ No valid CSV data found in data/sources/")

    return pd.concat(frames, ignore_index=True)
