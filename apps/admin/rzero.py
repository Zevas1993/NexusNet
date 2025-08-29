
import argparse, json
from training.rzero.runner import run_iterations
def run_many(model: str, seeds: str, experiment: str = "default", device: str = "cpu", iterations: int = 3):
    seed_list = [s.strip() for s in (seeds or "").split(",") if s.strip()]
    return run_iterations(model, seed_list, iterations=iterations, experiment=experiment, device=device)
def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--model", required=True)
    ap.add_argument("--seeds", default=""); ap.add_argument("--experiment", default="default")
    ap.add_argument("--device", default="cpu"); ap.add_argument("--iterations", type=int, default=1)
    args = ap.parse_args()
    print(json.dumps(run_many(args.model, args.seeds, args.experiment, args.device, args.iterations), indent=2))
if __name__ == "__main__": main()
