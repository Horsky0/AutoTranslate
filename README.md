# AutoTranslate

本项目是基于Selenium构建的自动化定时翻译脚本，可对[轻小说机翻网站](https://books.fishhawk.top)“我的收藏”列表的轻小说建立自动化翻译任务，从而实现对更新小说的自动化翻译，并使用[PushPlus](www.pushplus.plus) 通过微信公众号推送运行结果。

## 功能

- 自动登录 [AutoDL](www.autodl.com) ，检查账户余额，启动/关闭服务器，设置 SSH 隧道并启动远程命令。
- 自动登录[轻小说机翻网站](https://books.fishhawk.top)，获取需要翻译的书目列表，执行翻译任务并监控翻译进度。
- 使用[PushPlus](www.pushplus.plus)推送消息通知，支持错误提醒和任务完成通知。

## 快速开始

### 网站注册

请确保已有以下三个网站的账号，并完成相关设置

- 注册[轻小说机翻网站](https://books.fishhawk.top)
- 注册[AutoDL](www.autodl.com) ，并参考[Sakura模型AutoDL部署教程](https://books.fishhawk.top/forum/65719bf16843e12bd3a4dc98)完成Sakura模型实例创建
- 注册 [PushPlus](www.pushplus.plus) ，并进行实名认证

### 安装依赖

在项目根目录下运行以下命令安装依赖：

```bash
pip install selenium paramiko sshtunnel requests
```

**确保你已经下载了对应浏览器的 WebDriver，并将其路径配置到 `driver_manager.py` 中（本项目使用Edge浏览器，可在`driver_manage.py`中修改）。**

### 用户信息配置

将 `data/config.demo.json` 中的账户信息和 Token 填写为你的实际信息。

结构如下：

```json
{
    "AutoDL_account": "填写AutoDL账号",
    "AutoDL_password": "填写AutoDL密码",
    "AutoNovel_account": "填写轻小说机翻网站账号",
    "AutoNovel_password": "填写轻小说机翻网站密码",
    "pushplus_token":"填写pushplus的token"
}
```

**完成后请将 `data/config.demo.json` 重命名为 `data/config.json`** 

### **运行程序**

在项目根目录下运行以下命令：

```bash
python main.py
```

### 查看消息推送

程序默认采用**微信公众号**方式进行消息推送， [PushPlus](www.pushplus.plus) 还支持以下渠道进行推送：

- 企业微信应用
- webhook
- 邮件
- 短信

如需其他方式，请查看官方文档[介绍 | pushplus(推送加) 文档中心](https://www.pushplus.plus/doc/)，并在`pushplus.py`中进行修改。

### 查看日志信息

程序运行时的日志和报错信息会保存到 `data/log.txt` 文件中。

```
[2025-01-29 17:38:39] --- LOG START ---
[2025-01-29 17:38:45] 会话数据加载完成
[2025-01-29 17:38:48] LightNovel: 恢复登录状态成功
[2025-01-29 17:38:48] 正在获取需要翻译的书目...
[2025-01-29 17:38:59] 会话数据加载完成
[2025-01-29 17:39:00] AutoDL: 恢复登录状态成功
[2025-01-29 17:39:02] 当前账户余额: ￥4.01
[2025-01-29 17:39:03] 使用第 1 个容器
[2025-01-29 17:39:08] 服务器已开机
[2025-01-29 17:39:09] 本地端口 6006 已转发到远程 127.0.0.1:6006
[2025-01-29 17:39:15] SSH 连接已建立，端口转发成功
[2025-01-29 17:39:15] 正在加入翻译列表...
[2025-01-29 17:39:19] 翻译开始：
[2025-01-29 17:39:21] --模型为sakura-14b-qwen2.5-v1.0-iq4xs，允许上传
[2025-01-29 17:39:21] --获取翻译任务
[2025-01-29 17:39:26] --[603] syosetu/n3601eb/604
[2025-01-29 17:39:27] --分段1/3
[2025-01-29 17:39:30] --第1次　成功  [详细]
[2025-01-29 17:39:30] --分段2/3
[2025-01-29 17:39:33] --分段3/3
[2025-01-29 17:39:36] 翻译结束！
[2025-01-29 17:39:47] 登录数据已保存到 data/AutoDL_cookies.json
[2025-01-29 17:39:47] 服务器已关机
[2025-01-29 17:39:51] 消息发送成功！
```

## 注意

1. **无头模式**：

   - 默认浏览器运行在无头模式。如果需要可视化界面，可以在 `main.py` 中将 `headless` 参数设置为 `False`。

     ```python
     driver_manager = DriverManager(headless=True)
     ```

2. **错误处理**：

   - 程序会在遇到错误时通过 PushPlus 发送通知，并记录错误信息到日志文件中。

   - 如需debug，请将`main.py`中的全局变量`DEBUG`改为`True`

     ```python
     ···
     import builtins
     
     DEBUG = False
     ···
     ```

3. **服务器管理**：

   - 确保 AutoDL 平台账户余额充足，否则程序会抛出余额不足的错误，可在 `main.py` 中对最小余额参数 `min_balance` 进行更改。

     ```python
     autodl_manager = AutoDLManager(autodl_driver, autodl_account, autodl_password, autodl_cookies_path, min_balance=2.5)
     ```

4. **翻译任务**：

   - 如果没有需要翻译的书目，程序会提前退出并发送通知。
