from slack_sdk import WebClient
def fetch_slack(token:str, channel:str, limit=50):
    client=WebClient(token=token)
    r=client.conversations_history(channel=channel, limit=limit)
    for msg in r['messages']:
        yield {'id':msg['ts'],'text':msg.get('text',''),'user':msg.get('user','')}