import asyncio
import os
from navigation import BrowserManager


async def debug_elements():
    bm = BrowserManager()
    path = "file://" + os.path.abspath("test_site.html")
    print(f"Debug: Navigating to {path}")
    await bm.start(path)

    # Aguarda um pouco para garantir que o Shadow DOM e outros scripts carreguem
    await asyncio.sleep(2)

    elements = await bm.get_interactive_elements()
    print(f"Debug: Found {len(elements)} elements")
    for i, e in enumerate(elements):
        print(f"{i}: [{e['tag']}] '{e['text']}' - Priority: {e.get('priority', 'N/A')}")

    await bm.close()


if __name__ == "__main__":
    asyncio.run(debug_elements())
