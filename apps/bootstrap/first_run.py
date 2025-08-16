import json, pathlib
print('NexusNet First-Run Wizard'); pathlib.Path('runtime/models').mkdir(parents=True, exist_ok=True)
open('runtime/config/paths.json','w',encoding='utf-8').write(json.dumps({'model_dir':'runtime/models'},indent=2))
print('Done.')