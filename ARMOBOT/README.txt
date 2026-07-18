==================================================
 ARMOBOT - Robotic Arm Control System
==================================================

Two folders:

1) PICO_CODE\
   Everything that lives ON the Raspberry Pi Pico W.
   These files are already uploaded to the Pico - this is your backup copy.
   See PICO_CODE\README.txt for how to re-upload them.

2) LAPTOP\
   Everything the laptop runs to operate the arm from the browser.

--------------------------------------------------
 HOW TO OPERATE THE ARM (daily routine)
--------------------------------------------------
1. Power the robot arm (Pico).
2. Double-click:  LAPTOP\scripts\start_all.bat
3. Wait for "Pico is ONLINE at 192.168.137.50 - arm ready!"
4. Use the dashboard in the browser:  http://localhost:5173

Notes:
- Close Thonny before operating (Thonny halts the arm program).
- Do not run the GCS project at the same time (it also uses port 3000).
- The hotspot turns OFF every Windows reboot; start_all.bat turns it back on.

Network map:
  Laptop hotspot : RoboticArm_PC / 12345678
  Pico (arm)     : 192.168.137.50  (HTTP :80, TCP bridge :81)
  Backend        : http://localhost:3000
  Dashboard      : http://localhost:5173

The development repo (source of truth) is: D:\Robotic-Arm-dev\Robotic-Arm-dev
If you change code there, re-copy it here to keep this folder up to date.
