import requests
def fs_link_api():
    headers = {'User-Agent': 'Alicanto/1.0',
               'Connection': 'keep-alive'}
    api_url = 'https://reborn.assay.cl/api/v1/fs_elec'
    
    try:
        response = requests.get(api_url, headers=headers)
        response.raise_for_status()  # Verifica si hubo algún error en la solicitud HTTP (404, 500, etc.)
        
        # Intenta decodificar el JSON
        try:
            data = response.json()
        except requests.exceptions.JSONDecodeError:
            print("Error: La respuesta no es un JSON válido.")
            return None
        
        api_data = {
            'data': data.get('data', []),  # Protege contra claves faltantes
            'cant_fs': len(data.get('data', []))  # Usa lista vacía si 'data' no está presente
        }
        return api_data
    
    except requests.exceptions.RequestException as e:
        print(f"Error en la solicitud HTTP: {e}")
        return None