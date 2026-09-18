import pandas as pd
import numpy as np

from src.ingestion import dataset_ingestion
from src.query_engine import TicketQueryEngine
from src.llm import TicketLLM


class TicketDispatcher:

    def __init__(self):

        self.df = dataset_ingestion()

        self.engine = TicketQueryEngine(
            self.df
        )

        self.llm = TicketLLM()

    # --------------------------------------------------
    # Query validation
    # --------------------------------------------------

    def validate_query(self, query):

        allowed_operations = {
            "count_tickets",
            "get_tickets",
            "average_rating",
            "average_rating_by_group",
            "group_and_rank",
            "resolution_rate",
            "detect_resolution_anomalies",
            "unresolved_high_priority_tickets",
            "unsupported"
        }

        allowed_statuses = {
            "Open",
            "Resolved",
            "Escalated"
        }

        allowed_priorities = {
            "Low",
            "Medium",
            "High",
            "Critical"
        }

        allowed_categories = {
            "Billing",
            "Technical",
            "General"
        }

        allowed_group_by = {
            "agent_id",
            "category",
            "priority",
            "status"
        }

        allowed_time_periods = {
            "",
            "this_week"
        }

        operation = query.get("operation")

        if operation not in allowed_operations:
            raise ValueError(
                f"Unsupported operation: {operation}"
            )

        status = query.get("status", "")

        if status and status not in allowed_statuses:
            raise ValueError(
                f"Invalid status: {status}"
            )

        priority = query.get("priority", "")

        if priority and priority not in allowed_priorities:
            raise ValueError(
                f"Invalid priority: {priority}"
            )

        category = query.get("category", "")

        if category and category not in allowed_categories:
            raise ValueError(
                f"Invalid category: {category}"
            )

        group_by = query.get("group_by", "")

        if group_by and group_by not in allowed_group_by:
            raise ValueError(
                f"Invalid group_by: {group_by}"
            )

        month = query.get("month", 0)

        if not isinstance(month, int):
            raise ValueError(
                "Month must be an integer."
            )

        if month < 0 or month > 12:
            raise ValueError(
                "Month must be between 0 and 12."
            )

        resolution_time = query.get(
            "max_resolution_time_hrs",
            "0"
        )

        try:
            resolution_time = float(
                resolution_time
            )

        except (TypeError, ValueError):

            raise ValueError(
                "Resolution time must be a number."
            )

        if resolution_time < 0:

            raise ValueError(
                "Resolution time cannot be negative."
            )

        time_period = query.get(
            "time_period",
            ""
        )

        if time_period not in allowed_time_periods:

            raise ValueError(
                f"Invalid time period: {time_period}"
            )

        query["max_resolution_time_hrs"] = (
            resolution_time
        )

        return query

    # --------------------------------------------------
    # Result formatting
    # --------------------------------------------------

    def format_result(self, result):

        if isinstance(result, pd.DataFrame):

            records = result.to_dict(
                orient="records"
            )

            formatted_records = []

            for record in records:

                formatted_record = {}

                for key, value in record.items():

                    if pd.isna(value):

                        value = None

                    elif isinstance(
                        value,
                        pd.Timestamp
                    ):

                        value = value.isoformat()

                    elif isinstance(
                        value,
                        np.generic
                    ):

                        value = value.item()

                    formatted_record[key] = value

                formatted_records.append(
                    formatted_record
                )

            return formatted_records

        if isinstance(result, pd.Series):

            formatted_result = {}

            for key, value in result.items():

                if pd.isna(value):

                    value = None

                elif isinstance(
                    value,
                    np.generic
                ):

                    value = value.item()

                formatted_result[str(key)] = value

            return formatted_result

        if isinstance(result, np.generic):

            return result.item()

        return result

    # --------------------------------------------------
    # Execute query
    # --------------------------------------------------

    def execute_query(self, query):

        operation = query["operation"]

        if operation == "count_tickets":

            result = self.engine.count_tickets(
                status=query.get("status") or None,
                priority=query.get("priority") or None,
                category=query.get("category") or None
            )

        elif operation == "get_tickets":

            resolution_time = query.get(
                "max_resolution_time_hrs",
                0
            )

            if resolution_time == 0:

                resolution_time = None

            result = self.engine.get_tickets(
                priority=query.get("priority") or None,
                max_resolution_time_hrs=resolution_time
            )

        elif operation == "average_rating":

            result = self.engine.average_rating(
                category=query.get("category") or None
            )

        elif operation == "average_rating_by_group":

            result = (
                self.engine
                .average_rating_by_group(
                    group_by=query.get("group_by")
                    or "agent_id"
                )
            )

        elif operation == "group_and_rank":

            result = self.engine.group_and_rank(
                group_by=query.get("group_by")
                or "agent_id",

                status=query.get("status")
                or None,

                month=query.get("month")
                or None
            )

        elif operation == "resolution_rate":

            result = self.engine.resolution_rate(
                group_by=query.get("group_by")
                or "category"
            )

        elif operation == "detect_resolution_anomalies":

            time_period = query.get(
                "time_period",
                ""
            )

            if time_period == "this_week":

                latest_date = self.df[
                    "created_at"
                ].max()

                start_date = (
                    latest_date
                    - pd.Timedelta(
                        days=latest_date.weekday()
                    )
                ).normalize()

                end_date = (
                    start_date
                    + pd.Timedelta(days=6)
                    + pd.Timedelta(
                        hours=23,
                        minutes=59,
                        seconds=59
                    )
                )

                result = (
                    self.engine
                    .detect_resolution_anomalies(
                        start_date=start_date,
                        end_date=end_date
                    )
                )

            else:

                result = (
                    self.engine
                    .detect_resolution_anomalies()
                )

        elif operation == "unresolved_high_priority_tickets":

            hours = query.get(
                "max_resolution_time_hrs",
                24
            )

            if hours == 0:
                hours = 24

            result = (
                self.engine
                .unresolved_high_priority_tickets(
                    hours=hours
                )
            )

        elif operation == "unsupported":

            result = {
                "message":
                    "Sorry, I cannot answer "
                    "that question using the "
                    "available ticket data."
            }

        else:

            raise ValueError(
                f"Unsupported operation: {operation}"
            )

        return self.format_result(result)

    # --------------------------------------------------
    # Ask
    # --------------------------------------------------

    def ask(self, question):

        query = self.llm.understand_query(
            question
        )

        query = self.validate_query(
            query
        )

        result = self.execute_query(
            query
        )

        return {
            "query": query,
            "result": result
        }