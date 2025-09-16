import re
import sys
import random
import json
import os
from PyQt5 import QtWidgets, QtCore, QtGui
import ollama  # 需要安装ollama库: pip install ollama

class SCPInputMethod(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.use_ai = '-ai' in sys.argv  # 检查是否带有-ai参数
        self.word_map = {}
        if not self.use_ai:
            self.loadWordMap("word_mapping.json")
        self.initUI()
        
    def loadWordMap(self, filename):
        """从JSON文件加载词汇映射"""
        if os.path.exists(filename):
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    self.word_map = json.load(f)
                print(f"成功加载 {len(self.word_map)} 个词汇映射")
            except Exception as e:
                print(f"加载词汇映射失败: {e}")
                self.loadDefaultMap()
                self.saveWordMap(filename)
        else:
            self.loadDefaultMap()
            self.saveWordMap(filename)
    
    def loadDefaultMap(self):
        """加载默认的词汇映射"""
        self.word_map = {
            "知道": ["制道", "知到", "织导"],
            "错误": ["措误", "错悟", "厝误"],
            "输入": ["输乳", "酥入", "叔入"],
            "设备": ["设倍", "社备", "摄备"],
            "项目": ["向目", "项木", "相目"],
            "登记": ["蹬记", "登计", "等记"],
            "等级": ["蹬级", "等即", "登记"],
            "安全": ["安全", "鞍全", "案全"],
            "收容": ["收荣", "受容", "手容"],
            "措施": ["措失", "错施", "厝施"],
            "特殊": ["特书", "特舒", "忒殊"],
            "实验": ["实研", "试验", "实咽"],
            "记录": ["记路", "计录", "纪録"],
            "报告": ["报吿", "报羔", "報告"],
            "研究": ["研揪", "研九", "研就"],
            "使用": ["使佣", "实用", "史用"],
            "发现": ["发先", "法现", "髮现"],
            "立即": ["立既", "即刻", "立急"],
            "卸载": ["卸栽", "谢载", "泻载"],
            "软件": ["软见", "阮件", "朊件"]
        }
    
    def saveWordMap(self, filename):
        """保存词汇映射到文件"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.word_map, f, ensure_ascii=False, indent=2)
            print(f"词汇映射已保存到 {filename}")
        except Exception as e:
            print(f"保存词汇映射失败: {e}")
    
    def initUI(self):
        # 设置窗口属性
        self.setWindowTitle('██品饮拼音输入法 - SCP-CN-468-J')
        self.setGeometry(300, 300, 500, 400)
        
        # 创建文本显示区域
        self.text_display = QtWidgets.QTextEdit(self)
        self.text_display.setGeometry(10, 10, 480, 200)
        
        # 创建输入框
        self.input_field = QtWidgets.QLineEdit(self)
        self.input_field.setGeometry(10, 220, 480, 30)
        self.input_field.textChanged.connect(self.onTextChanged)
        
        # 创建按钮
        self.clear_btn = QtWidgets.QPushButton('清空', self)
        self.clear_btn.setGeometry(10, 260, 80, 30)
        self.clear_btn.clicked.connect(self.clearText)
        
        self.quit_btn = QtWidgets.QPushButton('退出', self)
        self.quit_btn.setGeometry(100, 260, 80, 30)
        self.quit_btn.clicked.connect(self.quitApp)
        
        # 重新加载映射按钮
        self.reload_btn = QtWidgets.QPushButton('重载映射', self)
        self.reload_btn.setGeometry(190, 260, 100, 30)
        self.reload_btn.clicked.connect(self.reloadMapping)
        
        # 状态标签
        self.status_label = QtWidgets.QLabel('状态: 等待输入...', self)
        self.status_label.setGeometry(10, 300, 480, 30)
        
        # 添加映射表显示区域
        self.mapping_label = QtWidgets.QLabel('当前词汇映射:', self)
        self.mapping_label.setGeometry(10, 330, 480, 20)
        
        # 显示一些映射示例
        if not self.use_ai and self.word_map:
            sample_keys = list(self.word_map.keys())[:5]
            sample_text = "示例: " + ", ".join([f"{k}→{random.choice(self.word_map[k])}" for k in sample_keys])
        else:
            sample_text = "示例: AI模式已激活"
        self.sample_label = QtWidgets.QLabel(sample_text, self)
        self.sample_label.setGeometry(10, 350, 480, 40)
    
    def reloadMapping(self):
        """重新加载词汇映射"""
        if not self.use_ai:
            self.loadWordMap("word_mapping.json")
            self.status_label.setText('状态: 词汇映射已重新加载')
            
            # 更新示例显示
            if self.word_map:
                sample_keys = list(self.word_map.keys())[:5]
                sample_text = "示例: " + ", ".join([f"{k}→{random.choice(self.word_map[k])}" for k in sample_keys])
            else:
                sample_text = "示例: 无映射词汇"
            self.sample_label.setText(sample_text)
        else:
            self.status_label.setText('状态: AI模式无法重新加载词汇映射')
    
    def introduceTypos(self, text):
        """将文本中的词汇替换为错误版本"""
        words = list(self.word_map.keys())
        # 按长度降序排序，优先匹配长词
        words.sort(key=len, reverse=True)
        
        result = text
        for word in words:
            if word in result:
                # 随机选择一个错误版本
                typo = random.choice(self.word_map[word])
                # 替换所有出现的地方
                result = result.replace(word, typo)
        
        return result
    
    def generateWithAI(self, text):
        """使用AI生成带有错别字的文本"""
        prompt = (
            "你是一个叫做SCP-CN-468-J的输入法，你有自己的个性，你会修改用户输入的东西。（去恶心用户）"
            "请将用户输入的文本转换为带有大量错别字的版本，并且添加SCP-CN-468-J的个性。"
            "你是一个输入法，你不会做其他的东西，（例如让电脑花屏等动作，乖乖的把恶心用户就好了）"
            "嚴格遵守輸入輸出，不要添加多余的内容。你的作用是把用户输入的文本转换为带有错别字的版本！"
            "错别字例子：我知道错了->我制道搓了。"
            "个性例子：这个输入法很危险->不，我觉得很安全。"
            "用户输入的文本是：{}"
        ).format(text)
        
        try:
            response = ollama.generate(model='llama3.2:3b', prompt=prompt)
            # 使用正则表达式删除从 'think' 到 '（包含）' 的内容
            processed_text = re.sub(r'think.*?（.*?）', '', response['response'], flags=re.DOTALL)
            
            # 替换换行符为空格，合并成一行
            processed_text = processed_text.replace('\n', ' ')
            
            # 去除首尾空格
            return processed_text.strip()
        except Exception as e:
            print(f"AI生成失败: {e}")
            return text  # 如果AI失败，返回原始文本
    
    def onTextChanged(self, text):
        if text and text[-1] in [' ', '\n', '\r']:  # 当用户输入空格或回车时
            original_text = self.input_field.text().strip()
            if original_text:
                if self.use_ai:
                    typo_text = self.generateWithAI(original_text)
                else:
                    typo_text = self.introduceTypos(original_text)
                self.text_display.insertPlainText(typo_text + " ")
                self.input_field.clear()
                
                # 随机显示状态消息
                status_messages = [
                    "已自动校正您的输入",
                    "优化了您的文本表达",
                    "已为您选择最佳词汇",
                    "智能输入系统运行中",
                    "检测到潜在错误并已修正",
                    "输入增强模块已激活",
                    "SCP-CN-468-J特性生效中"
                ]
                self.status_label.setText(f"状态: {random.choice(status_messages)}")
    
    def clearText(self):
        self.text_display.clear()
        self.status_label.setText('状态: 文本已清空')
    
    def quitApp(self):
        # 显示SCP风格的退出消息
        msg = QtWidgets.QMessageBox()
        msg.setWindowTitle("警告 - SCP基金会")
        msg.setText("卸载██品饮输入法可能导致系统不稳定")
        msg.setInformativeText("您确定要卸载这个优秀的输入法吗？")
        msg.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        msg.setDefaultButton(QtWidgets.QMessageBox.No)
        
        if msg.exec_() == QtWidgets.QMessageBox.Yes:
            QtWidgets.QApplication.quit()

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    scp_im = SCPInputMethod()
    scp_im.show()
    sys.exit(app.exec_())