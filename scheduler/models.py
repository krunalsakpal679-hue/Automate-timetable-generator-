from django.db import models

# --- Constants for days ---
DAYS = [
    (0, 'Monday'),
    (1, 'Tuesday'),
    (2, 'Wednesday'),
    (3, 'Thursday'),
    (4, 'Friday'),
]


# --- Teacher Model ---
class Teacher(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


# --- Room Model ---
class Room(models.Model):
    name = models.CharField(max_length=50, unique=True)
    capacity = models.PositiveIntegerField(default=30)

    def __str__(self):
        return f"{self.name} ({self.capacity})"


# --- Group (Class) Model ---
class Group(models.Model):
    name = models.CharField(max_length=100, unique=True)
    size = models.PositiveIntegerField(default=30)

    def __str__(self):
        return self.name


# --- Subject Model ---
class Subject(models.Model):
    name = models.CharField(max_length=100, unique=True)
    teacher = models.ForeignKey(
        'Teacher',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='subjects'
    )

    def __str__(self):
        return self.name


# --- GroupSubject Mapping ---
class GroupSubject(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    hours_per_week = models.PositiveIntegerField(default=3)

    class Meta:
        unique_together = ("group", "subject")

    def __str__(self):
        return f"{self.group} - {self.subject} ({self.hours_per_week}h)"


# --- TimeSlot (Day + Period) ---
class TimeSlot(models.Model):
    day = models.IntegerField(choices=DAYS)
    period = models.PositiveIntegerField()  # 1..6 or 1..7

    class Meta:
        unique_together = ("day", "period")
        ordering = ("day", "period")

    def __str__(self):
        return f"{dict(DAYS).get(self.day, 'Unknown')} - Period {self.period}"


# --- ScheduledPeriod (Final Timetable Entry) ---
class ScheduledPeriod(models.Model):
    timeslot = models.ForeignKey(TimeSlot, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        unique_together = ("timeslot", "group")

    def __str__(self):
        return f"{self.timeslot} — {self.group}: {self.subject} ({self.teacher}) @ {self.room or 'No Room'}"


# --- Timetable Settings (User-customizable) ---
class TimetableSettings(models.Model):
    periods_per_day = models.PositiveIntegerField(default=6)

    # Custom period times: e.g. {"P1": ["09:30", "10:30"], "P2": ["10:30", "11:30"], ...}
    period_times = models.JSONField(default=dict, blank=True)

    # Optional break times
    lunch_start = models.TimeField(blank=True, null=True)
    lunch_end = models.TimeField(blank=True, null=True)
    short_break_start = models.TimeField(blank=True, null=True)
    short_break_end = models.TimeField(blank=True, null=True)

    def __str__(self):
        return f"Custom Timetable ({self.periods_per_day} periods)"
 