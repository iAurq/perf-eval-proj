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


def start_heaven_benchmark():
    """
    Start Heaven Benchmark for set amount of time,
    then close it.
    """
    logger.debug("Clicking launcher Run button...")
    attempts = 10
    found = False
    while attempts > 0:
        try:
            autogui.click('images/run.png')
            found = True
        except pyautogui.ImageNotFoundException:
            attempts -= 1
            time.sleep(3)
    if not found:
        logger.error('Could not find the heaven start benchmark after 10 attempts.')
        sys.exit()
    time.sleep(1)

    wait_for_exe('Heaven.exe')

    logger.info("Heaven.exe detected. Giving it time to load...")
    time.sleep(10) #FIXME

    logger.info("Starting the benchmark...")
    autogui.press('f9')

    time.sleep(5) #FIXME
    logger.info("Benchmark ~finished.")

    logger.info("Closing all systems...")
    os.system('taskkill /f /im heaven.exe /t')


def open_heaven_benchmark():
    """
    Open Heaven Benchmark Launcher
    """
    current_dir = os.getcwd() # Save dir so you can come back
    logger.debug(f'Current Directory: {current_dir}')

    heaven_path = os.getenv('HEAVEN_PATH') + '\\bin'
    try:
        os.chdir(heaven_path)
        logger.debug(os.getcwd())
        app = subprocess.Popen('browser_x86.exe -config ../data/launcher/launcher.xml',
                               shell=True
                               )
        wait_for_exe('browser_x86.exe')
        os.chdir(current_dir)
        # app.kill()
    except Exception as e:
        logger.error(e)


def close_heaven_benchmark():
    """
    Close Heaven Benchmark Launcher
    """
    os.system('taskkill /im browser_x86.exe')

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    open_heaven_benchmark()
    start_heaven_benchmark()
    close_heaven_benchmark()