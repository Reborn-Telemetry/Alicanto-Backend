from django.forms import ModelForm
from .models import Bus

class BusForm(ModelForm):
  class Meta:
    model = Bus
    fields = [
      'bus_name', 'sniffer', 'plate_number',
      'bus_series', 'client', 'vision', 'mark', 'jarvis' ]