from gpt4all import GPT4All
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, "..", "model")
MODEL_NAME = "mistral-7b-instruct-v0.1.Q4_0.gguf"

model_path = os.path.join(MODEL_DIR, MODEL_NAME)

if not os.path.exists(model_path):
    raise FileNotFoundError(f"❌ Model not found at: {model_path}")

print("🔄 Loading GPT4All local model...")
gpt_model = GPT4All(model_name=MODEL_NAME, model_path=MODEL_DIR)

def generate_response(prompt, max_tokens=300):
    output = gpt_model.generate(
        prompt=prompt,
        max_tokens=max_tokens,
        temp=0.7,
        top_k=40,
        top_p=0.9
    )
    return output.strip()
