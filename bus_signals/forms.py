from django.forms import ModelForm
from .models import Bus, FusiMessage
from users.models import WorkOrder


class BusForm(ModelForm):
    class Meta:
        model = Bus
        fields = [
            'bus_name', 'sniffer', 'plate_number',
            'bus_series', 'client', 'vision', 'mark', 'jarvis', 'bus_img']


class FusiMessageForm(ModelForm):
    class Meta:
        model = FusiMessage
        fields = '__all__'


class WorkOrderForm(ModelForm):
    class Meta:
        model = WorkOrder
        fields = '__all__'
