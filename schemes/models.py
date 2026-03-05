from django.db import models

class SchemeCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Scheme Categories"

class GovernmentScheme(models.Model):
    category = models.ForeignKey(SchemeCategory, on_delete=models.CASCADE, related_name='schemes')
    title = models.CharField(max_length=255)
    description = models.TextField()
    eligibility = models.TextField()
    benefits = models.TextField()
    official_link = models.URLField(verbose_name="Official Reference Link")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title