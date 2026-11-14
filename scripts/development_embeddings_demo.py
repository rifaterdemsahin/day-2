#!/usr/bin/env python3
"""
S2-DEV: Embeddings & Vector Arithmetic Demonstration
Part of Day 2 Short: "From Numbers to Meaning: High-Dimensional Embeddings"

This script demonstrates the exact code mechanics behind the video script:
1. Clip c1: Token IDs as integers (king = 9246)
2. Clip c2: Unfolding integers into vector coordinates (D-dimensional space)
3. Clip c3: Distance reflecting semantic meaning (Fruit cluster vs Royalty cluster)
4. Clip c4 & c5: Vector arithmetic (king - man + woman = queen)
5. Clip c6: Preview of Attention (how vectors talk to each other)
"""

import math

# -----------------------------------------------------------------------------
# 1. Clip c1: "Tokens are just numbers... 9246 is a word"
# -----------------------------------------------------------------------------
VOCABULARY = {
    "king": 9246,
    "queen": 9247,
    "man": 512,
    "woman": 513,
    "crown": 9248,
    "apple": 2048,
    "pear": 2049,
    "grape": 2050,
}

ID_TO_WORD = {idx: word for word, idx in VOCABULARY.items()}


# -----------------------------------------------------------------------------
# 2. Clip c2: "So it gets unfolded. One number becomes coordinates."
# In real models (e.g. OpenAI text-embedding-3-small), D = 1,536.
# Here we use an intuitive 4-dimensional semantic subspace:
# [Royalty, Femininity, Fruit/Edible, Power/Status]
# -----------------------------------------------------------------------------
DIMENSIONS = ["Royalty", "Femininity", "Fruit", "Power"]

EMBEDDINGS = {
    "king":  [ 0.90, -0.75,  0.02,  0.95],
    "queen": [ 0.92,  0.80,  0.01,  0.94],
    "man":   [ 0.05, -0.80,  0.00,  0.20],
    "woman": [ 0.06,  0.78,  0.00,  0.20],
    "crown": [ 0.85,  0.00,  0.00,  0.88],
    "apple": [-0.85,  0.00,  0.95, -0.60],
    "pear":  [-0.82,  0.00,  0.93, -0.58],
    "grape": [-0.80,  0.00,  0.91, -0.55],
}


def lookup_embedding(token_id: int):
    """Retrieve vector coordinates for a given token ID."""
    word = ID_TO_WORD.get(token_id)
    if not word or word not in EMBEDDINGS:
        raise ValueError(f"Unknown token ID: {token_id}")
    return word, EMBEDDINGS[word]


# -----------------------------------------------------------------------------
# 3. Clip c3: "And meaning becomes distance. Apples, pears gather here..."
# Closeness is measured using Cosine Similarity: dot(u, v) / (|u| * |v|)
# -----------------------------------------------------------------------------
def dot_product(v1, v2):
    return sum(a * b for a, b in zip(v1, v2))


def vector_norm(v):
    return math.sqrt(sum(a * a for a in v))


def cosine_similarity(v1, v2):
    norm1 = vector_norm(v1)
    norm2 = vector_norm(v2)
    if norm1 == 0 or norm2 == 0:
        return 0.0
    return dot_product(v1, v2) / (norm1 * norm2)


def euclidean_distance(v1, v2):
    return math.sqrt(sum((a - b) ** 2 for a, b in zip(v1, v2)))


# -----------------------------------------------------------------------------
# 4. Clip c4 & c5: "Take king. Subtract man. Add woman. And you land on queen."
# -----------------------------------------------------------------------------
def vector_add(v1, v2):
    return [a + b for a, b in zip(v1, v2)]


def vector_subtract(v1, v2):
    return [a - b for a, b in zip(v1, v2)]


def find_nearest_words(target_vector, top_k=5, exclude_words=None):
    """Find words with highest cosine similarity to target_vector."""
    exclude = set(exclude_words or [])
    scored = []
    for word, vec in EMBEDDINGS.items():
        if word in exclude:
            continue
        sim = cosine_similarity(target_vector, vec)
        dist = euclidean_distance(target_vector, vec)
        scored.append((word, sim, dist))
    scored.sort(key=lambda x: x[1], reverse=True)
    return scored[:top_k]


def main():
    print("=" * 68)
    print("🎬 DAY 2 SHORT: FROM NUMBERS TO MEANING (CODE DEMONSTRATION)")
    print("=" * 68)

    # 1. Token lookup
    token_id = VOCABULARY["king"]
    word, king_vector = lookup_embedding(token_id)
    print(f"\n[Clip c1] Token ID Lookup:")
    print(f"  Word: '{word}' -> Token ID: {token_id}")
    print(f"  Note: To the AI, integer {token_id} is just a table row index.")

    # 2. Unfold into vector
    print(f"\n[Clip c2] Unfolding into coordinates (Dimensions: {DIMENSIONS}):")
    print(f"  Vector({word}) = {king_vector}")
    print(f"  In production models (e.g. OpenAI ada-002 / text-embedding-3),")
    print(f"  this unfolds into 1,536 coordinates.")

    # 3. Distance & Clusters
    print(f"\n[Clip c3] Meaning becomes distance (Cosine Similarity):")
    sim_fruit = cosine_similarity(EMBEDDINGS["apple"], EMBEDDINGS["pear"])
    sim_royalty = cosine_similarity(EMBEDDINGS["king"], EMBEDDINGS["queen"])
    sim_mixed = cosine_similarity(EMBEDDINGS["apple"], EMBEDDINGS["king"])
    print(f"  🍎 apple  <->  🍐 pear   similarity: {sim_fruit:.4f} (Very close!)")
    print(f"  👑 king   <->  👸 queen  similarity: {sim_royalty:.4f} (Very close!)")
    print(f"  🍎 apple  <->  👑 king   similarity: {sim_mixed:.4f} (Far apart!)")

    # 4. Vector arithmetic
    print(f"\n[Clip c4 & c5] Vector Arithmetic: king - man + woman")
    v_king = EMBEDDINGS["king"]
    v_man = EMBEDDINGS["man"]
    v_woman = EMBEDDINGS["woman"]

    # king - man
    v_royalty = vector_subtract(v_king, v_man)
    # + woman
    v_result = vector_add(v_royalty, v_woman)

    print(f"  1. king           : {v_king}")
    print(f"  2. - man          : {[-x for x in v_man]}")
    print(f"  3. + woman        : {v_woman}")
    print(f"  -------------------------------------------------------------")
    print(f"  = target vector   : {[round(x, 4) for x in v_result]}")

    print(f"\nSearching nearest neighbors to target vector:")
    # We search nearest neighbors (excluding the input words as standard in word2vec evaluation)
    nearest_all = find_nearest_words(v_result, top_k=4, exclude_words=["man", "woman"])
    for rank, (nbr_word, sim, dist) in enumerate(nearest_all, start=1):
        crown_indicator = "👑 LANDED HERE!" if nbr_word == "queen" else ""
        print(f"  {rank}. {nbr_word:<8} (cosine similarity: {sim:.4f}, distance: {dist:.4f}) {crown_indicator}")

    print(f"\n[Clip c6] Teaser: 'How do these vectors talk to each other?'")
    print(f"  Static embeddings give 'bank' one fixed position.")
    print(f"  Attention (Transformers) lets 'river bank' pull context from 'river',")
    print(f"  while 'bank account' pulls context from 'account'!")
    print("=" * 68)


if __name__ == "__main__":
    main()
