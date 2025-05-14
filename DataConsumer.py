import os
import time
import random
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


def clear_screen():
    # 清屏指令
    if os.name == 'nt':
        # Windows
        os.system('cls')
    else:
        # Mac和Linux
        os.system('clear')


def bytes_to_mb_gb(byte_count):
    # 单位转换
    if byte_count >= 1000**3:  # 如果大于或等于1 GB
        return byte_count / (1000**3), 'GB'
    elif byte_count >= 1000**2:  # 如果大于或等于1 MB
        return byte_count / (1000**2), 'MB'
    else:
        return byte_count, 'Bytes'


def download_file(url, user_agent, retry_count=3):
    # 下载文件并返回下载的字节数
    headers = {
        'User-Agent': user_agent
    }
    
    # 创建一个具有重试功能的会话
    session = requests.Session()
    
    # 设置重试策略
    retries = Retry(
        total=retry_count,
        backoff_factor=0.5,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET", "HEAD"]
    )
    
    # 将重试适配器挂载到会话对象上
    session.mount('http://', HTTPAdapter(max_retries=retries))
    session.mount('https://', HTTPAdapter(max_retries=retries))

    try:
        # 初始化计数器
        total_downloaded = 0

        # 使用流式请求，减少内存占用
        # 建立连接10s超时，下载文件每块的读取超时为30s，预防龟速任务占用线程池
        response = session.get(url, headers=headers, stream=True, timeout=(10, 30))
        response.raise_for_status()  # 检查请求是否成功

        # 下载文件时分块读取
        # 对小内存＆低配置设备优化（已调优）
        # 降低单次块大小，提高稳定性
        for chunk in response.iter_content(chunk_size=1024 * 512):  # 每次读取 0.5MB
            if chunk:  # 过滤掉保持连接活跃的空块
                total_downloaded += len(chunk)

        return total_downloaded

    except requests.exceptions.RequestException as e:
        print(f"下载错误: {e}")
        return 0
    finally:
        # 确保会话被关闭
        session.close()


