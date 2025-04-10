# sqlray/app/intent_parser.py

import re

def parse_natural_language_intent(question: str) -> dict:
    question = question.lower()
    intent = {
        "aggregations": [],
        "filters": [],
        "group_by": [],
        "limit": None
    }

    # Aggregation detection
    if "average" in question:
        intent["aggregations"].append("avg")
    if "sum" in question or "total" in question:
        intent["aggregations"].append("sum")
    if "count" in question:
        intent["aggregations"].append("count")
    if "max" in question:
        intent["aggregations"].append("max")
    if "min" in question:
        intent["aggregations"].append("min")

    # Group by detection
    group_by_keywords = ["by", "per"]
    for keyword in group_by_keywords:
        match = re.search(rf"{keyword} (\w+)", question)
        if match:
            intent["group_by"].append(match.group(1))

    # Filter detection
    known_filters = ["india", "usa", "europe", "china"]
    for f in known_filters:
        if f in question:
            intent["filters"].append(f)

    # Limit detection
    match = re.search(r"top (\d+)", question)
    if match:
        intent["limit"] = int(match.group(1))

    return intent

# Test
if __name__ == "__main__":
    from pprint import pprint
    q = "What is the total revenue by product in India? Show top 5."
    pprint(parse_natural_language_intent(q))
