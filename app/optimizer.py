import duckdb
import re

def extract_table_names(query):
    """
    Extracts table names used after FROM keyword in SQL.
    """
    return re.findall(r'FROM\s+([a-zA-Z_][a-zA-Z0-9_]*)', query, re.IGNORECASE)


def extract_columns_from_query(query):
    """
    Extracts column names from SELECT and ORDER BY clauses.
    """
    column_names = set()

    # Extract columns from SELECT
    select_match = re.search(r"SELECT\s+(.*?)\s+FROM", query, re.IGNORECASE | re.DOTALL)
    if select_match:
        select_part = select_match.group(1)
        if select_part.strip() != "*":
            for col in select_part.split(","):
                alias_match = re.search(r"AS\s+(\w+)", col, re.IGNORECASE)
                col_clean = alias_match.group(1) if alias_match else re.sub(r"[^\w]", "", col.strip().split()[-1])
                if col_clean:
                    column_names.add(col_clean)

    # Extract columns from ORDER BY
    order_match = re.search(r"ORDER BY\s+(.*?)($|LIMIT|OFFSET|;)", query, re.IGNORECASE | re.DOTALL)
    if order_match:
        order_part = order_match.group(1)
        for col in order_part.split(","):
            col_clean = re.sub(r"[^\w]", "", col.strip().split()[0])
            if col_clean:
                column_names.add(col_clean)

    # Fallback if nothing extracted
    if not column_names:
        column_names = {"id", "value"}

    return column_names


def run_explain(sql_query: str, database_path: str = ":memory:") -> str:
    """
    Runs EXPLAIN on the SQL query. If referenced tables don't exist,
    it creates mock tables with guessed columns to avoid failure.
    """
    con = duckdb.connect(database=database_path)
    try:
        tables = extract_table_names(sql_query)

        for table in tables:
            try:
                con.execute(f"SELECT 1 FROM {table} LIMIT 1")
            except duckdb.CatalogException:
                # Create mock table if not exists
                column_names = extract_columns_from_query(sql_query)
                col_defs = ", ".join(f"{col} TEXT" for col in column_names)
                con.execute(f"CREATE TABLE {table} ({col_defs})")

        explain_result = con.execute(f"EXPLAIN {sql_query}").fetchall()
        return "\n".join(row[0] for row in explain_result)
    finally:
        con.close()


def analyze_explain_plan(plan: str) -> dict:
    """
    Parses EXPLAIN plan to detect performance issues.

    Returns:
        A dictionary with scan type, join type, and potential issues.
    """
    analysis = {
        "full_table_scan": False,
        "joins": [],
        "issues": [],
        "raw_plan": plan
    }

    # Full table scan detection
    if re.search(r"seq_scan|Scan on", plan, re.IGNORECASE):
        analysis["full_table_scan"] = True
        analysis["issues"].append("full_table_scan")

    # JOIN detection
    joins = re.findall(r"(Nested Loop Join|Hash Join|Merge Join)", plan, re.IGNORECASE)
    analysis["joins"] = list(set(joins))

    if any("Nested Loop Join" in join for join in joins):
        analysis["issues"].append("nested_loop_join")

    # Placeholder for index (DuckDB doesn't use index hints clearly)
    if "no index" in plan.lower():
        analysis["issues"].append("no_index")

    return analysis
