from django.shortcuts import render, redirect
from bus_signals.forms import WorkOrderForm
from .models import WorkOrder


# Create your views here.

def profile(request):
    return render(request, 'users/profile.html')


def work_order(request):
    return render(request, 'users/work_order_form.html')


def create_work_order(request):
    form = WorkOrderForm()
    if request.method == 'POST':
        form = WorkOrderForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('bus_list')
    context = {'form': form}
    return render(request, 'users/work_order_form.html', context)


def update_ot(request, pk):
    ot = WorkOrder.objects.get(id=pk)
    form = WorkOrderForm(instance=ot)
    if request.method == 'POST':
        form = WorkOrderForm(request.POST, request.FILES, instance=ot)
        if form.is_valid():
            form.save()
            return redirect('bus_list')
    context = {'form': form}
    return render(request, 'users/work_order_form.html', context)