from django import forms
from .models import Quest, Note, Skill, Boss


class QuestForm(forms.ModelForm):
    class Meta:
        model = Quest
        fields = [
            'title', 'description', 'priority', 'rarity',
            'deadline', 'skill', 'penalty_xp', 'image',
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Назва квесту',
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Опис завдання',
            }),
            'priority': forms.Select(attrs={'class': 'form-select'}),
            'rarity': forms.Select(attrs={'class': 'form-select'}),
            'deadline': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local',
            }),
            'skill': forms.Select(attrs={'class': 'form-select'}),
            'penalty_xp': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Штраф XP за провал',
            }),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user is not None:
            self.fields['skill'].queryset = Skill.objects.filter(user=user)


class NoteForm(forms.ModelForm):
    class Meta:
        model = Note
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Нотатка до квесту...',
            }),
        }


class QuestFilterForm(forms.Form):
    status = forms.ChoiceField(
        choices=[('', 'Всі статуси')] + Quest.STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
    )
    priority = forms.ChoiceField(
        choices=[('', 'Всі пріоритети')] + Quest.PRIORITY_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
    )
    skill = forms.ModelChoiceField(
        queryset=Skill.objects.none(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
        empty_label='Всі навички',
    )
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Пошук за назвою',
        }),
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user is not None:
            self.fields['skill'].queryset = Skill.objects.filter(user=user)


class SkillForm(forms.ModelForm):
    class Meta:
        model = Skill
        fields = ['name', 'color']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Назва навички',
            }),
            'color': forms.TextInput(attrs={
                'class': 'form-control',
                'type': 'color',
                'style': 'height: 40px; padding: 2px;',
            }),
        }


class BossForm(forms.ModelForm):
    class Meta:
        model = Boss
        fields = ['name', 'skill', 'min_level', 'deadline', 'description', 'reward_xp']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Назва боса',
            }),
            'skill': forms.Select(attrs={'class': 'form-select'}),
            'min_level': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Мінімальний рівень навички',
            }),
            'deadline': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local',
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Опис боса',
            }),
            'reward_xp': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Нагорода XP',
            }),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user is not None:
            self.fields['skill'].queryset = Skill.objects.filter(user=user)