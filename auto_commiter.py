import os
import subprocess
import time
import math

TRACK_FILE = ".upload_tracker"
WAIT_SECONDS = 2  # Optional wait between commits
MAX_FILE_SIZE_MB = 100  # Maximum file size in MB
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024
BAR_WIDTH = 30  # Width of the visual progress bar

def ask_batch_size():
    while True:
        try:
            num = int(input("📥 How many files should be uploaded per commit? "))
            if num > 0:
                return num
            else:
                print("Please enter a number greater than 0.")
        except ValueError:
            print("Please enter a valid number.")

def load_uploaded_files():
    if os.path.exists(TRACK_FILE):
        with open(TRACK_FILE, "r") as f:
            return set(f.read().splitlines())
    return set()

def save_uploaded_files(files):
    with open(TRACK_FILE, "a") as f:
        for file in files:
            f.write(file + "\n")

def get_uncommitted_files():
    result = subprocess.run(["git", "ls-files", "--others", "--exclude-standard"], capture_output=True, text=True)
    return result.stdout.strip().split("\n")

def filter_large_files(files):
    filtered = []
    skipped = []
    for file in files:
        try:
            if os.path.getsize(file) <= MAX_FILE_SIZE_BYTES:
                filtered.append(file)
            else:
                skipped.append(file)
        except FileNotFoundError:
            continue
    if skipped:
        print(f"⚠️ Skipped {len(skipped)} file(s) over {MAX_FILE_SIZE_MB}MB: {skipped}")
    return filtered

def stage_and_commit(files):
    for file in files:
        subprocess.run(["git", "add", file])
    subprocess.run(["git", "commit", "-m", f"Auto upload next {len(files)} items"])
    subprocess.run(["git", "push"])

def format_time(seconds):
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    return f"{h}h {m}m {s}s"

def draw_progress_bar(done, total, elapsed_time):
    if done == 0:
        avg_time = 0
    else:
        avg_time = elapsed_time / done

    remaining = total - done
    est_time = remaining * avg_time
    est_time_str = format_time(est_time)

    bar_fill = int(BAR_WIDTH * done / total)
    bar = '|' * bar_fill + ' ' * (BAR_WIDTH - bar_fill)

    print(f"--------- ({done}/{total}) -------------")
    print(bar)
    print(f"--------- ({est_time_str}) --------")

def main():
    files_per_commit = ask_batch_size()

    uploaded = load_uploaded_files()
    all_untracked = get_uncommitted_files()
    unuploaded = [f for f in all_untracked if f and f not in uploaded]
    filtered = filter_large_files(unuploaded)
    total_files = len(filtered)

    if total_files == 0:
        print("✅ All files under 100MB have been uploaded.")
        return

    uploaded_count = 0
    start_time = time.time()

    while uploaded_count < total_files:
        uploaded = load_uploaded_files()
        all_untracked = get_uncommitted_files()
        unuploaded = [f for f in all_untracked if f and f not in uploaded]
        filtered = filter_large_files(unuploaded)

        remaining = filtered
        batch = remaining[:files_per_commit]

        if not batch:
            break

        print(f"\n📦 Uploading {len(batch)} files: {batch}")
        stage_and_commit(batch)
        save_uploaded_files(batch)
        uploaded_count += len(batch)

        elapsed = time.time() - start_time
        draw_progress_bar(uploaded_count, total_files, elapsed)

        time.sleep(WAIT_SECONDS)

    print("\n✅ All files under 100MB have been uploaded.")

if __name__ == "__main__":
    main()
