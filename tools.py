import os
import numexpr
from langchain.tools import tool
from langchain_community.tools import DuckDuckGoSearchRun
from utils.db_utils import run_query, get_schema


# ── Tool 1: Web Search ────────────────────────────────────────────────────────

search = DuckDuckGoSearchRun()

@tool
def web_search(query: str) -> str:
    """
    Search the web using DuckDuckGo for current information, news,
    or anything not available in the local workforce database.
    Use this for questions about SAP products, industry trends,
    or any real-world facts that need up-to-date information.
    """
    try:
        return search.run(query)
    except Exception as e:
        return f"Search error: {str(e)}"


# ── Tool 2: SQL Query ─────────────────────────────────────────────────────────

@tool
def sql_query(query: str) -> str:
    """
    Run a SQL SELECT query against the workforce SQLite database.
    Use this for any questions about employees, salaries, departments,
    headcount, contractors, performance ratings, or hire dates.

    The database has one table called 'employees' with these columns:
    id, name, department, role, employment_type, salary, location,
    years_experience, hire_date, performance_rating

    employment_type values are: 'full-time' or 'contractor'
    performance_rating values are: 'Exceeds Expectations', 'Meets Expectations',
    'Below Expectations', 'Outstanding'

    Example queries:
    - SELECT COUNT(*) FROM employees WHERE department = 'Engineering'
    - SELECT AVG(salary) FROM employees WHERE employment_type = 'contractor'
    - SELECT name, salary FROM employees WHERE salary > 80000 ORDER BY salary DESC
    """
    # Block any write operations — agent should only read the database
    forbidden = ["INSERT", "UPDATE", "DELETE", "DROP", "ALTER", "CREATE"]
    if any(word in query.upper() for word in forbidden):
        return "Error: Only SELECT queries are allowed."

    return run_query(query)


@tool
def get_db_schema(dummy: str = "") -> str:
    """
    Returns the workforce database schema showing all table and column names.
    Call this first if you are unsure what columns or tables exist
    before writing a SQL query.
    """
    return get_schema()


# ── Tool 3: Calculator ────────────────────────────────────────────────────────

@tool
def calculator(expression: str) -> str:
    """
    Evaluate a mathematical expression and return the result.
    Use this for any arithmetic: percentages, averages, ratios, totals.

    Examples:
    - "14 / 200 * 100"   → percentage calculation
    - "95000 * 1.1"      → salary with 10% raise
    - "sum([45000, 72000, 98000]) / 3"  → manual average
    """
    try:
        # numexpr safely evaluates math expressions without using eval()
        result = numexpr.evaluate(expression).item()

        # Round to 2 decimal places if it's a float
        if isinstance(result, float):
            return str(round(result, 2))
        return str(result)

    except Exception as e:
        return f"Calculation error: {str(e)}"


# ── Tools list — imported by agent.py ─────────────────────────────────────────

tools = [web_search, sql_query, get_db_schema, calculator]


# ── Quick test ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("Testing sql_query tool...")
    print(sql_query.invoke("SELECT COUNT(*) FROM employees"))
    print()

    print("Testing sql_query — contractors in Engineering above $80k...")
    print(sql_query.invoke(
        "SELECT COUNT(*) FROM employees WHERE department='Engineering' "
        "AND employment_type='contractor' AND salary > 80000"
    ))
    print()

    print("Testing calculator tool...")
    print(calculator.invoke("14 / 200 * 100"))
    print()

    print("Testing get_db_schema tool...")
    print(get_db_schema.invoke(""))
    print()

    print("Testing web_search tool...")
    print(web_search.invoke("SAP workforce management software 2024"))