import requests

url = 'http://reborn.assay.cl/api/v1/fs_elec'

session = requests.Session()

# Puedes agregar parámetros a la solicitud si es necesario
# params = {'parametro1': 'valor1', 'parametro2': 'valor2'}

try:
    response = session.get(url)

    # Verifica si la solicitud fue exitosa (código de estado 200)
    if response.status_code == 200:
        # El contenido de la respuesta está en formato JSON, puedes usar response.json()
        data = response.json()
        print(data)
    else:
        print(f"Error en la solicitud. Código de estado: {response.status_code}")

except Exception as e:
    print(f"Error: {e}")