import pandas as pd


class TicketQueryEngine:

    def __init__(self, df: pd.DataFrame):
        self.df = df

    # --------------------------------------------------
    # 1. Count tickets
    # --------------------------------------------------

    def count_tickets(
        self,
        status=None,
        priority=None,
        category=None
    ):

        data = self.df

        if status:
            data = data[
                data["status"].str.lower() == status.lower()
            ]

        if priority:
            data = data[
                data["priority"].str.lower() == priority.lower()
            ]

        if category:
            data = data[
                data["category"].str.lower() == category.lower()
            ]

        return len(data)

    # --------------------------------------------------
    # 2. Get tickets
    # --------------------------------------------------

    def get_tickets(
        self,
        priority=None,
        max_resolution_time_hrs=None
    ):

        data = self.df

        if priority:
            data = data[
                data["priority"].str.lower() == priority.lower()
            ]

        if max_resolution_time_hrs is not None:
            data = data[
                data["resolution_time_hrs"].isna()
                |
                (
                    data["resolution_time_hrs"]
                    > max_resolution_time_hrs
                )
            ]

        return data

    # --------------------------------------------------
    # 3. Average customer rating
    # --------------------------------------------------

    def average_rating(
        self,
        category=None
    ):

        data = self.df

        if category:
            data = data[
                data["category"].str.lower() == category.lower()
            ]

        return data["customer_rating"].mean()

    # --------------------------------------------------
    # 4. Average rating by group
    # --------------------------------------------------

    def average_rating_by_group(
        self,
        group_by="agent_id"
    ):

        data = self.df[
            self.df["customer_rating"].notna()
        ]

        result = (
            data.groupby(group_by)["customer_rating"]
            .mean()
            .sort_values(ascending=True)
        )

        return result

    # --------------------------------------------------
    # 5. Group and rank
    # --------------------------------------------------

    def group_and_rank(
        self,
        group_by="agent_id",
        status=None,
        month=None
    ):

        data = self.df

        if status:
            data = data[
                data["status"].str.lower() == status.lower()
            ]

        if month is not None:
            data = data[
                (data["created_at"].dt.year == 2024)
                &
                (
                    data["created_at"].dt.month == month
                )
            ]

        result = data.groupby(group_by).size()

        return result.sort_values(
            ascending=False
        )

    # --------------------------------------------------
    # 6. Resolution rate
    # --------------------------------------------------

    def resolution_rate(
        self,
        group_by="category"
    ):

        data = self.df

        total = data.groupby(group_by).size()

        resolved = data[
            data["status"].str.lower() == "resolved"
        ].groupby(group_by).size()

        result = (
            resolved / total * 100
        ).fillna(0)

        return result.sort_values(
            ascending=False
        )

    # --------------------------------------------------
    # 7. Resolution-time anomalies
    # --------------------------------------------------

    def detect_resolution_anomalies(
        self,
        start_date=None,
        end_date=None
    ):

        data = self.df[
            self.df["resolution_time_hrs"].notna()
        ]

        if start_date is not None:
            data = data[
                data["created_at"] >= start_date
            ]

        if end_date is not None:
            data = data[
                data["created_at"] <= end_date
            ]

        if data.empty:
            return data

        q1 = data[
            "resolution_time_hrs"
        ].quantile(0.25)

        q3 = data[
            "resolution_time_hrs"
        ].quantile(0.75)

        iqr = q3 - q1

        lower_bound = (
            q1 - (1.5 * iqr)
        )

        upper_bound = (
            q3 + (1.5 * iqr)
        )

        anomalies = data[
            (
                data["resolution_time_hrs"]
                < lower_bound
            )
            |
            (
                data["resolution_time_hrs"]
                > upper_bound
            )
        ]

        return anomalies

    # --------------------------------------------------
    # 8. Unresolved high-priority tickets
    # --------------------------------------------------

    def unresolved_high_priority_tickets(
        self,
        hours=24
    ):

        data = self.df.copy()

        current_time = data[
            "created_at"
        ].max()

        age_hours = (
            current_time
            - data["created_at"]
        ).dt.total_seconds() / 3600

        result = data[
            data["priority"].isin(
                ["High", "Critical"]
            )
            &
            data["resolution_time_hrs"].isna()
            &
            (age_hours > hours)
        ]

        return result