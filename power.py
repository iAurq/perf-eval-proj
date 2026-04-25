import os
import time
import sys
import logging
import signal
import subprocess

import heaven as h

# Logger setup
logging.basicConfig(
    filename='main.log',
    format='%(asctime)s %(filename)s %(levelname)s: %(message)s',
    filemode='w'
)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class Power(object):
    """
    Class to start nvidia-smi.
    It's a class bc I don't want there to be conflicts
    with the process variable
    """

    def __init__(self):
        """"""
        self.process = None

    def open_power(self, file_name):
        """
        Start nvidia-smi as a background process.
        """
        try:
            self.process = subprocess.Popen(
                "nvidia-smi --id=0 --query-gpu=timestamp,temperature.gpu,power.draw "
                f"--format=csv --loop=1 --filename=data\\{file_name}.csv", #TODO: Should I add lms?
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
        """
        Close the nvidia-smi process.
        It does this by sending a ctrl + c signal.
        Bc I did shell=True, things act a bit odd.
        The signal might sometimes affect the actual python process as well, terminating it early.
        """
        if self.process:
            time.sleep(1) # FIXME 10
            self.process.send_signal(signal.CTRL_BREAK_EVENT)
            logger.info('Giving time for csv dump')
            time.sleep(3) #FIXME 60
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                logger.warning('Force closing')
                self.process.kill()
            # subprocess.Popen("taskkill /F /PID {pid} /T".format(pid=self.process.pid)) # Backup
            logger.info('Stopped nvidia-smi')
            self.process = None

    def __del__(self):
        """
        Destructor in-case there is an exception so that nvidia-smi can close.
        """
        self.close_power()

if __name__ == '__main__':
    test = Power()
    test.open_power('plz2')
    # time.sleep(5)
    h.open_heaven_benchmark()
    h.start_heaven_benchmark()
    h.close_heaven_benchmark()
    test.close_power()
