import os
from django.db import models
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


class Task(models.Model):
    lookup = models.ForeignKey('ProgressLookup', models.DO_NOTHING)
    prep = models.ForeignKey(Animal, models.CASCADE)
    completed = models.BooleanField()
    resources = models.ManyToManyField('Resource', blank=True)
    active = models.IntegerField(default = 1, editable = False)
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = True
        db_table = 'task'
        unique_together = (('prep', 'lookup'),)
        verbose_name = 'Task'
        verbose_name_plural = 'Tasks'

    def __str__(self):
        return u'{} {}'.format(self.prep.prep_id, self.lookup.description)

class TaskView(models.Model):
    prep_id = models.CharField(primary_key=True, max_length=20)
    percent_complete = models.DecimalField(max_digits=6, decimal_places=2)
    complete = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'task_view'
        verbose_name = 'Pipeline Progress'
        verbose_name_plural = 'Pipeline Progress'

    def __str__(self):
        return u'{}'.format(self.prep_id)


class ProgressLookup(models.Model):
    ordinal = models.IntegerField(unique=True)
    description = models.TextField()
    category = models.CharField(max_length=200)
    script = models.CharField(max_length=200, blank=True, null=True)
    active = models.IntegerField(default = 1, editable = False)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = True
        db_table = 'progress_lookup'
        verbose_name = 'Pipeline lookup'
        verbose_name_plural = 'Pipeline lookups'

    def __str__(self):
        return u'{}'.format(self.description)



class WorkQueue(models.Model):
    prep = models.ForeignKey(Animal, models.CASCADE)
    ordinal = models.IntegerField(unique=True)
    description = models.TextField()
    completed = models.BooleanField(default = False)
    active = models.IntegerField(default = 1, editable = False)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = True
        db_table = 'work_queue'
        verbose_name = 'Work Queue'
        verbose_name_plural = 'Work Queues'

    def __str__(self):
        return u'{}'.format(self.description)



