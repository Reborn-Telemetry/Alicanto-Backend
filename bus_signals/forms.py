from django.forms import ModelForm
from .models import Bus

class BusForm(ModelForm):
  class Meta:
    model = Bus
    fields = '__all__' 