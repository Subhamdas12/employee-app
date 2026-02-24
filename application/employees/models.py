from django.db import models


class Employee(models.Model):
    education = models.CharField(max_length=50)
    joining_year = models.IntegerField()
    city = models.CharField(max_length=50)
    payment_tier = models.IntegerField()
    age = models.IntegerField()
    gender = models.CharField(max_length=10)
    ever_benched = models.CharField(max_length=5)
    experience_in_current_domain = models.IntegerField()
    leave_or_not = models.IntegerField()

    class Meta:
        db_table = "employees"
        ordering = ["id"]

    def __str__(self) -> str:
        return f"{self.education} | {self.city}"
