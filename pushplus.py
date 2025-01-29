import requests

class PushPlusNotifier:
    """
    PushPlus 消息推送类
    """
    def __init__(self, pushplus_token):
        """
        初始化 PushPlusNotifier 类

        :param pushplus_token: PushPlus 的用户 Token
        """
        self.url = "http://www.pushplus.plus/send/"
        self.headers = {
            "Content-Type": "application/json"
        }
        self.token = pushplus_token

    def send_message(self, title, content, topic=None):
        """
        发送消息到 PushPlus

        :param title: 消息标题
        :param content: 消息内容
        :param topic: 消息主题（可选）
        """
        payload = {
            "token": self.token,
            "title": title,
            "content": content
        }
        if topic:
            payload["topic"] = topic

        try:
            response = requests.post(self.url, headers=self.headers, json=payload)
            if response.status_code == 200:
                print("消息发送成功！")
                return True
            else:
                print(f"消息发送失败，状态码：{response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"发送消息时发生异常：{e}")
            return False
