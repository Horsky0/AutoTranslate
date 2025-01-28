from driver_manager import DriverManager
from autodl_manager import AutoDLManager
from lightnovel_manager import LightNovelManager
import traceback
import sys
import json

DEBUG = True

def main():
    try:
        # 读取 JSON 文件
        with open("data/config.json", "r") as file:
            config = json.load(file)

        # 加载账户和密码
        lightnovel_account = config["AutoNovel_account"]
        lightnovel_password = config["AutoNovel_password"]
        lightnovel_cookies_path = "data/AutoNovel_cookies.json"

        autodl_account = config["AutoDL_account"]
        autodl_password = config["AutoDL_password"]
        autodl_cookies_path = "data/AutoDL_cookies.json"

        # 初始化浏览器驱动
        driver_manager = DriverManager(headless=True)
        lightnovel_driver = driver_manager.setup()
        autodl_driver = driver_manager.setup()

        # 创建管理器实例
        lightnovel_manager = LightNovelManager(
            lightnovel_driver, lightnovel_account, lightnovel_password, lightnovel_cookies_path
        )
        autodl_manager = AutoDLManager(
            autodl_driver, autodl_account, autodl_password, autodl_cookies_path
        )

        # 执行任务
        lightnovel_manager.login()
        lightnovel_manager.get_book_list()
        autodl_manager.login()
        autodl_manager.start_server()
        lightnovel_manager.translate_books()
        autodl_manager.shutdown_server()

        # 关闭驱动
        driver_manager.teardown(lightnovel_driver)
        driver_manager.teardown(autodl_driver)

    except Exception as e:
        if DEBUG:
            print("\n--- 错误详情 ---")
            traceback.print_exc()
            print("---------------\n")
        else:
            print(f"错误: {str(e)}")

        # 确保资源释放
        try:
            autodl_manager.shutdown_server()
        except Exception:
            if DEBUG:
                print("\n--- 服务器关机错误详情 ---")
                traceback.print_exc()
                print("---------------\n")
            else:
                pass
        sys.exit()

if __name__ == "__main__":
    main()
