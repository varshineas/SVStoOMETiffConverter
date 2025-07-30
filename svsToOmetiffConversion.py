import os
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor
import shutil
import sys

BATCH_SIZE = 10

def process_file(svs_file):
    svs_path = os.path.join(svs_folder, svs_file)
    zarr_pyramid_folder = os.path.join(svs_folder, svs_file[:-4] + "_ZarrPyramid")
    ome_tiff_path = os.path.join(output_folder, svs_file[:-4] + ".ome.tiff")

    if os.path.exists(ome_tiff_path):
        log(f"[SKIP] {svs_file}: OME-TIFF already exists.")
        return

    if not os.path.exists(zarr_pyramid_folder):
        log(f"[INFO] Creating ZarrPyramid for {svs_file}...")
        try:
            bioformats2raw_cmd = f"bioformats2raw \"{svs_path}\" \"{zarr_pyramid_folder}\""
            result = subprocess.run(bioformats2raw_cmd, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            log(result.stdout.decode())
            log(result.stderr.decode())
        except subprocess.CalledProcessError as e:
            log(f"[ERROR] bioformats2raw failed for {svs_file}: {e}")
            log(e.stderr.decode())
            return

    try:
        raw2ometiff_cmd = f"raw2ometiff \"{zarr_pyramid_folder}\" \"{ome_tiff_path}\""
        result = subprocess.run(raw2ometiff_cmd, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        log(result.stdout.decode())
        log(result.stderr.decode())

        if os.path.exists(ome_tiff_path):
            shutil.rmtree(zarr_pyramid_folder)
            log(f"[CLEANUP] Removed ZarrPyramid: {zarr_pyramid_folder}")

        log(f"[DONE] Conversion complete: {svs_file}")
    except subprocess.CalledProcessError as e:
        log(f"[ERROR] raw2ometiff failed for {svs_file}: {e}")
        log(e.stderr.decode())

def log(message):
    with open(log_file, "a") as f:
        f.write(message + "\n")
    print(message)

def main():
    if len(sys.argv) != 2:
        print("Usage: python convert_svs_to_ome_tiff.py <path_to_svs_folder>")
        sys.exit(1)

    global svs_folder
    svs_folder = sys.argv[1]
    if not os.path.isdir(svs_folder):
        print(f"Invalid input directory: {svs_folder}")
        sys.exit(1)

    global output_folder
    output_folder = os.path.join(os.path.dirname(svs_folder), "ome_tiff_output")
    os.makedirs(output_folder, exist_ok=True)

    global log_file
    log_file = os.path.join(os.path.dirname(svs_folder), "conversion_log.txt")
    with open(log_file, "w") as f:
        f.write("OME-TIFF Conversion Log\n")

    all_files = [f for f in os.listdir(svs_folder) if f.endswith(".svs") and os.path.isfile(os.path.join(svs_folder, f))]

    # Filter out files that already have a corresponding .ome.tiff output
    svs_files = [f for f in all_files if not os.path.exists(os.path.join(output_folder, f[:-4] + ".ome.tiff"))]

    if not svs_files:
        log("No new .svs files to convert.")
        return

    start_time = time.time()

    try:
        for i in range(0, len(svs_files), BATCH_SIZE):
            batch = svs_files[i:i+BATCH_SIZE]
            log(f"[BATCH] Starting batch {i//BATCH_SIZE + 1} with {len(batch)} files.")
            with ThreadPoolExecutor(max_workers=BATCH_SIZE) as executor:
                executor.map(process_file, batch)
    except KeyboardInterrupt:
        log("[INTERRUPT] User terminated the process.")
    finally:
        elapsed = time.time() - start_time
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        log(f"[FINISHED] {timestamp} - Total time: {elapsed:.2f} seconds.")

if __name__ == "__main__":
    main()
