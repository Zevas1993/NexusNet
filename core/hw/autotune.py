import json, pathlib
from .scan import scan_hardware
def apply_autotune():
    hw = scan_hardware()
    out = {"cpu_threads": None, "gguf_ctx": None, "transformers_bits": None, "vllm": {}, "colbert": {}}
    cores = hw.get("cpu_logical", 8) or 8
    out["cpu_threads"] = max(2, int(cores*0.7))
    ram = hw.get("mem_total_gb", 16)
    out["gguf_ctx"] = 4096 if ram >= 32 else 2048
    out["transformers_bits"] = 8 if (hw.get("gpus") or []) else 16
    if hw.get("gpus"):
        vram = hw["gpus"][0]["vram_gb"]
        out["vllm"] = {"tensor_parallel_size": 1, "max_num_seqs": 64 if vram>=40 else 16}
        out["colbert"] = {"nprobe": 128 if vram>=40 else 64}
    path = pathlib.Path("runtime/state/autotune.json")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(out, indent=2), encoding="utf-8")
    return out
