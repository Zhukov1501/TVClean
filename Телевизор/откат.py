#!/usr/bin/env python3
"""Вернуть телевизор к снимку, снятому до оптимизации."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "tools"))

from tvopt import apply_actions, fetch_lists, load_snapshot, restore_actions  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Откат SSMART 43FSV22 к снимку")
    parser.add_argument("--host", default=os.environ.get("TV_HOST", ""))
    args = parser.parse_args(argv)

    snapshot = load_snapshot()
    if snapshot is None:
        print("Снимка нет: оптимизация телевизор ещё не меняла, откатывать нечего.")
        print("Когда снимок появится, он лежит в откат/снимок.json, а команды — в откат/ВЕРНУТЬ.sh.")
        return 0
    if not args.host:
        print("Снимок на месте. Чтобы вернуть его на телевизор:")
        print("  TV_HOST=192.168.50.65 python3 откат.py")
        print("Тот же возврат без Python: TV_HOST=192.168.50.65 sh откат/ВЕРНУТЬ.sh")
        return 2

    _enabled, current_disabled = fetch_lists(args.host)
    actions = restore_actions(snapshot["enabled"], snapshot["disabled"], current_disabled)
    if not actions:
        print("Телевизор уже совпадает со снимком.")
        return 0
    apply_actions(args.host, actions)
    print(f"Готово. Возвращено команд: {len(actions)}.")
    print("Выключите на телевизоре отладку по USB.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
