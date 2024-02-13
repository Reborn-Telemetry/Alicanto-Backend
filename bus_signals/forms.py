from django.forms import ModelForm
from .models import Bus, FusiMessage, FusiCode
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


class FusiForm(ModelForm):
    class Meta:
        model = FusiCode
        fields = '__all__'
