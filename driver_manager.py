from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.edge.service import Service
import json

class DriverManager:
    def __init__(self, headless=True, implicitly_wait_time=0.5, page_load_timeout=30):
        """
        浏览器驱动管理类，用于设置和管理 WebDriver
        :param headless: 是否开启无头模式
        :param implicitly_wait_time: 隐式等待时间（秒）
        :param page_load_timeout: 页面加载超时（秒）
        """
        self.headless = headless
        self.implicitly_wait_time = implicitly_wait_time
        self.page_load_timeout = page_load_timeout

    def setup(self):
        """
        初始化并返回一个 Edge WebDriver 实例
        """
        options = Options()
        if self.headless == True:
            options.add_argument("headless")
        options.add_experimental_option("detach", True)    
        options.add_experimental_option('useAutomationExtension', False)
        options.add_experimental_option('excludeSwitches', ['enable-logging','enable-automation'])
        options.add_argument("--disable-notifications")
        options.add_argument('--windows-size=1920,1080')  # 建议
        edge_driver_path = "C:/Users/86199/edgedriver_win64/msedgedriver.exe"
        service = Service(executable_path=edge_driver_path, log_output="nul")
        driver = webdriver.Edge(options=options, service=service)
        driver.implicitly_wait(self.implicitly_wait_time)
        driver.set_page_load_timeout(self.page_load_timeout)
        return driver

    @staticmethod
    def teardown(driver: webdriver.Edge):
        """
        关闭并退出 WebDriver
        :param driver: WebDriver 实例
        """
        driver.quit()

    @staticmethod
    def save_cookies_and_token(driver, file_path):
        """
        保存 Cookies、localStorage 和 sessionStorage 到文件
        :param driver: WebDriver 实例
        :param file_path: 保存路径
        """
        local_storage = driver.execute_script(
            "var items = {}; for (var i = 0; i < localStorage.length; i++) { "
            "var key = localStorage.key(i); items[key] = localStorage.getItem(key); } return items;"
        )
        session_storage = driver.execute_script(
            "var items = {}; for (var i = 0; i < sessionStorage.length; i++) { "
            "var key = sessionStorage.key(i); items[key] = sessionStorage.getItem(key); } return items;"
        )
        data = {
            "cookies": driver.get_cookies(),
            "local_storage": local_storage,
            "session_storage": session_storage,
        }
        with open(file_path, "w") as file:
            json.dump(data, file)
        print(f"登录数据已保存到 {file_path}")

    @staticmethod
    def load_cookies_and_token(driver, file_path):
        """
        从文件加载 Cookies、localStorage 和 sessionStorage
        :param driver: WebDriver 实例
        :param file_path: 文件路径
        """
        with open(file_path, "r") as file:
            data = json.load(file)
            # 加载 Cookies
            for cookie in data["cookies"]:
                driver.add_cookie(cookie)
            # 加载 localStorage
            for key, value in data["local_storage"].items():
                driver.execute_script(f"localStorage.setItem('{key}', '{value}');")
            # 加载 sessionStorage
            for key, value in data["session_storage"].items():
                driver.execute_script(f"sessionStorage.setItem('{key}', '{value}');")
        driver.refresh()
        print("会话数据加载完成")
