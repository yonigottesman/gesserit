# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "duckduckgo-search",
#     "gesserit",
# ]
# ///

from duckduckgo_search import DDGS

from gesserit import Gesserit, SearchItem


async def search_function(
    query: str,
    max_results: int = 10,
) -> list[SearchItem]:
    results = DDGS().text(query, max_results=max_results)
    return [SearchItem(text=r["body"], metadata={"href": r["href"]}) for r in results]


if __name__ == "__main__":
    app = Gesserit(search_function=search_function)
    app.run()
