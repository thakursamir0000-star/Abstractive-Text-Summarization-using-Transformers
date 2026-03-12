from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

model_path = "./fine_tuned_bart_model"

tokenizer = AutoTokenizer.from_pretrained(model_path)
model = AutoModelForSeq2SeqLM.from_pretrained(model_path)

def summarize(text):
    inputs = tokenizer(text, return_tensors="pt", max_length=1024, truncation=True)

    summary_ids = model.generate(
        inputs["input_ids"],
        max_length=150,
        min_length=40,
        num_beams=4,
        early_stopping=True
    )

    summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
    return summary
