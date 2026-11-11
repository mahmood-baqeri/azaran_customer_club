import os
import uvicorn
from config import settings

if __name__ == "__main__":
    DEVELOPMENT = os.environ.get('DEVELOPMENT', 'local')
    if DEVELOPMENT == 'server':
        CMD = "uvicorn config.asgi:application --host 0.0.0.0 --port 8000 --workers 4"
        
        # اجرای در پس‌زمینه روی سرور ابری
        print("🚀 Running in background with nohup on server...")
        os.system(f"nohup {CMD} > server.log 2>&1 &")
    else:
        
        if __name__ == "__main__":
            uvicorn.run(
                "config.asgi:application",
                host="0.0.0.0",
                port=8000,
                workers=1
            )

        # os.system("nohup python3 run.py > server.log 2>&1 &")
