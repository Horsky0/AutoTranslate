from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from driver_manager import DriverManager
import time

class LightNovelManager:
    def __init__(self, driver, account, password, cookies_path, timeout=30):
        """
        轻小说翻译机器人管理类
        :param driver: 浏览器驱动实例
        :param account: 登录账户
        :param password: 登录密码
        :param cookies_path: Cookies 文件路径
        :param timeout: 页面元素寻找超时/s
        """
        self.driver = driver
        self.account = account
        self.password = password
        self.cookies_path = cookies_path
        self.translate_list = []
        self.timeout = timeout

    def login(self):
        """
        登录轻小说翻译平台
        """
        try:
            self.driver.get("https://books.fishhawk.top/favorite/web")
            DriverManager.load_cookies_and_token(self.driver, self.cookies_path)
            self.driver.get("https://books.fishhawk.top/favorite/web")
            wait = WebDriverWait(self.driver, self.timeout)
            wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, "n-list-item"))
            )
            if self.driver.find_element(By.CLASS_NAME, "n-list-item").is_displayed():
                print("LightNovel: 恢复登录状态成功")
                return
        except Exception:
            print("LightNovel: 恢复登录状态失败, 正在重新登录...")

        self.driver.get("https://books.fishhawk.top/sign-in")
        account_input, password_input = self.driver.find_elements(By.CLASS_NAME, "n-input__input-el")
        account_input.clear()
        account_input.send_keys(self.account)
        password_input.clear()
        password_input.send_keys(self.password)

        login_button = self.driver.find_element(By.CLASS_NAME, "__button-131ezvy-lmmp")
        login_button.click()
        time.sleep(0.5)
        self.driver.get("https://books.fishhawk.top/favorite/web")
        DriverManager.save_cookies_and_token(self.driver, self.cookies_path)

    def get_book_list(self):
        """
        获取需要翻译的书目
        """
        print("正在获取需要翻译的书目...")
        wait = WebDriverWait(self.driver, self.timeout)
        wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".n-pagination-item.n-pagination-item--clickable"))
        )
        num_pages = int(
            self.driver.find_elements(By.CSS_SELECTOR, ".n-pagination-item.n-pagination-item--clickable")[-1].text
        )
        for i in range(num_pages):
            self.driver.get(f"https://books.fishhawk.top/favorite/web?page={i+1}")
            wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, "n-list-item"))
            )
            book_list = self.driver.find_elements(By.CLASS_NAME, "n-list-item")
            for book in book_list:
                translation_info = book.find_element(By.CSS_SELECTOR, ".n-text.__text-131ezvy-d3").text
                parts = translation_info.split("/")
                total = sakura = 0
                for part in parts:
                    part = part.strip()
                    if part.startswith("总计"):
                        total = int(part.split()[1])
                    elif part.startswith("Sakura"):
                        sakura = int(part.split()[1])
                if total > sakura:
                    html = book.find_element(By.CSS_SELECTOR, ".n-a.__a-131ezvy")
                    self.translate_list.append(html.get_attribute("href"))

        if not self.translate_list:
            print("没有需要翻译的书目！")
            return 'Exit'
        else:
            return 'Continue'

    def translate_books(self):
        """
        翻译书目
        """
        print("正在加入翻译列表...")
        wait = WebDriverWait(self.driver, self.timeout)
        for url in self.translate_list:
            if url:
                self.driver.get(url)
                wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".__button-131ezvy-lmmd.n-button.n-button--default-type.n-button--medium-type"))
                )
                self.driver.find_elements(
                    By.CSS_SELECTOR,
                    value=".__button-131ezvy-lmmd.n-button.n-button--default-type.n-button--medium-type",
                )[3].click()
                time.sleep(0.5)

        print("翻译开始：")
        self.driver.get("https://books.fishhawk.top/workspace/sakura")
        wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".__button-131ezvy-dfltmd.n-button.n-button--default-type.n-button--tiny-type.n-button--secondary"))
                )
        self.driver.find_elements(
            By.CSS_SELECTOR,
            value=".__button-131ezvy-dfltmd.n-button.n-button--default-type.n-button--tiny-type.n-button--secondary",
        )[1].click()

        old_logs = []
        wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".n-scrollbar-content"))
                )
        log_container = self.driver.find_elements(
            By.CSS_SELECTOR,
            value=".n-scrollbar-content",
        )[-1]
        start_time=time.time()
        while True:
            try:
                logs = log_container.find_elements(By.XPATH, ".//div")
                current_logs = [log.text.strip() for log in logs if log.text.strip()]                
                if len(current_logs) < len(old_logs):
                    old_logs = []
                if len(current_logs) != len(old_logs):
                    start_time=time.time()
                if time.time() - start_time > 30:
                    break

                new_logs = [log for log in current_logs if log not in old_logs]
                for log in new_logs:
                    print("--" + log)
                old_logs = current_logs
            except:
                pass
            
            time.sleep(0.5)

            try:
                if (
                    self.driver.find_element(By.XPATH, value="/html/body/div[1]/div/div/div/div[2]/div/div/div/div[4]/div[2]").text
                    == "没有任务"
                ):
                    break
            except:
                continue

        print("翻译结束！")
