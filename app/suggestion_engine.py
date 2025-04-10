import re

def suggest_from_query_structure(sql_query: str) -> list:
    """
    Generates basic suggestions by analyzing the SQL query string.
    """
    suggestions = []
    query = sql_query.lower()

    if "where" not in query:
        suggestions.append("Consider adding a WHERE clause to reduce scanned rows.")

    if "limit" not in query:
        suggestions.append("Add a LIMIT clause to speed up dashboard queries.")

    if "join" in query and "on" not in query:
        suggestions.append("Check JOIN conditions — missing ON clause detected.")

    return suggestions


def suggest_from_explain_plan(explain_output: str) -> list:
    """
    Parses DuckDB EXPLAIN output and suggests improvements.
    """
    suggestions = []

    if "seq scan" in explain_output.lower() or "table scan" in explain_output.lower():
        suggestions.append("Avoid full table scans — use WHERE clause or indexes.")

    if "nested loop join" in explain_output.lower():
        suggestions.append("Replace nested loop join with hash or merge join if possible.")

    if "no index" in explain_output.lower():
        suggestions.append("Consider creating indexes on frequently filtered columns.")

    return suggestions


def generate_suggestions(sql_query: str, explain_output: str) -> list:
    """
    Combines structural and execution plan suggestions.
    """
    structure_suggestions = suggest_from_query_structure(sql_query)
    plan_suggestions = suggest_from_explain_plan(explain_output)

    return list(set(structure_suggestions + plan_suggestions))  # Deduplicated
