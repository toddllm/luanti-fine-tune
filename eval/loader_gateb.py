from unsloth import FastLanguageModel

def load_gateb_model():
    """Exact loader function from successful Gate B evaluation"""
    # Copy/paste the exact call from working Gate B code:
    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name="unsloth/gpt-oss-20b-unsloth-bnb-4bit",
        max_seq_length=2048,
        dtype=None,
        load_in_4bit=True,
        local_files_only=True,
    )
    
    # Set for inference (same as Gate B)
    FastLanguageModel.for_inference(model)
    
    return model, tokenizer