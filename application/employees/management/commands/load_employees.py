import csv
from pathlib import Path

from django.core.cache import cache
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from employees.cache_service import clear_employee_page_cache
from employees.models import Employee


class Command(BaseCommand):
    help = "Load Employee.csv rows into the employee table."

    def add_arguments(self, parser):
        parser.add_argument(
            "--csv-path",
            default="/app/Employee.csv",
            help="Path to Employee.csv (default: /app/Employee.csv)",
        )

    def handle(self, *args, **options):
        csv_path = Path(options["csv_path"])
        if not csv_path.exists():
            raise CommandError(f"CSV not found: {csv_path}")

        with csv_path.open("r", encoding="utf-8", newline="") as fp:
            reader = csv.DictReader(fp)
            if not reader.fieldnames:
                raise CommandError("CSV has no header row.")

            required = {
                "Education",
                "JoiningYear",
                "City",
                "PaymentTier",
                "Age",
                "Gender",
                "EverBenched",
                "ExperienceInCurrentDomain",
                "LeaveOrNot",
            }
            missing = required.difference(reader.fieldnames)
            if missing:
                raise CommandError(f"CSV missing required columns: {sorted(missing)}")

            employees: list[Employee] = []
            for row in reader:
                employees.append(
                    Employee(
                        education=row["Education"].strip(),
                        joining_year=int(row["JoiningYear"]),
                        city=row["City"].strip(),
                        payment_tier=int(row["PaymentTier"]),
                        age=int(row["Age"]),
                        gender=row["Gender"].strip(),
                        ever_benched=row["EverBenched"].strip(),
                        experience_in_current_domain=int(row["ExperienceInCurrentDomain"]),
                        leave_or_not=int(row["LeaveOrNot"]),
                    )
                )

        with transaction.atomic():
            Employee.objects.all().delete()
            Employee.objects.bulk_create(employees, batch_size=1000)

        clear_employee_page_cache()
        cache.clear()
        self.stdout.write(self.style.SUCCESS(f"Loaded {len(employees)} employees from {csv_path}."))
