import binascii
import os.path
import subprocess
import argparse
import logging
import threading
import traceback

import yaml
from pymcuprog.backend import SessionConfig
from pymcuprog.deviceinfo.memorynames import MemoryNames
from pymcuprog.toolconnection import ToolSerialConnection
from pymcuprog.backend import Backend

import pymcuprog.pymcuprog_errors
import serial.serialutil

logging.basicConfig(format="%(levelname)s [%(name)s] %(message)s", level=logging.WARNING)

logging.getLogger('pymcuprog.serialupdi.nvm').disabled = True
logging.getLogger('pymcuprog.serialupdi.link').disabled = True
logging.getLogger('pymcuprog.serialupdi.physical').disabled = True
logging.getLogger('pymcuprog.deviceinfo.deviceinfo').disabled = True
logging.getLogger('pymcuprog.serialupdi.application').disabled = True

all_ok = True


def write_to_device(device_type, serial_path, hexfile, expected_fuses):
    global all_ok

    def log(*args):
        print(f"[{serial_path}]", *args)

    for _ in range(6):
        try:
            sessionconfig = SessionConfig(device_type)
            # sessionconfig.interface_speed = 250000
            # sessionconfig.interface_speed = 115200
            transport = ToolSerialConnection(serial_path)

            log("Connecting...")
            backend = Backend()
            backend.connect_to_tool(transport)
            # sessionconfig.special_options = {"chip-erase-locked-device": True}
            backend.start_session(sessionconfig)

            log("Set fuses...")
            fu = backend.read_memory(MemoryNames.FUSES, 0, len(expected_fuses))
            current_fuses = fu[0].data
            print(binascii.hexlify(bytes(current_fuses)).decode("ascii"))
            print(binascii.hexlify(bytes(expected_fuses)).decode("ascii"))
            backend.write_memory(expected_fuses, MemoryNames.FUSES, 0)

            log("Erase...")
            backend.erase(MemoryNames.FLASH)
            log("Write...")
            backend.write_hex_to_target(hexfile)
            log("Verify...")
            ok = backend.verify_hex(hexfile)

            if ok:
                log("Releasing...")
                backend.release_from_reset()

                log("Done")
                return

        except pymcuprog.pymcuprog_errors.PymcuprogError as e:
            log(f"ERROR: {e}")
        except serial.serialutil.SerialException as e:
            log(f"ERROR: {e}")
        except:
            traceback.print_exc()
            log("Retrying...")

    log("Unable to flash")
    all_ok = False


def build_fuses_for_device(config):
    device_type = config["device"]

    if device_type == "attiny414":
        from fuses_attiny414 import build_fuses
        return build_fuses(config)
    elif device_type == "attiny1626":
        from fuses_attiny1626 import build_fuses
        return build_fuses(config)
    else:
        raise Exception("Unknown device type")


def main():
    def log(*args):
        print(f"[main]", *args)

    argparser = argparse.ArgumentParser()
    argparser.add_argument('app', type=str, metavar="HEX_PATH")
    argparser.add_argument('config', type=str, metavar="CONFIG_PATH")
    argparser.add_argument('device', type=str, nargs="+", metavar="DEVICE")
    argparser.add_argument('--rebuild', action="store_true")

    args = argparser.parse_args()

    hexfile = args.app
    config = read_yaml_file(args.config)

    device_type = config["device"]

    assert hexfile.endswith(".hex")
    assert device_type in ("attiny414", "attiny1626")

    expected_fuses = build_fuses_for_device(config)
    print("expected_fuses", expected_fuses)

    hex_name = os.path.splitext(os.path.basename(hexfile))[0]
    hex_dir = os.path.dirname(hexfile)

    if args.rebuild and os.path.exists(os.path.join(hex_dir, "CMakeCache.txt")):
        log("CMakeCache.txt found, recompiling...")
        subprocess.check_call(["make", hex_name], cwd=hex_dir)

    if not os.path.exists(hexfile):
        log("Hex file doesn't exist")
        exit(1)

    threads = [threading.Thread(target=write_to_device, args=(device_type, dev, hexfile, expected_fuses)) for dev in args.device]

    for th in threads:
        th.daemon = False
        th.start()

    try:
        for th in threads:
            th.join()
    except KeyboardInterrupt:
        import signal
        os.kill(os.getpid(), signal.SIGTERM)

    if not all_ok:
        log("!!! ERROR !!!")
        exit(10)


def read_yaml_file(path):
    with open(path, "rt") as f:
        return yaml.load(f, Loader=yaml.SafeLoader)


main()
