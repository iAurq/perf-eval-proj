import os
import sys
import time
import subprocess
import logging
import psutil
import pyautogui
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
load_dotenv()


def wait_for_exe(exe_name: str):
    logger.info(f'Waiting for {exe_name} to open...')
    exe = False
    while not exe:
        for proc in psutil.process_iter(['name']):
            if proc.info['name'] == exe_name:
                exe = True
                break
        time.sleep(1)
    logger.info(f'{exe_name} opened!!')


def start_superposition_benchmark():
    """
    Start superposition Benchmark for set amount of time,
    then close it.
    """
    logger.debug("Clicking launcher Run button...")
    attempts = 10
    found = False
    while attempts > 0 and not found:
        try:
            autogui.click('images/run_superposition.png')
            found = True
        except pyautogui.ImageNotFoundException:
            attempts -= 1
            time.sleep(1)
    if not found:
        logger.error('Could not find the superposition start button after 10 attempts.')
        sys.exit()
    time.sleep(1)

    wait_for_exe('superposition.exe')

    logger.info("superposition.exe detected. Giving it time to load...")
    time.sleep(15) #FIXME

    logger.info("Giving benchmark time to run (it starts automatically)...")
    time.sleep(3*60) # It takes about 3 minutes #FIXME
    attempts = 10
    found = False
    while attempts > 0 and not found:
        try:
            autogui.locateOnScreen('images/done_superposition.png')
            found = True
        except pyautogui.ImageNotFoundException:
            attempts -= 1
            time.sleep(3)
    if not found:
        logger.error('Could not find the heaven start benchmark after 10 attempts.')
        sys.exit()

    time.sleep(5) #FIXME
    logger.info("Benchmark ~finished.")


def open_superposition_benchmark():
    """
    Open superposition Benchmark Launcher
    """
    current_dir = os.getcwd() # Save dir so you can come back
    logger.debug(f'Current Directory: {current_dir}')

    superposition_path = os.getenv('SUPERPOSITION_PATH') + '\\bin'
    try:
        os.chdir(superposition_path)
        logger.debug(os.getcwd())
        app = subprocess.Popen('launcher.exe',
                               shell=True
                               )
        wait_for_exe('launcher.exe')
        os.chdir(current_dir)
    except Exception as e:
        logger.error(e)


def close_superposition_benchmark():
    """
    Close superposition Benchmark Launcher
    """
    subprocess.run('taskkill /im launcher.exe')

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    open_superposition_benchmark()
    start_superposition_benchmark()
    close_superposition_benchmark()