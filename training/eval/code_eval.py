
import tempfile, os, subprocess
def run_unit(code: str, test: str, timeout: int = 5):
    with tempfile.TemporaryDirectory() as d:
        cp, tp = os.path.join(d,"solution.py"), os.path.join(d,"test_solution.py")
        open(cp,"w").write(code); open(tp,"w").write(test)
        p = subprocess.run(["pytest","-q"], cwd=d, capture_output=True, text=True, timeout=timeout)
        return p.returncode==0, p.stdout + "\n" + p.stderr
