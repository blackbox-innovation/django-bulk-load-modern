"""
SQL utility functions for psycopg3 compatibility and improved bulk operations.
"""
from typing import List, Tuple, Any
from django.db.backends.utils import CursorWrapper
from psycopg.sql import SQL, Placeholder, Composed


def execute_values_select(
    cursor: CursorWrapper,
    query: Composed,
    values_data: List[Tuple[Any, ...]],
) -> None:
    """
    Execute a SELECT query with VALUES clause using psycopg3's SQL composition.
    
    This function replaces the manual VALUES clause construction with psycopg3's
    safer SQL composition features, providing better protection against SQL injection
    and cleaner code.
    
    Args:
        cursor: Database cursor
        query: SQL query template with %s placeholder for VALUES data
        values_data: List of tuples containing the values
        
    Example:
        query = SQL("SELECT * FROM table WHERE (col1, col2) IN (VALUES %s)")
        values_data = [(1, 'a'), (2, 'b'), (3, 'c')]
        execute_values_select(cursor, query, values_data)
    """
    if not values_data:
        return
    
    # Build the VALUES clause using SQL composition
    # Create a placeholder for each value in each row
    values_placeholders = SQL(", ").join(
        SQL("({})").format(
            SQL(", ").join(Placeholder() * len(row))
        )
        for row in values_data
    )
    
    # Get the query string - use cursor directly for psycopg3 compatibility
    query_str = query.as_string(cursor)
    
    # The query should have a %s placeholder for VALUES
    if "%s" in query_str:
        # Replace %s with our VALUES placeholders
        # We need to split and reconstruct the query
        parts = query_str.split("%s", 1)
        if len(parts) == 2:
            # Reconstruct the query with proper VALUES clause
            final_query_str = parts[0] + values_placeholders.as_string(cursor) + parts[1]
            
            # Flatten the values data for parameter passing
            flattened_params = [item for row in values_data for item in row]
            
            # Execute the query with the flattened parameters
            cursor.execute(final_query_str, flattened_params)
        else:
            raise ValueError("Query template must contain exactly one %s placeholder")
    else:
        raise ValueError("Query template must contain a %s placeholder for VALUES")


def build_values_clause(values_data: List[Tuple[Any, ...]]) -> Tuple[str, List[Any]]:
    """
    Build a VALUES clause string and flattened parameters list.
    
    This is a fallback function for cases where SQL composition isn't available.
    
    Args:
        values_data: List of tuples containing the values
        
    Returns:
        Tuple of (values_clause_string, flattened_parameters)
    """
    if not values_data:
        return "", []
    
    placeholders = []
    flattened_data = []
    
    for row in values_data:
        placeholders.append("(" + ",".join(["%s"] * len(row)) + ")")
        flattened_data.extend(row)
    
    values_clause = ",".join(placeholders)
    return values_clause, flattened_data