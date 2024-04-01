from django.shortcuts import render
from bus_signals.models import Bus

import requests
no_update_list = ['27','34', '60', '24', '87', '116', '21', '61', '82', '83', '81']

# Create your views here.
def disponbilidad_flota(request):
   headers = { 'User-Agent': 'Alicanto/1.0', }
   api_url = 'https://reborn.assay.cl/api/v1/fs_elec'
   response = requests.get(api_url, headers=headers)
   data = response.json()
   bus_fs = []
   for i in data['data']:
      bus_fs.append(i['vehicle'].capitalize())

   bus_operativo = Bus.bus.all().exclude(bus_name__in=bus_fs)
   bus_operativo = bus_operativo.exclude(id__in=no_update_list)

   

   print(bus_fs) 
   print(bus_operativo)
   

   
   

   return render(request, 'reports/disponibilidad_flota.html')