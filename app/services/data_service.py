"""
    Data service class
"""

import os
import logging
from typing import List, Dict, Any
from abc import ABC, abstractmethod

from app.models.passenger import Passenger
from app.utils.validators import validate_passenger_id, validate_attributes, validate_data_not_empty


logger = logging.getLogger(__name__)

class DataLoader(ABC):
    """
        Abstract base class for data loaders
    """
    
    @abstractmethod
    def load_data(self) -> tuple[List[Dict[str, Any]], List[str]]:
        """
            Load data and return (data, columns)
        """
        

class CSVDataLoader(DataLoader):
    """
        CSV file data loader
    """
    
    def load_data(self) -> tuple:
        import csv
        
        csv_path = os.getenv("DATA_PATH", "/data/titanic.csv")
        
        try:
            with open(csv_path, 'r') as file:
                reader = csv.DictReader(file)
                columns = reader.fieldnames or []
                data = list(reader)
                
                # Convert types for each row
                for row in data:
                    self._convert_types(row)
                
                return data, columns
                
        except FileNotFoundError:
            logger.exception(f"CSV file not found: {csv_path}")
            raise ValueError(f"CSV file not found: {csv_path}")
        
        except Exception as exc:
            logger.exception(f"Error reading CSV file: {exc}")
            raise ValueError(f"Error reading CSV file: {exc}")
    
    def _convert_types(self, row: dict) -> None:
        """
            Convert string values to appropriate types
        """

        numeric_fields = ["PassengerId", "Survived", "Pclass", "SibSp", "Parch"]
        float_fields = ["Age", "Fare"]
        
        for field in numeric_fields:
            if field in row and row[field]:
                try:
                    row[field] = int(row[field])

                except (ValueError, TypeError):
                    pass
        
        for field in float_fields:
            if field in row and row[field]:
                try:
                    row[field] = float(row[field])

                except (ValueError, TypeError):
                    pass
        
        for key, value in row.items():
            if value == "" or value == "None":
                row[key] = None


class SQLiteDataLoader(DataLoader):
    """
        SQLite database data loader
    """
    
    def load_data(self) -> tuple:
        import sqlite3
        
        db_path = os.getenv("DATABASE_URL", "sqlite:///data/titanic.db").replace("sqlite://", "")
        
        try:
            with sqlite3.connect(db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                cursor.execute("SELECT * FROM passengers")
                rows = cursor.fetchall()
                data = [dict(row) for row in rows]
                
                cursor.execute("PRAGMA table_info(passengers)")
                columns_info = cursor.fetchall()
                columns = [col[1] for col in columns_info]
                
                return data, columns
                
        except Exception as exc:
            logger.exception(f"Error reading SQLite database: {exc}")
            raise ValueError(f"Error reading SQLite database: {exc}")


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

        loader_class = cls._loaders.get(data_source)

        if not loader_class:
            logger.error(f"Unsupported data source: {data_source}")
            raise ValueError(f"Unsupported data source: {data_source}")
        
        return loader_class()
    
    @classmethod
    def register_loader(cls, data_source: str, loader_class: type) -> None:
        """
            Register new data loader type
        """

        cls._loaders[data_source] = loader_class


class DataService:
    """
        Main data service
    """
    
    def __init__(self):
        self.data: List[Dict[str, Any]] = []
        self.columns: List[str] = []
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

        return passengers
    
    def get_passenger_by_id(self, passenger_id: int) -> Passenger | None:
        """
            Get passenger by ID
        """

        validate_passenger_id(passenger_id)
        
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

        validate_passenger_id(passenger_id)
        validate_attributes(attributes, self.columns)
        
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
            if fare is not None and isinstance(fare, (int, float)) and fare >= 0:
                fare_values.append(float(fare))

        return fare_values
    
    def get_columns(self) -> list:
        """
            Get available column names
        """

        return self.columns.copy()