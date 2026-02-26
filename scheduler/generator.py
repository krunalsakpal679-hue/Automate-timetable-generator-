from django.db import transaction
from .models import TimeSlot, GroupSubject, ScheduledPeriod, Room, TimetableSettings
import random


def generate_timetable(days=5, periods_per_day=None):
    """
    Generate timetable dynamically for all groups, based on user-defined settings.
    Ensures no conflicts between groups, teachers, and rooms.
    """

    # --- Step 1: Get timetable settings ---
    settings = TimetableSettings.objects.first()
    if settings:
        periods_per_day = settings.periods_per_day
    if not periods_per_day:
        periods_per_day = 6  # fallback

    # --- Step 2: Ensure timeslots exist for all days/periods ---
    timeslots = []
    for day in range(days):
        for p in range(1, periods_per_day + 1):
            ts, _ = TimeSlot.objects.get_or_create(day=day, period=p)
            timeslots.append(ts)

    if not timeslots:
        return False, "No timeslots available."

    # --- Step 3: Gather lessons from group–subject mappings ---
    lessons = []
    mappings = GroupSubject.objects.select_related('group', 'subject', 'subject__teacher').all()
    for gs in mappings:
        teacher = gs.subject.teacher
        if not teacher:
            return False, f"Subject '{gs.subject.name}' has no teacher assigned (group {gs.group.name})."
        for _ in range(gs.hours_per_week):
            lessons.append({
                'group': gs.group,
                'subject': gs.subject,
                'teacher': teacher,
            })

    if not lessons:
        return False, "No group-subject mappings found. Add subjects and groups first."

    # --- Step 4: Prepare resources ---
    rooms = list(Room.objects.all())
    if not rooms:
        return False, "No rooms found. Please add at least one room."

    random.shuffle(lessons)
    random.shuffle(timeslots)
    random.shuffle(rooms)

    # --- Step 5: Conflict trackers ---
    slot_group = {ts.id: set() for ts in timeslots}
    slot_teacher = {ts.id: set() for ts in timeslots}
    slot_room = {ts.id: set() for ts in timeslots}

    assignments = []

    # --- Step 6: Assign lessons to timeslots ---
    for lesson in lessons:
        assigned = False
        random.shuffle(timeslots)
        for ts in timeslots:
            sid = ts.id
            random.shuffle(rooms)
            for room in rooms:
                if (
                    lesson['group'].id not in slot_group[sid]
                    and lesson['teacher'].id not in slot_teacher[sid]
                    and room.id not in slot_room[sid]
                ):
                    assignments.append({
                        'timeslot': ts,
                        'group': lesson['group'],
                        'subject': lesson['subject'],
                        'teacher': lesson['teacher'],
                        'room': room,
                    })
                    slot_group[sid].add(lesson['group'].id)
                    slot_teacher[sid].add(lesson['teacher'].id)
                    slot_room[sid].add(room.id)
                    assigned = True
                    break
            if assigned:
                break

    # --- Step 7: Save to database atomically ---
    with transaction.atomic():
        ScheduledPeriod.objects.all().delete()
        ScheduledPeriod.objects.bulk_create([ScheduledPeriod(**a) for a in assignments])

    # --- Step 8: Return result ---
    if assignments:
        return True, f"✅ Timetable generated successfully with {len(assignments)} scheduled periods ({periods_per_day} per day)."
    else:
        return False, "⚠️ Could not generate timetable — try adding more rooms, teachers, or reducing weekly hours."
