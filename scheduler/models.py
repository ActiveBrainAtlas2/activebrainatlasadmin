from django.core.exceptions import ValidationError
from django.db import models
from django.conf import settings
from datetime import datetime, timedelta
# Create your models here.




class SchedulerModel(models.Model):
    active = models.BooleanField(default = True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True



class Location(SchedulerModel):
    room = models.CharField(max_length=25, blank=False, null=False)
    description = models.TextField(blank=False, null=False)
    people_allowed = models.IntegerField(blank=False, null=False, default=1)
    primary_people = models.ManyToManyField(settings.AUTH_USER_MODEL)

    class Meta:
        managed = False
        db_table = 'location'
        verbose_name = 'Location'
        verbose_name_plural = 'Locations'

    def __str__(self):
        return "{} {}".format(self.room, self.description)

def isScheduleInTimePeriod(startTime, endTime, scheduleTime):
    if startTime < endTime:
        return scheduleTime >= startTime and scheduleTime <= endTime
    else:  # Over midnight
        return scheduleTime >= startTime or scheduleTime <= endTime


class Schedule(SchedulerModel):
    start_time = models.DateTimeField(blank=False, null=False)
    end_time = models.DateTimeField(blank=False, null=False)
    person = models.ForeignKey(settings.AUTH_USER_MODEL, models.CASCADE, null=False)
    location = models.ForeignKey(Location, models.CASCADE, null=False, blank=False)

    class Meta:
        managed = False
        db_table = 'schedule'
        verbose_name = 'Schedule'
        verbose_name_plural = 'Schedules'

    def __str__(self):
        return "{} to {} in room {}".format(self.start_time.strftime('%b/%d/%Y %H:%M'), self.end_time.strftime('%b/%d/%Y %H:%M'), self.location.room)

    def has_location(self):
        return self.location is not None

    def clean(self):
        if self.start_time == None:
            raise ValidationError("Start time is required.")
        if self.end_time == None:
            raise ValidationError("End time is required.")
        if not self.has_location:
            raise ValidationError("Room is required.")
        duration = (self.end_time - self.start_time).total_seconds()
        if duration < 0:
            raise ValidationError("End time must be after start time.")


        occupied = []
        date_from = datetime.now() - timedelta(days=1)
        date_to = datetime.now() + timedelta(days=1)

        schedules = Schedule.objects.filter(start_time__lte=date_to).filter(start_time__gte=date_from)\
            .order_by('start_time')
        for schedule in schedules:
            start = isScheduleInTimePeriod(schedule.start_time, schedule.end_time, self.start_time)
            end = isScheduleInTimePeriod(schedule.start_time, schedule.end_time, self.end_time)
            if (start or end) and self.location.room == schedule.location.room:
                occupied.append(schedule)

        if len(occupied) >= self.location.people_allowed:
            schedule = occupied[0]
            raise ValidationError("That room is occupied. {} is in room: {} from {} to {}".format(
                schedule.person.username,
                schedule.location.room,
                schedule.start_time.strftime('%b/%d/%Y %H:%M'), schedule.end_time.strftime('%b/%d/%Y %H:%M')))
