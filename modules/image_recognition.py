#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
图像识别模块
用于识别游戏界面元素和进行图像匹配
"""

import os
import cv2
import numpy as np
import logging
import math
from PIL import Image
from io import BytesIO
import pytesseract


# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('ImageRecognizer')

class ImageRecognizer:
    """图像识别器类，负责游戏界面元素的识别和匹配"""
    
    def __init__(self, template_dir=None):
        """
        初始化图像识别器
        
        Args:
            template_dir: 模板图像目录，默认为None
        """
        self.template_dir = template_dir
        self.templates = {}
        
        # 如果提供了模板目录，则加载所有模板
        if template_dir and os.path.isdir(template_dir):
            self.load_templates(template_dir)
        
        logger.info("图像识别器初始化完成")
    
    def load_templates(self, template_dir):
        """
        加载指定目录中的所有模板图像
        
        Args:
            template_dir: 模板图像目录
            
        Returns:
            int: 加载的模板数量
        """
        if not os.path.isdir(template_dir):
            logger.error(f"模板目录不存在: {template_dir}")
            return 0
        
        count = 0
        for filename in os.listdir(template_dir):
            if filename.endswith(('.png', '.jpg', '.jpeg')):
                template_path = os.path.join(template_dir, filename)
                template_name = os.path.splitext(filename)[0]
                
                try:
                    template = cv2.imread(template_path)
                    if template is None:
                        logger.warning(f"无法加载模板图像: {template_path}")
                        continue
                    
                    self.templates[template_name] = template
                    count += 1
                    logger.debug(f"已加载模板: {template_name}")
                except Exception as e:
                    logger.error(f"加载模板 {template_path} 时出错: {str(e)}")
        
        logger.info(f"已加载 {count} 个模板图像")
        return count
    
    def add_template(self, name, template):
        """
        添加模板图像
        
        Args:
            name: 模板名称
            template: 模板图像（OpenCV格式）或模板图像路径
            
        Returns:
            bool: 是否成功添加
        """
        try:
            if isinstance(template, str):
                # 如果提供的是路径，则加载图像
                if not os.path.isfile(template):
                    logger.error(f"模板文件不存在: {template}")
                    return False
                
                template_img = cv2.imread(template)
                if template_img is None:
                    logger.error(f"无法加载模板图像: {template}")
                    return False
            else:
                # 直接使用提供的图像
                template_img = template
            
            self.templates[name] = template_img
            logger.info(f"已添加模板: {name}")
            return True
        except Exception as e:
            logger.error(f"添加模板 {name} 时出错: {str(e)}")
            return False
    
    def remove_template(self, name):
        """
        移除模板图像
        
        Args:
            name: 模板名称
            
        Returns:
            bool: 是否成功移除
        """
        if name in self.templates:
            del self.templates[name]
            logger.info(f"已移除模板: {name}")
            return True
        else:
            logger.warning(f"模板不存在: {name}")
            return False
    
    def get_template(self, name):
        """
        获取模板图像
        
        Args:
            name: 模板名称
            
        Returns:
            numpy.ndarray: 模板图像，如果不存在则返回None
        """
        return self.templates.get(name)
    
    def preprocess_image(self, image):
        """
        预处理图像
        
        Args:
            image: 输入图像（OpenCV格式）或图像数据（bytes）或图像路径
            
        Returns:
            numpy.ndarray: 预处理后的图像
        """
        try:
            if isinstance(image, bytes):
                # 如果是字节数据，转换为OpenCV格式
                nparr = np.frombuffer(image, np.uint8)
                img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            elif isinstance(image, str):
                # 如果是路径，加载图像
                img = cv2.imread(image)
            else:
                # 直接使用提供的图像
                img = image
            
            if img is None:
                logger.error("无法处理输入图像")
                return None
            
            return img
        except Exception as e:
            logger.error(f"预处理图像时出错: {str(e)}")
            return None
    
    def match_template(self, image, template_name=None, template=None, threshold=0.8):
        """
        模板匹配
        
        Args:
            image: 输入图像（OpenCV格式）或图像数据（bytes）或图像路径
            template_name: 模板名称，如果提供则使用已加载的模板
            template: 模板图像，如果template_name为None则使用此参数
            threshold: 匹配阈值，默认为0.8
            
        Returns:
            tuple: (是否匹配成功, 最佳匹配位置(x, y), 匹配得分)
        """
        # 输入数据校验
        if image is None:
            logger.error("输入图像不能为None")
            return False, (0, 0), 0.0

        # 预处理输入图像
        img = self.preprocess_image(image)
        if img is None or not isinstance(img, np.ndarray):
            logger.error("图像预处理失败或格式无效")
            return False, (0, 0), 0.0

        # 验证图像尺寸
        if img.size == 0 or img.shape[0] < 10 or img.shape[1] < 10:
            logger.error("输入图像尺寸过小或不合法")
            return False, (0, 0), 0.0
        
        # 获取模板
        if template_name is not None:
            if template_name not in self.templates:
                logger.error(f"模板不存在: {template_name}")
                return False, (0, 0), 0.0
            tpl = self.templates[template_name]
        elif template is not None:
            tpl = self.preprocess_image(template)
            if tpl is None:
                return False, (0, 0), 0.0
        else:
            logger.error("必须提供template_name或template参数")
            return False, (0, 0), 0.0
        
        try:
            # 执行模板匹配
            result = cv2.matchTemplate(img, tpl, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
            
            # 获取匹配位置（中心点）
            h, w = tpl.shape[:2]
            center_x = max_loc[0] + w // 2
            center_y = max_loc[1] + h // 2
            
            # 判断是否匹配成功
            if max_val >= threshold:
                logger.debug(f"模板匹配成功: 位置=({center_x}, {center_y}), 得分={max_val:.4f}")
                return True, (center_x, center_y), max_val
            else:
                logger.debug(f"模板匹配失败: 最高得分={max_val:.4f}, 阈值={threshold}")
                return False, (center_x, center_y), max_val
        except Exception as e:
            logger.error(f"模板匹配时出错: {str(e)}")
            return False, (0, 0), 0.0
    
    def find_all_matches(self, image, template_name=None, template=None, threshold=0.8, max_results=10):
        """
        查找所有匹配位置
        
        Args:
            image: 输入图像（OpenCV格式）或图像数据（bytes）或图像路径
            template_name: 模板名称，如果提供则使用已加载的模板
            template: 模板图像，如果template_name为None则使用此参数
            threshold: 匹配阈值，默认为0.8
            max_results: 最大结果数量，默认为10
            
        Returns:
            list: 匹配结果列表，每个元素为 (位置(x, y), 得分)
        """
        # 预处理输入图像
        img = self.preprocess_image(image)
        if img is None:
            return []
        
        # 获取模板
        if template_name is not None:
            if template_name not in self.templates:
                logger.error(f"模板不存在: {template_name}")
                return []
            tpl = self.templates[template_name]
        elif template is not None:
            tpl = self.preprocess_image(template)
            if tpl is None:
                return []
        else:
            logger.error("必须提供template_name或template参数")
            return []
        
        try:
            # 执行模板匹配
            result = cv2.matchTemplate(img, tpl, cv2.TM_CCOEFF_NORMED)
            h, w = tpl.shape[:2]
            
            # 查找所有匹配位置
            matches = []
            while len(matches) < max_results:
                min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
                if max_val < threshold:
                    break
                
                # 计算中心点
                center_x = max_loc[0] + w // 2
                center_y = max_loc[1] + h // 2
                matches.append(((center_x, center_y), max_val))
                
                # 将已找到的位置清零，避免重复查找
                cv2.rectangle(result, max_loc, (max_loc[0] + w, max_loc[1] + h), 0, -1)
            matches = self.merge_similar_positions(matches)
            logger.debug(f"找到 {len(matches)} 个匹配结果")
            return matches
        except Exception as e:
            logger.error(f"查找所有匹配位置时出错: {str(e)}")
            return []
    # 合并位置相近的匹配项
    def merge_similar_positions(self,matches, distance_threshold=20):
        """
        合并位置相近的匹配项
        Args:
            matches: 匹配结果列表，格式为 ((x, y), score)
            distance_threshold: 距离阈值，小于该值的点视为重复
        Returns:
            list: 合并后的匹配结果
        """
        if not matches:
            return []
        # 按得分降序排序
        sorted_matches = sorted(matches, key=lambda x: x[1], reverse=True)
        merged = []
        while sorted_matches:
            current = sorted_matches.pop(0)
            merged.append(current)
            # 筛选出与当前点距离较近的点
            to_remove = []
            for i, match in enumerate(sorted_matches):
                dx = current[0][0] - match[0][0]
                dy = current[0][1] - match[0][1]
                distance = math.hypot(dx, dy)  # 欧几里得距离
                if distance < distance_threshold:
                    to_remove.append(i)
            # 逆序删除以避免索引错乱
            for i in reversed(to_remove):
                sorted_matches.pop(i)
        return merged
    def find_color(self, image, color, tolerance=10):
        """
        查找指定颜色的位置
        
        Args:
            image: 输入图像（OpenCV格式）或图像数据（bytes）或图像路径
            color: 目标颜色，格式为(B, G, R)
            tolerance: 颜色容差，默认为10
            
        Returns:
            list: 匹配位置列表，每个元素为 (x, y)
        """
        # 预处理输入图像
        img = self.preprocess_image(image)
        if img is None:
            return []
        
        try:
            # 创建颜色范围
            lower_bound = np.array([max(0, c - tolerance) for c in color], dtype=np.uint8)
            upper_bound = np.array([min(255, c + tolerance) for c in color], dtype=np.uint8)
            
            # 创建颜色掩码
            mask = cv2.inRange(img, lower_bound, upper_bound)
            
            # 查找非零点
            points = cv2.findNonZero(mask)
            if points is None:
                return []
            
            # 转换为坐标列表
            coordinates = [(point[0][0], point[0][1]) for point in points]
            logger.debug(f"找到 {len(coordinates)} 个颜色匹配点")
            return coordinates
        except Exception as e:
            logger.error(f"查找颜色时出错: {str(e)}")
            return []
    
    def detect_text_area(self, image, min_area=100):
        """
        检测可能包含文本的区域
        
        Args:
            image: 输入图像（OpenCV格式）或图像数据（bytes）或图像路径
            min_area: 最小区域面积，默认为100
            
        Returns:
            list: 文本区域列表，每个元素为 (x, y, w, h)
        """
        # 预处理输入图像
        img = self.preprocess_image(image)
        if img is None:
            return []
        
        try:
            # 转换为灰度图
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # 二值化
            _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
            
            # 查找轮廓
            contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # 筛选可能的文本区域
            text_areas = []
            for contour in contours:
                x, y, w, h = cv2.boundingRect(contour)
                area = w * h
                aspect_ratio = float(w) / h if h > 0 else 0
                
                # 根据面积和宽高比筛选
                if area >= min_area and 0.1 <= aspect_ratio <= 10:
                    text_areas.append((x, y, w, h))
            
            logger.debug(f"检测到 {len(text_areas)} 个可能的文本区域")
            return text_areas
        except Exception as e:
            logger.error(f"检测文本区域时出错: {str(e)}")
            return []
    
    def crop_image(self, image, x, y, width, height):
        """
        裁剪图像
        
        Args:
            image: 输入图像（OpenCV格式）或图像数据（bytes）或图像路径
            x: 左上角x坐标
            y: 左上角y坐标
            width: 宽度
            height: 高度
            
        Returns:
            numpy.ndarray: 裁剪后的图像
        """
        # 预处理输入图像
        img = self.preprocess_image(image)
        if img is None:
            return None
        
        try:
            # 确保坐标在图像范围内
            img_height, img_width = img.shape[:2]
            x = max(0, min(x, img_width - 1))
            y = max(0, min(y, img_height - 1))
            width = max(1, min(width, img_width - x))
            height = max(1, min(height, img_height - y))
            
            # 裁剪图像
            cropped = img[y:y+height, x:x+width]
            return cropped
        except Exception as e:
            logger.error(f"裁剪图像时出错: {str(e)}")
            return None
    
    def save_image(self, image, path):
        """
        保存图像
        
        Args:
            image: 输入图像（OpenCV格式）或图像数据（bytes）
            path: 保存路径
            
        Returns:
            bool: 是否成功保存
        """
        try:
            # 预处理输入图像
            img = self.preprocess_image(image)
            if img is None:
                return False
            
            # 保存图像
            cv2.imwrite(path, img)
            logger.info(f"图像已保存到: {path}")
            return True
        except Exception as e:
            logger.error(f"保存图像时出错: {str(e)}")
            return False
    
    def draw_rectangle(self, image, x, y, width, height, color=(0, 255, 0), thickness=2):
        """
        在图像上绘制矩形
        
        Args:
            image: 输入图像（OpenCV格式）
            x: 左上角x坐标
            y: 左上角y坐标
            width: 宽度
            height: 高度
            color: 颜色，默认为绿色 (0, 255, 0)
            thickness: 线条粗细，默认为2
            
        Returns:
            numpy.ndarray: 绘制后的图像
        """
        try:
            # 创建图像副本
            img_copy = image.copy()
            
            # 绘制矩形
            cv2.rectangle(img_copy, (x, y), (x + width, y + height), color, thickness)
            return img_copy
        except Exception as e:
            logger.error(f"绘制矩形时出错: {str(e)}")
            return image
    
    def draw_circle(self, image, x, y, radius=5, color=(0, 0, 255), thickness=-1):
        """
        在图像上绘制圆形
        
        Args:
            image: 输入图像（OpenCV格式）
            x: 中心点x坐标
            y: 中心点y坐标
            radius: 半径，默认为5
            color: 颜色，默认为红色 (0, 0, 255)
            thickness: 线条粗细，默认为-1（填充）
            
        Returns:
            numpy.ndarray: 绘制后的图像
        """
        try:
            # 创建图像副本
            img_copy = image.copy()
            
            # 绘制圆形
            cv2.circle(img_copy, (x, y), radius, color, thickness)
            return img_copy
        except Exception as e:
            logger.error(f"绘制圆形时出错: {str(e)}")
            return image
    
    def compare_images(self, image1, image2, method=cv2.TM_CCOEFF_NORMED):
        """
        比较两个图像的相似度
        
        Args:
            image1: 第一个图像
            image2: 第二个图像
            method: 比较方法，默认为cv2.TM_CCOEFF_NORMED
            
        Returns:
            float: 相似度得分
        """
        # 预处理输入图像
        img1 = self.preprocess_image(image1)
        img2 = self.preprocess_image(image2)
        if img1 is None or img2 is None:
            return 0.0
        
        try:
            # 确保两个图像大小相同
            if img1.shape != img2.shape:
                img2 = cv2.resize(img2, (img1.shape[1], img1.shape[0]))
            
            # 计算相似度
            if method == cv2.TM_CCOEFF_NORMED:
                # 使用模板匹配方法
                result = cv2.matchTemplate(img1, img2, method)
                _, max_val, _, _ = cv2.minMaxLoc(result)
                return max_val
            else:
                # 使用结构相似性指数
                return cv2.compareSSIM(img1, img2)
        except Exception as e:
            logger.error(f"比较图像时出错: {str(e)}")
            return 0.0
    def find_text_center(self,image_path, template_path, threshold=0.8):
        # 读取图像和模板
        img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        template = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)

        # 获取模板尺寸
        w, h = template.shape[::-1]

        # 执行模板匹配
        res = cv2.matchTemplate(img, template, cv2.TM_CCOEFF_NORMED)

        # 获取匹配位置
        loc = np.where(res >= threshold)

        centers = []
        for pt in zip(*loc[::-1]):  # 交换x,y坐标
            center_x = pt[0] + w // 2
            center_y = pt[1] + h // 2
            centers.append((center_x, center_y))

        return centers
    def extract_text_from_region(self,image_path, region_coords, lang='eng'):
        """
        从图像的指定区域提取文本

        参数:
            image_path: 图像路径
            region_coords: 区域坐标 (x1, y1, x2, y2)
            lang: OCR语言包 (如 'chi_sim' 表示简体中文)

        返回:
            识别到的文本
        """
        # 读取图像
        img = cv2.imread(image_path)

        # 提取指定区域 (x1, y1, x2, y2)
        x1, y1, x2, y2 = region_coords
        cropped_img = img[y1:y2, x1:x2]

        # 转换为灰度图（提高OCR准确率）
        gray = cv2.cvtColor(cropped_img, cv2.COLOR_BGR2GRAY)

        # 使用Tesseract OCR识别文本
        text = pytesseract.image_to_string(gray, lang=lang)

        return str(text).replace(" ","")  # 去除首尾空格
 
# 测试代码
if __name__ == "__main__":
    # 创建图像识别器实例
    recognizer = ImageRecognizer()
    
    # 测试加载模板
    template_dir = "templates"
    if os.path.isdir(template_dir):
        count = recognizer.load_templates(template_dir)
        print(f"已加载 {count} 个模板")
    
    # 测试模板匹配
    test_image = "screenshot.png"
    if os.path.isfile(test_image):
        for template_name in recognizer.templates:
            success, position, score = recognizer.match_template(test_image, template_name)
            if success:
                print(f"找到模板 {template_name}: 位置={position}, 得分={score:.4f}")
