
import threading
import time
import psutil
import datetime
import json
import subprocess
import platform

stop_event = threading.Event()


def get_current_time():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
def get_cpu_usage():
    return psutil.cpu_percent()
def get_memory_usage():
    return psutil.virtual_memory().percent
def write_log():
    last_cpu_notification = 0
    last_memory_notification = 0
    with open("config.json", 'r') as file:
        config = json.load(file)
        cpu_limit = config["border_cpu"]
        memory_limit = config["border_memory"]
        interval = config["interval"]
    while not stop_event.is_set():
        current_time = time.time()
        if cpu_limit <= get_cpu_usage() and current_time - last_cpu_notification > 60:
            subprocess.run([
                "osascript",
                "-e",
                'display notification "CPU usage is over the limit!" with title "Task Manager"'
            ])
            last_cpu_notification = current_time
        if memory_limit <= get_memory_usage() and current_time - last_memory_notification > 60:
            subprocess.run([
                "osascript",
                "-e",
                'display notification "Memory usage is over the limit!" with title "Task Manager"'
            ])
            last_memory_notification = current_time
        log = f"{get_current_time()} | {get_cpu_usage()}% | {get_memory_usage()}%"
        with open("log.txt", "a") as f:
            f.write(log + "\n")
        time.sleep(interval)

def menu():
    while True:
        print("1. System information")
        print("2. Top 5 Processes by memory usage")
        print("0. Exit")
        unos = int(input("Choose an option: "))
        if unos == 0:
            stop_event.set()
            log_thread.join()
            break
        elif unos == 1:
            print(
                f"{'OS:':<25}{platform.system():>15}\n"
                f"{'Python Version:':<25}{platform.python_version():>15}\n"
                f"{'Physical Cores:':<25}{psutil.cpu_count(logical=False):>15}\n"
                f"{'Logical Cores:':<25}{psutil.cpu_count(logical=True):>15}\n"
                f"{'Total Memory:':<25}{psutil.virtual_memory().total / (2 ** 30):>15.2f} GB"
            )
        elif unos == 2:
            processes = []
            for p in psutil.process_iter(['name', 'memory_info']):
                try:
                    # Filter out processes missing memory_info to prevent errors
                    if p.info['memory_info'] is not None:
                        processes.append(p)
                except (psutil.AccessDenied, psutil.NoSuchProcess):
                    pass

            processes.sort(key=lambda p: p.memory_info().rss, reverse=True)

            print(f"{'Name':<25}{'Memory':<15}")
            print("-" * 40)

            for process in processes[:5]:
                try:
                    name = process.name()
                    mem_gb = process.memory_info().rss / (2 ** 30)
                    print(f"{name:<25}{mem_gb:<15.2f}GB")
                except (psutil.AccessDenied, psutil.NoSuchProcess):
                    pass

log_thread = threading.Thread(target=write_log)
log_thread.start()
menu()
