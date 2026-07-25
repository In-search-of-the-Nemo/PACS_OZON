import time
import zmq

# xsub-стороны каналов ether (из config.yml)
SIGNALS_URL = "ipc:///tmp/ether.signals.xsub"
TELEMETRY_URL = "ipc:///tmp/ether.telemetry.xsub"

ctx = zmq.Context()

signals = ctx.socket(zmq.PUB)
signals.connect(SIGNALS_URL)

telemetry = ctx.socket(zmq.PUB)
telemetry.connect(TELEMETRY_URL)

time.sleep(0.5)

# статус -> компонент Status
signals.send_json({
    "serviz": "status",
    "data": {
        "status": "ok",
        "object": {"length_mm": 312, "width_mm": 198, "height_mm": 74, "has_circle": True},
        "categories": {"Коробки": 128, "Пакеты": 67, "Негабарит": 4, "Брак": 2},
    },
})

# телеметрия -> компонент Telemetry (ключ = топик в выпадающем списке)
telemetry.send_json({
    "status_feed": "Объект #42\n  габариты: 312x198x74 мм\n  круг в сечении: да\n  категория: Коробки",
})

print("Отправлено")
