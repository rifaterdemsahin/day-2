#!/usr/bin/env python3
"""Real-model version of the S2-X sandbox test (NOT run yet): vanity - pride + confidence with GloVe.

  pip install gensim
  python3 -I scripts/pride_vanity_real.py

Downloads the public GloVe 100-d vectors through gensim (about 130 MB, once) and prints the nearest words.
"""
import gensim.downloader as api

m = api.load("glove-wiki-gigaword-100")
tests = [(["vanity", "confidence"], ["pride"], "arrogance"), (["pride", "arrogance"], ["vanity"], "confidence"),
         (["pride", "flattery"], ["vanity"], "honor"), (["pride", "honor"], ["vanity"], "virtue"), (["king", "woman"], ["man"], "queen")]
for pos, neg, want in tests:
    top = m.most_similar(positive=pos, negative=neg, topn=5)
    print(("✅" if top[0][0] == want else "❌"), " + ".join(pos), "-", " - ".join(neg), "→", [(w, round(s, 2)) for w, s in top], "expected", want)
