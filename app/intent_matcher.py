# sqlray/app/intent_matcher.py

def compare_intent_and_query(intent: dict, query: dict) -> dict:
    matches = {
        "aggregation": False,
        "group_by": False,
        "filter": False,
        "limit": False
    }
    suggestions = []

    # Safely extract and lowercase only strings
    intent_aggs = set(s.lower() for s in intent.get("aggregations", []) if isinstance(s, str))
    intent_group = set(s.lower() for s in intent.get("group_by", []) if isinstance(s, str))
    intent_filters = set(s.lower() for s in intent.get("filters", []) if isinstance(s, str))

    # Query aggregations
    query_aggs = set()
    for agg in query.get("aggregations", []):
        if isinstance(agg, dict):
            query_aggs.update(k.lower() for k in agg.keys() if isinstance(k, str))

    matches["aggregation"] = bool(intent_aggs & query_aggs)
    if not matches["aggregation"] and intent_aggs:
        suggestions.append(f"Consider using aggregation(s): {', '.join(intent_aggs)}")

    # Group by match
    query_group = set(s.lower() for s in query.get("group_by", []) if isinstance(s, str))
    matches["group_by"] = intent_group.issubset(query_group)
    if not matches["group_by"] and intent_group:
        suggestions.append(f"Consider grouping by: {', '.join(intent_group)}")

    # Filter match
    query_filters_str = str(query.get("filters", [])).lower()
    matches["filter"] = all(f in query_filters_str for f in intent_filters)
    if not matches["filter"] and intent_filters:
        suggestions.append(f"Consider filtering on: {', '.join(intent_filters)}")

    # Limit match
    intent_limit = intent.get("limit")
    query_limit = query.get("limit")
    matches["limit"] = query_limit is not None
    if not matches["limit"] and intent_limit:
        suggestions.append(f"Consider adding LIMIT {intent_limit} to restrict output")

    return {
        "matches": matches,
        "suggestions": suggestions
    }


# Test block
if __name__ == "__main__":
    from pprint import pprint

    intent = {
        "filters": ["India"],
        "aggregations": ["SUM"],
        "group_by": ["product"],
        "limit": 5
    }

    query = {
        "select": ["product"],
        "aggregations": [{"sum": "revenue"}],
        "filters": [{"=": ["region", "India"]}],
        "group_by": ["product"],
        "order_by": [{"sum": "revenue", "sort": "desc"}],
        "limit": None
    }

    pprint(compare_intent_and_query(intent, query))
