import argparse
import datetime
import json
import signal
import subprocess
import time
from pathlib import Path

from hypy_utils import color
from hypy_utils.logging_utils import setup_logger

log = setup_logger()
speeds = []


def signal_handler(sig, frame):
    global pending_stop
    pending_stop = True
    log.error("^C received, signaling for the main process to stop...")
    log.warning("Please wait for the current block to finish scanning, then the program will exit.")
    log.warning("If you want to stop immediately, press ^\\ (NOT RECOMMENDED)")


pending_stop = False
signal.signal(signal.SIGINT, signal_handler)


def to_gb(block: int):
    return block * BLOCK_SIZE / (1024 * 1024 * 1024)


def disk_info() -> (int, int):

    # Get the disk size in blocks
    disk_size = int(subprocess.run(f"sudo blockdev --getsize64 {DISK}", capture_output=True, text=True, shell=True).stdout) // BLOCK_SIZE
    log.info(f"Disk size: {to_gb(disk_size):,.0f} GB, {disk_size:#x} blocks")

    # Get the size of a logical sector (LDA)
    lss = int(subprocess.run(f"sudo blockdev --getss {DISK}", capture_output=True, text=True, shell=True).stdout)
    pss = int(subprocess.run(f"sudo blockdev --getpbsz {DISK}", capture_output=True, text=True, shell=True).stdout)
    log.info(f"Logical sector size: {lss} bytes, physical sector size: {pss} bytes")

    return disk_size, lss


def run_badblocks(start_block: int, end_block: int):
    # Print block address in hex
    log.debug(f"Scanning from {start_block:#x} ({to_gb(start_block):,.0f} GB) to {end_block:#x} ({to_gb(end_block):,.0f} GB)")

    command = f"sudo badblocks -b 4096 -v {DISK} {end_block} {start_block}"
    duration = time.time()
    result = subprocess.run(command, capture_output=True, text=True, shell=True, start_new_session=True)
    duration = time.time() - duration

    # stdout should be a list of bad blocks, parse it
    bad_blocks = [int(r) for r in result.stdout.strip().split("\n") if r]

    # Write the log as json
    logf = json.loads(LOG_FILE.read_text())
    logf["logs"].append({
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "duration": duration,
        "start_block": start_block,
        "end_block": end_block,
        "bad_blocks": bad_blocks,
        "stderr": result.stderr,
    })
    LOG_FILE.write_text(json.dumps(logf, indent=2))

    # Print logs
    if bad_blocks:
        log.error(f"> Bad blocks found: ")
        for block in bad_blocks:
            # Pint in hex
            log.error(f"> {block:#x} = LDA {block * BLOCK_SIZE // lss:#x} = {block * BLOCK_SIZE / (1024 * 1024 * 1024):,.0f} GB")
    else:
        log.debug(color(f"> Clean!"))

    # Print summary (speed, progress, eta, etc.)
    # The stored speed is in blocks per second
    speed = (end_block - start_block) / duration
    speeds.append(speed)
    avg_spd = sum(speeds) / len(speeds)
    progress = end_block / disk_size

    # Calculate ETA
    eta = (disk_size - end_block) / avg_spd
    eta = str(datetime.timedelta(seconds=eta))[:-7]

    # Convert speed to MB/s
    speed *= BLOCK_SIZE / (1024 * 1024)
    avg_spd *= BLOCK_SIZE / (1024 * 1024)

    log.info(f"> {progress * 100:.2f}% | Cur {speed:.1f} MB/s | Remain {eta} | "
             f"Avg {avg_spd:.1f} MB/s")


if __name__ == "__main__":
    # Take in disk and block size as optional arguments
    parser = argparse.ArgumentParser("Bad block detection utility")
    parser.add_argument("--disk", "-d", type=str, help="Disk to scan")
    parser.add_argument("--block-size", "-b", type=int, default=4096, help="Block size in bytes")
    parser.add_argument("--start", "-s", type=int, help="Start block")
    parser.add_argument("--end", "-e", type=int, help="End block")
    args = parser.parse_args()

    DISK = args.disk
    BLOCK_SIZE = args.block_size
    START = args.start
    END = args.end
    LOG_FILE = Path(__file__).parent / f"badblocks_log_{DISK.replace('/', '_')}.json"

    if not LOG_FILE.exists():
        LOG_FILE.write_text(json.dumps({"logs": [], "block_size": BLOCK_SIZE}, indent=2))
    else:
        # Check if the block size matches
        block_size = json.loads(LOG_FILE.read_text())["block_size"]
        if block_size != BLOCK_SIZE:
            raise ValueError(f"Block size mismatch: {block_size} != {BLOCK_SIZE}")

        # Resume from the last run
        logs = json.loads(LOG_FILE.read_text())["logs"]
        if logs:
            last_log = logs[-1]
            START = last_log["end_block"]
            log.info(f"Resuming from {START:#x}")

    gb_approx = 1024 * 1024 * 1024 // BLOCK_SIZE
    disk_size, lss = disk_info()

    for start in range(START or 0, END or disk_size, gb_approx):
        end = min(start + gb_approx, disk_size)
        run_badblocks(start, end)
        if pending_stop:
            break
