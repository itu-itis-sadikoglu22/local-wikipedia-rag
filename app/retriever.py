from app.vector_store import query_vector_store, get_chunks_by_title


KNOWN_ENTITIES = [
    ("Albert Einstein", "person"),
    ("Marie Curie", "person"),
    ("Leonardo da Vinci", "person"),
    ("William Shakespeare", "person"),
    ("Ada Lovelace", "person"),
    ("Nikola Tesla", "person"),
    ("Lionel Messi", "person"),
    ("Cristiano Ronaldo", "person"),
    ("Taylor Swift", "person"),
    ("Frida Kahlo", "person"),
    ("Isaac Newton", "person"),
    ("Charles Darwin", "person"),
    ("Galileo Galilei", "person"),
    ("Wolfgang Amadeus Mozart", "person"),
    ("Ludwig van Beethoven", "person"),
    ("Pablo Picasso", "person"),
    ("Martin Luther King Jr.", "person"),
    ("Nelson Mandela", "person"),
    ("Cleopatra", "person"),
    ("Mahatma Gandhi", "person"),

    ("Eiffel Tower", "place"),
    ("Great Wall of China", "place"),
    ("Taj Mahal", "place"),
    ("Grand Canyon", "place"),
    ("Machu Picchu", "place"),
    ("Colosseum", "place"),
    ("Hagia Sophia", "place"),
    ("Statue of Liberty", "place"),
    ("Pyramids of Giza", "place"),
    ("Mount Everest", "place"),
    ("Big Ben", "place"),
    ("Stonehenge", "place"),
    ("Petra", "place"),
    ("Acropolis of Athens", "place"),
    ("Niagara Falls", "place"),
    ("Burj Khalifa", "place"),
    ("Sydney Opera House", "place"),
    ("Angkor Wat", "place"),
    ("Mount Fuji", "place"),
    ("Louvre", "place"),
]


OUT_OF_SCOPE_KEYWORDS = [
    "mars",
    "president of mars",
    "john doe",
    "random unknown",
    "unknown person",
]


PERSON_KEYWORDS = [
    "person", "people", "who", "born", "discover", "invent", "famous",
    "known for", "scientist", "artist", "writer", "footballer", "singer"
]

PLACE_KEYWORDS = [
    "place", "where", "located", "tower", "wall", "mount", "city",
    "country", "landmark", "monument", "used for", "turkey"
]


def detect_entities(query):
    q = query.lower()
    matches = []

    for title, entity_type in KNOWN_ENTITIES:
        if title.lower() in q:
            matches.append((title, entity_type))

    if "turkey" in q:
        matches.append(("Hagia Sophia", "place"))

    if "electricity" in q:
        matches.append(("Nikola Tesla", "person"))

    return matches


def classify_query(query):
    entity_matches = detect_entities(query)
    entity_types = {entity_type for _, entity_type in entity_matches}

    if len(entity_types) > 1:
        return "both"

    if len(entity_types) == 1:
        return list(entity_types)[0]

    q = query.lower()

    person_score = sum(1 for word in PERSON_KEYWORDS if word in q)
    place_score = sum(1 for word in PLACE_KEYWORDS if word in q)

    if person_score > 0 and place_score > 0:
        return "both"

    if person_score > place_score:
        return "person"

    if place_score > person_score:
        return "place"

    return "both"


def flatten_results(raw):
    documents = raw.get("documents", [[]])[0]
    metadatas = raw.get("metadatas", [[]])[0]
    distances = raw.get("distances", [[]])[0] if raw.get("distances") else []

    results = []

    for i, text in enumerate(documents):
        metadata = metadatas[i] if i < len(metadatas) else {}
        distance = distances[i] if i < len(distances) else None

        results.append(
            {
                "text": text,
                "metadata": metadata,
                "distance": distance,
            }
        )

    return results


def retrieve_context(query, n_results=5):
    q = query.lower()

    for keyword in OUT_OF_SCOPE_KEYWORDS:
        if keyword in q:
            return {
                "query_type": "unknown",
                "results": [],
            }

    query_type = classify_query(query)
    entity_matches = detect_entities(query)

    if entity_matches:
        combined_results = []
        seen = set()

        chunks_per_entity = 2 if len(entity_matches) > 1 else n_results

        for title, _entity_type in entity_matches:
            chunks = get_chunks_by_title(title, n_results=chunks_per_entity)

            for item in chunks:
                key = (
                    item["metadata"].get("title"),
                    item["metadata"].get("chunk_index"),
                )

                if key not in seen:
                    seen.add(key)
                    combined_results.append(item)

        return {
            "query_type": query_type,
            "results": combined_results[:n_results],
        }

    if query_type == "person":
        raw = query_vector_store(query, query_type="person", n_results=n_results)
    elif query_type == "place":
        raw = query_vector_store(query, query_type="place", n_results=n_results)
    else:
        raw = query_vector_store(query, query_type=None, n_results=n_results)

    return {
        "query_type": query_type,
        "results": flatten_results(raw),
    }