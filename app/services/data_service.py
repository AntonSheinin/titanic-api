"""
    Data service class
"""

import os
import logging
from abc import ABC, abstractmethod
from typing import Any

from app.schemas.responses import Passenger
from app.schemas.validators import validate_data_not_empty


logger = logging.getLogger(__name__)

class DataLoader(ABC):
    """
        Abstract base class for data loaders
    """

    @abstractmethod
    def load_data(self) -> tuple[list[dict[str, Any]], list[str]]:
        """
            Load data and return (data, columns)
        """

    @staticmethod
    def _convert_types(row: dict) -> None:
        """
            Convert string values in the row to appropriate Python types
        """

        numeric_fields = {"PassengerId", "Survived", "Pclass", "SibSp", "Parch"}
        float_fields = {"Age", "Fare"}
        null_values = {"", "None", "NULL", "null", "none", "Null", "NONE"}

        def safe_convert(value, type_func, field):
            """
                Helper function
            """

            if value in null_values or value is None:
                return None

            try:
                return type_func(value)

            except (ValueError, TypeError):
                logger.warning(f"Could not convert {field}='{value}' to {type_func.__name__} for passenger {row.get('PassengerId', 'unknown')}")
                return None

        for field in row:
            if field in numeric_fields:
                row[field] = safe_convert(row[field], int, field)

            elif field in float_fields:
                row[field] = safe_convert(row[field], float, field)

            elif str(row[field]).strip() in null_values:
                row[field] = None
        

class CSVDataLoader(DataLoader):
    """
        CSV file data loader
    """
    
    def load_data(self) -> tuple:
        import csv
        
        csv_path = "/data/titanic.csv"
        
        try:
            with open(csv_path) as file:
                reader = csv.DictReader(file)
                columns = reader.fieldnames or []
                data = list(reader)
                
                for row in data:
                    self._convert_types(row)
                
                return data, columns
                
        except FileNotFoundError:
            logger.exception(f"CSV file not found: {csv_path}")
            raise ValueError(f"CSV file not found: {csv_path}")
        
        except Exception as exc:
            logger.exception(f"Error reading CSV file: {exc}")
            raise ValueError(f"Error reading CSV file: {exc}")


class SQLiteDataLoader(DataLoader):
    """
        SQLite database data loader
    """

    def load_data(self) -> tuple:
        import sqlite3

        db_path = "/data/titanic.db"

        try:
            with sqlite3.connect(db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                cursor.execute("SELECT * FROM passengers")
                rows = cursor.fetchall()
                data = [dict(row) for row in rows]

                for row in data:
                    self._convert_types(row)
                
                cursor.execute("PRAGMA table_info(passengers)")
                columns_info = cursor.fetchall()
                columns = [col[1] for col in columns_info]
                
                return data, columns

        except sqlite3.Error as db_err:
            logger.exception(f"SQLite error: {db_err}")
            raise ValueError(f"SQLite error: {db_err}") from db_err

        except Exception as exc:
            logger.exception(f"Unexpected error reading SQLite database: {exc}")
            raise ValueError(f"Unexpected error reading SQLite database: {exc}") from exc


class DataLoaderFactory:
    """
        Factory for creating data loaders
    """
    
    _loaders = {
        "csv": CSVDataLoader,
        "sqlite": SQLiteDataLoader,
    }
    
    @classmethod
    def create_loader(cls, data_source: str) -> DataLoader:
        """
            Create appropriate data loader
        """

        return cls._loaders.get(data_source)()
        

class DataService:
    """
        Main data service
    """
    
    def __init__(self):
        self.data: list[dict[str, any]] = []
        self.columns: list[str] = []
        self._load_data()
    
    def _load_data(self) -> None:
        """
            Load data using appropriate loader
        """

        data_source = os.getenv("DATA_SOURCE", "csv")
        
        loader = DataLoaderFactory.create_loader(data_source)
        self.data, self.columns = loader.load_data()
        
        validate_data_not_empty(self.data)
        logger.info(f"Loaded {len(self.data)} records from {data_source}")
    
    def get_all_passengers(self) -> list:
        """
            Get all passengers
        """

        passengers = []

        for row in self.data:
            try:
                passenger = Passenger(**row)
                passengers.append(passenger)

            except Exception as exc:
                logger.warning(f"Skipping invalid passenger record: {exc}")
                continue
        
        logger.info(f"found {len(passengers)} passengers")
        return passengers
    
    def get_passenger_by_id(self, passenger_id: int) -> Passenger | None:
        """
            Get passenger by ID
        """

        for row in self.data:
            if row.get("PassengerId") == passenger_id:
                try:
                    return Passenger(**row)
                
                except Exception as exc:
                    logger.exception(f"Invalid passenger data for ID {passenger_id}: {exc}")
                    return None
                
        return None
    
    def get_passenger_attributes(self, passenger_id: int, attributes: list) -> dict | None:
        """
            Get specific passenger attributes
        """

        for row in self.data:
            if row.get("PassengerId") == passenger_id:
                return {attr: row.get(attr) for attr in attributes}
            
        return None
    
    def get_fare_data(self) -> list:
        """
            Get all valid fare values
        """

        fare_values = []

        for row in self.data:
            fare = row.get("Fare")
            if fare is not None:
                fare_values.append(fare)

        return fare_values
    
    