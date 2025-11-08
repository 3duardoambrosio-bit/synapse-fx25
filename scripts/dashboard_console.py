# scripts/dashboard_console.py
import json, os, platform, time

def main():
    payload = {
        "system_status": "operational",
        "python": platform.python_version(),
        "cwd": os.getcwd(),
        "timestamp": int(time.time())
    }
    print(json.dumps(payload, ensure_ascii=False))

if __name__ == "__main__":
    main()