def main():
    # User-agent 数组，以便使用随机的浏览器请求头
    # User-agent 数据来源于互联网，可能不准确
    user_agent_array = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:94.0) Gecko/20100101 Firefox/94.0',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.1 Safari/605.1.15',
        'Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Mobile Safari/537.36',
        'Mozilla/5.0 (Android 13; Mobile; SM-G981B) Gecko/64.0 Firefox/64.0',
        'Mozilla/5.0 (Linux; Android 12;SM-G981B) AppleWebKit/537.36 (KHTML, like Gecko) SamsungBrowser/14.0 Chrome/96.0.4664.45 Mobile Safari/537.36',
        'Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1 Edg/131.0.0.0',
        'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/605.1.15',
        'Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/96.0.4664.45 Mobile/15E148 Safari/605.1.15'
    ]

    # 设置目标URL
    while True:
        try:
            url = input("\n 目标URL链接:\n")
            if not url:
                raise ValueError("输入不能为空")
            # 检查URL格式
            if not url.startswith(('http://', 'https://')):
                raise ValueError("URL必须以http://或https://开头")
            break
        except ValueError as e:
            print(f" 错误信息: {e}")

    # 设置下载次数
    while True:
        try:
            repeat_count = input("\n 下载次数: ")
            if not repeat_count:
                raise ValueError("输入不能为空")
            repeat_count = int(repeat_count)
            if repeat_count <= 0:
                raise ValueError("输入必须大于0")
            break
        except ValueError as e:
            print(f" 错误信息: {e}")

    # 设置下载间隔 (可选)
    interval = 0
    use_interval = input("\n 是否需要设置下载间隔? (y/n): ").lower() == 'y'
    if use_interval:
        while True:
            try:
                interval = input("\n 下载间隔(秒): ")
                if not interval:
                    raise ValueError("输入不能为空")
                interval = float(interval)
                if interval < 0:
                    raise ValueError("输入不能小于0")
                break
            except ValueError as e:
                print(f" 错误信息: {e}")

    # 设置最大线程数
    while True:
        try:
            max_workers = input("\n 最大线程数: ")
            if not max_workers:
                raise ValueError("输入不能为空")
            max_workers = int(max_workers)
            if max_workers <= 0:
                raise ValueError("输入必须大于0")
            break
        except ValueError as e:
            print(f" 错误信息: {e}")

    # 设置重试次数
    retry_count = 3
    custom_retry = input("\n 是否自定义重试次数? (y/n): ").lower() == 'y'
    if custom_retry:
        while True:
            try:
                retry_count = input("\n 重试次数: ")
                if not retry_count:
                    raise ValueError("输入不能为空")
                retry_count = int(retry_count)
                if retry_count < 0:
                    raise ValueError("输入不能小于0")
                break
            except ValueError as e:
                print(f" 错误信息: {e}")

    print('\n 正在启动测试任务... \n')

    # 任务初始化
    total_bytes = 0  # 初始化流量计数器
    completed_tasks = 0  # 初始化完成的任务次数
    failed_tasks = 0  # 失败任务计数

    time.sleep(3)
    clear_screen()

    print('\n 任务正在进行中 \n')
    start_time = time.time()  # 记录开始时间

    # 使用线程池
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = []
        for i in range(repeat_count):
            user_agent = random.choice(user_agent_array)
            futures.append(executor.submit(download_file, url, user_agent, retry_count))
            # 等待指定的时间间隔
            if use_interval and interval > 0:
                time.sleep(interval)

        for future in as_completed(futures):
            downloaded_bytes = future.result()
            total_bytes += downloaded_bytes
            completed_tasks += 1  # 任务完成次数加1
            
            if downloaded_bytes == 0:
                failed_tasks += 1  # 失败任务计数

            size, unit = bytes_to_mb_gb(downloaded_bytes)
            total_size, total_unit = bytes_to_mb_gb(total_bytes)

            # 显示完成的任务次数以及对应的下载信息
            print(f"  ({completed_tasks}/{repeat_count}) , 当前任务: {size:.2f} {unit} , 总计消耗: {total_size:.2f} {total_unit}")

    # 计算测试持续时间
    duration = time.time() - start_time
    
    # 显示优化
    time.sleep(3)
    clear_screen()

    # 任务结束
    print('\n 测试任务已完成 \n')

    # 显示统计信息
    total_size, total_unit = bytes_to_mb_gb(total_bytes)
    print(f"\n 任务总数: {repeat_count}")
    print(f" 成功任务: {completed_tasks - failed_tasks}")
    print(f" 失败任务: {failed_tasks}")
    print(f" 成功率: {((completed_tasks - failed_tasks) / completed_tasks * 100):.2f}%")
    print(f" 流量消耗: {total_size:.2f} {total_unit}")
    print(f" 测试持续时间: {duration:.2f} 秒")
    
    if duration > 0:
        speed, speed_unit = bytes_to_mb_gb(total_bytes / duration)
        print(f" 平均下载速度: {speed:.2f} {speed_unit}/s")
    
    input("\n\n 按任意键退出本工具")


if __name__ == "__main__":
    clear_screen()
    print(" ")

    # Info部分
    print(" --------------------------------------------------\n ")
    print("     欢迎使用 ZiChen's Data Consumer\n")
    print("     本工具旨在通过多线程下载指定文件测试当前")
    print("     宽带/流量的稳定性，以及途径相关设备的稳定性。\n")
    print("     Release Version: 1.0.1")
    print("     Release Date: 20250514\n")
    print(" --------------------------------------------------\n ")

    # EULA部分
    print(" 本工具仅供测试使用，确保有权进行下载测试，任何不良后果均由使用者承担。\n")
    input(" 按任意键即视为同意上述内容，如不同意请停止使用")

    clear_screen()

    main()
