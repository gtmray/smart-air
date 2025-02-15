import json


def format_sql(data: str) -> str:
    """Format SQL string by removing markdown code block syntax and
       extra whitespace.

    Args:
        data (str): The SQL string potentially containing markdown
                    formatting.

    Returns:
        str:  The cleaned SQL string without markdown code block syntax
              and extraneous whitespace.

    """
    return data.strip("```sql").strip()


def format_json(data: str) -> dict:
    """Format JSON string by removing markdown code block syntax.

    Args:
        data (str): The JSON string potentially containing markdown

    Returns:
        dict: The JSON string without markdown code block syntax.
    """
    return json.loads(data.strip("```json").strip())
