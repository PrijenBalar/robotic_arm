"""
boot.py  —  runs automatically before main.py on every boot
============================================================
Brings the network up robustly (station WiFi with AP fallback, via netboot.py)
so the arm is reachable on a cold boot WITHOUT Thonny.

DEV-SAFE INTERRUPT WINDOW:
  Before the (blocking) WiFi bring-up there is a short window where Ctrl-C
  skips networking entirely.  Thonny / mpremote send Ctrl-C on connect, so the
  board never becomes hard to reach over USB — without this, a blocking boot.py
  can wedge the REPL.  On a normal standalone boot nothing interrupts, the
  window elapses, and the network comes up automatically.

main.py reuses whatever interface this establishes via `netboot.iface`; if the
window was skipped, main.py brings the network up itself.
"""

import time

_skip = False
try:
    print("[boot] network bring-up in 2s  (Ctrl-C to skip for REPL access)...")
    time.sleep(2)
except KeyboardInterrupt:
    _skip = True
    print("[boot] network bring-up SKIPPED (Ctrl-C)")

if not _skip:
    try:
        import netboot
        netboot.bring_up_network()
    except KeyboardInterrupt:
        print("[boot] network bring-up interrupted")
    except Exception as e:
        print("[boot] network error:", e)

import gc
gc.collect()
