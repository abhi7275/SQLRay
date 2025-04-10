# app/sql_parser.py

import sqlglot
from sqlglot.expressions import Expression


def parse_sql(sql: str) -> dict:
    """
    Parses an input SQL string using sqlglot and returns its AST as a dictionary.
    If parsing fails, returns the error in a dict.
    """
    try:
        expression: Expression = sqlglot.parse_one(sql)
        return expression.to_dict()
    except Exception as e:
        return {"error": str(e)}


# Optional: For local testing
if __name__ == "__main__":
    from pprint import pprint

    sample_query = """
    SELECT customer_name, COUNT(*) AS total_orders
    FROM orders
    WHERE order_date >= '2024-01-01'
    GROUP BY customer_name
    ORDER BY total_orders DESC
    LIMIT 10;
    """
    parsed = parse_sql(sample_query)
    pprint(parsed)
