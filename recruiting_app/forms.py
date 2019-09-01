from django import forms
from .models import Planet, Recruit, Test


class RecruitForm(forms.Form):
    name = forms.CharField(label="Имя", max_length=30)
    planets = Planet.objects.all()
    planet = forms.ChoiceField(label="Планета", choices=tuple((pl.planetID, pl.name) for pl in planets))
    age = forms.IntegerField(label="Возраст", min_value=0, max_value=32767)
    email = forms.EmailField(label="Электронная почта", initial="@mail.ru")


class RecruitChoiceForm(forms.Form):
    choice = tuple((recr.id, recr.name) for recr in Recruit.objects.filter(isTested=False))
    recruit = forms.ChoiceField(label="Рекрут", choices=choice)
