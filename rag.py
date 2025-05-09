import re
from model import embed, index
from memory import get_preferences, add_preference

def format_matches(matches):
    if not matches:
        return "No cocktails found."

    lines = []
    for m in matches:
        metadata = m.get("metadata", {})
        name = metadata.get("name", "Unnamed")
        alcoholic = "alcoholic" if metadata.get("alcoholic", False) else "non-alcoholic"
        ingredients = ", ".join(metadata.get("ingredients", []))
        line = f"<strong>{name}</strong><br>Type: {alcoholic}<br>Ingredients: {ingredients}<br><br>"
        lines.append(line)

    return "\n".join(lines)

def find_cocktails_by_ingredient(ingredient):
    query_vector = embed(f"cocktails with {ingredient}")
    results = index.query(
        vector=query_vector,
        top_k=5,
        include_metadata=True
    )["matches"]

    return format_matches(results)

def recommend_by_favorites(favs):
    if not favs:
        return "You have no saved preferences yet. Try saying 'I love mint'."
    combined = embed(" ".join(favs))
    return format_matches(
        index.query(vector=combined, top_k=5, include_metadata=True).get("matches", [])
    )

def find_similar_by_name(name):
    print(f"[DEBUG] find_similar_by_name: looking for '{name}'")

    TOP_K = 6
    matches = index.query(
        vector=embed(name),
        top_k=TOP_K,
        include_metadata=True
    )["matches"]

    if not matches:
        return f"No cocktail found with the name '{name}'."

    target = matches[0]
    target_name = target["metadata"].get("name", "").strip().lower()
    target_id = target.get("id")

    vec = target.get("values") or target.get("vector")
    if vec is None:
        return "Could not extract vector of the original cocktail."

    SIMILAR_K = 10
    similar = index.query(
        vector=vec,
        top_k=SIMILAR_K,
        include_metadata=True
    )["matches"]

    filtered = []
    for m in similar:
        m_name = m["metadata"].get("name", "").strip().lower()
        if m.get("id") == target_id or m_name == target_name:
            continue
        filtered.append(m)
        if len(filtered) >= 5:
            break

    return format_matches(filtered)

def extract_ingredient_from_question(question):
    match = re.search(r'cocktails.*containing\s+([\w\s]+)', question.lower())
    if match:
        return match.group(1).strip()
    return None

def generate_answer(user_id, user_input):
    user_input_lower = user_input.lower()
    memories = get_preferences(user_id)

    print(f"[DEBUG] User query: {user_input}")

    match = re.search(
        r'similar to\s+["“”]?\s*([\w\s]+?)\s*["“”]?(?:\s|$)',
        user_input,
        re.IGNORECASE
    )
    if match:
        cocktail_name = match.group(1).strip()
        print(f"[DEBUG] Looking for cocktails similar to: '{cocktail_name}'")
        return find_similar_by_name(cocktail_name)

    ing = extract_ingredient_from_question(user_input)
    if ing:
        print(f"[DEBUG] Looking for cocktails with ingredient: {ing}")
        return find_cocktails_by_ingredient(ing)

    if "favourite" in user_input_lower or "favorite" in user_input_lower:
        return f"Your favourite ingredients are: {', '.join(memories)}." if memories else \
        "You have no saved preferences yet. Try saying 'I love mint'."

    if "recommend" in user_input_lower:
        print(f"[DEBUG] Recommending based on favorite ingredients.")
        return recommend_by_favorites(memories)

    match = re.search(r"i love ([\w\s]+)", user_input_lower)
    if match:
        ingredient = match.group(1).strip()
        add_preference(user_id, ingredient)
        return "Got it! I've saved your preference."

    return "I didn't understand your request. Try asking about cocktails with an ingredient or say 'I love [ingredient]'."
