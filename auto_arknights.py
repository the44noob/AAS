from config_loader import ConfigLoader
from modules.emulator import EmulatorController
from modules.game_controller import ArknightsOperator
from modules.image_recognition import ImageProcessor

# 初始化配置加载器
config = ConfigLoader.get_instance()
EMULATOR_CFG = {
    'emulator_path': config.get('emulator_path'),
    'adb_path': config.get('adb_path'),
    'package_name': config.get('package_name')
}


def start_emulator():
    emulator = EmulatorController(EMULATOR_CFG)
    return emulator.launch_emulator()


def get_device_serial():
    """获取已连接设备序列号"""
    try:
        result = subprocess.run([ADB_PATH, 'devices'], 
                               capture_output=True, 
                               text=True,
                               timeout=5)
        devices = [line.split('\t')[0] 
                  for line in result.stdout.splitlines() 
                  if '\tdevice' in line]
        
        if not devices:
            print("未找到已连接设备")
            return None
            
        if len(devices) > 1:
            print(f"检测到多个设备: {devices}")
            return devices[0]  # 默认选择第一个设备
            
        return devices[0]
    except Exception as e:
        print(f"获取设备列表失败: {str(e)}")
        return None

def connect_adb():
    try:
        # 先杀死已有ADB服务确保干净连接
        subprocess.run([ADB_PATH, 'kill-server'], capture_output=True)
        # 执行连接并获取输出
        result = subprocess.run([ADB_PATH, 'connect', '127.0.0.1:5555'], 
                              capture_output=True, 
                              text=True,
                              timeout=10)
        
        # 解析连接结果
        if 'connected' in result.stdout:
            print("ADB连接成功")
            # 验证设备连接状态
            device_serial = get_device_serial()
            return device_serial is not None
        else:
            print(f"ADB连接失败: {result.stderr or result.stdout}")
            return False
    except subprocess.TimeoutExpired:
        print("ADB连接超时，请检查模拟器状态")
        return False
    except Exception as e:
        print(f"ADB连接异常: {str(e)}")
        return False

def image_click_retry(image_path, confidence=0.8, max_retry=10, interval=3, region=None, similarity_threshold=0.7):
    """
    带重试机制的图像识别点击
    :param similarity_threshold: 相似度阈值(0-1)
    """
    try:
        import cv2
        import numpy as np
        from PIL import Image
        import os
        abs_path = os.path.abspath(image_path)
        if not os.path.exists(abs_path):
            print(f'图片文件不存在: {abs_path}')
            return False
        
        screen_w, screen_h = pyautogui.size()
        print(f'当前屏幕分辨率: {screen_w}x{screen_h}')
        
        template = cv2.cvtColor(np.array(Image.open(abs_path)), cv2.COLOR_RGB2HSV)
        h, s, v = cv2.split(template)
        template_hist = cv2.calcHist([h,s], [0,1], None, [50, 60], [0,180,0,256])
        
        for attempt in range(1, max_retry+1):
            try:
                if confidence < 1.0:  # 相似度匹配模式
                    screenshot = pyautogui.screenshot(region=region)
                    screen_img = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2HSV)
                    
                    # 直方图对比
                    h_screen, s_screen, _ = cv2.split(screen_img)
                    screen_hist = cv2.calcHist([h_screen,s_screen], [0,1], None, [50, 60], [0,180,0,256])
                    similarity = cv2.compareHist(template_hist, screen_hist, cv2.HISTCMP_CORREL)
                    
                    if similarity >= similarity_threshold:
                        # ADB坐标转换点击
                        x = (region[0] + region[2]/2) if region else screen_w/2
                        y = (region[1] + region[3]/2) if region else screen_h/2
                        subprocess.run([ADB_PATH, 'shell', 'input', 'tap', str(x), str(y)])
                        return True
                else:  # 原有精确匹配
                    position = pyautogui.locateOnScreen(abs_path, confidence=confidence, region=region)
                if position:
                    center = pyautogui.center(position)
                    print(f'第{attempt}次匹配成功 坐标: {center}')
                    pyautogui.click(center.x, center.y)
                    return True
            except pyautogui.ImageNotFoundException:
                print(f'第{attempt}次尝试: 未找到匹配图像')
            except Exception as e:
                print(f'第{attempt}次尝试异常: {str(e)}')
            time.sleep(interval)
    except Exception as e:
        print(f'初始化异常: {str(e)}')
    print(f'在{max_retry}次尝试后仍未找到{abs_path}')
    return False


def start_game(device_serial=None):
    try:
        # 构造基础命令
        base_cmd = [ADB_PATH]
        if device_serial:
            base_cmd.extend(['-s', device_serial])
        base_cmd.extend(['shell', 'monkey', '-p', ARKNIGHTS_PACKAGE, '1'])
        
        # 执行启动命令并设置超时
        result = subprocess.run(base_cmd,
                              capture_output=True,
                              text=True,
                              timeout=15,
                              check=True)
        
        # 验证进程是否真正启动
        time.sleep(5)  # 等待进程初始化
        check_process = subprocess.run([ADB_PATH, 'shell', 'ps', '|', 'grep', ARKNIGHTS_PACKAGE],
                                      capture_output=True,
                                      text=True)
        
        if ARKNIGHTS_PACKAGE not in check_process.stdout:
            print("游戏进程未找到，可能启动失败")
            return False
            
        print("明日方舟启动成功")
        
        # 获取模拟器窗口位置
        try:
            win = pyautogui.getWindowsWithTitle('雷电模拟器')[0]
            if win.isMinimized:
                win.restore()
            region = (win.left, win.top, win.width, win.height)
            print(f'模拟器窗口区域: {region}')
        except Exception as e:
            print(f'获取窗口位置失败: {str(e)}')
            region = None
        
        # 开始按钮检测
        if image_click_retry('start_button.png', confidence=0.8, region=region):
            print("成功点击开始按钮")
            
            # 公告关闭检测
            try:
                print('开始检测公告关闭按钮')
                if image_click_retry('del_borad.png', confidence=0.7, max_retry=5, interval=2, region=region):
                    print("成功关闭游戏公告")
                else:
                    print("未检测到公告界面")
            except Exception as e:
                print(f'公告关闭异常: {str(e)}')
            
            return True
        return False
    except subprocess.TimeoutExpired:
        print("游戏启动超时，请检查模拟器响应速度")
        return False
    except subprocess.CalledProcessError as e:
        print(f"游戏启动命令执行失败: {e.stderr}")
        return False
    except Exception as e:
        print(f"未知错误: {str(e)}")
        return False


if __name__ == "__main__":
    operator = ArknightsOperator(EMULATOR_CFG)
    if operator.initialize_environment():
        operator.start_game_sequence()
    input("按回车键退出...")