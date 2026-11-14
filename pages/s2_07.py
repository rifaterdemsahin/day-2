"""S2-07 Captions, title, description page: build() writes the page. Data: assets/short.json."""
from pages._lib import *  # noqa: F401,F403


def build():
    st = step_by_code("S2-07")
    m = D["metadata"]
    cards = "".join(f'<div class="card"><b>{lab}</b><p>{E(m[k])}</p>{copybtn(m[k])}{fb("S2-07." + k, lab)}</div>'
                    for k, lab in [("title", "🏷️ Title"), ("description", "📄 Description"), ("tags", "#️⃣ Hashtags"), ("pinned", "📌 Pinned comment")])
    body = step_head(st) + cards
    page("s2-07.html", "S2-07 Metadata", body)
