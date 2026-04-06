import psutil
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import time

# --- 設定 for mac---
UPDATE_INTERVAL = 1000 
HISTORY_LIMIT = 60      

times, cpu_values, mem_values = [], [], []
start_time = time.time()

# 初回スキャン
psutil.cpu_percent(interval=None)

def get_current_top_cpu_process():
    top_proc_info = None
    max_cpu = -1.0
    
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
        try:
            cpu = proc.info['cpu_percent']
            # --- 修正ポイント: cpu が None でないことを確認 ---
            if cpu is not None and cpu > max_cpu:
                max_cpu = cpu
                top_proc_info = proc.info
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
    return top_proc_info

fig, (ax_cpu, ax_mem) = plt.subplots(2, 1, figsize=(10, 8), sharex=True)

def update(frame):
    current_time = time.time() - start_time
    top = get_current_top_cpu_process()
    
    # topが取得できなかった場合の安全策
    cpu_val = top['cpu_percent'] if (top and top['cpu_percent'] is not None) else 0
    mem_val = top['memory_percent'] if (top and top['memory_percent'] is not None) else 0
    info_text = f"{top['name']} (PID:{top['pid']})" if top else "Scanning..."

    times.append(current_time)
    cpu_values.append(cpu_val)
    mem_values.append(mem_val)

    if len(times) > HISTORY_LIMIT:
        times.pop(0)
        cpu_values.pop(0)
        mem_values.pop(0)

    ax_cpu.clear()
    ax_cpu.plot(times, cpu_values, color='#FF3B30', linewidth=1.5)
    ax_cpu.set_title(f"Target: {info_text}", loc='left', fontsize=10)
    ax_cpu.set_ylabel("CPU (%)")
    ax_cpu.grid(True, alpha=0.2)
    ax_cpu.set_ylim(0, max(100, (max(cpu_values) * 1.1) if cpu_values else 100))

    ax_mem.clear()
    ax_mem.plot(times, mem_values, color='#007AFF', linewidth=1.5)
    ax_mem.set_ylabel("Mem (%)")
    ax_mem.set_xlabel("Time (s)")
    ax_mem.grid(True, alpha=0.2)
    ax_mem.set_ylim(0, max(20, (max(mem_values) * 1.2) if mem_values else 20))

    plt.tight_layout()

# Macでの描画安定化のため cache_frame_data=False を指定
ani = FuncAnimation(fig, update, interval=UPDATE_INTERVAL, cache_frame_data=False)
plt.show()
