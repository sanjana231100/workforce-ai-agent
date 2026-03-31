import sqlite3
import os

# Build absolute path to workforce.db regardless of where the script is run from
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DB_PATH  = os.path.join(BASE_DIR, "workforce.db")


def run_query(sql: str) -> str:
    if not os.path.exists(DB_PATH):
        return "Error: Database not found. Run 'python seed_db.py' first."

    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(sql)
        rows = cursor.fetchall()
        conn.close()

        if not rows:
            return "Query returned no results."

        columns = [desc[0] for desc in cursor.description]

        # Single value result (e.g. COUNT, AVG) — return it directly
        if len(rows) == 1 and len(columns) == 1:
            val = rows[0][0]
            if isinstance(val, float):
                return str(round(val, 2))
            return str(val)

        result_lines = [
            " | ".join(f"{col}: {val}" for col, val in zip(columns, row))
            for row in rows
        ]
        return "\n".join(result_lines)

    except sqlite3.Error as e:
        # Return error as string so the agent can self-correct on next loop
        return f"SQL Error: {str(e)}"


def get_schema() -> str:
    if not os.path.exists(DB_PATH):
        return "Database not found. Run python seed_db.py first."

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='employees'")
        row = cursor.fetchone()
        conn.close()
        return f"Table: employees\n{row[0]}" if row else "Table 'employees' not found."
    except sqlite3.Error as e:
        return f"Error reading schema: {str(e)}"


if __name__ == "__main__":
    print(get_schema())
    print()
    print(run_query("SELECT COUNT(*) FROM employees"))
    print()
    print(run_query("SELECT department, AVG(salary) as avg_sal FROM employees GROUP BY department ORDER BY avg_sal DESC"))
