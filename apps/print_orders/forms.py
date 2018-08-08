from django import forms

from .models import PrintOrder, PrintOrderItem, ModelFile
from apps.clients.models import Client


class PrintOrderForm(forms.ModelForm):
    client = forms.ModelChoiceField(queryset=Client.objects.all())

    class Meta:
        model = PrintOrder
        fields = ['client', 'delivery_type', 'delivery_address', 'comment']


class ModelFileForm(forms.ModelForm):
    class Meta:
        model = ModelFile
        fields = ['client', 'file']


class PrintOrderItemForm(forms.ModelForm):
    class Meta:
        model = PrintOrderItem
        fields = ["order", "model_file", "material", "colour", "count", "layer_height", "infill", "shells", "comment"]
