import os
import time
import subprocess
import logging
import psutil
import pyautogui as autogui
from dotenv import load_dotenv

# PyAutoGui Setup
autogui.PAUSE = 2.5
autogui.FAILSAFE = True

# Logger setup
logging.basicConfig(
    filename='main.log',
    format='%(asctime)s %(filename)s %(levelname)s: %(message)s',
    filemode='w'
)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Env setup
load_dotenv('tyler.env')

# ─────────────────────────────────────────────
# FIXED COORDINATES
# ─────────────────────────────────────────────
RUN_BUTTON = (1241, 669)


def wait_for_exe(exe_name: str):
    logger.info(f'Waiting for {exe_name} to open...')
    while True:
        for proc in psutil.process_iter(['name']):
            if proc.info['name'] == exe_name:
                logger.info(f'{exe_name} opened!')
                return
        time.sleep(1)
    logger.info(f'{exe_name} opened!!')


def start_heaven_benchmark():
    """
    Start Heaven Benchmark for set amount of time,
    then close it.
    """
    logger.debug("Clicking launcher Run button...")
    attempts = 10
    found = False
    while attempts > 0 and not found:
        try:
            x, y = pyautogui.locateCenterOnScreen('images/run.png', confidence=0.8)
            autogui.click(x, y)
            found = True
        except pyautogui.ImageNotFoundException:
            attempts -= 1
            time.sleep(1)
    if not found:
        logger.error('Could not find the heaven start benchmark after 10 attempts.')
        sys.exit()
    time.sleep(1)

    wait_for_exe('Heaven.exe')

    logger.info("Heaven.exe detected. Giving it time to load...")
    time.sleep(10) #FIXME

    logger.info("Starting the benchmark...")
    autogui.press('f9')

    time.sleep(4*60) # It takes about 4 minutes #FIXME
    attempts = 10
    found = False
    while attempts > 0 and not found:
        try:
            x, y = pyautogui.locateCenterOnScreen('images/done.png', confidence=0.8)
            autogui.click(x, y)
            found = True
        except pyautogui.ImageNotFoundException:
            attempts -= 1
            time.sleep(3)
    if not found:
        logger.error('Could not find the heaven start benchmark after 10 attempts.')
        sys.exit()

    time.sleep(5) #FIXME
    logger.info("Benchmark ~finished.")

    logger.info("Closing all systems...")
    subprocess.run('taskkill /f /im heaven.exe /t')


def open_heaven_benchmark():
    """Open Heaven Benchmark Launcher."""
    current_dir = os.getcwd()
    logger.debug(f'Current Directory: {current_dir}')
    heaven_path = os.getenv('HEAVEN_PATH') + '\\bin'
    try:
        os.chdir(heaven_path)
        subprocess.Popen('browser_x86.exe -config ../data/launcher/launcher.xml', shell=True)
        wait_for_exe('browser_x86.exe')
        os.chdir(current_dir)
        logger.info('Heaven launcher opened!')
    except Exception as e:
        logger.error(e)
        raise


def start_heaven_benchmark():
    """Click Run, wait for Heaven to load, press F9 to start benchmark."""
    logger.info('Waiting for launcher to fully render (3s)...')
    time.sleep(3)

    logger.info(f'Clicking Run button at {RUN_BUTTON}...')
    autogui.click(RUN_BUTTON[0], RUN_BUTTON[1])
    time.sleep(1)

    wait_for_exe('Heaven.exe')
    logger.info('Heaven.exe detected. Waiting for scene to load (10s)...')
    time.sleep(20)

    logger.info('Pressing F9 to start benchmark...')
    autogui.press('f9')
    autogui.click(RUN_BUTTON[0], RUN_BUTTON[1])
    start_time = time.time()

    logger.info('Waiting for benchmark to complete (~6 min)...')
    time.sleep(6 * 60)


def close_heaven_benchmark():
    logger.info('Closing Heaven...')
    autogui.hotkey('alt', 'f4')
    logger.info('1 minute cooldown period...')
    time.sleep(60)


if __name__ == '__main__':
    open_heaven_benchmark()
    start_heaven_benchmark()
    close_heaven_benchmark()
