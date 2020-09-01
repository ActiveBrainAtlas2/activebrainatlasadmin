from django.db import models
from django.conf import settings
import re
import json
import pandas as pd
from django.template.defaultfilters import truncatechars


class UrlModel(models.Model):
    url = models.TextField()
    person = models.ForeignKey(settings.AUTH_USER_MODEL, models.CASCADE, null=True, db_column="person_id",
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

    @property
    def points(self):
        df = None
        if self.url is not None:
            point_data = self.find_values('annotations', self.url)
            if len(point_data) > 0:
                d = [row['point'] for row in point_data[0]]
                df = pd.DataFrame(d, columns=['X', 'Y', 'Section'])
                df = df.round(decimals=0)
        return df

    class Meta:
        managed = True
        verbose_name = "Url"
        verbose_name_plural = "Urls"
        db_table = 'neuroglancer_urls'

    def __str__(self):
        return u'{}'.format(self.comments)

    def find_values(self, id, json_repr):
        results = []

        def _decode_dict(a_dict):
            try:
                results.append(a_dict[id])
            except KeyError:
                pass
            return a_dict

        json.loads(json_repr, object_hook=_decode_dict)  # Return value ignored.
        return results

