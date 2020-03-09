from django import forms
from .models import Planet, Recruit, Test


class RecruitForm(forms.Form):
    name = forms.CharField(label="Имя", max_length=30)
    planet = forms.ChoiceField(label="Планета", choices=Planet.get_choices())
    age = forms.IntegerField(label="Возраст", min_value=0, max_value=32767)
    email = forms.EmailField(label="Электронная почта", initial="@mail.ru")


class RecruitChoiceForm(forms.Form):
    recruit = forms.ChoiceField(
        label="Рекрут", choices=Recruit.get_not_tested_recruit_choices())
