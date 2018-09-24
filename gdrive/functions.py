
import os, os.path, io, logging, mimetypes, tempfile, shutil, bz2, sqlite3
import pandas as pd
from singleton_decorator import singleton

logging.getLogger('googleapiclient.discovery').setLevel(logging.ERROR)

@singleton
def GDrive():
    from pydrive.auth import GoogleAuth
    from pydrive.drive import GoogleDrive
    from google.colab import auth
    from oauth2client.client import GoogleCredentials

    auth.authenticate_user()
    gauth = GoogleAuth()
    gauth.credentials = GoogleCredentials.get_application_default()
    return GoogleDrive(gauth)

def idof(title, root='root'):
    try:
      ido = root
      for t in title:
        ido = next(i['id'] for i in 
               GDrive().ListFile({'q': "'{}' in parents and trashed=false".format(ido)}).GetList() 
               if i['title'].lower() == t.lower())
      return ido
    except StopIteration:
      raise FileNotFoundError('gdrive file "{}" not found at folder "{}"'.format('/'.join(title), root))

def mkdir(title, root='root'):
    ido = root
    for t in title:
        try:
            ido = next(i['id'] for i in 
                GDrive().ListFile({'q': "'{}' in parents and trashed=false".format(ido)}).GetList() 
                if i['title'].lower() == t.lower())
        except StopIteration:
            f = GDrive().CreateFile({'title':t,'parents':[{'id':ido}],'mimeType':'application/vnd.google-apps.folder'})
            f.Upload()
            ido = f['id']
    return ido

def _compression(name):
    return {'.bz2':'bz2', '.bz':'bz2', '.gz':'gzip', '.zip':'zip'}\
                    .get(os.path.splitext(name)[1],None)

def get_csv(name, root='root', **k):
    ido = idof(name.split('/'),root=root)
    f = GDrive().CreateFile({'id':ido})  
    f.FetchContent()
    return pd.read_csv(f.content, compression=_compression(name), **k)

def file(name, root='root'):
    try:
        return getfile(name, root=root)
    except FileNotFoundError:
        return newfile(name, root)

def getfile(name, root='root'):
    return GDrive().CreateFile( {'id':idof(name.split('/'),root=root)} )

def newfile(name, root='root'):
    path = name.split('/')
    mimetype = mimetypes.guess_type(path[-1])[0]
    ido = mkdir(path[:-1], root=root)
    return GDrive().CreateFile( {'title':path[-1],'parents':[{'id':ido}],'mimeType':mimetype})

def put_csv(df, name, root='root', **k):
    f = file(name, root)
    compression=_compression(name)
    if compression == 'bz2':
        bf = io.BytesIO()
        bz = bz2.open(bf,'wt',compresslevel=9, newline='\n')
        df.to_csv(bz, **k)
        bz.close()
        bf.seek(0)
        f.content = bf
        f['mimeType'] = 'application/x-bzip2'
        f.Upload()
    elif compression is None:
        bf = io.TextIOWrapper(io.BytesIO(), newline='\n')
        df.to_csv(bf, **k)
        bf.seek(0)        
        f.content = bf
        f['mimeType'] = mimetypes.guess_type(name[-1])[0]
        f.Upload()
    else:
        tf = tempfile.mktemp()
        try:
            df.to_csv(tf, compression=_compression(name), **k)
            f.content = open(tf,'rb')
            f['mimeType'] = mimetypes.guess_type(name[-1])[0]
            f.Upload()
        finally:
            if os.path.exists(tf):
                os.unlink(tf)

def upload(name, root='root', subdir=None, pack=True):
    ext = '.bz2' if pack else ''
    path = os.path.basename(name)+ext
    if subdir is not None:
        path = subdir+'/'+path
    f = file(path, root=root)
    
    with open(name,'rb') as s:
        if pack:
            bf = io.BytesIO()
            bz = bz2.open(bf,'wb',compresslevel=9)
            shutil.copyfileobj(s,bz)
            bz.close()
            bf.seek(0)
            f.content = bf
            f['mimeType'] = 'application/x-bzip2'
        else:
            f.content = s
            f['mimeType'] = mimetypes.guess_type(name[-1])[0]
        f.Upload()

def download(path, root='root', uniq=False, unpack=None):
    name = os.path.basename(path)
    
    if unpack is None:
        try:
            f = getfile(path, root=root)
        except FileNotFoundError:
            f = getfile(path+'.bz2', root=root)
            unpack = True
    else:
        if unpack:
            if not path.lower().endswith('.bz2'):
                path = path + '.bz2'
            else:
                name = os.path.splitext(name)[0]
        f = getfile(path, root=root)
    
    f.FetchContent()
    f.content.seek(0)

    if uniq is None:
        name = name
    elif uniq is True:
        name = f['id'] + '-' + name
    else:
        name = uniq

    try:
        with open(name,'wb') as o:
            if unpack:
                bz = bz2.open(f.content)
                shutil.copyfileobj(bz, o)
            else:
                shutil.copyfileobj(f.content, o)
            f.content.seek(0)
    except:
        if os.path.exists(name):
            os.unlink(name)
        raise

    return name

def get_sqlite(path, root='root'):
    name = download(path, root=root, uniq=True, \
                   unpack=True if path.lower().endswith('.bz2') else None)
    return sqlite3.connect(name)

