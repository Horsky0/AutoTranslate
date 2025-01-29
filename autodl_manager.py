from selenium.webdriver.common.by import By
from sshtunnel import SSHTunnelForwarder
import paramiko
import time, sys

class AutoDLManager:
    def __init__(self, driver, account, password, cookies_path, min_balance=3):
        """
        AutoDL 管理类
        :param driver: 浏览器驱动实例
        :param account: 登录账户
        :param password: 登录密码
        :param cookies_path: Cookies 文件路径
        :param min_balance: 最低余额要求
        """
        self.driver = driver
        self.account = account
        self.password = password
        self.cookies_path = cookies_path
        self.container_index = 0
        self.min_balance = min_balance

    def login(self):
        """
        登录 AutoDL 并保存会话数据
        """
        try:
            self.driver.get("https://www.autodl.com/console/instance/list")
            from driver_manager import DriverManager
            DriverManager.load_cookies_and_token(self.driver, self.cookies_path)
            self.driver.get("https://www.autodl.com/console/instance/list")
            if self.driver.find_element(By.CLASS_NAME, "user-info").is_displayed():
                print("AutoDL: 恢复登录状态成功")
                return
        except Exception:
            print("AutoDL: 恢复登录状态失败, 正在重新登录...")

        # 手动登录流程
        self.driver.get("https://www.autodl.com/login")
        account_input = self.driver.find_element(
            By.XPATH,
            "/html/body/div[1]/div[2]/div[3]/div/div[2]/div[1]/form/div[2]/div/div[1]/input",
        )
        account_input.clear()
        account_input.send_keys(self.account)

        password_input = self.driver.find_element(
            By.XPATH,
            "/html/body/div[1]/div[2]/div[3]/div/div[2]/div[1]/form/div[3]/div/div/input",
        )
        password_input.clear()
        password_input.send_keys(self.password)

        login_button = self.driver.find_element(
            By.XPATH,
            "/html/body/div[1]/div[2]/div[3]/div/div[2]/div[1]/button[1]",
        )
        login_button.click()
        time.sleep(1)

        self.driver.get("https://www.autodl.com/console/instance/list")
        DriverManager.save_cookies_and_token(self.driver, self.cookies_path)

    def check_balance(self):
        """
        检查 AutoDL 账户余额
        """
        self.driver.get("https://www.autodl.com/console/homepage/personal")
        time.sleep(2)
        balance_element = self.driver.find_element(By.CLASS_NAME, "num-bold")
        balance = float(balance_element.text)
        print(f"当前账户余额: ￥{balance}")
        
        if balance < self.min_balance:
            raise ValueError(f"余额不足（小于￥{self.min_balance}），无法启动服务器")
    
    def start_server(self):
        """
        启动 AutoDL 服务器
        """
        self.driver.get("https://www.autodl.com/console/instance/list")
        gpu_status = self.driver.find_elements(By.CLASS_NAME, "gpuTips")
        boot_buttons = self.driver.find_elements(
            By.CSS_SELECTOR, ".el-button.el-button--text.el-button--small.thirteenSize"
        )

        for i, element in enumerate(gpu_status):
            if element.text == "GPU充足":
                print(f"使用第 {i + 1} 个容器")
                self.container_index = i
                boot_buttons[i * 2].click()
                break
        else:
            raise ValueError("未找到GPU充足的服务器")

        time.sleep(1)
        assert self.driver.find_element(
            By.XPATH,
            "/html/body/div[41]/div/div[2]/div[1]/div[2]/div/div/span[1]",
        ).text == "确认开机吗？", "开机确认异常"
        confirm_button = self.driver.find_element(
            By.CSS_SELECTOR, ".el-button.el-button--default.el-button--small.el-button--primary"
        )
        confirm_button.click()

        start_time = time.time()
        timeout = 30
        while self.driver.find_elements(By.CLASS_NAME, "status")[self.container_index].text != "运行中":
            if time.time() - start_time > timeout:
                raise Exception("开机状态异常")
            time.sleep(0.5)

        print("服务器已开机")
        self._setup_ssh()

    def shutdown_server(self):
        """
        关闭 AutoDL 服务器
        """
        self.driver.get("https://www.autodl.com/console/instance/list")
        shutdown_button = self.driver.find_elements(
            By.CSS_SELECTOR, ".el-button.el-button--text.el-button--small.thirteenSize"
        )[self.container_index * 2]
        shutdown_button.click()

        time.sleep(1)
        assert self.driver.find_element(
            By.XPATH,
            "/html/body/div[41]/div/div[2]/div[1]/div[2]/div/div/span[1]",
        ).text == "确认关机吗？", "关机确认异常"
        confirm_button = self.driver.find_element(
            By.CSS_SELECTOR, ".el-button.el-button--default.el-button--small.el-button--primary"
        )
        confirm_button.click()

        start_time = time.time()
        timeout = 30
        while self.driver.find_elements(By.CLASS_NAME, "status")[self.container_index].text != "已关机":
            if time.time() - start_time > timeout:
                raise Exception("关机状态异常")
            time.sleep(0.5)

        from driver_manager import DriverManager
        DriverManager.save_cookies_and_token(self.driver, self.cookies_path)
        print("服务器已关机")

    def _setup_ssh(self):
        """
        设置 SSH 隧道并启动远程命令
        """
        self.driver.execute_script(
            """
            document.addEventListener('copy', (event) => {
                const selection = document.getSelection().toString();
                window._lastCopiedText = selection;
            });
            """
        )
        ssh_buttons = self.driver.find_elements(By.CSS_SELECTOR, ".iconfont.icon-fuzhi")
        ssh_buttons[0].click()
        ssh_command = self.driver.execute_script("return window._lastCopiedText;")
        ssh_buttons[1].click()
        ssh_password = self.driver.execute_script("return window._lastCopiedText;")

        to_insert = "-L 6006:127.0.0.1:6006"
        parts = ssh_command.split(" ", 3)
        ssh_command = f"{parts[0]} {parts[1]} {parts[2]} {to_insert} {parts[3]}"
        ssh_port = int(parts[2])
        ssh_user, ssh_host = parts[3].split("@")
        local_port = 6006
        remote_host = "127.0.0.1"
        remote_port = 6006

        tunnel = SSHTunnelForwarder(
            (ssh_host, ssh_port),
            ssh_username=ssh_user,
            ssh_password=ssh_password,
            remote_bind_address=(remote_host, remote_port),
            local_bind_address=("0.0.0.0", local_port),
        )
        tunnel.start()
        print(f"本地端口 {local_port} 已转发到远程 {remote_host}:{remote_port}")

        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(ssh_host, port=ssh_port, username=ssh_user, password=ssh_password)
        client.exec_command("./run")
        time.sleep(5)

        try:
            self.driver.get("http://127.0.0.1:6006/v1/models")
            print("SSH 连接已建立，端口转发成功")
        except Exception as e:
            raise Exception(f"测试连接失败: {str(e)}")