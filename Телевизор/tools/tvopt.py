"""Оптимизация SSMART 43FSV22 и откат к снимку.

Скрипт ничего не удаляет. Выключает только рекламу и встроенный очиститель,
если они есть на телевизоре. Пульт, каналы, магазин, главный экран, YouTube,
Netflix, Кинопоиск, Музыка и Happ остаются. Перед первым выключением пишется
снимок, из которого откат возвращает прежнее состояние.
"""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SNAPSHOT_DIR = ROOT / "откат"
SNAPSHOT_PATH = SNAPSHOT_DIR / "снимок.json"
ROLLBACK_SH = SNAPSHOT_DIR / "ВЕРНУТЬ.sh"

PACKAGE_RE = re.compile(r"^[A-Za-z][A-Za-z0-9_]*(\.[A-Za-z0-9_]+)+$")

# То, что просили оставить, и то, без чего эта плата не показывает картинку,
# не переключает HDMI и не слушает пульт. Совпадает с тем, что на соседней
# прошивке Hi3751V352E оставляли включённым.
KEEP_EXACT = {
    "android",
    "com.android.vending",
    "com.android.settings",
    "com.android.tv.settings",
    "com.android.systemui",
    "com.android.shell",
    "com.android.bluetooth",
    "com.google.android.gms",
    "com.google.android.gsf",
    "com.google.android.katniss",
    "com.google.android.apps.mediashell",
    "com.google.android.youtube",
    "com.google.android.youtube.tv",
    "com.netflix.ninja",
    "com.netflix.mediaclient",
    "ru.kinopoisk",
    "ru.kinopoisk.tv",
    "ru.yandex.music",
    "com.happproxy",
    "com.cvte.tv.launcher",
    "com.cvte.tv.launcher.space",
    "com.cvte.tv.launcher.space.skin",
    "com.cvte.tv.setting",
    "com.cvte.tv.globalui",
    "com.cvte.tvservice",
    "com.cvte.tv.api.impl",
    "com.cvte.settings",
    "com.cvte.tv.media",
    "com.cvte.tv.systemupgrade",
    "com.cvte.tv.ucservice",
    "com.cvte.tv.weather",
    "com.hisilicon.rmservice",
    "com.hisilicon.higallery",
    "com.hisilicon.miracast",
    "com.vendor.vnaudiomanager",
    "com.maxhub.screenshare.server.tv",
    "com.screenshare.platform",
    "com.cvte.dssshare.dlna",
    "com.stark.store",
}

KEEP_PREFIXES = (
    "com.android.",
    "com.google.android.gms",
    "com.google.android.gsf",
    "com.google.android.overlay",
    "com.google.android.permission",
    "com.google.android.packageinstaller",
    "com.google.android.ext.",
    "com.google.android.setup",
    "com.google.android.youtube",
    "com.google.android.apps.tv.launcher",
    "com.google.android.tvlauncher",
    "com.google.android.leanbacklauncher",
    "com.netflix.",
    "ru.kinopoisk",
    "ru.yandex.",
    "com.yandex.",
    "com.happproxy",
    "com.cvte.tv.launcher",
    "com.cvte.tv.setting",
    "com.cvte.tv.globalui",
    "com.cvte.tvservice",
    "com.cvte.tv.api",
    "com.cvte.tv.media",
    "com.cvte.tv.systemupgrade",
    "com.cvte.dssshare",
    "com.hisilicon.rmservice",
    "com.maxhub.",
    "com.screenshare.",
)

# Только то, что на соседней прошивке той же платы было рекламой или очистителем.
# Погоды, магазина платы, Miracast и главного экрана здесь нет.
CANDIDATES = {
    "com.cvte.gaia.ad.service": "реклама на главном экране",
    "com.cvte.wonder.cloud.service": "рекламная служба",
    "com.cvte.industries": "рекламные сообщения",
    "com.cvte.tv.pictorial": "заставка с рекламой",
    "com.cvte.tv.steward": "встроенный очиститель",
    "com.google.android.feedback": "отправка отзывов",
}

def valid_package(name: str) -> bool:
    return bool(PACKAGE_RE.fullmatch(name))


def is_factory(name: str) -> bool:
    lowered = name.lower()
    if "factory" in lowered or ".fac." in lowered or lowered.endswith(".fac") or "fac.menu" in lowered:
        return True
    return lowered.endswith(".at") and lowered.startswith(("com.cvte.", "cn.cvte."))


def decide(name: str) -> str:
    """keep, disable или leave. keep всегда побеждает disable."""
    if not valid_package(name) or is_factory(name):
        return "keep" if valid_package(name) else "leave"
    if name in KEEP_EXACT or name.startswith(KEEP_PREFIXES):
        return "keep"
    if name in CANDIDATES:
        return "disable"
    return "leave"


def classify(packages: list[str]) -> dict[str, list[str]]:
    groups = {"keep": [], "disable": [], "leave": []}
    for name in packages:
        groups[decide(name)].append(name)
    for key in groups:
        groups[key].sort()
    return groups


def parse_pm_list(text: str) -> list[str]:
    names = []
    for line in text.splitlines():
        line = line.strip()
        if line.startswith("package:"):
            name = line.split(":", 1)[1].strip()
            if valid_package(name):
                names.append(name)
    return sorted(set(names))


