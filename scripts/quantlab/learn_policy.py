import os, requests

from quantlab.policy import learn_from_bench, current_policy
if __name__ == "__main__":
    pol = learn_from_bench()
    print("Learned policy:", pol or current_policy())


try:
    base = os.environ.get("NEXUSNET_API_BASE","http://127.0.0.1:8000")
    requests.post(f"{base}/admin/policy/notify", json={"policy": (pol or current_policy())}, timeout=5)
except Exception:
    pass
