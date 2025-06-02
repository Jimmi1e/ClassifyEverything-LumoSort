import os
import sys
import shutil
from PIL import Image
import torch
from clip import clip
from labels import CLIP_LABELS, LABEL_DISPLAY
import clip.simple_tokenizer as st

if getattr(sys, 'frozen', False):
    base_path = sys._MEIPASS
else:
    base_path = os.path.dirname(__file__)
st.BPE_PATH = os.path.join(os.path.dirname(__file__), "clip_vocab", "bpe_simple_vocab_16e6.txt.gz")
# Load model
# clip_model, preprocess_clip = clip.load("ViT-B/32", device="cpu")
# clip_model, preprocess_clip = clip.load("ViT-B/32", device="cpu", download_root="./models")
clip_model, preprocess_clip = clip.load("ViT-B/32", device="cpu", download_root=os.path.join(base_path, "models"))
text_tokens = clip.tokenize(CLIP_LABELS).to("cpu")

# Image classification using CLIP
def classify_images_by_clip(paths, output_dir, progress_callback=None):
    os.makedirs(output_dir, exist_ok=True)
    results ={}
    low_conf_log = []

    for idx, path in enumerate(paths):
        try:
            image = preprocess_clip(Image.open(path).convert("RGB")).unsqueeze(0)
            with torch.no_grad():
                image_features = clip_model.encode_image(image)
                text_features = clip_model.encode_text(text_tokens)
                logits = image_features @ text_features.T
                probs = logits.softmax(dim=-1).cpu().numpy()[0]
                best_idx = int(probs.argmax())
                best_score = probs[best_idx]
                label = CLIP_LABELS[best_idx]
                display_name = LABEL_DISPLAY.get(label, label)

                dest_dir = os.path.join(output_dir, display_name)
                os.makedirs(dest_dir, exist_ok=True)

                filename = os.path.basename(path)
                if best_score < 0.4:
                    low_conf_log.append(f"{filename}\t{display_name}\t{best_score:.3f}")

                shutil.copy(path, os.path.join(dest_dir, filename))

        except Exception as e:
            print(f"Skipped {path}: {e}")

        if progress_callback:
            progress_callback(int((idx + 1) / len(paths) * 100))
    #I have to say low_conf means the picture may not belong to this category!!!
    if low_conf_log:
        with open(os.path.join(output_dir, "low_confidence.txt"), "w", encoding="utf-8") as f:
            f.write("File Name\tCategory\tConfidence\n")
            f.write("\n".join(low_conf_log))
    return results
