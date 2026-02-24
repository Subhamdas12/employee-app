import psycopg2
import csv
import os
from urllib.parse import urlparse


def load_employee_csv_to_postgres(
    csv_file="Employee.csv",
    host="localhost",
    port=5432,
    database="mydb",
    user="postgres",
    password="postgres",
    force_reload=False
):
    conn = psycopg2.connect(
        host=host,
        port=port,
        database=database,
        user=user,
        password=password
    )

    cur = conn.cursor()

    # Create table matching CSV structure (Django auth tables are handled by migrate)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS employees (
            id BIGSERIAL PRIMARY KEY,
            education VARCHAR(50),
            joining_year INT,
            city VARCHAR(50),
            payment_tier INT,
            age INT,
            gender VARCHAR(10),
            ever_benched VARCHAR(5),
            experience_in_current_domain INT,
            leave_or_not INT
        );
    """)

    conn.commit()

    cur.execute("SELECT EXISTS (SELECT 1 FROM employees LIMIT 1);")
    has_existing_data = bool(cur.fetchone()[0])
    if has_existing_data and not force_reload:
        cur.close()
        conn.close()
        print("Employees table already has data. Skipping CSV load.")
        return

    if force_reload:
        cur.execute("TRUNCATE TABLE employees RESTART IDENTITY;")
        conn.commit()

    # Use COPY for fastest bulk insert
    with open(csv_file, "r") as f:
        next(f)  # skip header
        cur.copy_expert("""
            COPY employees(
                education,
                joining_year,
                city,
                payment_tier,
                age,
                gender,
                ever_benched,
                experience_in_current_domain,
                leave_or_not
            )
            FROM STDIN WITH CSV
        """, f)

    conn.commit()
    cur.close()
    conn.close()

    print("CSV data loaded successfully into employees table.")

database_url = os.getenv("DATABASE_URL")
if database_url:
    parsed_db = urlparse(database_url)
    db_host = parsed_db.hostname or "localhost"
    db_port = int(parsed_db.port or 5432)
    db_name = (parsed_db.path or "/mydb").lstrip("/")
    db_user = parsed_db.username or "postgres"
    db_password = parsed_db.password or "postgres"
else:
    db_host = os.getenv("POSTGRES_HOST", "localhost")
    db_port = int(os.getenv("POSTGRES_PORT", "5432"))
    db_name = os.getenv("POSTGRES_DB", "mydb")
    db_user = os.getenv("POSTGRES_USER", "postgres")
    db_password = os.getenv("POSTGRES_PASSWORD", "postgres")

load_employee_csv_to_postgres(
    csv_file=os.getenv("EMPLOYEE_CSV_FILE", "Employee.csv"),
    host=db_host,
    port=db_port,
    database=db_name,
    user=db_user,
    password=db_password,
    force_reload=os.getenv("FORCE_RELOAD_EMPLOYEES", "false").lower() == "true",
)
