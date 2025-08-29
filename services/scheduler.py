
from __future__ import annotations
import threading, time, subprocess, yaml, shlex

class _Job(threading.Thread):
    daemon = True
    def __init__(self, name: str, period_s: int, cmd: str):
        super().__init__(name=name)
        self.period_s = period_s
        self.cmd = cmd
        self._stop = False
    def run(self):
        while not self._stop:
            try:
                subprocess.run(shlex.split(self.cmd), check=False)
            except Exception:
                pass
            for _ in range(self.period_s):
                if self._stop: break
                time.sleep(1)
    def stop(self): self._stop = True

class Scheduler:
    def __init__(self, cfg_path: str = "runtime/config/automation.yaml"):
        self.jobs: list[_Job] = []
        try:
            cfg = yaml.safe_load(open(cfg_path,"r",encoding="utf-8")) or {}
            sc = cfg.get("scheduler", {})
            if sc.get("enabled", False):
                for j in sc.get("jobs", []):
                    period = int(j.get("every_minutes", 60))*60
                    self.jobs.append(_Job(j.get("name","job"), period, j.get("cmd","echo noop")))
        except Exception:
            pass
    def start(self):
        for j in self.jobs: j.start()
    def stop(self):
        for j in self.jobs: j.stop()
