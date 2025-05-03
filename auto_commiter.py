import os
import subprocess
import time

TRACK_FILE = ".upload_tracker"
WAIT_SECONDS = 2  # Optional wait between commits

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

def stage_and_commit(files):
    for file in files:
        subprocess.run(["git", "add", file])
    subprocess.run(["git", "commit", "-m", f"Auto upload next {len(files)} items"])
    subprocess.run(["git", "push"])

def main():
    files_per_commit = ask_batch_size()

    while True:
        uploaded = load_uploaded_files()
        all_untracked = get_uncommitted_files()
        remaining = [f for f in all_untracked if f and f not in uploaded]

        if not remaining:
            print("✅ All files have been uploaded.")
            break

        batch = remaining[:files_per_commit]
        print(f"📦 Uploading {len(batch)} files: {batch}")
        stage_and_commit(batch)
        save_uploaded_files(batch)
        time.sleep(WAIT_SECONDS)

if __name__ == "__main__":
    main()
