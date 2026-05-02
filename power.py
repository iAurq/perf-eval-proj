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
                "nvidia-smi --id=0 --query-gpu=timestamp,temperature.gpu,temperature.memory,power.draw,utilization.gpu,utilization.memory," \
                "memory.used,clocks_throttle_reasons.active "
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
        """Destructor to ensure nvidia-smi closes on exception."""
        try:
            self.close_power()
        except Exception:
            pass


BENCHMARKS = {
    0: 'heaven',
    1: 'valley',
    2: 'superposition'
}


def run_benchmark(benchmark_id, test_name):
    """Run the selected benchmark with power monitoring."""
    name = BENCHMARKS[benchmark_id]
    logger.info(f'=== Running {name} benchmark (test: {test_name}) ===')

    test = Power()

    try:
        print("Starting power monitoring...")
        test.open_power(test_name)
        print(f"Power monitoring started, opening {name}...")
        time.sleep(5)

        if benchmark_id == 0:
            h.open_heaven_benchmark()
            print("Heaven opened, starting benchmark...")
            time.sleep(5)
            h.start_heaven_benchmark()
            h.close_heaven_benchmark()

        elif benchmark_id == 1:
            v.open_valley_benchmark()
            print("Valley opened, starting benchmark...")
            time.sleep(5)
            v.start_valley_benchmark()
            v.close_valley_benchmark()

        elif benchmark_id == 2:
            sp.open_superposition_benchmark()
            print("Superposition opened, starting benchmark...")
            time.sleep(5)
            sp.start_superposition_benchmark()
            sp.close_superposition_benchmark()

        print("Benchmark done, closing...")

    except Exception as e:
        logger.error(f'Benchmark failed: {e}')
        print(f'ERROR: {e}')

    finally:
        test.close_power()
        print("Done!")


if __name__ == '__main__':
    os.makedirs('data', exist_ok=True)

    parser = argparse.ArgumentParser(description="Power.py - Run GPU benchmark with nvidia-smi monitoring")
    parser.add_argument(
        '--test',
        type=str,
        default='test',
        help='Name for the output CSV file (saved to data/<name>.csv)'
    )
    parser.add_argument(
        '--benchmark',
        type=int,
        choices=[0, 1, 2],
        default=0,
        help='Benchmark to run: 0=heaven, 1=valley, 2=superposition'
    )
    args = parser.parse_args()

    logger.info(f'Benchmark: {BENCHMARKS[args.benchmark]} | Test: {args.test}')
    run_benchmark(args.benchmark, args.test)