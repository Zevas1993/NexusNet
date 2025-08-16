from googleapiclient.discovery import build
from google.auth.transport.requests import Request
def fetch_gdrive(creds, folder_id=None):
    service=build('drive','v3',credentials=creds)
    q=f"'{folder_id}' in parents" if folder_id else "mimeType='text/plain'"
    r=service.files().list(q=q,fields='files(id,name)').execute()
    for f in r.get('files',[]):
        content=service.files().get_media(fileId=f['id']).execute()
        yield {'id':f['id'],'text':content.decode('utf-8'),'name':f['name']}