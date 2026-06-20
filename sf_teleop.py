#!/usr/bin/env python3
"""sf_teleop.py - simple WASD keyboard teleop for Red Team Hack Sim.

Low-level angle-rate + throttle control via drone.set_controls(). Works best on
Windows (uses GetAsyncKeyState so you can fly while the game window is focused).

Launch the sim first, then:
    python sf_teleop.py
    .\\run_client.ps1 sf_teleop.py

Controls (hold keys):
    W / S     pitch forward / back
    A / D     roll left / right
    Q / E     yaw left / right
    R / F     climb / descend (throttle)
    H         hover (zero rates, reset throttle)
    L         land, disarm, and exit
    Esc       quit (lands first if still armed)
"""
from __future__ import annotations

import argparse
import asyncio
import sys
import time

from redteam_sim import START_POSE, connect

# Default spawn matches sf_scene.jsonc / redteam_sim.START_POSE (NED metres).
DEFAULT_ALT_M = 5.0
HOVER_THROTTLE = 0.55
LOOP_HZ = 30

# Virtual-key codes (Windows).
VK = {
    "w": 0x57,
    "a": 0x41,
    "s": 0x53,
    "d": 0x44,
    "q": 0x51,
    "e": 0x45,
    "r": 0x52,
    "f": 0x46,
    "h": 0x48,
    "l": 0x4C,
    "esc": 0x1B,
}


def _key_down(vk: int) -> bool:
    """Return True while a key is held. Windows only."""
    if sys.platform != "win32":
        raise RuntimeError("sf_teleop.py currently supports Windows only.")
    import ctypes

    return bool(ctypes.windll.user32.GetAsyncKeyState(vk) & 0x8000)


async def _do(cmd):
    await (await cmd)


def _print_help(roll_rate: float, pitch_rate: float, yaw_rate: float, throttle_step: float):
    spawn = START_POSE["translation"]
    print(
        f">> teleop ready at start line NED "
        f"({spawn['x']}, {spawn['y']}, {spawn['z']}) — focus the game window and fly\n"
        "   W/S  pitch forward/back\n"
        "   A/D  roll left/right\n"
        "   Q/E  yaw left/right\n"
        "   R/F  climb/descend\n"
        "   H    hover   L land+quit   Esc quit\n"
        f"   rates: roll/pitch={roll_rate:.2f} rad/s  yaw={yaw_rate:.2f}  "
        f"throttle step={throttle_step:.3f}/frame\n"
    )


async def teleop(
    address: str,
    alt_m: float,
    climb_speed: float,
    roll_rate: float,
    pitch_rate: float,
    yaw_rate: float,
    throttle_step: float,
):
    client, _world, drone = connect(address)
    armed = False
    throttle = HOVER_THROTTLE

    try:
        print(">> connecting, arming, taking off")
        drone.enable_api_control()
        drone.arm()
        await _do(drone.takeoff_async())
        if alt_m > 0:
            y = START_POSE["translation"]["y"]
            await _do(drone.move_to_position_async(0.0, y, -alt_m, climb_speed))
        armed = True

        _print_help(roll_rate, pitch_rate, yaw_rate, throttle_step)
        dt = 1.0 / LOOP_HZ
    except Exception:
        client.disconnect()
        raise

    try:
        while True:
            if _key_down(VK["esc"]):
                print(">> Esc — landing")
                break

            if _key_down(VK["l"]):
                print(">> L — landing")
                break

            roll = pitch = yaw = 0.0
            if _key_down(VK["a"]):
                roll -= roll_rate
            if _key_down(VK["d"]):
                roll += roll_rate
            if _key_down(VK["w"]):
                pitch -= pitch_rate
            if _key_down(VK["s"]):
                pitch += pitch_rate
            if _key_down(VK["q"]):
                yaw -= yaw_rate
            if _key_down(VK["e"]):
                yaw += yaw_rate

            if _key_down(VK["h"]):
                roll = pitch = yaw = 0.0
                throttle = HOVER_THROTTLE

            if _key_down(VK["r"]):
                throttle = min(1.0, throttle + throttle_step)
            if _key_down(VK["f"]):
                throttle = max(0.0, throttle - throttle_step)

            drone.set_controls(roll, pitch, yaw, throttle)
            time.sleep(dt)
    except KeyboardInterrupt:
        print("\n>> interrupted — landing")
    finally:
        if armed:
            try:
                drone.cancel_last_task()
            except Exception:
                pass
            drone.set_controls(0.0, 0.0, 0.0, HOVER_THROTTLE)
            try:
                await _do(drone.hover_async())
                await _do(drone.land_async())
                drone.disarm()
            except Exception as exc:
                print(f">> land/disarm warning: {exc}")
        client.disconnect()
        print(">> done")


def main():
    if sys.platform != "win32":
        print("sf_teleop.py requires Windows (GetAsyncKeyState).", file=sys.stderr)
        sys.exit(1)

    ap = argparse.ArgumentParser(description="WASD keyboard teleop for Red Team Hack Sim.")
    ap.add_argument("--address", default="127.0.0.1", help="sim host (WSL2: Windows host IP)")
    ap.add_argument(
        "--alt",
        type=float,
        default=DEFAULT_ALT_M,
        help="climb to this altitude after takeoff (m); 0 = stay at takeoff height",
    )
    ap.add_argument("--climb-speed", type=float, default=3.0, help="m/s for initial climb")
    ap.add_argument("--roll-rate", type=float, default=0.9, help="rad/s when A/D held")
    ap.add_argument("--pitch-rate", type=float, default=0.9, help="rad/s when W/S held")
    ap.add_argument("--yaw-rate", type=float, default=0.7, help="rad/s when Q/E held")
    ap.add_argument("--throttle-step", type=float, default=0.02, help="R/F throttle change per frame")
    args = ap.parse_args()

    asyncio.run(
        teleop(
            args.address,
            args.alt,
            args.climb_speed,
            args.roll_rate,
            args.pitch_rate,
            args.yaw_rate,
            args.throttle_step,
        )
    )


if __name__ == "__main__":
    main()
