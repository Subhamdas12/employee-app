from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Employee",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("education", models.CharField(max_length=50)),
                ("joining_year", models.IntegerField()),
                ("city", models.CharField(max_length=50)),
                ("payment_tier", models.IntegerField()),
                ("age", models.IntegerField()),
                ("gender", models.CharField(max_length=10)),
                ("ever_benched", models.CharField(max_length=5)),
                ("experience_in_current_domain", models.IntegerField()),
                ("leave_or_not", models.IntegerField()),
            ],
            options={
                "db_table": "employees",
                "ordering": ["id"],
            },
        ),
    ]
