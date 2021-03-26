from django.db import models
from django.conf import settings
from django.utils.html import escape
import re
import json
import pandas as pd
from django.template.defaultfilters import truncatechars
from django_mysql.models import EnumField

from brain.models import AtlasModel, Animal


COL_LENGTH = 1000
ROW_LENGTH = 1000
Z_LENGTH = 300
ATLAS_X_BOX_SCALE = 10
ATLAS_Y_BOX_SCALE = 10
ATLAS_Z_BOX_SCALE = 20
ATLAS_RAW_SCALE = 10

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
    def escape_url(self):
        return escape(self.url)

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
            description = None
            json_txt = json.loads(self.url)
            layers = json_txt['layers']
            for layer in layers:
                if 'annotations' in layer:
                    name = layer['name']
                    annotation = layer['annotations']
                    d = [row['point'] for row in annotation]
                    df = pd.DataFrame(d, columns=['X', 'Y', 'Section'])
                    df['X'] = df['X'].astype(int)
                    # test to see if the points were inputted at the wrong scale
                    if df['X'].mean() < 2000:
                        df['X'] = df['X'] * 32
                        df['Y'] = df['Y'] * 32
                    df['Y'] = df['Y'].astype(int)
                    df['Section'] = df['Section'].astype(int)
                    df['Layer'] = name
                    structures = [row['description'] for row in annotation if 'description' in row]
                    if len(structures) != len(df):
                        structures = ['' for row in annotation]
                    df['Description'] = structures
                    df = df[['Layer', 'Description', 'X', 'Y', 'Section']]
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
        ordering = ('comments', 'created')
        db_table = 'neuroglancer_urls'

    def __str__(self):
        return u'{}'.format(self.comments)

    @property
    def point_count(self):
        result = "display:none;"
        if self.points is not None:
            df = self.points
            df = df[(df.Layer == 'PM nucleus') | (df.Layer == 'premotor')]
            if len(df) > 0:
                result = "display:inline;"
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
        return f'{self.description} {self.abbreviation}'


class LayerData(models.Model):
    id = models.BigAutoField(primary_key=True)
    url = models.ForeignKey(UrlModel, models.CASCADE, null=True, db_column="url_id",
                               verbose_name="Url")
    layer = models.CharField(max_length=255)
    x = models.FloatField()
    y = models.FloatField()
    section = models.FloatField()
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
    person = models.ForeignKey(settings.AUTH_USER_MODEL, models.CASCADE, db_column="person_id",
                               verbose_name="User", blank=False, null=False)

    x = models.FloatField()
    y = models.FloatField()
    section = models.FloatField()
    input_type = EnumField(choices=['manual','detected','aligned'], blank=False, null=False, verbose_name='Input')

    active = models.BooleanField(default = True, db_column='active')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True, editable=False, null=False, blank=False)

    class Meta:
        managed = False
        db_table = 'center_of_mass'
        verbose_name = 'Center Of Mass'
        verbose_name_plural = 'Center of Mass'
        constraints = [
        models.UniqueConstraint(fields=['prep', 'structure', 'active', 'person', 'input_type'], name='unique COM')
    ]

    def __str__(self):
        return u'{}'.format(self.structure.abbreviation)

