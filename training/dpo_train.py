#!/usr/bin/env python3
"""Direct DPO training on assimilated data"""
import torch
from transformers import TrainingArguments
from trl import DPOTrainer, DPOConfig
from datasets import Dataset
import json
from pathlib import Path
from core.config import STATE_DIR

def load_dpo_data():
    """Load assimilated training data"""
    data_path = STATE_DIR / "dpo_data.jsonl"
    if not data_path.exists():
        return None
    
    data = []
    with open(data_path, 'r') as f:
        for line in f:
            data.append(json.loads(line.strip()))
    
    return Dataset.from_list(data)

def train_dpo(model_name: str = "microsoft/DialoGPT-medium"):
    """Train using DPO on preference data"""
    print(f"Starting DPO training with {model_name}")
    
    # Load data
    dataset = load_dpo_data()
    if dataset is None:
        print("No DPO data found. Run assimilation first.")
        return
    
    print(f"Loaded {len(dataset)} training examples")
    
    # Configure training
    config = DPOConfig(
        model_name=model_name,
        learning_rate=1e-6,
        per_device_train_batch_size=1,
        gradient_accumulation_steps=4,
        num_train_epochs=3,
        warmup_steps=100,
        logging_steps=10,
        save_steps=500,
        output_dir=str(STATE_DIR / "dpo_checkpoints"),
        remove_unused_columns=False,
        run_name="nexusnet_dpo"
    )
    
    # Initialize trainer
    trainer = DPOTrainer(
        config=config,
        train_dataset=dataset,
        tokenizer=None,  # Will be loaded automatically
    )
    
    # Train
    print("Starting training...")
    trainer.train()
    
    # Save final model
    model_path = STATE_DIR / "fine_tuned_model"
    trainer.save_model(str(model_path))
    print(f"Model saved to {model_path}")

if __name__ == "__main__":
    train_dpo()
