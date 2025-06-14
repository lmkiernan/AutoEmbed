import json
import os
from src.Embedding import OpenAIEmbedder, HFEmbedder
import time
from src.vectorStore import upsert_vector
# Adjust the path as needed
with open(os.path.join(os.path.dirname(__file__), '..', 'APIKeys.json')) as f:
       api_keys = json.load(f)

   # Access keys like:
openai_key = api_keys.get('openai')
huggingface_key = api_keys.get('huggingface')

def embed(chunk, config):
        for model in config["embedding"]:
            if model["provider"] == "openai":
                embed_openai(chunk, config)
            elif model["provider"] == "huggingface":
                embed_huggingface(chunk, config)

def embed_openai(chunk, config):
    for model in config["openai"]:
        embedder = get_embedder("openai", model["model"])
        t0 = time.time()
        vector = embedder.embed(chunk["text"])
        t1 = time.time()
        latency = (t1 - t0) *1000
        payload = {
            "chunk_id": chunk["chunk_id"],
            "source": chunk["source"],
            "strategy": chunk["strategy"],
            "token_count": list(chunk["tokens"].values())[0],
            "latency": latency,
            "cost":  list(chunk["tokens"].values())[0] * model["pricing_per_1k_tokens"] / 1000

        }
        upsert_vector(vector, payload, chunk["chunk_id"])
    
def embed_huggingface(chunk, config):
     for model in config["huggingface"]:
        return


def get_embedder(provider: str, model_name: str, **kwargs):
    provider = provider.lower()
    if provider == "openai":
        return OpenAIEmbedder(model_name, openai_key)
    elif provider in ("huggingface", "hf"):
        return HFEmbedder(model_name)
    else:
        raise ValueError(f"Unsupported provider: {provider}. Use 'openai' or 'huggingface'.")
