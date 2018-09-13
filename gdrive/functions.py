
import os, os.path
import pandas as pd

from singleton_decorator import singleton

@singleton
def GDrive():
    from pydrive.auth import GoogleAuth
    from pydrive.drive import GoogleDrive
    from google.colab import auth
    from oauth2client.client import GoogleCredentials

    # 1. Authenticate and create the PyDrive client.
    auth.authenticate_user()
    gauth = GoogleAuth()
    gauth.credentials = GoogleCredentials.get_application_default()
    return GoogleDrive(gauth)

def idof(title,root='root'):
    try:
      ido = root    
      for t in title:      
        ido = next(i['id'] for i in 
               GDrive().ListFile({'q': "'{}' in parents and trashed=false".format(ido)}).GetList() 
               if i['title'].lower() == t.lower())
      return ido
    except StopIteration:
      raise FileNotFoundError('gdrive file "{}" not found at folder "{}"'.format('/'.join(title),root))

def get_csv(name,root='root'):
    ido = idof(name.split('/'),root=root)
    f = GDrive().CreateFile({'id':ido})  
    f.FetchContent()
    compression = {'.bz2':'bz2', '.bz':'bz2', '.gz':'gzip', '.zip':'zip'}\
                    .get(os.path.splitext(name)[1],None)
    return pd.read_csv(f.content,compression=compression)


