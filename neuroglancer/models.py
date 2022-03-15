from django.db import models
from django.conf import settings
from django.utils.html import escape
import re
import json
import pandas as pd
from enum import Enum
from django.template.defaultfilters import truncatechars
from brain.models import AtlasModel, Animal

LAUREN_ID = 16
MANUAL = 1
CORRECTED = 2
POINT_ID = 52
LINE_ID = 53
POLYGON_ID = 54

class AnnotationChoice(str, Enum):
    POINT = 'point'
    LINE = 'line'

    @classmethod
    def choices(cls):
        return tuple((x.value, x.name) for x in cls)

    def __str__(self):
        return self.value

class UrlModel(models.Model):
    id = models.BigAutoField(primary_key=True)
    url = models.JSONField(verbose_name="Neuroglancer State")
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, models.CASCADE, null=False,
                              blank=False, db_column="person_id",
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
        match = re.search('data/(.+?)/neuroglancer_data', str(self.url))
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
            json_txt = self.url
            layers = json_txt['layers']
            for layer in layers:
                if 'annotations' in layer:
                    name = layer['name']
                    annotation = layer['annotations']
                    d = [row['point'] for row in annotation if 'point' in row and 'pointA' not in row]
                    df = pd.DataFrame(d, columns=['X', 'Y', 'Section'])
                    df['Section'] = df['Section'].astype(int)
                    df['Layer'] = name
                    structures = [row['description'] for row in annotation if 'description' in row]
                    if len(structures) != len(df):
                        structures = ['' for row in annotation if 'point' in row and 'pointA' not in row]
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

    @property
    def layers(self):
        layer_list = []
        if self.url is not None:
            json_txt = self.url
            layers = json_txt['layers']
            for layer in layers:
                if 'annotations' in layer:
                    layer_name = layer['name']
                    layer_list.append(layer_name)

        return layer_list

    class Meta:
        managed = False
        verbose_name = "Neuroglancer state"
        verbose_name_plural = "Neuroglancer states"
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

class BrainRegion(AtlasModel):
    id = models.BigAutoField(primary_key=True)
    abbreviation = models.CharField(max_length=200)
    description = models.TextField(max_length=2001, blank=False, null=False)
    color = models.PositiveIntegerField()
    hexadecimal = models.CharField(max_length=7)

    class Meta:
        managed = False
        db_table = 'structure'
        verbose_name = 'Brain region'
        verbose_name_plural = 'Brain regions'

    def __str__(self):
        return f'{self.description} {self.abbreviation}'

class InputType(models.Model):
    id = models.BigAutoField(primary_key=True)
    input_type = models.CharField(max_length=50, blank=False, null=False, verbose_name='Input')
    description = models.TextField(max_length=255, blank=False, null=False)
    active = models.BooleanField(default = True, db_column='active')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True, editable=False, null=False, blank=False)

    class Meta:
        managed = False
        db_table = 'com_type'
        verbose_name = 'Input Type'
        verbose_name_plural = 'Input Types'

    def __str__(self):
        return u'{}'.format(self.input_type)

# new models for th eannotation data

class AnnotationAbstract(models.Model):
    id = models.BigAutoField(primary_key=True)
    animal = models.ForeignKey(Animal, models.CASCADE, null=True, db_column="prep_id", verbose_name="Animal")
    brain_region = models.ForeignKey(BrainRegion, models.CASCADE, null=True, db_column="FK_structure_id",
                               verbose_name="Brain region")
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, models.CASCADE, db_column="FK_owner_id",
                               verbose_name="Owner", blank=False, null=False)
    input_type = models.ForeignKey(InputType, models.CASCADE, db_column="FK_input_id",
                               verbose_name="Input", blank=False, null=False)
    label = models.CharField(max_length=255)
    segment_id = models.CharField(max_length=40, blank=True, null=True, 
                                  db_column="segment_id", verbose_name="Polygon ID")
    x = models.FloatField(verbose_name="X (um)")
    y = models.FloatField(verbose_name="Y (um)")
    z = models.FloatField(verbose_name="Z (um)")
    ordering = models.IntegerField(verbose_name="polygon point ordering")
    class Meta:
        abstract = True

