import pandas as pd
import numpy as np

from src.ingestion import dataset_ingestion
from src.query_engine import TicketQueryEngine
from src.llm import TicketLLM


class TicketDispatcher:

    def __init__(self):

        # Load dataset through ingestion layer
        self.df = dataset_ingestion()

        # Initialize query engine
        self.engine = TicketQueryEngine(self.df)

        # Initialize LLM
        self.llm = TicketLLM()

    # --------------------------------------------------
    # Validate LLM generated query
    # --------------------------------------------------

    def validate_query(self, query):

        allowed_operations = {
            "count_tickets",
            "get_tickets",
            "average_rating",
            "group_and_rank",
            "resolution_rate",
            "detect_resolution_anomalies",
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

        # --------------------------------------------------
        # Operation
        # --------------------------------------------------

        operation = query.get("operation")

        if operation not in allowed_operations:
            raise ValueError(
                f"Unsupported operation: {operation}"
            )

        # --------------------------------------------------
        # Status
        # --------------------------------------------------

        status = query.get("status", "")

        if status and status not in allowed_statuses:
            raise ValueError(
                f"Invalid status: {status}"
            )

        # --------------------------------------------------
        # Priority
        # --------------------------------------------------

        priority = query.get("priority", "")

        if priority and priority not in allowed_priorities:
            raise ValueError(
                f"Invalid priority: {priority}"
            )

        # --------------------------------------------------
        # Category
        # --------------------------------------------------

        category = query.get("category", "")

        if category and category not in allowed_categories:
            raise ValueError(
                f"Invalid category: {category}"
            )

        # --------------------------------------------------
        # Group by
        # --------------------------------------------------

        group_by = query.get("group_by", "")

        if group_by and group_by not in allowed_group_by:
            raise ValueError(
                f"Invalid group_by: {group_by}"
            )

        # --------------------------------------------------
        # Month
        # --------------------------------------------------

        month = query.get("month", 0)

        if not isinstance(month, int):
            raise ValueError(
                "Month must be an integer."
            )

        if month < 0 or month > 12:
            raise ValueError(
                "Month must be between 0 and 12."
            )

        # --------------------------------------------------
        # Resolution time
        # --------------------------------------------------

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

        # Save converted value
        query["max_resolution_time_hrs"] = resolution_time

        return query

    # --------------------------------------------------
    # Format result
    # --------------------------------------------------

    def format_result(self, result):

        # DataFrame
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

        # Series
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

        # NumPy value
        if isinstance(result, np.generic):

            return result.item()

        # Normal value
        return result

    # --------------------------------------------------
    # Execute query
    # --------------------------------------------------

    def execute_query(self, query):

        operation = query["operation"]

        # --------------------------------------------------
        # Count tickets
        # --------------------------------------------------

        if operation == "count_tickets":

            result = self.engine.count_tickets(

                status=query.get("status") or None,

                priority=query.get("priority") or None,

                category=query.get("category") or None
            )

        # --------------------------------------------------
        # Get tickets
        # --------------------------------------------------

        elif operation == "get_tickets":

            resolution_time = query.get(
                "max_resolution_time_hrs",
                0
            )

            if resolution_time == 0:

                resolution_time = None

            result = self.engine.get_tickets(

                priority=query.get(
                    "priority"
                ) or None,

                max_resolution_time_hrs=resolution_time
            )

        # --------------------------------------------------
        # Average rating
        # --------------------------------------------------

        elif operation == "average_rating":

            result = self.engine.average_rating(

                category=query.get(
                    "category"
                ) or None
            )

        # --------------------------------------------------
        # Group and rank
        # --------------------------------------------------

        elif operation == "group_and_rank":

            result = self.engine.group_and_rank(

                group_by=query.get(
                    "group_by"
                ) or "agent_id",

                status=query.get(
                    "status"
                ) or None,

                month=query.get(
                    "month"
                ) or None
            )

        # --------------------------------------------------
        # Resolution rate
        # --------------------------------------------------

        elif operation == "resolution_rate":

            result = self.engine.resolution_rate(

                group_by=query.get(
                    "group_by"
                ) or "category"
            )

        # --------------------------------------------------
        # Resolution anomalies
        # --------------------------------------------------

        elif operation == "detect_resolution_anomalies":

            result = self.engine.detect_resolution_anomalies()

        # --------------------------------------------------
        # Unsupported
        # --------------------------------------------------

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
    # Ask question
    # --------------------------------------------------

    def ask(self, question):

        # 1. LLM understands the question
        query = self.llm.understand_query(
            question
        )

        # 2. Validate structured query
        query = self.validate_query(
            query
        )

        # 3. Execute query
        result = self.execute_query(
            query
        )

        # 4. Return query + result
        return {
            "query": query,
            "result": result
        }