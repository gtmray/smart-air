from src.utils.helpers import format_sql, format_json


def test_format_sql_cleans_markdown():
    test_cases = [
        ("```sql\nSELECT * FROM flights;\n```", "SELECT * FROM flights;"),
        ("```SELECT * FROM flights;```", "SELECT * FROM flights;"),
        ("SELECT * FROM flights;", "SELECT * FROM flights;"),
    ]

    for input_sql, expected in test_cases:
        assert format_sql(input_sql).strip() == expected


def test_format_json_parses_correctly():
    test_cases = [
        ('```json\n{"valid": true}\n```', {"valid": True}),
        ('{"valid": false}', {"valid": False}),
        ('  \n\n{"count": 5}  ', {"count": 5}),
    ]

    for input_json, expected in test_cases:
        assert format_json(input_json) == expected
