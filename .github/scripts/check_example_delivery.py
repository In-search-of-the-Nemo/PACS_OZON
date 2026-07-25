"""Проверяет, что сообщения из examples/send_status.py доходят до фронта.

Подключается к backend тем же Socket.IO, что и браузер (см. socketManager.ts),
и ждёт события, которые слушают компоненты:

    "status"            -> компонент Status   (statusTopic в status.ts)
    "update_telemetry"  -> компонент Telemetry (ключ status_feed)

Полный путь сообщения:
    send_status.py -> ether.*.xsub -> transnet (прокси) -> ether.*.xpub
                   -> serviz backend -> Socket.IO -> фронт

Требует запущенный стек (make up). Код возврата: 0 — обе доставки прошли, 1 — нет.
"""
import os
import subprocess
import sys
import threading
import time
from pathlib import Path

import socketio

REPO_ROOT = Path(__file__).resolve().parents[2]  # .github/scripts/<файл> -> корень репозитория
EXAMPLE = REPO_ROOT / "examples" / "send_status.py"

BACKEND_URL = "http://localhost:8100"
STATUS_EVENT = "status"
TELEMETRY_EVENT = "update_telemetry"
TELEMETRY_KEY = "status_feed"

CONNECT_TIMEOUT = int(os.environ.get("E2E_CONNECT_TIMEOUT", "90"))  # сек на подъём стека
ATTEMPTS = 5            # повторы примера: PUB/SUB теряет сообщение, если transnet ещё не поднял прокси
WAIT_PER_ATTEMPT = 6    # сек ожидания событий после каждой отправки

received = {}
got_all = threading.Event()


def _check_done():
    if STATUS_EVENT in received and TELEMETRY_EVENT in received:
        got_all.set()


def main() -> int:
    sio = socketio.Client()

    @sio.on(STATUS_EVENT)
    def _on_status(data):
        received.setdefault(STATUS_EVENT, data)
        _check_done()

    @sio.on(TELEMETRY_EVENT)
    def _on_telemetry(data):
        # backend шлёт update_telemetry постоянно; ждём тот, где есть наш ключ
        if isinstance(data, dict) and TELEMETRY_KEY in data:
            received.setdefault(TELEMETRY_EVENT, data)
            _check_done()

    # Ждём, пока backend начнёт принимать подключения
    deadline = time.time() + CONNECT_TIMEOUT
    while True:
        try:
            sio.connect(BACKEND_URL, wait_timeout=10)
            break
        except Exception as exc:
            if time.time() > deadline:
                print(f"FAIL: не удалось подключиться к {BACKEND_URL}: {exc}")
                return 1
            time.sleep(1)
    print(f"OK: подключились к {BACKEND_URL} как фронт")

    for attempt in range(1, ATTEMPTS + 1):
        result = subprocess.run(
            [sys.executable, str(EXAMPLE)],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            print(f"FAIL: {EXAMPLE.name} завершился с кодом {result.returncode}")
            print(result.stdout, result.stderr)
            sio.disconnect()
            return 1

        if got_all.wait(WAIT_PER_ATTEMPT):
            break
        print(f"  попытка {attempt}/{ATTEMPTS}: получено {sorted(received)}, повторяем")

    sio.disconnect()

    ok = True

    # --- событие status ---
    status = received.get(STATUS_EVENT)
    if status is None:
        print(f"FAIL: событие '{STATUS_EVENT}' не дошло до фронта")
        ok = False
    else:
        print(f"OK: получено '{STATUS_EVENT}': {status}")
        for field in ("status", "object", "categories"):
            if field not in status:
                print(f"FAIL: в '{STATUS_EVENT}' нет поля '{field}'")
                ok = False

    # --- телеметрия ---
    telemetry = received.get(TELEMETRY_EVENT)
    if telemetry is None:
        print(f"FAIL: телеметрия с ключом '{TELEMETRY_KEY}' не дошла до фронта")
        ok = False
    else:
        print(f"OK: получено '{TELEMETRY_EVENT}' с ключом '{TELEMETRY_KEY}'")

    print("PASSED" if ok else "FAILED")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
