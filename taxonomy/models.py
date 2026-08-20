from django.db import models


class TaxonomyCategory(models.Model):
    name = models.CharField(max_length=255)

    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="children"
    )

    full_path = models.TextField(blank=True)

    category_id = models.CharField(
        max_length=255,
        unique=True
    )

    def __str__(self):
        return self.full_path or self.name