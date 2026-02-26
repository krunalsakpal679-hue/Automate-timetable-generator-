from django.contrib import admin

from .models import Teacher, Room, Group, Subject, GroupSubject, TimeSlot, ScheduledPeriod


admin.site.register(Teacher)
admin.site.register(Room)
admin.site.register(Group)
admin.site.register(Subject)
admin.site.register(GroupSubject)
admin.site.register(TimeSlot)
admin.site.register(ScheduledPeriod)
