import torch, datasets, json
from transformers import AutoTokenizer, AutoModelForCausalLM, TrainingArguments
from peft import LoraConfig, get_peft_model, TaskType
from trl import DPOTrainer
from typing import Dict, List

class DPOTrainingPipeline:
    def __init__(self, model_name: str, output_dir: str = "runtime/models/dpo_trained"):
        self.model_name = model_name
        self.output_dir = output_dir
        self.tokenizer = None
        self.model = None
        self.lora_config = LoraConfig(
            task_type=TaskType.CAUSAL_LM,
            r=16,
            lora_alpha=32,
            lora_dropout=0.1,
            target_modules=["q_proj", "v_proj"],
        )
    
    def load_model(self):
        """Load base model and tokenizer"""
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            torch_dtype=torch.float16,
            device_map="auto"
        )
        
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
        
        # Apply LoRA
        self.model = get_peft_model(self.model, self.lora_config)
    
    def prepare_dataset(self, data_file: str) -> datasets.Dataset:
        """Prepare DPO dataset from JSONL file"""
        def format_example(example):
            return {
                "prompt": example["prompt"],
                "chosen": example["chosen"],
                "rejected": example["rejected"]
            }
        
        dataset = datasets.load_dataset("json", data_files=data_file)["train"]
        dataset = dataset.map(format_example)
        return dataset
    
    def train(self, dataset: datasets.Dataset, num_epochs: int = 3, batch_size: int = 4):
        """Train model with DPO"""
        training_args = TrainingArguments(
            output_dir=self.output_dir,
            num_train_epochs=num_epochs,
            per_device_train_batch_size=batch_size,
            gradient_accumulation_steps=4,
            warmup_steps=100,
            logging_steps=10,
            save_steps=500,
            evaluation_strategy="no",
            fp16=True,
            report_to=None,
        )
        
        trainer = DPOTrainer(
            model=self.model,
            tokenizer=self.tokenizer,
            args=training_args,
            train_dataset=dataset,
            beta=0.1,  # DPO beta parameter
        )
        
        trainer.train()
        trainer.save_model()

if __name__ == "__main__":
    # Example usage
    trainer = DPOTrainingPipeline("microsoft/DialoGPT-small")
    trainer.load_model()
    
    # Load training data (should be in DPO format)
    dataset = trainer.prepare_dataset("runtime/state/packages/training_data.jsonl")
    trainer.train(dataset)