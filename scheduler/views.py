from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponse
from datetime import datetime, timedelta, time
from django.db import IntegrityError
from reportlab.lib.pagesizes import landscape, A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

from .forms import (
    TeacherForm, SubjectForm, GroupForm, GroupSubjectForm,
    RoomForm, TimetableSettingsForm
)
from .models import Teacher, Subject, Group, GroupSubject, Room, ScheduledPeriod, TimeSlot, TimetableSettings
from .generator import generate_timetable

DAY_NAMES = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]


# ---------------- ENSURE TIMESLOTS ----------------
def ensure_timeslots(days=5, periods=6):
    for d in range(days):
        for p in range(1, periods + 1):
            TimeSlot.objects.get_or_create(day=d, period=p)


# ---------------- HOME VIEW ----------------
def home(request):
    teacher_form = TeacherForm(request.POST or None, prefix="teacher")
    subject_form = SubjectForm(request.POST or None, prefix="subject")
    group_form = GroupForm(request.POST or None, prefix="group")
    mapping_form = GroupSubjectForm(request.POST or None, prefix="mapping")
    room_form = RoomForm(request.POST or None, prefix="room")

    settings_instance, _ = TimetableSettings.objects.get_or_create(id=1)
    settings_form = TimetableSettingsForm(request.POST or None, instance=settings_instance, prefix="settings")

    if request.method == "POST":
        saved = False
        new_teacher = None
        new_subject = None
        new_group = None
        new_room = None

        # Save teacher
        if teacher_form.is_valid():
            new_teacher = teacher_form.save()
            saved = True
            messages.success(request, f"Teacher '{new_teacher.name}' saved.")

        # Save subject
        if subject_form.is_valid():
            new_subject = subject_form.save(commit=False)
            if new_teacher:
                new_subject.teacher = new_teacher
            new_subject.save()
            saved = True
            messages.success(request, f"Subject '{new_subject.name}' saved.")

        # Save group
        if group_form.is_valid():
            new_group = group_form.save()
            saved = True
            messages.success(request, f"Group '{new_group.name}' saved.")

        # Save room
        if room_form.is_valid():
            new_room = room_form.save()
            saved = True
            messages.success(request, f"Room '{new_room.name}' saved.")

        # Save settings
        if settings_form.is_valid():
            settings_form.save()
            saved = True

        # Automatically link teacher ↔ subject if both are new
        if new_teacher and new_subject:
            try:
                new_subject.teacher = new_teacher
                new_subject.save()
                messages.success(request, f"Linked teacher '{new_teacher.name}' to subject '{new_subject.name}'.")
            except Exception as e:
                messages.warning(request, f"Could not link teacher and subject: {e}")

        # Save mapping (Group ↔ Subject)
        if mapping_form.is_valid():
            group = mapping_form.cleaned_data.get("group") or new_group
            subject = mapping_form.cleaned_data.get("subject") or new_subject
            hours = mapping_form.cleaned_data.get("hours_per_week")

            if group and subject:
                teacher = getattr(subject, "teacher", None)
                if not teacher and new_teacher:
                    subject.teacher = new_teacher
                    subject.save()
                GroupSubject.objects.update_or_create(
                    group=group, subject=subject, defaults={"hours_per_week": hours}
                )
                messages.success(
                    request,
                    f"Mapping for {group} ↔ {subject} saved (Teacher: {subject.teacher.name if subject.teacher else 'N/A'})."
                )
                saved = True
            else:
                messages.warning(request, "Please select both Group and Subject before saving mapping.")

        # Save period timings
        periods = settings_instance.periods_per_day
        period_times = {}
        for i in range(1, periods + 1):
            start = request.POST.get(f"period_{i}_start")
            end = request.POST.get(f"period_{i}_end")
            if start and end:
                period_times[f"P{i}"] = [start, end]
        if period_times:
            settings_instance.period_times = period_times
            settings_instance.save()
            saved = True

        # Generate timetable
        if "generate" in request.POST:
            ensure_timeslots(periods=settings_instance.periods_per_day)
            try:
                success, msg = generate_timetable()
                messages.success(request, msg if success else "Failed to generate timetable.")
            except Exception as e:
                messages.error(request, f"Error generating timetable: {e}")
            return redirect("home")

        messages.success(request, "Data saved successfully." if saved else "No valid data to save.")
        return redirect("home")

    # ---------- DISPLAY ----------
    scheduled = ScheduledPeriod.objects.select_related("group", "subject", "teacher", "room", "timeslot")
    structured = {}
    for sp in scheduled:
        gname = sp.group.name
        dname = DAY_NAMES[sp.timeslot.day]
        if gname not in structured:
            structured[gname] = {d: {} for d in DAY_NAMES}
        structured[gname][dname][sp.timeslot.period] = sp

    period_with_breaks = []
    period_times = settings_instance.period_times or {}
    lunch_start = settings_instance.lunch_start
    lunch_end = settings_instance.lunch_end
    short_start = settings_instance.short_break_start
    short_end = settings_instance.short_break_end

    default_start = datetime.combine(datetime.today(), time(9, 30))
    for i in range(1, settings_instance.periods_per_day + 1):
        key = f"P{i}"
        if key in period_times and isinstance(period_times[key], (list, tuple)):
            start_str, end_str = period_times[key]
        else:
            start_dt = default_start + timedelta(hours=(i - 1))
            end_dt = start_dt + timedelta(hours=1)
            start_str, end_str = start_dt.strftime("%H:%M"), end_dt.strftime("%H:%M")

        period_with_breaks.append({"type": "period", "number": i, "time": f"{start_str} - {end_str}"})

        if short_start and end_str == short_start.strftime("%H:%M"):
            period_with_breaks.append({
                "type": "break",
                "name": "☕ Short Break",
                "time": f"{short_start.strftime('%H:%M')} - {short_end.strftime('%H:%M')}",
            })

        if lunch_start and end_str == lunch_start.strftime("%H:%M"):
            period_with_breaks.append({
                "type": "break",
                "name": "🍱 Lunch Break",
                "time": f"{lunch_start.strftime('%H:%M')} - {lunch_end.strftime('%H:%M')}",
            })

    context = {
        "teacher_form": teacher_form,
        "subject_form": subject_form,
        "group_form": group_form,
        "mapping_form": mapping_form,
        "room_form": room_form,
        "settings_form": settings_form,
        "structured_timetable": structured,
        "period_with_breaks": period_with_breaks,
        "day_names": DAY_NAMES,
        "settings": settings_instance,
    }
    return render(request, "scheduler/home.html", context)


