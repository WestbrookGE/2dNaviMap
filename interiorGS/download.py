import os
import time
from huggingface_hub import snapshot_download
from huggingface_hub.utils import HfHubHTTPError, GatedRepoError
import requests.exceptions

# 代理设置
PROXY_URL = "http://127.0.0.1:7890"
os.environ["HTTP_PROXY"] = PROXY_URL
os.environ["HTTPS_PROXY"] = PROXY_URL

# Hugging Face 数据集信息
REPO_ID = "spatialverse/InteriorGS"
LOCAL_DIR = "./InteriorGS"  # 你的目标文件夹

# 设置重试参数
MAX_RETRIES = 5
RETRY_DELAY = 10  # 秒

def download_with_retries():
    """
    尝试下载数据集，并在出现网络错误时重试。
    """
    if not os.path.exists(LOCAL_DIR):
        print(f"文件夹 '{LOCAL_DIR}' 不存在，正在创建...")
        os.makedirs(LOCAL_DIR)
    else:
        print(f"文件夹 '{LOCAL_DIR}' 已存在。")

    print(f"使用代理: {PROXY_URL}")

    for attempt in range(MAX_RETRIES):
        print(f"\n尝试下载 (第 {attempt + 1} 次)...")
        try:
            snapshot_download(
                repo_id=REPO_ID,
                repo_type="dataset",
                local_dir=LOCAL_DIR,
                allow_patterns=["*.png", "*.json"],
                max_workers=8
            )
            print("\n-------------------------------------------")
            print(f"下载完成！所有文件已成功保存到 ./{LOCAL_DIR} 文件夹。")
            return

        except (HfHubHTTPError, requests.exceptions.ConnectionError, OSError) as e:
            # 捕获网络相关的错误
            print(f"\n下载过程中出现网络错误: {e}")
            if attempt < MAX_RETRIES - 1:
                print(f"等待 {RETRY_DELAY} 秒后重试...")
                time.sleep(RETRY_DELAY)
            else:
                print("\n达到最大重试次数，下载失败。请检查您的网络连接和代理设置并重试。")
                break
        
        except GatedRepoError as e:
            # 认证错误
            print(f"\n认证错误: {e}")
            print("请确认您已使用 `huggingface-cli login` 成功登录，并有权访问该数据集。")
            break
        
        except Exception as e:
            # 其他未知错误
            print(f"\n下载过程中出现未知错误: {e}")
            break

if __name__ == "__main__":
    download_with_retries()