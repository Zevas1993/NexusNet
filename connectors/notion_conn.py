from notion_client import Client
def fetch_notion(token:str, db_id:str):
    client=Client(auth=token)
    r=client.databases.query(database_id=db_id)
    for page in r['results']:
        title=page['properties'].get('title',{}).get('title',[{}])[0].get('plain_text','')
        yield {'id':page['id'],'text':title,'type':'notion_page'}