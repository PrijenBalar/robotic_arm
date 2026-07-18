==================================================
 LAPTOP - files the laptop runs to operate the arm
==================================================

TO START EVERYTHING:  double-click  scripts\start_all.bat
Then use the dashboard at  http://localhost:5173

What start_all.bat does, in order:
  1. Turns on the WiFi hotspot (RoboticArm_PC) that the Pico joins
  2. Warns if port 3000 is blocked by another program
  3. Starts the backend  (web\backend,  port 3000)
  4. Starts the frontend (web\frontend, port 5173) and opens the browser
  5. Waits until the Pico appears at 192.168.137.50

Folders:
  scripts\
    start_all.bat      <- THE one to run (does everything below)
    start_hotspot.ps1  hotspot only
    start_armobot.bat  backend + frontend + browser only
  web\backend\         Node.js server: login, Pico TCP bridge, jog relay
  web\frontend\        React dashboard (3D view, jog, calibrate, pick&place)

Manual start (what the bat automates), in two terminals:
  cd web\backend   ->  npm start
  cd web\frontend  ->  npm run dev
  browser          ->  http://localhost:5173

node_modules are included - no npm install needed on this machine.
