import json
import random

with open("chunks.json", "r", encoding="utf-8") as f:
    chunks = json.load(f)

sample = random.sample(chunks, 5)

for i, chunk in enumerate(sample, 1):
    print(f"\n--- Chunk {i} of 5 ---")
    print(f"Source    : {chunk['source']}")
    if chunk.get("professor"):
        print(f"Professor : {chunk['professor']}")
    if chunk.get("course"):
        print(f"Course    : {chunk['course']}")
    print(f"Text      : {chunk['text']}")
