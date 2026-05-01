import subprocess
import time
import os
import logging
import sys
from datetime import datetime

WORKLOADS = [
    "3dsmax-08",      # DirectX 11
    "blender-01",     # OpenGL
    "catia-07",       # OpenGL
    "creo-04",        # OpenGL
    "energy-04",      # OpenGL
    "enscape-01",     # Vulkan
    "maya-07",        # OpenGL
    "medical-04",     # OpenGL
    "snx-05",         # OpenGL
    "solidworks-08",  # OpenGL
    "unreal-engine-01" # DirectX 12 + Ray Tracing
]

# API mapping for trace selection
API_TRACE_MAP = {
    "3dsmax-08": "dx11",
    "blender-01": "opengl",
    "catia-07": "opengl",
    "creo-04": "opengl",
    "energy-04": "opengl",
    "enscape-01": "vulkan",
    "maya-07": "opengl",
    "medical-04": "opengl",
    "snx-05": "opengl",
    "solidworks-08": "opengl",
    "unreal-engine-01": "dx12"
}

# SPEC directory
SPEC_DIR = r"C:\Program Files\SPECviewperf 15"
SPEC_EXE = "SPECviewperf-CLI.exe"

OUTPUT_DIR = r"C:\Users\Aura\Documents\spring26\ece382n-21-performance_eval_benchmarking\FinalProj\outputs"
RUN_NAME = datetime.now().strftime("%Y%m%d_%H%M%S")

spec_exe_full = os.path.join(SPEC_DIR, SPEC_EXE)
# Create output directory if it doesn't exist
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Logging setup
logFilename = os.path.join(OUTPUT_DIR, f"spec_script_log_{RUN_NAME}.log")

logging.basicConfig(
    filename=logFilename,
    format='%(asctime)s - %(levelname)s: %(message)s',
    filemode='w',
    level=logging.DEBUG
)

logger = logging.getLogger(__name__)

console = logging.StreamHandler()
console.setLevel(logging.DEBUG)
console.setFormatter(logging.Formatter('[%(asctime)s] %(levelname)s: %(message)s', datefmt='%H:%M:%S'))
logger.addHandler(console)

