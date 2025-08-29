
#!/usr/bin/env python3
import yaml, sys
from transformers import AutoTokenizer, AutoModelForCausalLM
cfg = yaml.safe_load(open('runtime/models/models.yaml'))
ids = [cfg.get('solver'), cfg.get('challenger'), cfg.get('unified')]
for mid in ids:
    if not mid: continue
    print('[bootstrap] downloading', mid)
    AutoTokenizer.from_pretrained(mid)
    AutoModelForCausalLM.from_pretrained(mid)
print('[bootstrap] done.')
