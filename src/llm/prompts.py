DB_ENGINE = "SQLite"
SCHEMA = """
Database Schema:
- airlines (IATA_CODE, AIRLINE)
- airports (IATA_CODE, AIRPORT, CITY, STATE, COUNTRY, LATITUDE, LONGITUDE)
- flights (
    YEAR, MONTH, DAY, DAY_OF_WEEK, AIRLINE, FLIGHT_NUMBER, TAIL_NUMBER,
    ORIGIN_AIRPORT, DESTINATION_AIRPORT, SCHEDULED_DEPARTURE, DEPARTURE_TIME,
    DEPARTURE_DELAY, TAXI_OUT, WHEELS_OFF, SCHEDULED_TIME, ELAPSED_TIME,
    AIR_TIME, DISTANCE, WHEELS_ON, TAXI_IN, SCHEDULED_ARRIVAL, ARRIVAL_TIME,
    ARRIVAL_DELAY, DIVERTED, CANCELLED, CANCELLATION_REASON,
    AIR_SYSTEM_DELAY, SECURITY_DELAY, AIRLINE_DELAY, LATE_AIRCRAFT_DELAY,
    WEATHER_DELAY
)

Table Relationships:
- airlines.IATA_CODE = flights.AIRLINE
- airports.IATA_CODE = flights.ORIGIN_AIRPORT
- airports.IATA_CODE = flights.DESTINATION_AIRPORT
"""

SQL_GEN_SYSTEM_PROMPT = """\
You are an expert SQL query generator. Your task is to produce correct, optimized, and syntactically valid SQL queries based on the provided schema and DB engine specifications. Always follow the instructions exactly and output only the final SQL query without any commentary.
If the user is asking something out of the scope of this information (not related to queries regarding airlines, flights or airports), return None.
"""

SQL_GEN_HUMAN_PROMPT = f"""
Database Schema:
{SCHEMA}

Task: Generate {DB_ENGINE}-compatible SQL to answer: "<question>{{question}}</question>"

Requirements:
1. Schema Compliance:
   - Use only existing columns/tables
   - Qualify ambiguous columns
   - Use explicit ANSI JOINs with ON clauses
   - Apply table aliases (e.g., FROM employees AS e)

2. Robustness:
   - Handle NULLs with COALESCE/ISNULL where appropriate
   - Use type-safe comparisons
   - Consider potential duplicate records
   - Implement proper GROUP BY logic

3. Optimization:
   - Select only necessary columns
   - Use EXISTS() instead of IN() when applicable
   - Apply sargable WHERE clauses
   - Use CTEs for complex logic

4. Formatting:
   - Use standard SQL formatting
   - Apply meaningful aliases (e.g., SUM(sales) AS total_sales)
   - Include schema prefixes when needed

Example JOIN pattern:
FROM orders AS o
INNER JOIN customers AS c 
  ON o.customer_id = c.id

Additional Instruction:
If the user's question is not related to queries regarding airlines, flights, or airports, return None.

Return either the final SQL code using {DB_ENGINE} syntax or None.
"""


SQL_VAL_SYSTEM_PROMPT = """\
You are a seasoned SQL syntax validator. Your role is to assess whether an input string is a syntactically valid SQL query. Focus solely on syntax: disregard semantic issues or execution context.
"""

SQL_VAL_HUMAN_PROMPT = """\
Examine the SQL query below and determine its syntactic validity based on standard SQL rules. Do not provide any extra commentary—output only the final result in JSON format.

Input SQL Query:
<input>{query}</input>

Return a JSON object in the following format:
{{"is_valid": true}}  or  {{"is_valid": false}}
"""

NATURAL_SYSTEM_PROMPT = """\
You are an expert data interpreter and natural language response generator. Your role is to translate SQL query results into clear, concise key insights that summarize the known results. Prioritize clarity, brevity, and accuracy. Follow all instructions precisely and avoid adding any extra commentary.
"""

NATURAL_HUMAN_PROMPT = """\
Below, you will find a user query along with the corresponding SQL result. Your task is to generate a natural language response that summarizes the key insights from the SQL result, as the results are already known. Ensure that your answer is clear, concise, and addresses the question in a single, self-contained paragraph without including any additional commentary or extraneous context.

Inputs:
- User Query: <question> {question} </question>
- SQL Result: "<result> {result} </result>

Please provide your final summary as a single, short, self-contained paragraph.
"""
