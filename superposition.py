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
RUN_BUTTON = (1378, 793)


def wait_for_exe(exe_name: str):
    logger.info(f'Waiting for {exe_name} to open...')
    while True:
        for proc in psutil.process_iter(['name']):
            if proc.info['name'] == exe_name:
                logger.info(f'{exe_name} opened!')
                return
        time.sleep(1)


def open_superposition_benchmark():
    """Open Superposition Benchmark Launcher."""
    current_dir = os.getcwd()
    logger.debug(f'Current Directory: {current_dir}')
    superposition_path = os.getenv('SUPERPOSITION_PATH') + '\\bin'
    try:
        os.chdir(superposition_path)
        subprocess.Popen('launcher.exe', shell=True)
        wait_for_exe('launcher.exe')
        os.chdir(current_dir)
        logger.info('Superposition launcher opened!')
    except Exception as e:
        logger.error(e)
        raise


def start_superposition_benchmark():
    """Click Run, wait for Superposition to load, benchmark starts automatically."""
    logger.info('Waiting for launcher to fully render (3s)...')
    time.sleep(3)

    logger.info(f'Clicking Run button at {RUN_BUTTON}...')
    autogui.click(RUN_BUTTON[0], RUN_BUTTON[1])
    time.sleep(1)

    wait_for_exe('superposition.exe')
    logger.info('superposition.exe detected. Waiting for scene to load (15s)...')
    time.sleep(15)

    # Superposition starts automatically, just start the timer
    start_time = time.time()
    logger.info('Benchmark running (starts automatically)...')

    logger.info('Waiting for benchmark to complete (~8 min)...')
    time.sleep(8 * 60)


def close_superposition_benchmark():
    logger.info('Closing Superposition...')
    autogui.hotkey('alt', 'f4')
    logger.info('1 minute cooldown period...')
    time.sleep(60)


if __name__ == '__main__':
    open_superposition_benchmark()
    start_superposition_benchmark()
    close_superposition_benchmark()
