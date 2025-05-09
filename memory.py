user_memories = {}

def add_preference(user_id: str, ingredient: str):
    if user_id not in user_memories:
        user_memories[user_id] = []
    if ingredient.lower() not in user_memories[user_id]:
        user_memories[user_id].append(ingredient.lower())

def get_preferences(user_id: str):
    return user_memories.get(user_id, [])