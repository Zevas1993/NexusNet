import re, torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
_SENT_SPLIT = re.compile(r'(?<=[.!?])\s+')
_CITE = re.compile(r'\[(\d+)\]')
def temporal_consistent(evidence):
    dates = [ (e.get('meta') or {}).get('valid_from') or (e.get('meta') or {}).get('observed_at') for e in evidence ]
    uniq = {str(d)[:10] for d in dates if d}
    return len(uniq) <= 1
class AISVerifier:
    def __init__(self, model_name='microsoft/deberta-v3-base-mnli', device=None):
        try:
            self.tok = AutoTokenizer.from_pretrained(model_name)
            self.m = AutoModelForSequenceClassification.from_pretrained(model_name).eval()
            self.device = device or ('cuda' if torch.cuda.is_available() else 'cpu')
            self.m.to(self.device); self._entail = 2; self.ready = True
        except Exception:
            self.ready = False
    def _ent(self, prem, hyp):
        inputs = self.tok(prem, hyp, return_tensors='pt', truncation=True, max_length=512).to(self.device)
        with torch.no_grad(): logits = self.m(**inputs).logits[0]
        p = torch.softmax(logits, dim=-1).tolist(); return p[self._entail]
    def lexical_overlap(self, a,b):
        A=set(a.lower().split()); B=set(b.lower().split()); 
        return len(A&B)/max(1,len(A))
    def check(self, answer, evidence, entail_thresh=0.70):
        sents = [s.strip() for s in _SENT_SPLIT.split(answer) if s.strip()]
        supported, details, unsupported = 0, [], []
        for i,s in enumerate(sents):
            cites = [int(n) for n in _CITE.findall(s)]
            if not cites: details.append({'i':i,'ok':False,'reason':'no_citation'}); unsupported.append(i); continue
            ok=False; best=0.0; src=None
            for c in cites:
                if 1<=c<=len(evidence):
                    prem = evidence[c-1]['snippet']; 
                    if self.ready:
                        p=self._ent(prem, s); best=max(best,p); src=evidence[c-1].get('source','')
                        if p>=entail_thresh: ok=True; break
                    else:
                        if self.lexical_overlap(prem, s) > 0.15: ok=True; best=0.9; src=evidence[c-1].get('source',''); break
            if ok: supported+=1; details.append({'i':i,'ok':True,'entail_p':best,'source':src})
            else: details.append({'i':i,'ok':False,'entail_p':best,'source':src}); unsupported.append(i)
        cov = supported / max(1,len(sents))
        return {'coverage':cov,'unsupported':unsupported,'details':details,'temporal_ok': temporal_consistent(evidence)}