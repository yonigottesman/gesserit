# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "gesserit",
#     "lancedb",
#     "pylance",
#     "requests",
#     "tantivy",
# ]
# ///
import io
import json
import tempfile
import zipfile
from pathlib import Path

import lancedb
import requests

from gesserit import Gesserit, SearchItem

table = None


async def search_function(
    query: str = "How Phytates Fight Cancer Cells", limit: int = 10, return_score: bool = False
) -> list[SearchItem]:
    results = table.search(query, query_type="fts").limit(limit).to_list()
    if return_score:
        return [SearchItem(text=r["text"], metadata={"id": r["id"], "score": r["_score"]}) for r in results]
    else:
        return [SearchItem(text=r["text"], metadata={"id": r["id"]}) for r in results]


def build_index(temp_dir: str):
    global table
    nfcorpus_link = "https://public.ukp.informatik.tu-darmstadt.de/thakur/BEIR/datasets/nfcorpus.zip"

    zip_content = io.BytesIO(requests.get(nfcorpus_link).content)
    with zipfile.ZipFile(zip_content, "r") as zip_ref:
        zip_ref.extractall(temp_dir)
    nfcorpus_root = Path(temp_dir) / "nfcorpus"
    corpus_file = nfcorpus_root / "corpus.jsonl"

    data = []
    for jline in corpus_file.read_text().splitlines():
        j = json.loads(jline)
        data.append({"id": j["_id"], "title": j["title"], "text": j["text"]})

    db = lancedb.connect(Path(temp_dir) / "lancedb")
    table = db.create_table("nfcorpus", data=data)
    table.create_fts_index("text", use_tantivy=True)


def main():
    with tempfile.TemporaryDirectory() as temp_dir:
        build_index(temp_dir)
        app = Gesserit(search_function=search_function)
        app.run()


if __name__ == "__main__":
    main()
