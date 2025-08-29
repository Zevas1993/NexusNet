import argparse, json
from datasets import Dataset
from transformers import AutoTokenizer, AutoModelForCausalLM, TrainingArguments
from peft import LoraConfig, get_peft_model
from trl import DPOTrainer
def load_jsonl(path):
    rows=[]
    with open(path,"r",encoding="utf-8") as f:
        for line in f:
            try: rows.append(json.loads(line))
            except Exception: pass
    return Dataset.from_list(rows)
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--base_model', required=True)
    ap.add_argument('--train_file', required=True)
    ap.add_argument('--output_dir', default='runtime/state/dpo_out')
    ap.add_argument('--beta', type=float, default=0.1)
    args=ap.parse_args()
    ds=load_jsonl(args.train_file)
    tok=AutoTokenizer.from_pretrained(args.base_model, use_fast=True)
    base=AutoModelForCausalLM.from_pretrained(args.base_model, device_map="auto")
    lora=LoraConfig(r=16,lora_alpha=32,target_modules=["q_proj","v_proj","k_proj","o_proj","gate_proj","down_proj","up_proj"],lora_dropout=0.05,task_type="CAUSAL_LM")
    model=get_peft_model(base, lora)
    def map_pair(x):
        resp=x['response']; mid=len(resp)//2
        return {'prompt':x['prompt'],'chosen':resp[:mid] or resp,'rejected':resp[mid:] or resp}
    dspo=ds.map(map_pair)
    trainer=DPOTrainer(model=model, ref_model=None, beta=args.beta, args=TrainingArguments(
        output_dir=args.output_dir, per_device_train_batch_size=2, gradient_accumulation_steps=8,
        learning_rate=2e-5, num_train_epochs=1, bf16=True, logging_steps=10, save_steps=200
    ), tokenizer=tok, train_dataset=dspo)
    trainer.train(); trainer.save_model(args.output_dir)
if __name__=="__main__": main()
