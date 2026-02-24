import psycopg2
import csv
import os


def create_auth_tables(cur):
    # Tracks applied migrations if you are managing schema manually.
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS django_migrations (
            id BIGSERIAL PRIMARY KEY,
            app VARCHAR(255) NOT NULL,
            name VARCHAR(255) NOT NULL,
            applied TIMESTAMPTZ NOT NULL
        );
        """
    )

    # Needed by Django auth permissions model.
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS django_content_type (
            id BIGSERIAL PRIMARY KEY,
            app_label VARCHAR(100) NOT NULL,
            model VARCHAR(100) NOT NULL,
            CONSTRAINT django_content_type_app_label_model_uniq UNIQUE (app_label, model)
        );
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS auth_permission (
            id BIGSERIAL PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            content_type_id BIGINT NOT NULL REFERENCES django_content_type(id) ON DELETE CASCADE,
            codename VARCHAR(100) NOT NULL,
            CONSTRAINT auth_permission_content_type_id_codename_uniq UNIQUE (content_type_id, codename)
        );
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS auth_group (
            id BIGSERIAL PRIMARY KEY,
            name VARCHAR(150) NOT NULL UNIQUE
        );
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS auth_group_permissions (
            id BIGSERIAL PRIMARY KEY,
            group_id BIGINT NOT NULL REFERENCES auth_group(id) ON DELETE CASCADE,
            permission_id BIGINT NOT NULL REFERENCES auth_permission(id) ON DELETE CASCADE,
            CONSTRAINT auth_group_permissions_group_id_permission_id_uniq UNIQUE (group_id, permission_id)
        );
        """
    )

    # Default Django user model table.
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS auth_user (
            id BIGSERIAL PRIMARY KEY,
            password VARCHAR(128) NOT NULL,
            last_login TIMESTAMPTZ NULL,
            is_superuser BOOLEAN NOT NULL,
            username VARCHAR(150) NOT NULL UNIQUE,
            first_name VARCHAR(150) NOT NULL,
            last_name VARCHAR(150) NOT NULL,
            email VARCHAR(254) NOT NULL,
            is_staff BOOLEAN NOT NULL,
            is_active BOOLEAN NOT NULL,
            date_joined TIMESTAMPTZ NOT NULL
        );
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS auth_user_groups (
            id BIGSERIAL PRIMARY KEY,
            user_id BIGINT NOT NULL REFERENCES auth_user(id) ON DELETE CASCADE,
            group_id BIGINT NOT NULL REFERENCES auth_group(id) ON DELETE CASCADE,
            CONSTRAINT auth_user_groups_user_id_group_id_uniq UNIQUE (user_id, group_id)
        );
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS auth_user_user_permissions (
            id BIGSERIAL PRIMARY KEY,
            user_id BIGINT NOT NULL REFERENCES auth_user(id) ON DELETE CASCADE,
            permission_id BIGINT NOT NULL REFERENCES auth_permission(id) ON DELETE CASCADE,
            CONSTRAINT auth_user_user_permissions_user_id_permission_id_uniq UNIQUE (user_id, permission_id)
        );
        """
    )

    # Required by Django session middleware/auth session storage.
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS django_session (
            session_key VARCHAR(40) PRIMARY KEY,
            session_data TEXT NOT NULL,
            expire_date TIMESTAMPTZ NOT NULL
        );
        """
    )
    cur.execute(
        """
        CREATE INDEX IF NOT EXISTS django_session_expire_date_idx
        ON django_session (expire_date);
        """
    )


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
    create_auth_tables(cur)

    # Create table matching CSV structure
    cur.execute("""
        CREATE TABLE IF NOT EXISTS employees (
            id SERIAL PRIMARY KEY,
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

load_employee_csv_to_postgres(
    csv_file=os.getenv("EMPLOYEE_CSV_FILE", "Employee.csv"),
    host=os.getenv("POSTGRES_HOST", "localhost"),
    port=int(os.getenv("POSTGRES_PORT", "5432")),
    database=os.getenv("POSTGRES_DB", "mydb"),
    user=os.getenv("POSTGRES_USER", "postgres"),
    password=os.getenv("POSTGRES_PASSWORD", "postgres"),
    force_reload=os.getenv("FORCE_RELOAD_EMPLOYEES", "false").lower() == "true",
)
