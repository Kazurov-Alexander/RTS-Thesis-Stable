import json
import os
from src.map.obstacles import Obstacle, MountainGroup, WaterGroup

SAVE_FILE = "savegame.json"  # один файл для сохранения

def save_game(player, enemies, obstacles):
    """Сохраняем состояние игры в JSON."""
    data = {
        "player": {
            "x": player.x,
            "y": player.y,
            "health": player.health
        },
        "enemies": [
            {"x": e.x, "y": e.y, "alive": e.alive}
            for e in enemies
        ],
        "obstacles": []
    }

    for o in obstacles:
        if hasattr(o, "x"):  # одиночный объект-препятствие
            data["obstacles"].append({
                "x": o.x,
                "y": o.y,
                "kind": getattr(o, "kind", None),
                "type": o.__class__.__name__
            })
        elif hasattr(o, "cells"):  # группы клеток (горы, вода)
            data["obstacles"].append({
                "cells": [list(c) for c in o.cells],  # кортежи → списки для JSON
                "type": o.__class__.__name__
            })

    with open(SAVE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print(f"Игра сохранена → {SAVE_FILE}")


def load_game():
    """Загружаем состояние игры из JSON."""
    if not os.path.exists(SAVE_FILE):
        print("Сохранение отсутствует.")
        return None

    if os.path.getsize(SAVE_FILE) == 0:
        print("Файл сохранения пуст.")
        return None

    with open(SAVE_FILE, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            print("Ошибка: повреждённый файл сохранения.")
            return None

    player_data = data.get("player", {})
    enemies_data = data.get("enemies", [])
    obstacles_data = data.get("obstacles", [])

    obstacles = []
    for saved in obstacles_data:
        if "x" in saved:
            obstacles.append(Obstacle(saved["x"], saved["y"], saved.get("kind", "tree-1")))
        elif "cells" in saved:
            cells = [tuple(c) for c in saved["cells"]]
            if saved["type"] == "MountainGroup":
                obstacles.append(MountainGroup(cells))
            elif saved["type"] == "WaterGroup":
                obstacles.append(WaterGroup(cells))

    return {
        "player": player_data,
        "enemies": enemies_data,
        "obstacles": obstacles
    }
