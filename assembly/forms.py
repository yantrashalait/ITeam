from django import forms

from .models import AssemblyComponent, Accessory
from PIL import Image
from dashboard.widgets import SelectWithPop


class AssemblyComponentForm(forms.ModelForm):
    class Meta:
        model = AssemblyComponent
        fields = ("name", )


class AccessoryForm(forms.ModelForm):
    x = forms.FloatField(widget=forms.HiddenInput(), required=False)
    y = forms.FloatField(widget=forms.HiddenInput(), required=False)
    width = forms.FloatField(widget=forms.HiddenInput(), required=False)
    height = forms.FloatField(widget=forms.HiddenInput(), required=False)
    category = forms.ModelChoiceField(AssemblyComponent.objects, widget=SelectWithPop)

    class Meta:
        model = Accessory
        fields = ('category', 'name', 'old_price', 'new_price', 'availability', 'visibility', 'image', 'use_in_assembly')

    def save(self):
        accessory = super(AccessoryForm, self).save()
        x = self.cleaned_data.get('x')
        y = self.cleaned_data.get('y')
        w = self.cleaned_data.get('width')
        h = self.cleaned_data.get('height')
        if x is not None and y is not None:
            image = Image.open(accessory.image)
            cropped_image = image.crop((x, y, w+x, h+y))
            resized_image = cropped_image.resize((265, 290), Image.ANTIALIAS)
            resized_image.save(accessory.image.path)
        return accessory
