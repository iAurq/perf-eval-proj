#!/usr/bin/env python3          # use python3 to run this script

import os
import time
import subprocess
import logging
import psutil
import pyautogui as autogui
from dotenv import load_dotenv
from datetime import datetime

# buttons and their options (default option is the first) idea is to use image rec to find dropdown menu options and keystrokes to confirm
# aaButton options: off, 2x, 4x, 8x
# apiButton options: directX11, directX9, OpenGL
# qualityButton options: low, medium, high, ultra
# tessellationButton options: disabled, moderate, normal, extreme


autogui.FAILSAFE = True  # Enable fail-safe mode to allow moving the mouse to the corner to stop the script
autogui.PAUSE = 1  # 1 sec pause after each pyautogui call

logFilename = f"heaven_script_log_{datetime.now().strftime('%Y-%m-%d_%H%M%S')}.log"

logging.basicConfig(
    filename=logFilename,
    format='%(asctime)s - %(levelname)s: %(message)s',
    filemode='w',
    level=logging.DEBUG
)

logger = logging.getLogger(__name__)

console = logging.StreamHandler()
console.setLevel(logging.DEBUG)
console.setFormatter(logging.Formatter('[%(asctime)s] %(levelname)s: %(message)s',  datefmt='%H:%M:%S'))
logger.addHandler(console)

load_dotenv('tyler.env')

runButton = "images/run.png"
aaButton = "images/aa.png"
apiButton = "images/api.png"
qualityButton = "images/quality.png"
tessellationButton = "images/tessellation.png"

# settings for run, change for options wanted
settings = {
    "aa": "off",                # off, 2x, 4x, 8x
    "api": "directX11",         # directX11, directX9, OpenGL
    "quality": "low",           # low, medium, high, ultra
    "tessellation": "disabled"  # disabled, moderate, normal, extreme

}

aaMap = {
    0: "off",
    1: "2x",
    2: "4x",
    3: "8x"
}

apiMap = {
    0: "directX11",
    1: "directX9",
    2: "OpenGL"
}

qualityMap = {
    0: "low",
    1: "medium",
    2: "high",
    3: "ultra"
}

tessellationMap = {
    0: "disabled",
    1: "moderate",
    2: "normal",
    3: "extreme"
}

CONFIDENCE_THRESHOLD = 0.85 # for image rec, adjust (higher = stricter)

# --- waiting for process to exist ---
def waitForProcess(procName: str):
    logger.info(f'Waiting for {procName} to exist...')
    while True:
        for proc in psutil.process_iter(['name']):
            if proc.info['name'].lower() == procName.lower():
                logger.info(f'{procName} detected!')
                return
        time.sleep(1)

# --- kill proc ---
def killProcess(procName: str):
    logger.info(f'Killing {procName}...')
    killed = False
    for proc in psutil.process_iter(['name']):
        if proc.info['name'].lower() == procName.lower():
            try:
                proc.kill()  # or proc.terminate() for graceful shutdown
                killed = True
                logger.info(f'Killed PID {proc.pid}')
            except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
                logger.error(f'Failed to kill {proc.pid}: {e}')
    
    if not killed:
        logger.warning(f'No {procName} process found')
    time.sleep(2)

# --- wait for image ---
def waitForImage(img, timeout=30, confidence=CONFIDENCE_THRESHOLD):
    logger.debug(f'Waiting for image: {img}')
    start = time.time()
    while time.time() - start < timeout:
        location = autogui.locateOnScreen(img, confidence=confidence)
        if location:
            return autogui.center(location) # gives xy coord for center 
        time.sleep(0.5)
    raise TimeoutError(f'Image not found within {timeout}s: {img}')

# --- click func ---
def click(img, timeout=30, confidence=CONFIDENCE_THRESHOLD):
    point = waitForImage(img, timeout, confidence)
    autogui.click(point.x, point.y)
    return point


# --- dropdown func ---
def dropdown(buttonImage, presses):
     


def main():
    #placeholder


if __name__ == "__main__":
    main()