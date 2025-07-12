# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "datasets",
#     "gesserit==0.3.0",
#     "numpy",
#     "transformers[torch]",
# ]
# ///
import io
from functools import cache

import numpy as np
from datasets import load_dataset
from transformers import AutoImageProcessor, AutoModel, AutoTokenizer

from gesserit.core import Gesserit, SearchItem


def create_ds():
    model = AutoModel.from_pretrained("openai/clip-vit-base-patch16")
    processor = AutoImageProcessor.from_pretrained("openai/clip-vit-base-patch16")

    ds = load_dataset(
        "timm/mini-imagenet",
        split="test",
        cache_dir="/Users/yonigo/gesserit/cache",
    )
    # very strange to save embeddings like this but huggingface upload api doesn't support storing single embedding list field
    ds = ds.map(
        lambda example: {
            f"image_embeddings_{i}": v
            for i, v in enumerate(
                model.get_image_features(**processor([example["image"]], return_tensors="pt"))[0]
                .detach()
                .cpu()
                .numpy()
            )
        }
    )
    ds = ds.select(range(0, 5000, 10))
    ds.push_to_hub("yonigo/mini-imagenet-clip-embeddings", private=False)


@cache
def get_vector_db():
    ds = load_dataset("yonigo/mini-imagenet-clip-embeddings")
    vectors = []
    for i in ds["test"]:
        v = [i[key] for key in [f"image_embeddings_{j}" for j in range(512)]]
        vectors.append(v)
    images = ds["test"]["image"]
    vectors = np.array(vectors)
    return vectors, images


@cache
def get_model_and_tokenizer():
    model = AutoModel.from_pretrained("openai/clip-vit-base-patch16")
    tokenizer = AutoTokenizer.from_pretrained("openai/clip-vit-base-patch16")
    return model, tokenizer


async def search_function(query: str = "brown dog", k: int = 5):
    model, tokenizer = get_model_and_tokenizer()
    text_embedding = (
        model.get_text_features(**tokenizer([query], return_tensors="pt", truncation=True))[0].detach().numpy()
    )
    vectors, images = get_vector_db()

    # cosine similarity
    scores = np.dot(vectors, text_embedding) / (np.linalg.norm(vectors, axis=1) * np.linalg.norm(text_embedding))
    indices = np.argpartition(scores, -k)[-k:]

    results = []
    for i in indices:
        buffer = io.BytesIO()
        images[int(i)].save(buffer, format="JPEG")
        results.append(SearchItem(image_bytes=buffer.getvalue(), metadata={"score": scores[i]}))
    return results


if __name__ == "__main__":
    app = Gesserit(search_function=search_function)
    app.run()
