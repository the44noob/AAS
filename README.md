# 明日方舟自动化系统使用指南

## 简介

明日方舟自动化系统是一个基于Python的自动化工具，用于辅助玩家完成《明日方舟》游戏中的日常任务。系统通过图像识别和模拟器控制技术，实现了游戏登录、公开招募、基建收菜、作战重放和奖励领取等功能的自动化。

本系统具有以下特点：
- 模块化设计，各功能模块独立且可扩展
- 基于图像识别的界面元素定位，适应性强
- 可配置的任务执行流程，满足不同玩家需求
- 完善的日志记录，方便问题排查

## 系统要求

- Python 3.6+
- 安卓模拟器（推荐使用MuMu模拟器、雷电模拟器或夜神模拟器）
- ADB工具（用于与模拟器通信）
- 以下Python库：
  - OpenCV（图像识别）
  - PyAutoGUI（屏幕操作）
  - pure-python-adb（ADB通信）
  - NumPy（数据处理）
  - Pillow（图像处理）
  - pytesseract (文本识别)

## 安装步骤

1. 确保已安装Python 3.6或更高版本

2. 安装所需的Python库：
   ```
   pip install opencv-python pyautogui pure-python-adb numpy pillow pytesseract 
   ```
   
3. 安装并配置安卓模拟器，确保能够正常运行《明日方舟》游戏

4. 确保安装tesseract，并配置环境变量

   [Release 5.5.0 · tesseract-ocr/tesseract](https://github.com/tesseract-ocr/tesseract/releases/tag/5.5.0)

   并且需要下载中文的识别库（chi_sim.traineddata）放到安装目录下的tessdata目录中

   下载地址为[tessdata/chi_sim.traineddata at main · tesseract-ocr/tessdata](https://github.com/tesseract-ocr/tessdata/blob/main/chi_sim.traineddata)

5. 确保ADB服务已启动，可通过以下命令检查：

   ```
   adb devices
   ```
   如果显示了模拟器设备，则表示ADB服务正常

6. 下载本系统代码并解压到本地目录

## 目录结构

```
arknights_auto/
├── assets/
│   └── templates/       # 图像模板目录
├── modules/
│   ├── emulator.py      # 模拟器连接模块
│   ├── image_recognition.py  # 图像识别模块
│   ├── game_controller.py    # 游戏控制器模块
│   ├── arknights_login.py    # 游戏登录模块
│   ├── arknights_recruitment.py  # 公开招募模块
│   ├── arknights_base.py     # 基建收菜模块
│   ├── arknights_combat.py   # 作战模块
│   └── arknights_reward.py   # 奖励领取模块
├── screenshots/         # 截图保存目录
├── main.py              # 主程序
├── test.py              # 测试脚本
└── config.json          # 配置文件
```

## 准备工作

在使用本系统前，需要进行以下准备工作：

1. 确保模拟器已启动并运行《明日方舟》游戏
2. 确保游戏账号已经设置为自动登录（或在配置文件中设置账号密码）
3. 准备游戏界面的模板图像，放置在`assets/templates`目录下
4. 根据需要修改配置文件`config.json`

### 模板图像准备

系统需要使用模板图像来识别游戏界面元素。您可以通过以下步骤准备模板图像：

1. 在游戏中截取需要识别的界面元素（如按钮、图标等）
2. 将截图裁剪为只包含目标元素的小图像
3. 保存为PNG格式，并放置在`assets/templates`目录下
4. 确保文件名与代码中的模板名称一致

主要需要的模板图像包括：
- 登录相关：开始游戏按钮、登录按钮等
- 公开招募相关：公开招募图标、立即招募按钮等
- 基建相关：基建图标、收取按钮等
- 作战相关：作战图标、开始行动按钮等
- 奖励相关：任务图标、收取按钮等

## 配置文件说明

配置文件`config.json`用于设置系统的各项参数，主要包括以下内容：

```json
{
    "emulator": {
        "host": "127.0.0.1",
        "port": 5037,
        "device_serial": null
    },
    "template_dir": "assets/templates",
    "screenshot_dir": "screenshots",
    "tasks": {
        "login": true,
        "recruitment": true,
        "base": true,
        "combat": true,
        "reward": true
    },
    "combat": {
        "use_sanity_item": false,
        "max_times": 5
    },
    "recruitment": {
        "use_expedited": false
    }
}
```

参数说明：
- `emulator`: 模拟器连接设置
  - `host`: ADB服务器主机地址，默认为本地127.0.0.1
  - `port`: ADB服务器端口，默认为5037
  - `device_serial`: 设备序列号，如果为null则连接到第一个可用设备
- `template_dir`: 模板图像目录
- `screenshot_dir`: 截图保存目录
- `tasks`: 任务执行设置
  - `login`: 是否执行登录任务
  - `recruitment`: 是否执行公开招募任务
  - `base`: 是否执行基建收菜任务
  - `combat`: 是否执行作战任务
  - `reward`: 是否执行奖励领取任务
- `combat`: 作战设置
  - `use_sanity_item`: 是否使用理智药剂
  - `max_times`: 最大作战次数
- `recruitment`: 公开招募设置
  - `use_expedited`: 是否使用加急许可

您可以根据自己的需求修改这些参数。

## 使用方法

### 创建默认配置文件

首次使用时，可以通过以下命令创建默认配置文件：

```
python main.py --create-config
```

这将在当前目录下生成`config.json`文件，您可以根据需要修改其中的参数。

### 运行自动化任务

运行所有任务：

```
python main.py
```

运行特定任务（通过命令行参数指定）：

```
python main.py --no-combat --no-base  # 不执行作战和基建任务
python main.py --use-sanity-item      # 使用理智药剂
python main.py --max-combat 10        # 设置最大作战次数为10
```

### 命令行参数说明

主程序支持以下命令行参数：

- `-c, --config`: 指定配置文件路径
- `--create-config`: 创建默认配置文件
- `--no-login`: 跳过登录
- `--no-recruitment`: 跳过公开招募
- `--no-base`: 跳过基建收菜
- `--no-combat`: 跳过上一次作战
- `--no-reward`: 跳过领取奖励
- `--use-sanity-item`: 使用理智药剂
- `--max-combat`: 设置最大作战次数
- `--use-expedited`: 使用加急许可

### 测试系统

您可以使用测试脚本来测试系统的各个模块：

```
python test.py                  # 运行所有测试
python test.py --module login   # 只测试登录模块
python test.py --save           # 保存测试结果
```

### 可视化界面 ###

运行start_it.py