import psutil
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import datetime

# --- 設定 ---
MAX_POINTS = 60
UPDATE_INTERVAL = 1000
CPU_COUNT = psutil.cpu_count() or 1

# データ保持用
history = [] # (time, sys_cpu, p_cpu, sys_mem, p_mem, pid, name) のタプルを保存
last_pid = None
colors = ['#FF3B30', '#FF9500'] # 交代時に使う2色（赤とオレンジ）
current_color_idx = 0

fig, (ax_cpu, ax_mem) = plt.subplots(2, 1, figsize=(10, 8))

def get_top_process():
    max_cpu = -1.0
    top_proc = None
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
        try:
            cpu = proc.info.get('cpu_percent')
            if cpu is not None and cpu > max_cpu:
                max_cpu = cpu
                top_proc = proc.info
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return top_proc

def update(frame):
    global last_pid, current_color_idx
    now = datetime.datetime.now()
    
    sys_cpu = psutil.cpu_percent()
    sys_mem = psutil.virtual_memory().percent
    top = get_top_process()
    
    p_pid = top.get('pid') if top else None
    p_name = top.get('name', 'Unknown') if top else "Scanning"
    p_cpu = (top.get('cpu_percent') or 0) / CPU_COUNT if top else 0
    p_mem = top.get('memory_percent') or 0 if top else 0

    # 履歴に追加
    history.append({
        'time': now, 'sys_cpu': sys_cpu, 'p_cpu': p_cpu, 
        'sys_mem': sys_mem, 'p_mem': p_mem, 'pid': p_pid, 'name': p_name
    })
    if len(history) > MAX_POINTS:
        history.pop(0)

    # 描画リセット
    ax_cpu.clear()
    ax_mem.clear()

    # システム全体の背景描画（これは常に一定）
    times = [h['time'] for h in history]
    ax_cpu.plot(times, [h['sys_cpu'] for h in history], color='#00d1b2', alpha=0.2, linestyle='--')
    ax_mem.plot(times, [h['sys_mem'] for h in history], color='#ff3860', alpha=0.2, linestyle='--')

    # PIDごとのセグメント描画
    start_idx = 0
    for i in range(1, len(history)):
        # PIDが変わった、または最後のデータの場合
        if history[i]['pid'] != history[i-1]['pid'] or i == len(history) - 1:
            segment = history[start_idx:i+1]
            seg_times = [s['time'] for s in segment]
            seg_cpu = [s['p_cpu'] for s in segment]
            seg_mem = [s['p_mem'] for s in segment]
            
            # 色の決定（PIDが変わるたびにインデックスを回す）
            color = colors[current_color_idx % len(colors)]
            
            # CPUセグメント描画
            ax_cpu.plot(seg_times, seg_cpu, color=color, linewidth=2)
            # メモリセグメント描画
            ax_mem.plot(seg_times, seg_mem, color='#007AFF', linewidth=2) # メモリは青固定
            
            # PIDが変わった境界に垂直線を引く
            if history[i]['pid'] != history[i-1]['pid']:
                ax_cpu.axvline(history[i]['time'], color='gray', linestyle=':', alpha=0.5)
                current_color_idx += 1 # 次のセグメントの色を変える
            
            start_idx = i

    # 仕上げ（軸設定など）
    ax_cpu.set_ylim(0, 100)
    ax_mem.set_ylim(0, 100)
    ax_cpu.set_title(f"Top Process: {p_name} (PID:{p_pid})", loc='left', fontsize=10)
    ax_cpu.grid(True, alpha=0.2)
    ax_mem.grid(True, alpha=0.2)
    plt.tight_layout()

ani = FuncAnimation(fig, update, interval=UPDATE_INTERVAL, cache_frame_data=False)
plt.show()
