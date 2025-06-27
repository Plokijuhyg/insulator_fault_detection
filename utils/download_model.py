import os
import requests

def ensure_model_file(file_path, download_url):
    if not os.path.exists(file_path):
        print(f"⬇️ Downloading model from:\n{download_url}")
        r = requests.get(download_url, stream=True)
        with open(file_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        print("✅ Download complete:", file_path)
    else:
        print("✔️ Model already exists:", file_path)
