import json
import time
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError


DATA_DIR = Path("data/raw")
DATA_DIR.mkdir(parents=True, exist_ok=True)


PEOPLE = [
    "Albert Einstein",
    "Marie Curie",
    "Leonardo da Vinci",
    "William Shakespeare",
    "Ada Lovelace",
    "Nikola Tesla",
    "Lionel Messi",
    "Cristiano Ronaldo",
    "Taylor Swift",
    "Frida Kahlo",
    "Isaac Newton",
    "Charles Darwin",
    "Galileo Galilei",
    "Wolfgang Amadeus Mozart",
    "Ludwig van Beethoven",
    "Pablo Picasso",
    "Martin Luther King Jr.",
    "Nelson Mandela",
    "Cleopatra",
    "Mahatma Gandhi",
]

PLACES = [
    "Eiffel Tower",
    "Great Wall of China",
    "Taj Mahal",
    "Grand Canyon",
    "Machu Picchu",
    "Colosseum",
    "Hagia Sophia",
    "Statue of Liberty",
    "Pyramids of Giza",
    "Mount Everest",
    "Big Ben",
    "Stonehenge",
    "Petra",
    "Acropolis of Athens",
    "Niagara Falls",
    "Burj Khalifa",
    "Sydney Opera House",
    "Angkor Wat",
    "Mount Fuji",
    "Louvre",
]


def load_existing(entity_type):
    output_path = DATA_DIR / f"{entity_type}.json"

    if not output_path.exists():
        return []

    try:
        with open(output_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def save_results(entity_type, results):
    output_path = DATA_DIR / f"{entity_type}.json"

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"Saved {len(results)} items to {output_path}")


def fetch_wikipedia(title, max_retries=5):
    params = {
        "action": "query",
        "format": "json",
        "prop": "extracts",
        "explaintext": "1",
        "redirects": "1",
        "titles": title,
    }

    url = "https://en.wikipedia.org/w/api.php?" + urlencode(params)

    headers = {
        "User-Agent": "LocalWikipediaRAG/1.0 (student project; localhost use)",
        "Accept": "application/json",
    }

    for attempt in range(max_retries):
        request = Request(url, headers=headers)

        try:
            with urlopen(request, timeout=30) as response:
                raw = response.read().decode("utf-8", errors="replace")
                data = json.loads(raw)

            pages = data.get("query", {}).get("pages", {})

            for page_id, page in pages.items():
                if page_id == "-1":
                    print(f"Failed: {title} - page not found")
                    return None

                text = page.get("extract", "").strip()
                page_title = page.get("title", title)

                if not text:
                    print(f"Failed: {title} - empty extract")
                    return None

                return {
                    "title": page_title,
                    "text": text,
                    "source": f"https://en.wikipedia.org/wiki/{page_title.replace(' ', '_')}",
                }

            print(f"Failed: {title} - no page returned")
            return None

        except HTTPError as e:
            if e.code == 429:
                wait_time = 10 * (attempt + 1)
                print(f"Rate limited for {title}. Waiting {wait_time} seconds...")
                time.sleep(wait_time)
                continue

            print(f"Failed: {title} - HTTP status {e.code}")
            return None

        except URLError as e:
            wait_time = 5 * (attempt + 1)
            print(f"Network error for {title}: {e.reason}. Waiting {wait_time} seconds...")
            time.sleep(wait_time)
            continue

        except Exception as e:
            print(f"Failed: {title} - unexpected error {e}")
            return None

    print(f"Failed: {title} - max retries exceeded")
    return None


def ingest_entities(entities, entity_type):
    results = load_existing(entity_type)
    existing_titles = {item["title"].lower() for item in results}

    print(f"Loaded {len(results)} existing {entity_type} items.")

    for name in entities:
        if name.lower() in existing_titles:
            print(f"Skipping existing item: {name}")
            continue

        print(f"Fetching {name}...")
        item = fetch_wikipedia(name)

        if item:
            item["type"] = entity_type
            results.append(item)
            existing_titles.add(item["title"].lower())
            save_results(entity_type, results)

        time.sleep(3)

    save_results(entity_type, results)


def main():
    ingest_entities(PEOPLE, "person")
    ingest_entities(PLACES, "place")


if __name__ == "__main__":
    main()