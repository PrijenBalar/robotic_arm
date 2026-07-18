==================================================
 PICO_CODE - files that live ON the Pico W
==================================================

Files (all four must be on the Pico):
  boot.py                  runs first at power-on: 2s Ctrl-C window, then WiFi
  netboot.py               WiFi logic (hotspot "RoboticArm_PC", AP fallback)
  main.py                  the arm program: HTTP :80 + TCP jog bridge :81,
                           debounced limit switches, calibration, gripper
  lib\stepper\__init__.py  stepper driver (timers off while idle)

These are ALREADY uploaded to the Pico. Nothing runs from this folder -
the Pico starts everything automatically at power-on.

--------------------------------------------------
 HOW TO RE-UPLOAD (only after changing the code)
--------------------------------------------------
Close Thonny first! Then in a terminal:

  python -m mpremote connect COM14 fs cp main.py :main.py
  python -m mpremote connect COM14 fs cp boot.py :boot.py
  python -m mpremote connect COM14 fs cp netboot.py :netboot.py
  python -m mpremote connect COM14 fs cp lib\stepper\__init__.py :lib/stepper/__init__.py
  python -m mpremote connect COM14 reset

(or use Thonny: open the file, File -> Save as -> Raspberry Pi Pico)

To watch the arm's terminal output: open Thonny, press Stop, then Ctrl+D
in the Shell - you will see the boot messages and server logs live.
