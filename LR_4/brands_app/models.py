from django.db import models

class Brand(models.Model):
    name = models.CharField("Название", max_length=200)
    country = models.CharField("Страна", max_length=100)
    founded = models.PositiveIntegerField("Год основания", null=True, blank=True)
    note = models.TextField("Примечание", blank=True)
    color = models.CharField("Цвет", max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('name', 'country', 'founded')
        ordering = ['-created_at']

    def __str__(self):
        y = self.founded or ""
        return f"{self.name} ({self.country}, {y})"
