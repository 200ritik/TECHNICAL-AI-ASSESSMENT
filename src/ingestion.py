import pandas as pd


ticket_file = "https://raw.githubusercontent.com/200ritik/TECHNICAL-AI-ASSESSMENT/6202be2324ecfd73a1d2d529bc54ee15fd2bf190/data/support_tickets.csv"


def dataset_ingestion():

    df = pd.read_csv(ticket_file)

    df["created_at"] = pd.to_datetime(
        df["created_at"]
    )

    return df