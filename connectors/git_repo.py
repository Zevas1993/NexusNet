import git, pathlib
def clone_repo(url:str, dest='runtime/state/repos'):
    d=pathlib.Path(dest); d.mkdir(parents=True, exist_ok=True)
    name=url.split('/')[-1].replace('.git','')
    path=str(d/name)
    git.Repo.clone_from(url, path)
    return path