def run_nvidia_smi_monitoring(output_file):
    """Start nvidia-smi in background for GPU monitoring"""
    logger.info(f"Starting nvidia-smi monitoring -> {output_file}")
    process = subprocess.Popen(
        [
            "nvidia-smi",
            "--query-gpu=timestamp,name,utilization.gpu,utilization.memory,memory.used,power.draw,temperature.gpu,clocks.gr,clocks.mem,clocks_throttle_reasons.active",
            "--format=csv",
            "--loop-ms=500",
            f"--filename={output_file}"
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    return process

def run_nsys_profiling(output_file, workload):
    """
    Run SPECviewperf with NVIDIA Nsight Systems profiling.
    Traces API calls and their effects on GPU/CPU.
    """
    api = API_TRACE_MAP.get(workload, "opengl")
    logger.info(f"Starting Nsight Systems profiling for {workload} (API: {api}) -> {output_file}.nsys-rep")
    
    # Build trace string - only use supported options from the list
    # Available: opengl, opengl-annotations, vulkan, vulkan-annotations, dx11, dx11-annotations, dx12, dx12-annotations
    trace_string = api
    
    # Add annotations if available (gives more detailed API call info)
    if api == "opengl":
        trace_string = "opengl,opengl-annotations"
    elif api == "vulkan":
        trace_string = "vulkan,vulkan-annotations"
    elif api == "dx11":
        trace_string = "dx11,dx11-annotations,wddm"
    elif api == "dx12":
        trace_string = "dx12,dx12-annotations,wddm"
    
    # Build nsys command
    nsys_cmd = [
    "nsys", "profile",
    "--output", output_file,
    "--trace=none",
    "--force-overwrite=true"
]
    
    # Add API-specific GPU workload tracing for detailed GPU activity
    if api == "opengl":
        nsys_cmd.append("--opengl-gpu-workload=true")
    elif api == "vulkan":
        nsys_cmd.append("--vulkan-gpu-workload=individual")
    elif api == "dx12":
        nsys_cmd.append("--dx12-gpu-workload=individual")
    # dx11 doesn't need extra flag
    
    # Add the SPEC command with full path
    nsys_cmd.extend(["--", spec_exe_full, "-w", workload])
    
    logger.debug(f"Running command: {' '.join(nsys_cmd)}")
    logger.debug(f"Working directory: {SPEC_DIR}")
    
    # Run nsys with cwd set to SPEC directory
    process = subprocess.run(
        nsys_cmd,
        capture_output=True,
        text=True,
        cwd=SPEC_DIR
    )
    
    # Log any warnings/errors from nsys
    if process.stderr:
        if "warning" in process.stderr.lower():
            logger.warning(f"nsys warnings: {process.stderr[:500]}")
        elif process.returncode != 0:
            logger.error(f"nsys error: {process.stderr[:500]}")
    
    return process

def run_spec_with_nvidia_smi(workload, output_dir):
    """Run SPECviewperf with nvidia-smi monitoring (GPU metrics only)"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    smi_log = os.path.join(output_dir, f"{workload}_{timestamp}_smi.csv")
    
    # Start nvidia-smi in background
    smi_process = run_nvidia_smi_monitoring(smi_log)
    time.sleep(1)  # Give nvidia-smi time to start
    
    # Run SPECviewperf
    logger.info(f"Running SPECviewperf: {workload} with nvidia-smi monitoring")
    spec_process = subprocess.run(
        [
            SPEC_EXE,
            "-w", workload
        ],
        capture_output=True,
        text=True,
        cwd=SPEC_DIR
    )
    
    # Stop nvidia-smi
    smi_process.terminate()
    smi_process.wait(timeout=5)
    
    logger.info(f"nvidia-smi data saved to {smi_log}")
    
    return spec_process, smi_log

def run_spec_with_nsys(workload, output_dir):
    """Run SPECviewperf with Nsight Systems profiling (API calls + GPU/CPU effects)"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    nsys_log = os.path.join(output_dir, f"{workload}_{timestamp}_nsys")
    
    logger.info(f"Running SPECviewperf: {workload} with Nsight Systems profiling")
    spec_process = run_nsys_profiling(nsys_log, workload)
    
    logger.info(f"Nsight Systems data saved to {nsys_log}.nsys-rep")
    
    return spec_process, nsys_log

def run_benchmark(profiler_choice, workload, output_dir):
    """Run benchmark with selected profiler"""
    
    try:
        if profiler_choice == 0:
            # nvidia-smi monitoring only (GPU metrics)
            spec_process, output_file = run_spec_with_nvidia_smi(workload, output_dir)
            
        elif profiler_choice == 1:
            # Nsight Systems profiling (API calls + GPU/CPU effects)
            spec_process, output_file = run_spec_with_nsys(workload, output_dir)
            
        else:
            logger.error(f"Invalid profiler choice: {profiler_choice}")
            return False
        
        # Check results
        if spec_process and spec_process.returncode == 0:
            logger.info(f"SUCCESS: {workload} completed successfully")
            if spec_process.stdout:
                # Look for results location in output
                for line in spec_process.stdout.split('\n'):
                    if "results and logs available" in line.lower():
                        logger.info(f"Results: {line.strip()}")
            return True
        else:
            exit_code = spec_process.returncode if spec_process else "N/A"
            logger.error(f"FAILED: {workload} failed with return code {exit_code}")
            if spec_process and spec_process.stderr:
                # Filter common non-critical warnings
                stderr_lines = spec_process.stderr.split('\n')
                for line in stderr_lines:
                    if "does not meet" in line.lower():
                        logger.warning(f"Note: {line.strip()}")
                    elif "error" in line.lower():
                        logger.error(f"Error: {line.strip()}")
            return False
            
    except Exception as e:
        logger.error(f"Exception during benchmark: {e}")
        import traceback
        logger.debug(traceback.format_exc())
        return False

def print_usage():
    """Print usage information"""
    print("=" * 70)
    print("SPECviewperf Benchmark Script with GPU Profiling")
    print("=" * 70)
    print("\nUsage: python script.py <workload_number> <profiler_choice>")
    print("\nWorkload Numbers (1-11):")
    for i, w in enumerate(WORKLOADS, 1):
        api = API_TRACE_MAP.get(w, "unknown")
        print(f"  {i:2d}. {w:<18} ({api})")
    print("\nProfiler Choices:")
    print("  0 - nvidia-smi (GPU metrics only)")
    print("      - Power draw, utilization, temperature, clock speeds")
    print("      - Memory usage, GPU throttling detection")
    print("")
    print("  1 - Nsight Systems (API calls + GPU/CPU effects)")
    print("      - Graphics API call durations (OpenGL/DX11/DX12/Vulkan)")
    print("      - GPU metrics: SM active [throughput %], memory bandwidth")
    print("      - CPU sampling: thread activity, function calls")
    print("      - CPU/GPU timeline correlation")
    print("\nSupported trace options for this nsys version:")
    print("  opengl, opengl-annotations, vulkan, vulkan-annotations")
    print("  dx11, dx11-annotations, dx12, dx12-annotations")
    print("\nExamples:")
    print("  python script.py 7 0    # maya-07 with nvidia-smi")
    print("  python script.py 10 1   # solidworks-08 with Nsight Systems")
    print("=" * 70)

def verify_profiler_tools(profiler_choice):
    """Verify that required profiler tools are installed"""
    if profiler_choice == 1:
        logger.info("Checking nsys installation...")
        try:
            check = subprocess.run(["nsys", "--version"], capture_output=True, text=True)
            if check.returncode != 0:
                logger.error("nsys not found! Please install Nsight Systems")
                return False
            logger.info(f"nsys version: {check.stdout.strip()}")
            logger.info("Supported trace options: opengl, dx11, dx12, vulkan (with annotations)")
        except FileNotFoundError:
            logger.error("nsys not found! Please install Nsight Systems")
            return False
    return True

def main():
    # Check arguments
    if len(sys.argv) < 3:
        print_usage()
        sys.exit(1)
    
    # Parse workload number
    try:
        wIndex = int(sys.argv[1]) - 1
        if wIndex < 0 or wIndex >= len(WORKLOADS):
            raise IndexError
    except (ValueError, IndexError):
        print(f"Error: Please provide a valid workload number between 1 and {len(WORKLOADS)}")
        print_usage()
        sys.exit(1)
    
    # Parse profiler choice
    try:
        profiler_choice = int(sys.argv[2])
        if profiler_choice not in [0, 1]:
            raise ValueError
    except ValueError:
        print("Error: Profiler choice must be 0 (nvidia-smi) or 1 (Nsight Systems)")
        print_usage()
        sys.exit(1)
    
    selectedWorkload = WORKLOADS[wIndex]
    profiler_names = ["nvidia-smi", "Nsight Systems"]
    api_used = API_TRACE_MAP.get(selectedWorkload, "unknown")
    
    logger.info("=" * 70)
    logger.info(f"Starting benchmark - Workload: {selectedWorkload} (API: {api_used})")
    logger.info(f"Profiler: {profiler_names[profiler_choice]}")
    logger.info("=" * 70)
    
    # Verify profiler tools are available
    if not verify_profiler_tools(profiler_choice):
        sys.exit(1)
    
    # Run the benchmark
    success = run_benchmark(profiler_choice, selectedWorkload, OUTPUT_DIR)
    
    if success:
        logger.info("Benchmark completed successfully")
    else:
        logger.error("Benchmark failed")
        sys.exit(1)

if __name__ == "__main__":
    main()