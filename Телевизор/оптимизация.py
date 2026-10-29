#!/usr/bin/env python3
"""Снять снимок телевизора и выключить только рекламу и очиститель.

По умолчанию телевизор не меняется: пишется снимок и файл отката.
Выключение начинается только с флагом --применить, и только после снимка.
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "tools"))

from tvopt import (  # noqa: E402
    apply_disables,
    classify,
    fetch_lists,
    parse_pm_list,
    plan_lines,
    write_snapshot,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Оптимизация SSMART 43FSV22")
    parser.add_argument("--host", default=os.environ.get("TV_HOST", ""), help="Адрес телевизора в домашней сети")
    parser.add_argument("--packages", help="Файл со списком package:имя, без подключения к телевизору")
    parser.add_argument("--применить", action="store_true", help="Выключить рекламу после записи снимка")
    args = parser.parse_args(argv)

    if args.packages:
        installed = parse_pm_list(Path(args.packages).read_text(encoding="utf-8"))
        print("\n".join(plan_lines(installed)))
        print("Это просмотр списка из файла. Телевизор не менялся, снимок не записан.")
        return 0

    if not args.host:
        print("Нужен адрес телевизора в вашей сети: TV_HOST=192.168.50.65 python3 оптимизация.py")
        print("Без этого флага телевизор не трогается.")
        return 2

    try:
        enabled, disabled = fetch_lists(args.host)
    except Exception as exc:
        print("Телевизор не ответил, поэтому на его экране ничего не появилось.")
        print("Сам телевизор не менялся.")
        print("Проверьте короткую строку адреса, она начинается с 192.168.")
        print("На телевизоре должна быть включена отладка по USB, компьютер и телевизор в одной сети.")
        print(exc)
        return 1
    installed = sorted(set(enabled) | set(disabled))
    print("\n".join(plan_lines(installed)))
    write_snapshot(enabled, disabled)
    print("Снимок записан: откат/снимок.json")
    print("Файл отката записан: откат/ВЕРНУТЬ.sh")
    turning_off = classify(enabled)["disable"]
    if not args.применить:
        print("Телевизор пока не изменён. Когда будете готовы:")
        print(f"  TV_HOST={args.host} python3 оптимизация.py --применить")
        return 0
    if not turning_off:
        print("Выключать нечего.")
        return 0
    try:
        apply_disables(args.host, turning_off)
    except Exception as exc:
        print("Остановка. Телевизор мог измениться частично. Верните снимок:")
        print(f"  TV_HOST={args.host} python3 откат.py")
        print(exc)
        return 1
    print("Реклама и очиститель выключены. Пульт, каналы и ваши программы не трогались.")
    print("Если что-то не так: TV_HOST=... python3 откат.py")
    print("После этого выключите на телевизоре отладку по USB.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
