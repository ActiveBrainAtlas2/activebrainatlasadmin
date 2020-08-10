from django.db import models
from django.conf import settings
import re
from django.template.defaultfilters import truncatechars


class UrlModel(models.Model):
    url = models.TextField()
    person = models.ForeignKey(settings.AUTH_USER_MODEL, models.CASCADE, null=False, db_column="person_id",
                               verbose_name="User")
    public = models.BooleanField(default = True, db_column='active')
    vetted = models.BooleanField(default = False)
    created = models.DateTimeField(auto_now_add=True)
    user_date = models.CharField(max_length=25)
    comments = models.CharField(max_length=255)

    @property
    def short_description(self):
        return truncatechars(self.url, 50)

    @property
    def animal(self):
        """
        find the animal within the url between data/ and /neuroglancer_data:
        data/MD589/neuroglancer_data/C1
        return: the first match if found, otherwise NA
        """
        animal = "NA"
        match = re.search('data/(.+?)/neuroglancer_data', self.url)
        if match is not None and match.group(1) is not None:
            animal = match.group(1)
        return animal

    class Meta:
        managed = True
        verbose_name = "Url"
        verbose_name_plural = "Urls"
        db_table = 'neuroglancer_urls'
