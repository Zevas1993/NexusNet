
def route(task: str):
    t = task.lower()
    if any(k in t for k in ['math','algebra','number','solve']): return 'rzero_math'
    if any(k in t for k in ['code','python','bug','function']): return 'rzero_code'
    return 'rzero_reasoning'
