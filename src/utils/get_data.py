import os
import zipfile
import io
import urllib.request

def extract_Http(url):
    Mozilla = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:101.0) Gecko/20100101 Firefox/101.0'
    output_dir = 'data/rawdata'

    os.makedirs(output_dir, exist_ok=True)
    
    try:
        req = urllib.request.Request(url)
        req.add_header('User-Agent', Mozilla)
    
        with urllib.request.urlopen(req) as response:
            with zipfile.ZipFile(io.BytesIO(response.read())) as zip_ref:
                csv_filename = zip_ref.namelist()[0]
                output_path = os.path.join(output_dir, csv_filename)
                with zip_ref.open(csv_filename) as csv_file:
                    with open(output_path, 'wb') as output_file:
                        output_file.write(csv_file.read())
                
                print(f"Fichier CSV extrait et enregistré sous : {output_path}")
    
    except Exception as e:
        print(f"Erreur lors du téléchargement ou de l'extraction du fichier CSV : {e}")