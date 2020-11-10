import math
from typing import List

from django.db import models
from django.conf import settings
import re
import json
import pandas as pd
from django.template.defaultfilters import truncatechars
from django_mysql.models import EnumField

from brain.models import AtlasModel, Animal


class UrlModel(models.Model):
    id = models.BigAutoField(primary_key=True)
    url = models.TextField()
    person = models.ForeignKey(settings.AUTH_USER_MODEL, models.CASCADE, null=True, db_column="person_id",
                               verbose_name="User")
    public = models.BooleanField(default = True, db_column='active')
    vetted = models.BooleanField(default = False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True, editable=False, null=False, blank=False)
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
    def point_frame(self):
        df = None
        if self.url is not None:
            point_data = self.find_values('annotations', self.url)
            if len(point_data) > 0:
                d = [row['point'] for row in point_data[0]]
                df = pd.DataFrame(d, columns=['X', 'Y', 'Section'])
                df = df.round(decimals=0)
        return df

    @property
    def points(self):
        result = None
        dfs = []
        if self.url is not None:
            json_txt = json.loads(self.url)
            layers = json_txt['layers']
            for l in layers:
                if 'annotations' in l:
                    name = l['name']
                    annotation = l['annotations']
                    d = [row['point'] for row in annotation]
                    df = pd.DataFrame(d, columns=['X', 'Y', 'Section'])
                    df['X'] = df['X'].astype(int)
                    df['Y'] = df['Y'].astype(int)
                    df['Section'] = df['Section'].astype(int)
                    df['Layer'] = name
                    df = df[['Layer', 'X', 'Y', 'Section']]
                    dfs.append(df)
            if len(dfs) == 0:
                result = None
            elif len(dfs) == 1:
                result = dfs[0]
            else:
                result = pd.concat(dfs)

        return result

    class Meta:
        managed = False
        verbose_name = "Url"
        verbose_name_plural = "Urls"
        db_table = 'neuroglancer_urls'

    def __str__(self):
        return u'{}'.format(self.comments)

    @property
    def point_count(self):
        result = False
        if self.url is not None:
            point_data = self.find_values('annotations', self.url)
            if len(point_data) > 0:
                result = True
        return result


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

class Points(UrlModel):

    class Meta:
        managed = False
        proxy = True
        verbose_name = 'Points'
        verbose_name_plural = 'Points'

class Structure(AtlasModel):
    id = models.BigAutoField(primary_key=True)
    abbreviation = models.CharField(max_length=200)
    description = models.TextField(max_length=2001, blank=False, null=False)
    color = models.PositiveIntegerField()
    hexadecimal = models.CharField(max_length=7)

    class Meta:
        managed = False
        db_table = 'structure'
        verbose_name = 'Structure'
        verbose_name_plural = 'Structures'

    def __str__(self):
        return u'{}'.format(self.description)


class LayerData(models.Model):
    id = models.BigAutoField(primary_key=True)
    url = models.ForeignKey(UrlModel, models.CASCADE, null=True, db_column="url_id",
                               verbose_name="Url")
    layer = models.CharField(max_length=255)
    x = models.FloatField()
    y = models.FloatField()
    section = models.IntegerField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True, editable=False, null=False, blank=False)

    class Meta:
        managed = False
        db_table = 'layer_data'
        verbose_name = 'Layer Data'
        verbose_name_plural = 'Layer Data'

    def __str__(self):
        return u'{}'.format(self.layer)

class CenterOfMass(models.Model):
    """
    I set both structure and prep to be nullable. This is just to make it easier
    for the serializers. The database will ensure they are not null.
    """
    id = models.BigAutoField(primary_key=True)
    structure = models.ForeignKey(Structure, models.CASCADE, null=True, db_column="structure_id",
                               verbose_name="Structure")
    prep = models.ForeignKey(Animal, models.CASCADE, null=True, db_column="prep_id", verbose_name="Animal")

    x = models.FloatField()
    y = models.FloatField()
    section = models.FloatField()

    active = models.BooleanField(default = True, db_column='active')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True, editable=False, null=False, blank=False)

    class Meta:
        managed = False
        db_table = 'center_of_mass'
        verbose_name = 'Center Of Mass'
        verbose_name_plural = 'Center of Mass'

    def __str__(self):
        return u'{}'.format(self.structure.abbreviation)

