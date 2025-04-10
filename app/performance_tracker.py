import duckdb
import time

def run_query_with_metrics(sql_query: str, database_path: str = ":memory:") -> dict:
    """
    Executes SQL query in DuckDB and returns performance metrics.
    
    Returns:
        dict containing execution time, row count, and output preview
    """
    con = duckdb.connect(database=database_path)
    try:
        start_time = time.perf_counter()
        result = con.execute(sql_query).fetchall()
        end_time = time.perf_counter()

        execution_time = round((end_time - start_time) * 1000, 2)  # ms
        row_count = len(result)

        return {
            "execution_time_ms": execution_time,
            "row_count": row_count,
            "sample_output": result[:5]  # Show top 5 rows as preview
        }
    except Exception as e:
        return {
            "error": str(e),
            "execution_time_ms": None,
            "row_count": None,
            "sample_output": []
        }
    finally:
        con.close()
