import sys
import os
import json
import urllib.request
import urllib.parse

def check_steam_mods(mod_ids):
    print(f"Verificando {len(mod_ids)} mods en Steam...")
    
    url = "https://api.steampowered.com/ISteamRemoteStorage/GetPublishedFileDetails/v1/"
    valid_mods = []
    
    # Podemos enviar en lotes para no sobrecargar si son muchos, 
    # pero Steam soporta varios cientos en una sola petición.
    # Enviaremos en lotes de 100
    batch_size = 100
    for i in range(0, len(mod_ids), batch_size):
        batch = mod_ids[i:i + batch_size]
        
        data = {
            "itemcount": len(batch)
        }
        
        for index, mod_id in enumerate(batch):
            data[f"publishedfileids[{index}]"] = mod_id
        
        encoded_data = urllib.parse.urlencode(data).encode('utf-8')
        
        req = urllib.request.Request(url, data=encoded_data, method="POST")
        try:
            with urllib.request.urlopen(req) as response:
                result = json.loads(response.read().decode('utf-8'))
                
                # 'response' -> 'publishedfiledetails'
                if result and 'response' in result and 'publishedfiledetails' in result['response']:
                    details = result['response']['publishedfiledetails']
                    for detail in details:
                        # Si tiene 'title', normalmente significa que existe (o no falló o no fue eliminado).
                        # returncode == 1 significa éxito en Steam
                        if detail.get('result') == 1 and 'title' in detail:
                            # A veces title está vacío para mods eliminados, verifiquemos que existe
                            valid_mods.append({
                                'id': detail['publishedfileid'],
                                'name': detail['title']
                            })
                        else:
                            print(f"Mod {detail.get('publishedfileid', 'Desconocido')} no encontrado o inválido.")
        except Exception as e:
            print(f"Error al verificar en Steam: {e}")
            
    return valid_mods

def main():
    input_file = "mods_input.txt"
    if not os.path.exists(input_file):
        # Crear un archivo de prueba si no existe
        print(f"No se encontró '{input_file}'. Creando un archivo de prueba de ejemplo...")
        with open(input_file, "w", encoding="utf-8") as f:
            f.write("2169435993, 2717703136, 99999999999")
        print(f"Edita '{input_file}' con tus IDs y vuelve a ejecutar el script.")
        return

    # Leer el archivo
    with open(input_file, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Separar por comas y limpiar espacios
    raw_ids = [m.strip() for m in content.split(",") if m.strip()]
    
    # Filtrar solo numéricos por si acaso
    mod_ids = [m for m in raw_ids if m.isdigit()]
    
    if not mod_ids:
        print("No se encontraron IDs válidos en el archivo de entrada.")
        return
        
    valid_mods = check_steam_mods(mod_ids)
    
    if not valid_mods:
        print("Ninguno de los mods fue encontrado en Steam.")
        return
        
    # Crear archivo de IDs válidos (separados por coma)
    valid_ids = [mod['id'] for mod in valid_mods]
    with open("valid_mod_ids.txt", "w", encoding="utf-8") as f:
        f.write(", ".join(valid_ids))
    print(f"-> Creado valid_mod_ids.txt con {len(valid_ids)} IDs.")
        
    # Crear archivo de Nombres válidos (separados por punto y coma y slash ;/)
    valid_names = [mod['name'] for mod in valid_mods]
    with open("valid_mod_names.txt", "w", encoding="utf-8") as f:
        f.write(";/".join(valid_names))
    print(f"-> Creado valid_mod_names.txt con nombres separados por ';/'.")
    
    print("\nProceso terminado con éxito.")

if __name__ == "__main__":
    main()
