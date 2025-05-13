import os
import json
import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from queue import Queue


def move_processed_files():
    # 读取进度文件
    if not os.path.exists('progress.json'):
        messagebox.showerror("错误", "未找到进度文件 progress.json")
        return

    with open('progress.json', 'r') as f:
        progress_data = json.load(f)

    processed_files = progress_data.get("processed_files", [])

    if not processed_files:
        messagebox.showinfo("提示", "没有已处理的文件需要移动")
        return

    # 获取第一个文件所在的目录作为基础目录
    base_dir = os.path.dirname(processed_files[0])
    processed_dir = os.path.join(base_dir, "processed_mca")
    os.makedirs(processed_dir, exist_ok=True)

    # 创建进度窗口
    root = tk.Tk()
    root.title("移动已处理的MCA文件")
    root.geometry("500x150")

    label = tk.Label(root, text="正在移动文件...")
    label.pack(pady=10)

    progress_var = tk.DoubleVar()
    progress_bar = ttk.Progressbar(root, variable=progress_var, maximum=100, length=400)
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
        local_success = 0
        local_failed = []

        while not file_queue.empty():
            try:
                file_path = file_queue.get(block=False)
            except:
                break

            try:
                if os.path.exists(file_path):
                    target_path = os.path.join(processed_dir, os.path.basename(file_path))
                    os.replace(file_path, target_path)
                    local_success += 1
                else:
                    local_failed.append(file_path)
            except Exception as e:
                local_failed.append(file_path)
                print(f"Worker {worker_id}: 移动文件 {file_path} 时出错: {e}")
            finally:
                file_queue.task_done()

        # 批量更新全局计数
        with lock:
            processed_count += local_success
            failed_files.extend(local_failed)

            # 每处理 50 个文件更新一次 UI
            if processed_count % 50 == 0 or file_queue.empty():
                progress = processed_count / total_files * 100
                root.after(0, lambda p=progress: progress_var.set(p))
                root.after(0, lambda: status_label.config(
                    text=f"已移动 {processed_count}/{total_files} 个文件"
                ))

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
    move_processed_files()