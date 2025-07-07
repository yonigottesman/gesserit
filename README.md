<div align="center">
  
# Gesserit

</div>

<div align="center">
  <img src="gesserit/static/gesserit.svg" alt="drawing" style="width:200px;"/>
</div>

A tiny utility to inspect retrieval results.

## Installation
Install `gesserit` from PyPI using your favorite package manager:

```bash
pip install gesserit
# or
uv add gesserit
```

## Usage

Create a search function that returns a list of `SearchItem` objects, then launch the web UI:

```python
from gesserit import Gesserit, SearchItem

def search_function(query: str, limit: int = 10, include_metadata: bool = False):
    # Your search implementation here
    return [
        SearchItem(text="chunk text 1", metadata={"id": "1"}), 
        SearchItem(text="chunk text 2", metadata={"id": "2"})
    ]

app = Gesserit(search_function=search_function)
app.run()  # Accepts any uvicorn parameters
```

## BEIR example
Run `uv run example.py` to see a simple example using `gesserit` to inspect retrieval results. This example demonstrates text search on the NFCorpus dataset using LanceDB full-text search.