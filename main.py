from driver_manager import DriverManager
from autodl_manager import AutoDLManager
from lightnovel_manager import LightNovelManager
from pushplus import PushPlusNotifier
import traceback
import sys
import json
from datetime import datetime
import builtins

DEBUG = False

LOG_FILE = "data/log.txt"

# 重定义全局的 print 函数
original_print = print
log_list=''

def custom_print(*args, **kwargs):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    original_print( *args, **kwargs)
    with open(LOG_FILE, "a+", encoding="utf-8") as file:
        original_print(f"[{timestamp}]", *args, file=file, **kwargs)
    message = " ".join(map(str, args))  # 将参数拼接成字符串
    global log_list
    log_list += f"{message}\n"

# 替换 builtins.print
builtins.print = custom_print

def main():
    try:
        print('--- LOG START ---')
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
        
        pushplus_token=config["pushplus_token"]
        
        # 创建消息推送
        pushplus=PushPlusNotifier(pushplus_token=pushplus_token)

        # 初始化浏览器驱动
        driver_manager = DriverManager(headless=True)
        lightnovel_driver = driver_manager.setup()
        autodl_driver = driver_manager.setup()

        # 创建管理器实例
        lightnovel_manager = LightNovelManager(
            lightnovel_driver, lightnovel_account, lightnovel_password, lightnovel_cookies_path
        )
        autodl_manager = AutoDLManager(
            autodl_driver, autodl_account, autodl_password, autodl_cookies_path, min_balance=2.5
        )

        # 执行任务
        lightnovel_manager.login()
        if lightnovel_manager.get_book_list()=='Exit':
            pushplus.send_message('没有需要翻译的书目', log_list)
            sys.exit()
        autodl_manager.login()
        autodl_manager.check_balance()
        
    except Exception as e:
        if DEBUG:
            builtins.print = original_print
            traceback.print_exc()
        else:
            tb = traceback.extract_tb(e.__traceback__)
            filename, line_number, func_name, text = tb[-1]  # 获取最后一个错误的位置信息
            error_message = f"错误信息: {str(e)}，文件: {filename}，行号: {line_number}"
            print(f"服务器开机前错误: [{error_message}]")
            pushplus.send_message('程序错误，服务器未开机', log_list)
            
        sys.exit()
        
    #-------------------------------------------------------------
    
    try:
        autodl_manager.start_server()
        lightnovel_manager.translate_books()
        autodl_manager.shutdown_server()

        # 关闭驱动
        driver_manager.teardown(lightnovel_driver)
        driver_manager.teardown(autodl_driver)
        
    except Exception as e:
        if DEBUG:
            builtins.print = original_print
            traceback.print_exc()
        else:
            tb = traceback.extract_tb(e.__traceback__)
            filename, line_number, func_name, text = tb[-1]  # 获取最后一个错误的位置信息
            error_message = f"错误信息: {str(e)}，文件: {filename}，行号: {line_number}"
            print(f"服务器开机后错误: [{error_message}]")

        # 确保资源释放
        try:
            autodl_manager.shutdown_server()
            pushplus.send_message('程序错误，服务器已自动关机', log_list)
        except Exception as err:
            if DEBUG:
                builtins.print = original_print
                traceback.print_exc()
            else:
                tb = traceback.extract_tb(e.__traceback__)
                filename, line_number, func_name, text = tb[-1]  # 获取最后一个错误的位置信息
                error_message = f"错误信息: {str(e)}，文件: {filename}，行号: {line_number}"
                print(f"⚠服务器关机错误! [{error_message}]")
                pushplus.send_message('⚠程序错误，服务器未关机！！！', log_list)
                
        sys.exit()
        
    pushplus.send_message('翻译任务已完成', log_list)

if __name__ == "__main__":
    main()
    