from django import forms
from .models import Teacher, Subject, Group, GroupSubject, Room, TimetableSettings


class TeacherForm(forms.ModelForm):
    class Meta:
        model = Teacher
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter teacher name',
            })
        }


class SubjectForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter subject name',
            }),
        }


class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ['name', 'size']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter group/class name (e.g. SY IT-A)',
            }),
            'size': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter number of students',
            }),
        }


class RoomForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = ['name', 'capacity']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter room name (e.g. F201 / Lab 1)',
            }),
            'capacity': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter room capacity',
            }),
        }


class GroupSubjectForm(forms.ModelForm):
    class Meta:
        model = GroupSubject
        fields = ['group', 'hours_per_week']
        widgets = {
            'group': forms.Select(attrs={'class': 'form-control'}),
            'hours_per_week': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Hours per week (e.g. 3)',
            }),
        }


# --- Updated Timetable Settings Form ---
class TimetableSettingsForm(forms.ModelForm):
    # Dynamic fields for period start/end times
    period_1_start = forms.TimeField(widget=forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}), required=False)
    period_1_end = forms.TimeField(widget=forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}), required=False)
    period_2_start = forms.TimeField(widget=forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}), required=False)
    period_2_end = forms.TimeField(widget=forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}), required=False)
    period_3_start = forms.TimeField(widget=forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}), required=False)
    period_3_end = forms.TimeField(widget=forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}), required=False)
    period_4_start = forms.TimeField(widget=forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}), required=False)
    period_4_end = forms.TimeField(widget=forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}), required=False)
    period_5_start = forms.TimeField(widget=forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}), required=False)
    period_5_end = forms.TimeField(widget=forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}), required=False)
    period_6_start = forms.TimeField(widget=forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}), required=False)
    period_6_end = forms.TimeField(widget=forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}), required=False)
    period_7_start = forms.TimeField(widget=forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}), required=False)
    period_7_end = forms.TimeField(widget=forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}), required=False)

    class Meta:
        model = TimetableSettings
        fields = [
            'periods_per_day',
            'lunch_start',
            'lunch_end',
            'short_break_start',
            'short_break_end',
        ]
        widgets = {
            'periods_per_day': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Number of periods per day (e.g. 6 or 7)',
            }),
            'lunch_start': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'lunch_end': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'short_break_start': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'short_break_end': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
        }

    def save(self, commit=True):
        """Save custom period timings as JSON."""
        instance = super().save(commit=False)
        periods = {}
        for i in range(1, instance.periods_per_day + 1):
            start = self.cleaned_data.get(f'period_{i}_start')
            end = self.cleaned_data.get(f'period_{i}_end')
            if start and end:
                periods[f'P{i}'] = [start.strftime('%H:%M'), end.strftime('%H:%M')]
        instance.period_times = periods
        if commit:
            instance.save()
        return instance
