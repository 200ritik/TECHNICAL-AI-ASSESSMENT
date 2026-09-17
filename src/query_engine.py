import pandas as pd

class TicketQueryEngine:
    def __init__(self, df: pd.DataFrame):
        self.df = df

    # function 1--------------------------

    def count_tickets(self, status = None, priority=None, category = None):
        data = self.df
        
        if status:
            data = data[data["status"].str.lower() == status.lower()]
        if priority:
            data = data[data['priority'].str.lower() == priority.lower()]
            
        if category:
            data = data[data['category'].str.lower() == category.lower()]
                               
        return len(data)
    
    # function 2-----------------------------
    
    def get_tickets(self, priority=None, max_resolution_time_hrs=None):
        data = self.df

        if priority:
            data = data[
                data["priority"].str.lower() == priority.lower()
            ]

        if max_resolution_time_hrs is not None:
            data = data[
                data["resolution_time_hrs"].isna()
                | (data["resolution_time_hrs"] > max_resolution_time_hrs)
            ]

        return data
    
    
    # function 3------------------       
    def average_rating(self, category= None):
        data = self.df    
        
        if category:
            data = data[data["category"].str.lower() == category.lower()]
        
        result = data["customer_rating"].mean()
        
        return result    
        
    #function 4---------------   
    def group_and_rank(self, group_by="agent_id", status=None, month=None):
        data = self.df

        # Filter by status
        if status:
            data = data[
                data["status"].str.lower() == status.lower()
            ]

        # Filter by month in 2024
        if month is not None:
            data = data[
                (data["created_at"].dt.year == 2024) &
                (data["created_at"].dt.month == month)
            ]

        # Group and count
        result = data.groupby(group_by).size()

        # Highest count first
        result = result.sort_values(ascending=False)

        return result
        
        
    # function 5------------------------    
    def resolution_rate(self, group_by="category"):
        data = self.df

        total = data.groupby(group_by).size()

        resolved = data[
            data["status"].str.lower() == "resolved"
        ].groupby(group_by).size()

        result = (resolved / total * 100).fillna(0)

        return result.sort_values(ascending=False)    
            
     
    # function 6--------------------------       
    def detect_resolution_anomalies(self, start_date=None, end_date=None):
        data = self.df

        # Remove unresolved tickets
        data = data[
            data["resolution_time_hrs"].notna()
        ]

        # Filter by date range
        if start_date is not None:
            data = data[
                data["created_at"] >= start_date
            ]

        if end_date is not None:
            data = data[
                data["created_at"] <= end_date
            ]

        # Calculate IQR
        Q1 = data["resolution_time_hrs"].quantile(0.25)
        Q3 = data["resolution_time_hrs"].quantile(0.75)

        IQR = Q3 - Q1

        lower_bound = Q1 - (1.5 * IQR)
        upper_bound = Q3 + (1.5 * IQR)

        # Find anomalies
        anomalies = data[
            (data["resolution_time_hrs"] < lower_bound) |
            (data["resolution_time_hrs"] > upper_bound)
        ]

        return anomalies 
            
            
                
                