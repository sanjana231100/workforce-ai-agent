import sqlite3
import random
from faker import Faker

DB_PATH = "workforce.db"
NUM_EMPLOYEES = 200

DEPARTMENTS = [
    "Engineering", "Finance", "Human Resources",
    "Sales", "Marketing", "Operations", "Legal", "IT",
]

ROLES = {
    "Engineering":     ["Junior Developer", "Senior Developer", "Lead Engineer", "DevOps Engineer", "QA Engineer", "Solutions Architect"],
    "Finance":         ["Financial Analyst", "Senior Accountant", "Finance Manager", "Controller", "Budget Analyst"],
    "Human Resources": ["HR Coordinator", "HR Business Partner", "Recruiter", "Compensation Analyst", "HR Manager"],
    "Sales":           ["Sales Representative", "Account Executive", "Sales Manager", "Business Development Rep", "Regional Sales Director"],
    "Marketing":       ["Marketing Coordinator", "Content Strategist", "Digital Marketing Manager", "Brand Manager", "CMO"],
    "Operations":      ["Operations Analyst", "Project Manager", "Supply Chain Manager", "Operations Director", "Process Improvement Specialist"],
    "Legal":           ["Legal Counsel", "Paralegal", "Compliance Officer", "Contract Manager", "General Counsel"],
    "IT":              ["IT Support Specialist", "Systems Administrator", "Network Engineer", "IT Manager", "Cloud Architect"],
}

# Salary bands keyed by role title keyword
SALARY_RANGES = {
    "Junior": (45000, 70000),   "Senior": (95000, 150000),
    "Lead":   (110000, 160000), "Manager": (100000, 145000),
    "Director": (130000, 200000), "Coordinator": (45000, 65000),
    "Analyst": (60000, 90000),  "Specialist": (55000, 85000),
    "Engineer": (75000, 120000), "Architect": (120000, 180000),
    "Counsel": (110000, 160000), "Representative": (50000, 80000),
    "Executive": (80000, 130000), "Paralegal": (50000, 75000),
    "Administrator": (55000, 80000), "Strategist": (65000, 95000),
    "Partner": (90000, 135000), "Officer": (75000, 110000),
    "CMO": (150000, 220000),    "Controller": (110000, 155000),
    "Recruiter": (55000, 85000), "Rep": (50000, 80000),
    "Accountant": (60000, 90000),
}

LOCATIONS = ["San Francisco", "New York", "Austin", "Chicago", "Seattle", "Boston", "Atlanta", "Denver", "Remote"]

PERFORMANCE_RATINGS = ["Exceeds Expectations", "Meets Expectations", "Below Expectations", "Outstanding"]
RATING_WEIGHTS      = [0.25, 0.50, 0.10, 0.15]


def get_salary(role: str) -> float:
    for keyword, (low, high) in SALARY_RANGES.items():
        if keyword in role:
            return round(random.randint(low, high) / 500) * 500
    return round(random.randint(60000, 100000) / 500) * 500


def seed_database():
    fake = Faker()
    Faker.seed(42)
    random.seed(42)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("DROP TABLE IF EXISTS employees")
    cursor.execute("""
        CREATE TABLE employees (
            id                 INTEGER PRIMARY KEY AUTOINCREMENT,
            name               TEXT    NOT NULL,
            department         TEXT    NOT NULL,
            role               TEXT    NOT NULL,
            employment_type    TEXT    NOT NULL,
            salary             REAL    NOT NULL,
            location           TEXT    NOT NULL,
            years_experience   INTEGER NOT NULL,
            hire_date          TEXT    NOT NULL,
            performance_rating TEXT    NOT NULL
        )
    """)

    employees = []
    for _ in range(NUM_EMPLOYEES):
        department = random.choice(DEPARTMENTS)
        role       = random.choice(ROLES[department])

        employee = (
            fake.name(),
            department,
            role,
            # 70% full-time, 30% contractor
            random.choices(["full-time", "contractor"], weights=[0.70, 0.30])[0],
            get_salary(role),
            random.choice(LOCATIONS),
            random.randint(1, 20),
            fake.date_between(start_date="-10y", end_date="today").strftime("%Y-%m-%d"),
            random.choices(PERFORMANCE_RATINGS, weights=RATING_WEIGHTS)[0],
        )
        employees.append(employee)

    # ? placeholders prevent SQL injection
    cursor.executemany("""
        INSERT INTO employees (
            name, department, role, employment_type,
            salary, location, years_experience,
            hire_date, performance_rating
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, employees)

    conn.commit()

    total      = cursor.execute("SELECT COUNT(*) FROM employees").fetchone()[0]
    contractors = cursor.execute("SELECT COUNT(*) FROM employees WHERE employment_type = 'contractor'").fetchone()[0]
    avg_salary  = cursor.execute("SELECT AVG(salary) FROM employees").fetchone()[0]

    print(f"✅ Database created: {DB_PATH}")
    print(f"   Total     : {total}")
    print(f"   Contractors: {contractors}  |  Full-time: {total - contractors}")
    print(f"   Avg salary : ${avg_salary:,.0f}")
    print()

    rows = cursor.execute("""
        SELECT department, COUNT(*) as count
        FROM employees
        GROUP BY department
        ORDER BY count DESC
    """).fetchall()

    for dept, count in rows:
        print(f"   {dept:<25} {count} employees")

    conn.close()


if __name__ == "__main__":
    seed_database()
