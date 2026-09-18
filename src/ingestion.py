import pandas as pd
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent

ticket_file = BASE_DIR / "data" / "support_tickets.csv"


def dataset_ingestion():

    df = pd.read_csv(ticket_file)

    df["created_at"] = pd.to_datetime(
        df["created_at"]
    )

    return df