
from enum import Enum
from typing import Dict

import zmq

from thread_proxy_switch import ThreadProxySwitch
import time

from argparse import ArgumentParser
import yaml

parser = ArgumentParser()
parser.add_argument("--config", default="config.yml")
args = parser.parse_args()

config = yaml.safe_load(open(args.config))

if config["ether"]["api_version"] != 3:
    raise Exception("Only Ether v3 is supported")

context = zmq.Context()

s_signals = context.socket(zmq.SUB)
s_signals.connect(config["ether"]["s_signals_pub_url"])
s_signals.setsockopt_string(zmq.SUBSCRIBE, '{"transnet":')
s_signals.setsockopt_string(zmq.SUBSCRIBE, "{'transnet':")

poller = zmq.Poller()
poller.register(s_signals, zmq.POLLIN)

s_signals_ctrl = context.socket(zmq.REQ)
s_draw_ctrl = context.socket(zmq.REQ)
s_telemetry_ctrl = context.socket(zmq.REQ)
s_geometry_ctrl = context.socket(zmq.REQ)


class PhantomCtrl(Enum):
    ETHER = 0
    PHANTOM = 1


def steer_send_cmd(sock: zmq.Socket, cmd: str):
    sock.send(cmd.encode())
    return sock.recv()


def ether_switch_handler(mode: PhantomCtrl):
    # steer_send_cmd(s_signals_ctrl, mode.name)
    steer_send_cmd(s_telemetry_ctrl, mode.name)
    steer_send_cmd(s_draw_ctrl, mode.name)


def setup_proxy():

    s_signals_ctrl.bind(config["transnet"]["s_signals_ctrl_url"])
    s_draw_ctrl.bind(config["transnet"]["s_draw_ctrl_url"])
    s_telemetry_ctrl.bind(config["transnet"]["s_telemetry_ctrl_url"])
    s_geometry_ctrl.bind(config["transnet"]["s_geometry_ctrl_url"])

    print("Setting up proxy")

    signals_proxy = ThreadProxySwitch(
        zmq.XSUB, zmq.XSUB, zmq.XPUB, zmq.XPUB, ctrl_type=zmq.REP
    )
    signals_proxy.bind_real(config["ether"]["s_signals_sub_url"])
    signals_proxy.bind_phantom(
        config["ether"]["s_signals_sub_url"] + config["ether"]["phantom_suffix"]
    )
    signals_proxy.bind_out(config["ether"]["s_signals_pub_url"])
    signals_proxy.bind_monitor(
        config["ether"]["s_signals_pub_url"] + config["ether"]["monitor_suffix"]
    )
    signals_proxy.connect_ctrl(config["transnet"]["s_signals_ctrl_url"])

    signals_proxy.start()

    print("Signal proxy UP")

    telemetry_proxy = ThreadProxySwitch(
        zmq.XSUB, zmq.XSUB, zmq.XPUB, zmq.XPUB, ctrl_type=zmq.REP
    )
    telemetry_proxy.bind_real(config["ether"]["s_telemetry_sub_url"])
    telemetry_proxy.bind_phantom(
        config["ether"]["s_telemetry_sub_url"] + config["ether"]["phantom_suffix"]
    )
    telemetry_proxy.bind_out(config["ether"]["s_telemetry_pub_url"])
    telemetry_proxy.bind_monitor(
        config["ether"]["s_telemetry_pub_url"] + config["ether"]["monitor_suffix"]
    )
    telemetry_proxy.connect_ctrl(config["transnet"]["s_telemetry_ctrl_url"])
    telemetry_proxy.start()

    print("Telemetry proxy UP")

    draw_proxy = ThreadProxySwitch(
        zmq.XSUB, zmq.XSUB, zmq.XPUB, zmq.XPUB, ctrl_type=zmq.REP
    )
    draw_proxy.bind_real(config["ether"]["s_draw_sub_url"])
    draw_proxy.bind_phantom(
        config["ether"]["s_draw_sub_url"] + config["ether"]["phantom_suffix"]
    )
    draw_proxy.bind_out(config["ether"]["s_draw_pub_url"])
    draw_proxy.bind_monitor(
        config["ether"]["s_draw_pub_url"] + config["ether"]["monitor_suffix"]
    )
    draw_proxy.connect_ctrl(config["transnet"]["s_draw_ctrl_url"])
    draw_proxy.start()

    print("Draw proxy UP")

    geometry_proxy = ThreadProxySwitch(
        zmq.XSUB, zmq.XSUB, zmq.XPUB, zmq.XPUB, ctrl_type=zmq.REP
    )
    geometry_proxy.bind_real(config["ether"]["s_geometry_sub_url"])
    geometry_proxy.bind_phantom(
        config["ether"]["s_geometry_sub_url"] + config["ether"]["phantom_suffix"]
    )
    geometry_proxy.bind_out(config["ether"]["s_geometry_pub_url"])
    geometry_proxy.bind_monitor(
        config["ether"]["s_geometry_pub_url"] + config["ether"]["monitor_suffix"]
    )
    geometry_proxy.connect_ctrl(config["transnet"]["s_geometry_ctrl_url"])
    geometry_proxy.start()

    print("Geometry proxy UP")

    ether_switch_handler(PhantomCtrl.ETHER)

    print("Proxy UP")


def proxy_ctrl_handler(signal: Dict):
    signal_type = signal["transnet"]

    if signal_type == "ether_select":
        print("Ether select")
        ether_switch_handler(PhantomCtrl.ETHER)
        return True
    elif signal_type == "phantom_select":
        print("Phantom select")
        ether_switch_handler(PhantomCtrl.PHANTOM)
        return True

    return False


if __name__ == "__main__":

    print("Enter Transnet")

    setup_proxy()

    print("Transnet ready")
    while True:
        for _ in range(100):
            try:
                socks = dict(poller.poll(timeout=0))
            except KeyboardInterrupt:
                break

            if socks == {}:
                break

            if s_signals in socks:
                signal = s_signals.recv_json()
                if proxy_ctrl_handler(signal):
                    continue

                print("Invalid signal: ", signal)

        time.sleep(0.001)
