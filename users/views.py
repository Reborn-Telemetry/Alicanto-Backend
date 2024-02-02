from django.shortcuts import render


# Create your views here.

def profile(request):
    return render(request, 'users/profile.html')


def work_order(request):
    return render(request, 'users/work_order_form.html')
