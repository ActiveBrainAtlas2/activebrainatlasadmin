from django.db import models
from django.template.defaultfilters import truncatechars


class UrlModel(models.Model):
    url = models.TextField()
    active = models.BooleanField(default = True)
    created = models.DateTimeField(auto_now_add=True)

    @property
    def short_description(self):
        return truncatechars(self.url, 50)



    class Meta:
        managed = True
        verbose_name = "Url"
        verbose_name_plural = "Urls"
        db_table = 'neuroglancer_urls'