def restore_actions(enabled: list[str], disabled: list[str], current_disabled: list[str]) -> list[tuple[str, str]]:
    """Команды, которые возвращают снимок. Пара: (enable|disable, пакет)."""
    current = set(current_disabled)
    was_enabled = set(enabled)
    was_disabled = set(disabled)
    actions: list[tuple[str, str]] = []
    for name in sorted(was_enabled & current):
        if valid_package(name):
            actions.append(("enable", name))
    for name in sorted(was_disabled - current):
        if valid_package(name) and not is_factory(name):
            actions.append(("disable", name))
    return actions


def pm_command(kind: str, name: str) -> str:
    if not valid_package(name):
        raise ValueError(name)
    if kind == "enable":
        return f"pm enable --user 0 {name}"
    if kind == "disable":
        return f"pm disable-user --user 0 {name}"
    raise ValueError(kind)


def render_rollback_script(enabled: list[str], disabled: list[str]) -> str:
    lines = [
        "#!/bin/sh",
        "# Возвращает телевизор к снимку, снятому до оптимизации.",
        "# Ничего не удаляет и не ставит. Заводские меню не открывает.",
        "# Запуск из папки проекта: TV_HOST=192.168.50.65 sh откат/ВЕРНУТЬ.sh",
        "set -eu",
        'if [ -z "${TV_HOST:-}" ]; then',
        '  echo "Напишите адрес телевизора: TV_HOST=192.168.x.x sh откат/ВЕРНУТЬ.sh"',
        "  exit 1",
        "fi",
        'ROOT=$(CDPATH= cd -- "$(dirname "$0")/.." && pwd)',
        'if [ -x "$ROOT/platform-tools/adb" ]; then ADB="$ROOT/platform-tools/adb"',
        'elif [ -x "$ROOT/adb" ]; then ADB="$ROOT/adb"',
        "else ADB=adb; fi",
        'SERIAL="$TV_HOST"',
        'case "$SERIAL" in *:*) ;; *) SERIAL="$SERIAL:5555" ;; esac',
        '"$ADB" connect "$SERIAL"',
        "run() {",
        '  "$ADB" -s "$SERIAL" shell "$1"',
        "}",
    ]
    for name in sorted(set(enabled)):
        if valid_package(name):
            lines.append(f"run '{pm_command('enable', name)}'")
    for name in sorted(set(disabled)):
        if valid_package(name) and not is_factory(name):
            lines.append(f"run '{pm_command('disable', name)}'")
    lines.append('echo "Готово: пакеты возвращены к снимку."')
    lines.append("")
    return "\n".join(lines)


def write_snapshot(enabled: list[str], disabled: list[str]) -> None:
    SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "device": "SSMART 43FSV22",
        "enabled": sorted(set(enabled)),
        "disabled": sorted(set(disabled)),
    }
    SNAPSHOT_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    ROLLBACK_SH.write_text(render_rollback_script(payload["enabled"], payload["disabled"]), encoding="utf-8")
    ROLLBACK_SH.chmod(0o755)


def load_snapshot() -> dict[str, list[str]] | None:
    if not SNAPSHOT_PATH.exists():
        return None
    data = json.loads(SNAPSHOT_PATH.read_text(encoding="utf-8"))
    return {"enabled": list(data["enabled"]), "disabled": list(data["disabled"])}


def adb_program() -> str:
    for candidate in (
        ROOT / "platform-tools" / "adb",
        ROOT / "platform-tools" / "adb.exe",
        ROOT / "adb",
        ROOT / "adb.exe",
    ):
        if candidate.is_file():
            return str(candidate)
    return "adb"


def adb_serial(host: str) -> str:
    host = host.strip()
    if ":" not in host:
        return f"{host}:5555"
    return host


def adb_shell(host: str, command: str) -> str:
    serial = adb_serial(host)
    adb = adb_program()
    subprocess.run([adb, "connect", serial], check=False, timeout=20, capture_output=True, text=True)
    result = subprocess.run(
        [adb, "-s", serial, "shell", command],
        check=False,
        timeout=60,
        capture_output=True,
        text=True,
    )
    output = ((result.stdout or "") + (result.stderr or "")).strip()
    if result.returncode != 0:
        raise RuntimeError(output or f"adb завершился с кодом {result.returncode}")
    return output + ("\n" if output else "")


def fetch_lists(host: str) -> tuple[list[str], list[str]]:
    installed = parse_pm_list(adb_shell(host, "pm list packages"))
    disabled = parse_pm_list(adb_shell(host, "pm list packages -d"))
    enabled = [name for name in installed if name not in set(disabled)]
    return enabled, disabled


def plan_lines(installed: list[str]) -> list[str]:
    groups = classify(installed)
    lines = ["Будут выключены, если стоят на телевизоре:"]
    if groups["disable"]:
        for name in groups["disable"]:
            lines.append(f"  {name} — {CANDIDATES[name]}")
    else:
        lines.append("  ничего из рекламного списка на телевизоре нет")
    lines.append("Остаются ваши программы, пульт, каналы, HDMI, магазин и главный экран.")
    lines.append("Всё остальное скрипт не трогает: для этой модели это не мусор, пока не доказано обратное.")
    return lines


def apply_disables(host: str, names: list[str]) -> None:
    for name in names:
        if decide(name) != "disable":
            raise RuntimeError(f"отказ выключать {name}")
        output = adb_shell(host, pm_command("disable", name))
        if "SecurityException" in output or "not found" in output.lower():
            raise RuntimeError(output.strip() or name)


def apply_actions(host: str, actions: list[tuple[str, str]]) -> None:
    for kind, name in actions:
        adb_shell(host, pm_command(kind, name))
