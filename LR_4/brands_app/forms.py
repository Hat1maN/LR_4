from django import forms
from .config import FIELDS
from .models import Brand

class BrandForm(forms.Form):
    # сохраняем для обратной совместимости (тот, что был)
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, label, required, ftype in FIELDS:
            field = forms.CharField(label=label, required=required)
            if ftype == "int":
                field = forms.IntegerField(label=label, required=required)
            self.fields[name] = field

class BrandModelForm(forms.ModelForm):
    storage_choice = forms.ChoiceField(
        choices=(('db', 'Сохранить в БД'), ('xml', 'Сохранить в XML')),
        widget=forms.RadioSelect,
        initial='db',
        label='Куда сохранять'
    )

    class Meta:
        model = Brand
        fields = ['name', 'country', 'founded', 'note', 'color']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'country': forms.TextInput(attrs={'class': 'form-control'}),
            'founded': forms.NumberInput(attrs={'class': 'form-control'}),
            'note': forms.Textarea(attrs={'class': 'form-control', 'rows':3}),
            'color': forms.TextInput(attrs={'class': 'form-control'}),
        }
