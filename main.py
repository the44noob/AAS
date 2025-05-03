#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
明日方舟自动化主程序
整合所有功能模块，提供统一的界面和配置
"""

import os
import time
import logging
import argparse
import json
import sys
import math
from datetime import datetime

# 导入功能模块
from modules.emulator import EmulatorController
from modules.image_recognition import ImageRecognizer
from modules.game_controller import GameController
from modules.arknights_login import ArknightsLogin
from modules.arknights_recruitment import ArknightsRecruitment
from modules.arknights_base import ArknightsBase
from modules.arknights_combat import ArknightsCombat
from modules.arknights_reward import ArknightsReward

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("arknights_auto.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('ArknightsAuto')

class ArknightsAuto:
    """明日方舟自动化主类，整合所有功能模块"""
    
    def __init__(self, config_file="./config.json"):
        """
        初始化明日方舟自动化系统
        
        Args:
            config_file: 配置文件路径，默认为None
        """
        # 加载配置
        self.config = self._load_config(config_file)
        
        # 初始化模块
        self._init_modules()
        
        logger.info("明日方舟自动化系统初始化完成")
    
    def _load_config(self, config_file):
        """
        加载配置文件
        
        Args:
            config_file: 配置文件路径
            
        Returns:
            dict: 配置字典
        """
        if not config_file:
            config_file = "config.json"
        # 默认配置
        default_config = {
            "emulator": {
                "host": "127.0.0.1",
                "port": 5037,
                "emulator_path": "E:/MuMu/MuMu Player 12",
                "adb_path": "E:/develop/platform-tools/adb.exe",
                "device_serial": None,
                "device_port" : 5555,
                "username": None,
                "password": None
            },
            "template_dir": "assets/templates",
            "screenshot_dir": "screenshots",
            "tasks": {
                "login": False,
                "recruitment": True,
                "base": True,
                "combat": True,
                "reward": True
            },
            "combat": {
                "use_sanity_item": False,
                "max_times": 5
            },
            "recruitment": {
                "use_expedited": False
            }
        }
        
        # 如果提供了配置文件，则加载并合并
        if config_file and os.path.isfile(config_file):
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                
                # 合并配置
                default_config = self._merge_config(default_config, user_config)
                logger.info(f"已加载配置文件: {config_file}")
            except Exception as e:
                logger.error(f"加载配置文件时出错: {str(e)}")
        
        return default_config
    
    def _merge_config(self, default_config, user_config):
        """
        合并配置
        
        Args:
            default_config: 默认配置字典
            user_config: 用户配置字典
        """
        for key, value in user_config.items():
            if key in default_config:
                if value == "None" or value == "":
                    value = None
                if isinstance(value, dict) and isinstance(default_config[key], dict):
                    self._merge_config(default_config[key], value)
                else:
                    default_config[key] = value
            else:
                default_config[key] = value
        return default_config
    
    def _init_modules(self):
        """初始化各功能模块"""
        # 获取配置
        emulator_config = self.config["emulator"]
        template_dir = self.config["template_dir"]
        screenshot_dir = self.config["screenshot_dir"]
        
        # 确保目录存在
        os.makedirs(template_dir, exist_ok=True)
        os.makedirs(screenshot_dir, exist_ok=True)
        
        # 初始化基础模块
        self.emulator = EmulatorController(
            config=emulator_config
        )
        self.recognizer = ImageRecognizer(template_dir=template_dir)
        self.controller = GameController(
            emulator=self.emulator,
            recognizer=self.recognizer,
            screenshot_dir=screenshot_dir
        )
        
        # 初始化功能模块
        self.login = ArknightsLogin(
            controller=self.controller,
            template_dir=template_dir
        )
        self.recruitment = ArknightsRecruitment(
            controller=self.controller,
            template_dir=template_dir
        )
        self.base = ArknightsBase(
            controller=self.controller,
            template_dir=template_dir
        )
        self.combat = ArknightsCombat(
            controller=self.controller,
            template_dir=template_dir
        )
        self.reward = ArknightsReward(
            controller=self.controller,
            template_dir=template_dir
        )
    
    def connect(self):
        """
        连接到模拟器
        
        Returns:
            bool: 连接是否成功
        """
        device_serial = self.config["emulator"]["device_serial"]
        return self.emulator.connect(device_serial)
    
    def run_tasks(self):
        """
        运行配置的任务
        
        Returns:
            bool: 所有任务是否成功完成
        """
        logger.info("开始运行任务...")
        
        # 连接到模拟器
        if not self.connect():
            logger.error("连接模拟器失败，无法执行任务")
            return False
        
        # 获取任务配置
        tasks = self.config["tasks"]
        
        # 执行登录任务
        if tasks.get("login", True):
            logger.info("执行登录任务...")
            if not self.login.start_game() or not self.login.login(self.config["emulator"]["username"], self.config["emulator"]["password"]):
                logger.error("登录失败，无法继续执行其他任务")
                return False
            logger.info("登录任务完成")
        
        # 执行公开招募任务
        if tasks.get("recruitment", True):
            logger.info("执行公开招募任务...")
            use_expedited = self.config["recruitment"].get("use_expedited", False)
            self.recruitment.execute_recruitment(use_expedited=use_expedited)
            logger.info("公开招募任务完成")
        
        # 执行基建收菜任务
        if tasks.get("base", True):
            logger.info("执行基建收菜任务...")
            self.base.execute_base_collection()
            logger.info("基建收菜任务完成")
        
        # 执行上一次作战任务
        if tasks.get("combat", True):
            logger.info("执行上一次作战任务...")
            combat_config = self.config["combat"]
            use_sanity_item = combat_config.get("use_sanity_item", False)
            max_times = combat_config.get("max_times", 5)
            completed = self.combat.execute_last_combat(
                use_sanity_item=use_sanity_item,
                max_times=max_times
            )
            logger.info(f"上一次作战任务完成，共完成 {completed}/{max_times} 次作战")
        
        # 执行领取奖励任务
        if tasks.get("reward", True):
            logger.info("执行领取奖励任务...")
            self.reward.execute_reward_collection()
            logger.info("领取奖励任务完成")
        
        logger.info("所有任务执行完成")
        return True
    
    def save_config(self, config_file="config.json"):
        """
        保存当前配置到文件
        
        Args:
            config_file: 配置文件路径，默认为"config.json"
            
        Returns:
            bool: 保存是否成功
        """
        try:
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
            logger.info(f"配置已保存到: {config_file}")
            return True
        except Exception as e:
            logger.error(f"保存配置时出错: {str(e)}")
            return False
    
    def create_default_config(self, config_file="config.json"):
        """
        创建默认配置文件
        
        Args:
            config_file: 配置文件路径，默认为"config.json"
            
        Returns:
            bool: 创建是否成功
        """
        return self.save_config(config_file)

def main():
    """主函数"""
    # 解析命令行参数
    parser = argparse.ArgumentParser(description="明日方舟自动化工具")
    parser.add_argument("-c", "--config", help="配置文件路径")
    parser.add_argument("--create-config", action="store_true", help="创建默认配置文件")
    parser.add_argument("--no-login", action="store_true", help="跳过登录")
    parser.add_argument("--no-recruitment", action="store_true", help="跳过公开招募")
    parser.add_argument("--no-base", action="store_true", help="跳过基建收菜")
    parser.add_argument("--no-combat", action="store_true", help="跳过上一次作战")
    parser.add_argument("--no-reward", action="store_true", help="跳过领取奖励")
    parser.add_argument("--use-sanity-item", action="store_true", help="使用理智药剂")
    parser.add_argument("--max-combat", type=int, help="最大作战次数")
    parser.add_argument("--use-expedited", action="store_true", help="使用加急许可")
    args = parser.parse_args()
    
    # 创建自动化实例
    auto = ArknightsAuto(config_file=args.config)
    
    # 如果指定了创建配置文件
    if args.create_config:
        auto.create_default_config()
        return
    # 根据命令行参数修改配置
    if args.no_login:
        auto.config["tasks"]["login"] = False
    if args.no_recruitment:
        auto.config["tasks"]["recruitment"] = False
    if args.no_base:
        auto.config["tasks"]["base"] = False
    if args.no_combat:
        auto.config["tasks"]["combat"] = False
    if args.no_reward:
        auto.config["tasks"]["reward"] = False
    if args.use_sanity_item:
        auto.config["combat"]["use_sanity_item"] = True
    if args.max_combat:
        auto.config["combat"]["max_times"] = args.max_combat
    if args.use_expedited:
        auto.config["recruitment"]["use_expedited"] = True
    
    # 运行任务
    auto.run_tasks()


def delete_folder_contents(folder_path):
    """
    删除指定文件夹中的所有内容（包括子文件夹和文件）
    """
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)  # 删除文件或符号链接
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)  # 删除子文件夹及其内容
        except Exception as e:
            print(f'删除 {file_path} 失败。原因: {e}')

if __name__ == "__main__":
    try:
        main()
        logger.info("开始清理屏幕快照...")
        delete_folder_contents("screenshots")
    except KeyboardInterrupt:
        logger.info("用户中断，程序退出")
    except Exception as e:
        logger.exception(f"程序运行时出错: {str(e)}")
