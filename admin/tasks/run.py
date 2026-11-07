import subprocess
import os
import time
from pathlib import Path

# ----------------------------
# مسیر پروژه و virtualenv
# ----------------------------
BASE_DIR = Path("/home/hrclub.azaran.group/public_html/")
VENV_PYTHON = BASE_DIR / "venv/bin/python"

# مسیر ذخیره لاگ‌ها
LOG_DIR = BASE_DIR / "celery_logs"
LOG_DIR.mkdir(exist_ok=True)

WORKER_LOG = LOG_DIR / "worker.log"
BEAT_LOG = LOG_DIR / "beat.log"

# ----------------------------
# تغییر مسیر به پروژه
# ----------------------------
os.chdir(BASE_DIR)

# ----------------------------
# دستورات Worker و Beat
# ----------------------------
worker_cmd = [
    str(VENV_PYTHON), "-m", "celery",
    "-A", "bootstrap", "worker",
    "--loglevel=info",
    "--logfile", str(WORKER_LOG)
]

beat_cmd = [
    str(VENV_PYTHON), "-m", "celery",
    "-A", "bootstrap", "beat",
    "--loglevel=info",
    "--logfile", str(BEAT_LOG)
]

# ----------------------------
# فانکشن اجرا با نگهداری
# ----------------------------
def start_process(cmd, name):
    while True:
        print(f"Starting {name}...")
        proc = subprocess.Popen(cmd)
        proc.wait()
        print(f"{name} stopped! Restarting in 5 seconds...")
        time.sleep(5)

# ----------------------------
# اجرای هر دو در پس‌زمینه
# ----------------------------
import threading

worker_thread = threading.Thread(target=start_process, args=(worker_cmd, "Celery Worker"))
beat_thread = threading.Thread(target=start_process, args=(beat_cmd, "Celery Beat"))

worker_thread.start()
beat_thread.start()

worker_thread.join()
beat_thread.join()
