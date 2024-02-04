# from typing import Any
# from django import forms
# from django.core.exceptions import ValidationError

# from .models import Color, Variety

# class ColorValidation(forms.ModelForm):
#     class Meta:
#         model = Variety
#         fields = ['color',]

#     def clean(self):
#         cleaned_data = super().clean()
#         color = cleaned_data.get('color')
#         existing_color = Variety.objects.filter(object_id=self.instance.object_id, color=color)

#         if self.instance and self.instance.id:
#             existing_color = existing_color.exclude(id=self.instance.id)

#         if existing_color.exists():
#             raise ValidationError({'color':'This color already exists.'})

#         return cleaned_data
