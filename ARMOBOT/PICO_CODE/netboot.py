"""
netboot.py  —  Robust network bring-up for the Pico W arm (station + AP fallback)
=================================================================================
Single source of truth for the arm's WiFi.  Called once from boot.py at cold
boot; main.py reuses the established interface via `netboot.iface` (and brings
it up itself when main.py is run directly, e.g. from Thonny where boot.py does
not run).

Robustness vs. the old single-shot connect:
  - several attempts per network, with a clean radio reset between tries;
  - fast-fail on hard errors (wrong password / AP not found) instead of
    burning the whole timeout;
  - always ends with a reachable interface — station if possible, else the
    AP fallback at 192.168.4.1.

Edit the SSIDs / static IP / AP credentials HERE (not in main.py).
"""

import network
import time

# ── Access Point credentials (fallback when station WiFi is unreachable) ─────
AP_SSID     = 'RoboticArm_AP'
AP_PASSWORD = '12345678'
AP_IP       = '192.168.4.1'

# ── Station WiFi networks — tried in order:
# (ssid, password, static_ifconfig, bssid).
# static_ifconfig = (ip, netmask, gateway, dns), or None for DHCP.
# bssid = 6-byte AP MAC to pin, or None to join by SSID alone.
#
# 'RoboticArm_PC' — Windows Mobile Hotspot on the control PC (started by
# scripts/start_hotspot.ps1).  Static IP keeps the arm at 192.168.137.50.
#
# BSSID pin (added 2026-07-16): a SECOND access point broadcasts the same
# SSID + password (impostor BSSID 92:c7:d3:c4:ef:8e, ch 9) and often wins on
# signal strength; joining it gives "connected" with the static IP but the
# control PC is unreachable.  Pinning the PC hotspot's BSSID
# (26:4e:f6:88:98:6f = MAC of the "Local Area Connection* 10" virtual
# adapter) forces the right AP.  If the PC's hotspot MAC ever changes, the
# pinned join fails and the arm drops to AP fallback — update the bytes here.
#
# NOTE: 'ARS' (router 2.4 GHz) was intentionally removed.  It is the only other
# reachable network, and it has client isolation (arm unreachable on it), so it
# would pre-empt the AP fallback.  With only the hotspot listed, the arm falls
# straight to AP mode (192.168.4.1) whenever the hotspot is off.
WIFI_NETWORKS = [
    ('RoboticArm_PC', '12345678',
     ('192.168.137.50', '255.255.255.0', '192.168.137.1', '192.168.137.1'),
     b'\x26\x4e\xf6\x88\x98\x6f'),
]
WIFI_TIMEOUT_S = 8     # per-attempt join timeout (s)
WIFI_ATTEMPTS  = 2     # attempts per network before moving to the next

# Optional captive-portal DNS for AP mode
try:
    from microDNSSrv import MicroDNSSrv
    DNS_AVAILABLE = True
except Exception:
    DNS_AVAILABLE = False

# ── established state (read by main.py) ──────────────────────────────────────
iface = None      # active network.WLAN interface, or None
mode  = None      # 'sta' | 'ap' | None


def _try_station():
    """Try every known network, WIFI_ATTEMPTS each. Return a connected wlan or None."""
    wlan = network.WLAN(network.STA_IF)
    for ssid, password, static_cfg, bssid in WIFI_NETWORKS:
        for attempt in range(1, WIFI_ATTEMPTS + 1):
            try:
                wlan.active(False)         # clean radio reset before each attempt
                time.sleep_ms(200)
                wlan.active(True)
                wlan.config(pm=0xa11140)   # disable WiFi power-save (server must stay reachable)
                if static_cfg:
                    wlan.ifconfig(static_cfg)
                print("[net] '%s' attempt %d/%d ..." % (ssid, attempt, WIFI_ATTEMPTS))
                wlan.connect(ssid, password, bssid=bssid)
                deadline = time.ticks_add(time.ticks_ms(), WIFI_TIMEOUT_S * 1000)
                while time.ticks_diff(deadline, time.ticks_ms()) > 0:
                    if wlan.isconnected():
                        print("[net] connected to '%s'  IP %s" % (ssid, wlan.ifconfig()[0]))
                        return wlan
                    try:
                        if wlan.status() < 0:   # wrong password / AP not found -> fast retry
                            break
                    except Exception:
                        pass
                    time.sleep_ms(250)
            except Exception as e:
                print("[net] error joining '%s': %s" % (ssid, e))
            try:
                wlan.disconnect()
            except Exception:
                pass
        print("[net] gave up on '%s'" % ssid)
    try:
        wlan.active(False)
    except Exception:
        pass
    return None


def _start_ap(keep_sta=False):
    """Bring up the Access Point. Return the AP interface.

    keep_sta=False — fallback mode: station radio is switched off first and
      captive DNS starts, so a phone/laptop joining the AP gets the arm
      without typing an IP.
    keep_sta=True — dual mode: the AP comes up ALONGSIDE the connected
      station (cyw43 supports concurrent STA+AP), so the arm is reachable
      both via the PC hotspot (192.168.137.50) and directly at 192.168.4.1.
      Captive DNS is skipped in this mode.
    """
    if not keep_sta:
        try:
            network.WLAN(network.STA_IF).active(False)   # free the radio for AP
        except Exception:
            pass
    ap = network.WLAN(network.AP_IF)
    ap.active(True)
    ap.ifconfig((AP_IP, '255.255.255.0', AP_IP, AP_IP))
    ap.config(essid=AP_SSID, password=AP_PASSWORD)
    deadline = time.ticks_add(time.ticks_ms(), 5000)
    while not ap.active() and time.ticks_diff(deadline, time.ticks_ms()) > 0:
        time.sleep_ms(100)
    print("[net] AP '%s' active  IP %s" % (AP_SSID, ap.ifconfig()[0]))
    if DNS_AVAILABLE and not keep_sta:
        try:
            if MicroDNSSrv.Create({"*": AP_IP}):
                print("[net] captive DNS started")
        except Exception as e:
            print("[net] DNS start failed:", e)
    return ap


def bring_up_network(force=False):
    """
    Robust station-with-AP-fallback.  Idempotent: returns the existing
    connection unless force=True.  Stores the result in module globals
    `iface` / `mode`.  Returns (iface, mode).
    """
    global iface, mode
    if iface is not None and not force:
        if mode == 'sta':
            try:
                if iface.isconnected():
                    return iface, mode
            except Exception:
                pass
        else:
            return iface, mode
    wlan = _try_station()
    if wlan is not None:
        iface, mode = wlan, 'sta'
        # Dual mode: keep the direct-connect AP up alongside the station link
        # so a laptop/phone can always reach the arm at 192.168.4.1 even while
        # it is on the PC hotspot.
        try:
            _start_ap(keep_sta=True)
        except Exception as e:
            print("[net] dual-mode AP failed:", e)
    else:
        print("[net] station WiFi unreachable — starting AP fallback")
        iface, mode = _start_ap(), 'ap'
    return iface, mode
