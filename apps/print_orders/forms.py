from django import forms

from .models import PrintOrder, PrintOrderItem, ModelFile
from apps.clients.models import Client


class PrintOrderCreateForm(forms.ModelForm):
    client = forms.ModelChoiceField(queryset=Client.objects.all())
    #delivery_type = forms.IntegerField()
    #delivery_address = forms.CharField()
    #comment = forms.CharField()

    class Meta:
        model = PrintOrder
        fields = ['client', 'delivery_type', 'delivery_address', 'comment']


class ModelFileCreateForm(forms.ModelForm):
    class Meta:
        model = ModelFile
        fields = ['client', 'file']


class PrintOrderItemCreateForm(forms.ModelForm):
    class Meta:
        model = PrintOrderItem
        fields = ["order", "model_file", "material", "colour", "count", "layer_height", "infill", "shells", "comment"]
