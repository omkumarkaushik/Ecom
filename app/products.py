import json
from pathlib import Path
from typing import List, Dict

DATA_FILE = Path(__file__).parent.parent / 'data' / 'dummy.json'

def load_items() -> List[Dict]:
    if not DATA_FILE.exists():
        return [] 
    with open(DATA_FILE, 'r', encoding='utf-8') as file:
        items = json.load(file)
    return items.get("products", [])

def get_all_items() -> List[Dict]:
    return load_items()

def add_item(item: Dict) -> Dict:
    items = load_items()
    new_id = max([i.get('id', 0) for i in items], default=0) + 1
    
    # Create new item with id first
    new_item = {"id": new_id, **item}
    items.append(new_item)
    with open(DATA_FILE, 'w', encoding='utf-8') as file:
        json.dump({"products": items}, file, indent=4)
    return new_item

def delete_item(item_id: int) -> bool:
    items = load_items()
    initial_count = len(items)
    items = [i for i in items if i.get('id') != item_id]
    
    if len(items) == initial_count:
        return False  # Item not found
    
    with open(DATA_FILE, 'w', encoding='utf-8') as file:
        json.dump({"products": items}, file, indent=4)
    return True

def update_item(item_id: int, updated_data: Dict) -> Dict:
    items = load_items()
    for i, item in enumerate(items):
        if item.get('id') == item_id:
            items[i] = {"id": item_id, **updated_data}
            with open(DATA_FILE, 'w', encoding='utf-8') as file:
                json.dump({"products": items}, file, indent=4)
            return items[i]
    return None

