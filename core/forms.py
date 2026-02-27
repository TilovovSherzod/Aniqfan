from django import forms
from .models import Guide, Video, Topic, Practical, Lab, Test
from django.forms import inlineformset_factory
from .models import Question, Choice


class GuideForm(forms.ModelForm):
    class Meta:
        model = Guide
        fields = ["title", "description", "file", "is_published"]


class VideoForm(forms.ModelForm):
    class Meta:
        model = Video
        fields = ["title", "description", "file", "url", "is_published"]


class TopicForm(forms.ModelForm):
    class Meta:
        model = Topic
        fields = ["title", "description", "content", "file", "url", "is_published"]


class PracticalForm(forms.ModelForm):
    class Meta:
        model = Practical
        fields = ["title", "description", "files", "is_published"]


class LabForm(forms.ModelForm):
    class Meta:
        model = Lab
        fields = ["title", "description", "files", "is_published"]


class TestForm(forms.ModelForm):
    # expose time limit to teacher in minutes for easier input
    time_limit_minutes = forms.IntegerField(required=False, min_value=0, label='Vaqt (daqiqa)', help_text='0 = cheksiz')

    class Meta:
        model = Test
        fields = ["title", "description", "file", "allow_manual_review", "is_published"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # initialize minutes from seconds stored in instance
        if self.instance and getattr(self.instance, 'time_limit', None) is not None:
            self.fields['time_limit_minutes'].initial = int(self.instance.time_limit / 60) if self.instance.time_limit else 0

    def save(self, commit=True):
        obj = super().save(commit=False)
        minutes = self.cleaned_data.get('time_limit_minutes')
        try:
            minutes = int(minutes) if minutes is not None else 0
        except (TypeError, ValueError):
            minutes = 0
        obj.time_limit = max(0, int(minutes) * 60)
        if commit:
            obj.save()
        return obj


class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ["text", "order", "points", "allow_multiple"]


class ChoiceForm(forms.ModelForm):
    class Meta:
        model = Choice
        fields = ["text", "is_correct"]


ChoiceFormSet = inlineformset_factory(Question, Choice, form=ChoiceForm, fields=("text", "is_correct"), extra=1, can_delete=True)
