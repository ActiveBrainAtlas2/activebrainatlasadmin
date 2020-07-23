import os
from django.db import models
from brain.models import AtlasModel
from brain.models import Animal




class Roles(models.Model):
    name = models.CharField('Name', max_length=30, blank=True)
    def __str__(self):
        return u'{}'.format(self.name)

    class Meta:
        managed = True
        db_table = 'task_roles'
        verbose_name = 'Role'
        verbose_name_plural = 'Roles'


class Resource(models.Model):
    # Fields
    first_name = models.CharField(('first name'), max_length=30, blank=True)
    last_name = models.CharField(('last name'), max_length=30, blank=True)
    role = models.ForeignKey('Roles', null=True, blank=True, on_delete=models.DO_NOTHING)

    class Meta:
        managed = True
        db_table = 'resource'
    def __str__(self):
        return u'{} {}'.format(self.first_name, self.last_name)


class Task(AtlasModel):
    lookup = models.ForeignKey('ProgressLookup', models.DO_NOTHING)
    prep = models.ForeignKey(Animal, models.CASCADE)
    completed = models.BooleanField()
    resources = models.ManyToManyField('Resource', blank=True)
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        managed = True
        db_table = 'task'
        unique_together = (('prep', 'lookup'),)
        verbose_name = 'Task'
        verbose_name_plural = 'Tasks'

    def __str__(self):
        return u'{} {}'.format(self.prep.prep_id, self.lookup.description)

class Log(AtlasModel):
    prep = models.ForeignKey(Animal, models.CASCADE)
    logger = models.CharField(max_length=100, blank=False, verbose_name='Log Source')
    level = models.CharField(max_length=25)
    msg = models.CharField(max_length=255, blank=False, verbose_name='Message')

    class Meta:
        managed = False
        db_table = 'logs'
        verbose_name = 'Log'
        verbose_name_plural = 'Logs'

    def __str__(self):
        return u'{} {}'.format(self.prep.prep_id, self.msg)

class Journal(AtlasModel):
    prep = models.ForeignKey(Animal, models.DO_NOTHING, null=True)
    entry = models.TextField(blank=False, verbose_name='Journal Entry')
    completed = models.BooleanField(default = False)

    class Meta:
        managed = False
        db_table = 'journals'
        verbose_name = 'Journal'
        verbose_name_plural = 'Journals'

    def __str__(self):
        return u'{} {}'.format(self.prep.prep_id, self.entry[0:50])

class TaskView(models.Model):
    prep_id = models.CharField(primary_key=True, max_length=20)
    percent_complete = models.DecimalField(max_digits=6, decimal_places=2)
    complete = models.IntegerField()
    created = models.CharField(max_length=20)

    class Meta:
        managed = False
        db_table = 'task_view'
        verbose_name = 'Pipeline Progress'
        verbose_name_plural = 'Pipeline Progress'

    def __str__(self):
        return u'{}'.format(self.prep_id)


class ProgressLookup(AtlasModel):
    description = models.TextField()
    script = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'progress_lookup'
        verbose_name = 'Pipeline lookup'
        verbose_name_plural = 'Pipeline lookups'

    def __str__(self):
        return u'{}'.format(self.description)



class WorkQueue(AtlasModel):
    prep = models.ForeignKey(Animal, models.CASCADE)
    description = models.TextField()
    completed = models.BooleanField(default = False)

    class Meta:
        managed = True
        db_table = 'work_queue'
        verbose_name = 'Work Queue'
        verbose_name_plural = 'Work Queues'

    def __str__(self):
        return u'{}'.format(self.description)



