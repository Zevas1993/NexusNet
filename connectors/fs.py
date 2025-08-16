import pathlib, mimetypes
def scan_dir(path:str, patterns=['*.md','*.txt','*.py']):
    p=pathlib.Path(path)
    for pattern in patterns:
        for f in p.rglob(pattern):
            if f.is_file():
                yield str(f), f.read_text(errors='ignore')