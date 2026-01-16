from typing_extensions import override
from django.db import models
from django.contrib.auth.models import User


class Note(models.Model):
    @override
    def __str__(self) -> str:
        return self.text

    text = models.CharField(max_length=500)
    submitted_by = models.ForeignKey(User, on_delete=models.CASCADE)
    pub_date = models.DateField("date published")
