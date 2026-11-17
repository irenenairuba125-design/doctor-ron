from django.db import models


class Gender(models.TextChoices):
    MALE = "M", "Male"
    FEMALE = "F", "Female"
    OTHER = "O", "Other"


class PersonMixin(models.Model):
    """Shared helpers for models with first/last names."""

    class Meta:
        abstract = True

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"


def code(prefix, pk):
    return f"{prefix}{pk:05d}" if pk else "-"