# ---------------- REGENERATE TIMETABLE ----------------
def regenerate_timetable(request):
    if request.method != "POST":
        return redirect("home")
    settings = TimetableSettings.objects.first()
    ensure_timeslots(periods=settings.periods_per_day if settings else 6)
    try:
        success, msg = generate_timetable()
        messages.success(request, msg if success else "Timetable regeneration failed.")
    except Exception as e:
        messages.error(request, f"Error regenerating timetable: {e}")
    return redirect("home")


# ---------------- DOWNLOAD PDF ----------------
def download_timetable_pdf(request):
    settings = TimetableSettings.objects.first()
    if not settings:
        messages.error(request, "No timetable found to export.")
        return redirect("home")

    scheduled = ScheduledPeriod.objects.select_related("group", "subject", "teacher", "room", "timeslot")
    structured = {}
    for sp in scheduled:
        gname = sp.group.name
        dname = DAY_NAMES[sp.timeslot.day]
        if gname not in structured:
            structured[gname] = {d: {} for d in DAY_NAMES}
        structured[gname][dname][sp.timeslot.period] = sp

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="timetable.pdf"'

    doc = SimpleDocTemplate(response, pagesize=landscape(A4))
    styles = getSampleStyleSheet()
    cell_style = ParagraphStyle(name='cell', fontSize=9, leading=10, alignment=1)
    elements = [Paragraph("Automatic Timetable", styles["Title"]), Spacer(1, 12)]

    for group, days in structured.items():
        elements.append(Paragraph(f"<b>{group}</b>", styles["Heading2"]))
        data = [["Period", "Time"] + DAY_NAMES]
        span_rows = []

        period_times = settings.period_times or {}
        lunch_start, lunch_end = settings.lunch_start, settings.lunch_end
        short_start, short_end = settings.short_break_start, settings.short_break_end

        for i in range(1, settings.periods_per_day + 1):
            key = f"P{i}"
            start, end = period_times.get(key, ["", ""])
            row = [str(i), f"{start} - {end}"]
            for d in DAY_NAMES:
                val = days[d].get(i)
                if val:
                    text = f"{val.subject.name}<br/>{val.teacher.name}<br/>{val.room.name}"
                    cell = Paragraph(text, cell_style)
                else:
                    cell = "-"
                row.append(cell)
            data.append(row)

            # Add Short Break
            if short_start and end == short_start.strftime("%H:%M"):
                data.append(["☕", f"{short_start.strftime('%H:%M')} - {short_end.strftime('%H:%M')}", "Short Break"] + [""] * (len(DAY_NAMES) - 1))
                span_rows.append(len(data) - 1)

            # Add Lunch Break
            if lunch_start and end == lunch_start.strftime("%H:%M"):
                data.append(["🍱", f"{lunch_start.strftime('%H:%M')} - {lunch_end.strftime('%H:%M')}", "Lunch Break"] + [""] * (len(DAY_NAMES) - 1))
                span_rows.append(len(data) - 1)

        table = Table(data, repeatRows=1)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1976d2")),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('BACKGROUND', (0, 1), (-1, -1), colors.whitesmoke),
        ]))

        # Merge (SPAN) break rows to align properly across columns
        for row_index in span_rows:
            table.setStyle(TableStyle([
                ('SPAN', (2, row_index), (-1, row_index)),
                ('BACKGROUND', (0, row_index), (-1, row_index), colors.HexColor("#FFF3CD")),
                ('TEXTCOLOR', (0, row_index), (-1, row_index), colors.HexColor("#795548")),
                ('ALIGN', (0, row_index), (-1, row_index), 'CENTER'),
            ]))

        elements.append(table)
        elements.append(Spacer(1, 20))

    doc.build(elements)
    return response