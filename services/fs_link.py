import requests
def fs_link_api():
   headers = {'User-Agent': 'Alicanto/1.0',}
   api_url = 'https://reborn.assay.cl/api/v1/fs_elec'
   response = requests.get(api_url, headers=headers)
   data = response.json()
   api_data = {
      'data': data['data'],
      'cant_fs': len(data['data'])
   }
   return api_data