class ArchiveSet(models.Model):
    '''
    ANTICIPATED OPERATION: 
    1) USER SAVES ANNOTATION POINTS IN NEUROGLANCER 
    2) NEW ENTRY IN archive_set TABLE (PARENT 'archive_id' - 0 IF FIRST; UPDATE USER; TIMESTAMP ) 
    3) ALL CURRENT POINTS FOR USER ARE MOVED TO annotations_points_archive 
    4) NEW POINTS ARE ADDED TO annotations_points *    
    - CONSIDERATIONS: *      
        A) IF LATENCY -> DB MODIFICATIONS MAY BE QUEUED AND MADE VIA CRON JOB (DURING OFF-PEAK)
        B) annotations_points_archive, archive_sets WILL NOT BE STORED ON LIVE DB
    #2 - INSERT entry into archive_sets table   
    This will store the versioning  is the 
    'SELECT INTO' with concurrent/subsequent entry into #2 (archive_sets table).  
    After INSERT, we should receive the id of the insert (id field).  
    This will be the unique key to identify an archive set.
    '''
    id = models.BigAutoField(primary_key=True)
    animal = models.ForeignKey(Animal, models.CASCADE, null=True, db_column="prep_id", verbose_name="Animal")
    input_type = models.ForeignKey(InputType, models.CASCADE, db_column="FK_input_id",
                               verbose_name="Input", blank=False, null=False)
    label = models.CharField(max_length=255)
    created = models.DateTimeField(auto_now_add=True)
    parent =  models.IntegerField(db_column='FK_parent')
    updatedby = models.ForeignKey(settings.AUTH_USER_MODEL, models.CASCADE, 
                               verbose_name="Updated by", blank=False, null=False, 
                               db_column='FK_update_user_id')
    class Meta:
        managed = False
        db_table = 'archive_set'
        verbose_name = 'Archive set'
        verbose_name_plural = 'Archive sets'

class AnnotationPoints(AnnotationAbstract):
    active = models.BooleanField(default = True, db_column='active')

    class Meta:
        managed = False
        db_table = 'annotations_points'
        verbose_name = 'Annotation Point'
        verbose_name_plural = 'Annotation Points'
        constraints = [
                models.UniqueConstraint(fields=['animal', 'label', 'input_type'], name='unique annotations')
            ]        

    def __str__(self):
        return u'{} {}'.format(self.animal, self.label)


class AnnotationPointArchive(AnnotationAbstract):
    archive = models.ForeignKey(ArchiveSet, models.CASCADE, 
                               verbose_name="Archive Set", blank=False, null=False, 
                               db_column='FK_archive_set_id')

    class Meta:
        managed = False
        db_table = 'annotations_point_archive'
        verbose_name = 'Annotation Point Archive'
        verbose_name_plural = 'Annotation Points Archive'
        constraints = [
                models.UniqueConstraint(fields=['animal', 'label', 'input_type', 'archive'], name='unique backup')
            ]        
    def __str__(self):
        return u'{} {}'.format(self.animal, self.label)



class AlignmentScore(models.Model):
    class Meta:
        managed = False
        db_table = 'annotations_points'
        verbose_name = 'Alignment Score'
        verbose_name_plural = 'Alignment Scores'

    def __str__(self):
        return u'{}'.format(self.prep_id)

class AtlasToBeth(models.Model):
    class Meta:
        managed = False
        db_table = 'annotations_points'
        verbose_name = 'Aligned Atlas to Beth'
        verbose_name_plural = 'Aligned Atlas to Beth'

    def __str__(self):
        return u'{}'.format(self.prep_id)

class AnnotationStatus(models.Model):
    class Meta:
        managed = False
        db_table = 'annotations_points'
        verbose_name = 'Annotation Status'
        verbose_name_plural = 'Annotation Status'

    def __str__(self):
        return u'{}'.format(self.prep_id)