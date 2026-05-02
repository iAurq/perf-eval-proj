import os
import argparse
import time
import sys
import logging
import signal
import subprocess

import heaven as h
import valley as v
import superposition as sp

# Logger setup
logging.basicConfig(
    filename='main.log',
    format='%(asctime)s %(filename)s %(levelname)s: %(message)s',
    filemode='w'
)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

console = logging.StreamHandler()
console.setLevel(logging.DEBUG)
console.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s'))
logger.addHandler(console)


class Power(object):
    """
    Class to start nvidia-smi.
    It's a class bc I don't want there to be conflicts
    with the process variable.
    """

    def __init__(self):
        self.process = None

    def open_power(self, file_name):
        """Start nvidia-smi as a background process."""
        try:
            self.process = subprocess.Popen(
                "nvidia-smi --id=0 --query-gpu=timestamp,temperature.gpu,power.draw,utilization.gpu,clocks.current.graphics,clocks.current.memory,clocks.current.sm,clocks_throttle_reasons.active "
                f"--format=csv --loop-ms=500 --filename=data\\{file_name}.csv",
                stdout=subprocess.PIPE,
                shell=True,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
            )
            logger.info('Started nvidia-smi')
        except Exception as e:
            print(e)
            logger.error(e)
            sys.exit()
        time.sleep(10)

    def close_power(self):
        """Close the nvidia-smi process via CTRL+BREAK signal."""
        if self.process and self.process.poll() is None:
            time.sleep(1)
            try:
                self.process.send_signal(signal.CTRL_BREAK_EVENT)
            except OSError:
                pass
            logger.info('Giving time for csv dump')
            time.sleep(10)
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                logger.warning('Force closing')
                self.process.kill()
            logger.info('Stopped nvidia-smi')
            self.process = None

    def __del__(self):
        """
        Destructor in-case there is an exception so that nvidia-smi can close.
        """
        self.close_power()

if __name__ == '__main__':
    os.makedirs('data', exist_ok=True)  # create data dir if missing

    parser = argparse.ArgumentParser(description="Power.py")
    parser.add_argument('--test', type=str, default='test', help='Test name')
    args = parser.parse_args()

    print("Starting power monitoring...")
    test = Power()
    test.open_power(args.test)
    print("Power monitoring started, opening heaven...")
    time.sleep(5)
    h.open_heaven_benchmark()
    print("Heaven opened, starting benchmark...")
    time.sleep(5)
    h.start_heaven_benchmark()
    print("Benchmark done, closing...")
    h.close_heaven_benchmark()
    test.close_power()
    print("Done!")
