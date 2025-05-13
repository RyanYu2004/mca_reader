import os
import json
import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import sys  # 添加sys模块导入
from concurrent.futures import ThreadPoolExecutor, as_completed
from queue import Queue

# 启用高DPI支持（Windows系统）
def enable_high_dpi_support():
    if sys.platform.startswith('win'):
        from ctypes import windll
        try:
            # 尝试启用系统DPI感知
            windll.shcore.SetProcessDpiAwareness(2)  # 2 = PROCESS_PER_MONITOR_DPI_AWARE
        except:
            # 回退到系统DPI感知
            windll.user32.SetProcessDPIAware()

def move_processed_files():
    if not os.path.exists('progress.json'):
        messagebox.showerror("错误", "未找到进度文件 progress.json")
        return

    with open('progress.json', 'r') as f:
        progress_data = json.load(f)

    processed_files = progress_data.get("processed_files", [])
    if not processed_files:
        messagebox.showinfo("提示", "没有已处理的文件需要移动")
        return

    base_dir = os.path.dirname(processed_files[0])
    processed_dir = os.path.join(base_dir, "processed_mca")
    os.makedirs(processed_dir, exist_ok=True)

    # 创建进度窗口
    root = tk.Tk()
    root.title("移动已处理的MCA文件")
    root.geometry("500x150")
    root.resizable(False, False)  # 禁止调整窗口大小

    # 创建居中的信息标签
    info_frame = tk.Frame(root)
    info_frame.pack(fill=tk.X, padx=10, pady=10)

    label = tk.Label(info_frame, text="正在移动文件...")
    label.pack(expand=True)

    progress_var = tk.DoubleVar()
    progress_bar = ttk.Progressbar(root, variable=progress_var, maximum=len(processed_files), length=400)
    progress_bar.pack(pady=10)

    status_label = tk.Label(root, text="准备中...")
    status_label.pack(pady=10)

    total_files = len(processed_files)
    processed_count = 0
    failed_files = []
    lock = threading.Lock()
    file_queue = Queue()

    # 将文件路径放入队列
    for file_path in processed_files:
        file_queue.put(file_path)

    def batch_move_files(worker_id):
        nonlocal processed_count
        while not file_queue.empty():
            try:
                file_path = file_queue.get()  # 使用block=True等待获取，避免空队列异常
                try:
                    if os.path.exists(file_path):
                        target_path = os.path.join(processed_dir, os.path.basename(file_path))
                        os.replace(file_path, target_path)
                    else:
                        failed_files.append(file_path)
                except Exception as e:
                    failed_files.append(file_path)
                    print(f"Worker {worker_id}: 移动文件 {file_path} 时出错: {e}")
                finally:
                    file_queue.task_done()  # 标记任务完成

                    # 每个文件移动后更新UI（线程安全）
                    with lock:
                        processed_count += 1
                        progress = processed_count
                        root.after(0, lambda p=progress: progress_var.set(p))
                        root.after(0, lambda: status_label.config(
                            text=f"已移动 {processed_count}/{total_files} 个文件"
                        ))
            except Exception as e:
                print(f"Worker {worker_id} 处理队列时出错: {e}")

    def move_files_thread():
        # 根据 CPU 核心数动态设置线程数
        num_workers = min(os.cpu_count() * 4, 100)  # 最多 100 个线程
        start_time = time.time()

        with ThreadPoolExecutor(max_workers=num_workers) as executor:
            # 创建并启动工作线程
            futures = [executor.submit(batch_move_files, i) for i in range(num_workers)]

            # 等待所有任务完成
            for future in as_completed(futures):
                future.result()  # 获取结果，触发异常处理

        elapsed_time = time.time() - start_time
        print(f"处理完成，耗时: {elapsed_time:.2f} 秒")

        # 处理完成后更新UI
        root.after(0, show_completion)

    def show_completion():
        progress_bar.destroy()
        status_label.destroy()
        label.destroy()

        success_count = total_files - len(failed_files)
        result_text = f"已完成！\n成功移动 {success_count} 个文件"
        if failed_files:
            result_text += f"\n{len(failed_files)} 个文件移动失败"

        # 创建结果和按钮的容器
        result_frame = tk.Frame(root)
        result_frame.pack(pady=20)

        # 结果文本
        tk.Label(result_frame, text=result_text).pack(pady=(0, 10))

        # 上移的关闭按钮
        tk.Button(result_frame, text="关闭", command=root.destroy).pack(pady=5)

    # 启动移动文件的线程
    threading.Thread(target=move_files_thread, daemon=True).start()

    root.mainloop()


if __name__ == "__main__":
    # 启用高DPI支持
    enable_high_dpi_support()
    move_processed_files()
