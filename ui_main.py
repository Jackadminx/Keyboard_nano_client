import datetime
import json
import yaml
import time, copy, re, sys, struct, os
import hid

from PySide2.QtCore import Qt, QUrl, QRect, QPropertyAnimation, QCoreApplication, QSequentialAnimationGroup
from PySide2.QtWidgets import QApplication, QMessageBox, QColorDialog, QSizePolicy, QGridLayout, QMenu, QProgressDialog
from PySide2.QtGui import QColor, QKeySequence, QScreen, QGuiApplication, QIcon, QDesktopServices, QCursor, QMouseEvent
from PySide2.QtUiTools import QUiLoader


# from PySide2.QtWebEngineWidgets import QWebEngineView

# from qt_material import apply_stylesheet


def init_usb(vendor_id, usage_page):
    global h
    h = hid.device()
    hid_enumerate = hid.enumerate()
    device_path = 0
    for i in range(len(hid_enumerate)):
        if (hid_enumerate[i]['usage_page'] == usage_page and hid_enumerate[i]['vendor_id'] == vendor_id):
            device_path = hid_enumerate[i]['path']
    if (device_path == 0): return "找不到设备"
    try:
        h.open_path(device_path)
        h.set_nonblocking(1)  # enable non-blocking mode
    except OSError:
        print("打开设备失败")


def out_data(vendor_id, usage_page, buffer):
    # h = hid.device()
    # hid_enumerate = hid.enumerate()
    # device_path = 0
    # for i in range(len(hid_enumerate)):
    #     if (hid_enumerate[i]['usage_page'] == usage_page and hid_enumerate[i]['vendor_id'] == vendor_id):
    #         device_path = hid_enumerate[i]['path']
    # if (device_path == 0):
    #     print("未找到设备")
    #     return 1
    #
    # h.open_path(device_path)
    # h.set_nonblocking(1)  # enable non-blocking mode
    print("------")
    print("<", buffer)
    try:
        code = h.write(buffer)
    except (OSError, ValueError):
        return 1
    if code == -1:
        print("写入失败")
    print("------")
    # h.close()
    return code


def ping(vendor_id, usage_page, page_id):
    # h = hid.device()
    # hid_enumerate = hid.enumerate()
    # device_path = 0
    # for i in range(len(hid_enumerate)):
    #     if (hid_enumerate[i]['usage_page'] == usage_page and hid_enumerate[i]['vendor_id'] == vendor_id):
    #         device_path = hid_enumerate[i]['path']
    # if (device_path == 0): return "找不到设备"
    # h.open_path(device_path)
    # h.set_nonblocking(1)  # enable non-blocking mode

    buffer = [0] * 60
    buffer[0] = page_id  # report_id
    buffer[1] = 0x03  # 读取/写入/复位/测试 0=r 1=w 2=reset 3=test

    print("------")
    print("<", buffer)
    time_start = time.time()
    try:
        h.write(buffer)
    except (OSError, ValueError):
        return 1
    while 1:
        try:
            d = h.read(64)
        except (OSError, ValueError):
            return 1
        if d:
            print(">", d)
            time_end = time.time()
            break
    print("------")
    # h.close()
    return 'Pong！ %ims' % ((time_end - time_start) * 1000)


def read_report(vendor_id, usage_page, buffer):
    # h = hid.device()
    # hid_enumerate = hid.enumerate()
    # device_path = 0
    # for i in range(len(hid_enumerate)):
    #     if (hid_enumerate[i]['usage_page'] == usage_page and hid_enumerate[i]['vendor_id'] == vendor_id):
    #         device_path = hid_enumerate[i]['path']
    # if (device_path == 0):
    #     print("未找到设备")
    #     return 1
    # h.open_path(device_path)
    # h.set_nonblocking(1)  # enable non-blocking mode

    print("------")
    print("<", buffer)
    time_start = time.time()
    try:
        h.write(buffer)
    except (OSError, ValueError, UnicodeEncodeError):
        print("写入设备错误")
        return 1
    while 1:
        try:
            d = h.read(64)
        except (OSError, ValueError):
            print("读取数据错误")
            return 1
        if d:
            print(">", d)
            break
        if time.time() - time_start > 3:
            d = 2
            break
    print("------")
    # h.close()
    return d


def configfile_init():
    try:
        with open('Data/config.yaml', 'r', encoding='utf-8') as f:
            result = yaml.load(f.read(), Loader=yaml.FullLoader)
    except FileNotFoundError:
        print("FileNotFoundError")
        sys.exit()
    # 高DPI适配
    # os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = result["QT_AUTO_SCREEN_SCALE_FACTOR"]
    if result["AA_EnableHighDpiScaling"] == 1:
        print("enable high dpi scaling")
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)  # enable high dpi scaling
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)  # use high dpi icons


class Stats:

    def __init__(self):
        self.rgb_data_FLASH = [0 for i in range(0, 64)]
        self.mode_data_FLASH = [0 for i in range(0, 64)]
        self.rgb_data = [0 for i in range(0, 64)]
        self.mode_data = [0 for i in range(0, 64)]
        # self.key_data_FLASH = [0 for i in range(0, 64)]
        # self.key_data = [0 for i in range(0, 64)]
        self.touch_dialog_data = {
            0: {"slide_ms": 20, "slide_px": 100, "osu_finish_ms": 100, "osu_r": 40, "osu_n": 6, "mouse_X": 0,
                "mouse_Y": 0, "mouse_ms": 100},
            1: {"slide_ms": 20, "slide_px": 100, "osu_finish_ms": 100, "osu_r": 40, "osu_n": 6, "mouse_X": 0,
                "mouse_Y": 0, "mouse_ms": 100},
            2: {"slide_ms": 20, "slide_px": 100, "osu_finish_ms": 100, "osu_r": 40, "osu_n": 6, "mouse_X": 0,
                "mouse_Y": 0, "mouse_ms": 100}, }
        self.mouse_dialog_data = {
            0: {"mouse_x": 40, "mouse_y": 0, "mouse_scroll": 0, "mouse_btn": 0},
            1: {"mouse_x": 40, "mouse_y": 0, "mouse_scroll": 0, "mouse_btn": 0},
            2: {"mouse_x": 40, "mouse_y": 0, "mouse_scroll": 0, "mouse_btn": 0}}
        self.dial_dialog_data = {
            0: {"delay": 10, "scroll": 2, "scroll_enable": False},
            1: {"delay": 10, "scroll": 2, "scroll_enable": False},
            2: {"delay": 10, "scroll": 2, "scroll_enable": False}}
        self.key_flag = [0, 0, 0]  # 按键修改触发标志位
        self.key_light = 7  # 点灯自锁
        self.mian_data = []
        self.keyboard_map = []

        # 从文件中加载UI定义
        self.ui = QUiLoader().load('QtUI/main.ui')
        self.helper = QUiLoader().load('QtUI/helper.ui')
        self.key_dialog = QUiLoader().load('QtUI/Standard_keyboard_Attributes.ui')
        self.touch_dialog = QUiLoader().load('QtUI/Touch_Attributes.ui')
        self.mouse_dialog = QUiLoader().load('QtUI/Mouse_func.ui')
        self.dial_dialog = QUiLoader().load('QtUI/VM_Dial.ui')
        self.ui.setWindowIcon(QIcon("QtUI/IMG/logo_transparent.ico"))

        # 动态调整窗口大小 暂定
        self.ui.tabWidget.currentChanged['int'].connect(self.tab_change)

        # 获取屏幕分辨率
        self.screenRect = QGuiApplication.primaryScreen().geometry()

        # 点击处理
        # ------------------------------------mode-------------------------------------------
        self.ui.mian_button_r.clicked.connect(self.mian_button_r)
        self.ui.mian_button_w.clicked.connect(self.mian_button_w)
        self.ui.ping.clicked.connect(self.ping)
        self.ui.reset.clicked.connect(self.reset)
        self.ui.reload.clicked.connect(self.reload)

        # ------------------------------------rgb-------------------------------------------
        self.ui.colorset_1_1.clicked.connect(self.colorset_1_1_func)
        self.ui.colorset_1_2.clicked.connect(self.colorset_1_2_func)
        self.ui.colorset_1_3.clicked.connect(self.colorset_1_3_func)
        self.ui.colorset_2_1.clicked.connect(self.colorset_2_1_func)
        self.ui.colorset_2_2.clicked.connect(self.colorset_2_2_func)
        self.ui.colorset_2_3.clicked.connect(self.colorset_2_3_func)
        self.ui.colorset_3_1.clicked.connect(self.colorset_3_1_func)
        self.ui.colorset_3_2.clicked.connect(self.colorset_3_2_func)
        self.ui.colorset_3_3.clicked.connect(self.colorset_3_3_func)
        self.ui.colorset_4_1.clicked.connect(self.colorset_4_1_func)
        self.ui.colorset_4_2.clicked.connect(self.colorset_4_2_func)
        self.ui.colorset_4_3.clicked.connect(self.colorset_4_3_func)
        self.ui.colorset_5_1.clicked.connect(self.colorset_5_1_func)
        self.ui.colorset_5_2.clicked.connect(self.colorset_5_2_func)
        self.ui.colorset_5_3.clicked.connect(self.colorset_5_3_func)
        self.ui.colorset_6_1.clicked.connect(self.colorset_6_1_func)
        self.ui.colorset_6_2.clicked.connect(self.colorset_6_2_func)
        self.ui.colorset_6_3.clicked.connect(self.colorset_6_3_func)
        # 右键
        # self.ui.colorset_1_1.customContextMenuRequested.connect(lambda: self.right_menu_show([1, 1]))
        self.ui.rgb_r.clicked.connect(self.rgb_r_func)
        self.ui.rgb_w.clicked.connect(self.rgb_w_func)
        self.ui.rgb_reset.clicked.connect(self.rgb_reset)
        # ------------------------------------raw-------------------------------------------
        self.ui.raw_send_button.clicked.connect(self.raw_send_button_func)
        self.ui.raw_send_button_2.clicked.connect(self.raw_send_button_2_func)
        self.ui.raw_help_button.clicked.connect(self.raw_help_button_func)
        # ------------------------------------key-------------------------------------------
        self.ui.k1_button.clicked.connect(self.k1_button_func)
        self.ui.k2_button.clicked.connect(self.k2_button_func)
        self.ui.k3_button.clicked.connect(self.k3_button_func)
        self.ui.key_r_button.clicked.connect(self.key_r_button_func)
        self.ui.key_w_button.clicked.connect(self.key_w_button_func)

        self.ui.k1_keySequenceEdit.editingFinished.connect(self.k1_keySequenceEdit_func)
        self.ui.k2_keySequenceEdit.editingFinished.connect(self.k2_keySequenceEdit_func)
        self.ui.k3_keySequenceEdit.editingFinished.connect(self.k3_keySequenceEdit_func)
        self.ui.k1_comboBox.currentIndexChanged.connect(self.k1_comboBox_func)
        self.ui.k2_comboBox.currentIndexChanged.connect(self.k2_comboBox_func)
        self.ui.k3_comboBox.currentIndexChanged.connect(self.k3_comboBox_func)
        self.ui.k1_comboBox_second.currentIndexChanged.connect(lambda: self.key_comboBox_second_changed(0))
        self.ui.k2_comboBox_second.currentIndexChanged.connect(lambda: self.key_comboBox_second_changed(1))
        self.ui.k3_comboBox_second.currentIndexChanged.connect(lambda: self.key_comboBox_second_changed(2))
        self.ui.k1_button_attribute.clicked.connect(self.k1_button_attribute_func)
        self.ui.k2_button_attribute.clicked.connect(self.k2_button_attribute_func)
        self.ui.k3_button_attribute.clicked.connect(self.k3_button_attribute_func)

        self.ui.expand_button.clicked.connect(self.expand_button_func)
        self.ui.expand_button_2.clicked.connect(self.expand_button_2_func)
        self.ui.expand_button_3.clicked.connect(self.expand_button_3_func)

        self.touch_dialog.mouse_click_1.clicked.connect(self.mouse_position)

        self.ui.get_resolution.clicked.connect(self.get_resolution_func)

        self.ui.led_effect_button_r.clicked.connect(self.mian_button_r)
        self.ui.led_effect_button_w.clicked.connect(self.mian_button_w)

        # ------------------------------------key_dialog_keySequenceEdit-------------------------------------------
        self.key_dialog.keySequenceEdit.editingFinished.connect(self.key_dialog_keySequenceEdit_func)

        self.animation_group = QSequentialAnimationGroup()
        self.device_init(0)
        self.animation_group.finished.connect(self.lock_window_size)
        # def handleCalc(self):
        #     # QMessageBox.about(self.ui, "info", "OK")
        #     self.ui.statusBar().showMessage("Ready")

        # ------------------------------------模式选择-------------------------------------------

    def device_init(self, code):
        # 重载设备
        if code == 1:
            vendor_id = int((self.ui.vendor_id.text()), 16)
            usage_page = int((self.ui.vendor_page.text()), 16)
            init_usb(vendor_id, usage_page)
        # 初始化
        elif code == 0:
            if (sys.platform == "linux"):
                self.ui.vendor_page.setText("0")
                self.ui.about_label2.setText("Client for Linux")
                if os.geteuid() != 0:
                    QMessageBox.information(self.ui, "Tips", "如果不能读取设备，建议以根权限运行")
            try:
                with open("./Data/keyboard.json", 'r') as load_f:
                    self.keyboard_map = json.load(load_f)
                with open("./Data/main.json", 'r', encoding='gbk') as load_f:
                    self.mian_data = json.load(load_f)
            except FileNotFoundError:
                print("FileNotFoundError")
                sys.exit()

            # 隐藏未启用功能
            self.ui.expand_button.setVisible(False)
            self.ui.expand_button_2.setVisible(False)
            self.ui.expand_button_3.setVisible(False)
            self.ui.k1_button_attribute.setVisible(True)
            self.ui.k2_button_attribute.setVisible(True)
            self.ui.k3_button_attribute.setVisible(True)
            self.ui.k1_comboBox_second.setVisible(False)
            self.ui.k2_comboBox_second.setVisible(False)
            self.ui.k3_comboBox_second.setVisible(False)

            # 标准键盘属性菜单 隐藏未开发功能
            self.key_dialog.checkBox_5.setVisible(False)
            self.key_dialog.checkBox_6.setVisible(False)
            self.key_dialog.checkBox_7.setVisible(False)
            self.key_dialog.checkBox_8.setVisible(False)

            # 加载键盘功能下拉列表
            if self.ui.k1_comboBox.count() != len(self.mian_data["key_func_list"]):
                self.ui.k1_comboBox.clear()
                for i in self.mian_data["key_func_list"]:
                    self.ui.k1_comboBox.addItem(i)
            if self.ui.k2_comboBox.count() != len(self.mian_data["key_func_list"]):
                self.ui.k2_comboBox.clear()
                for i in self.mian_data["key_func_list"]:
                    self.ui.k2_comboBox.addItem(i)
            if self.ui.k3_comboBox.count() != len(self.mian_data["key_func_list"]):
                self.ui.k3_comboBox.clear()
                for i in self.mian_data["key_func_list"]:
                    self.ui.k3_comboBox.addItem(i)

            # 加载预设模式名
            self.ui.keyboard_mode_1.setText(self.mian_data["keyboard_mode_group"]["name"][0])
            self.ui.keyboard_mode_2.setText(self.mian_data["keyboard_mode_group"]["name"][1])
            self.ui.keyboard_mode_3.setText(self.mian_data["keyboard_mode_group"]["name"][2])
            self.ui.keyboard_mode_4.setText(self.mian_data["keyboard_mode_group"]["name"][3])
            self.ui.keyboard_mode_5.setText(self.mian_data["keyboard_mode_group"]["name"][4])
            self.ui.keyboard_mode_6.setText(self.mian_data["keyboard_mode_group"]["name"][5])
            self.ui.keyboard_mode_7.setText(self.mian_data["keyboard_mode_group"]["name"][6])
            self.ui.keyboard_mode_8.setText(self.mian_data["keyboard_mode_group"]["name"][7])
            self.ui.keyboard_mode_9.setText(self.mian_data["keyboard_mode_group"]["name"][8])
            self.ui.keyboard_mode_10.setText(self.mian_data["keyboard_mode_group"]["name"][9])
            self.ui.keyboard_mode_11.setText(self.mian_data["keyboard_mode_group"]["name"][10])
            self.ui.keyboard_mode_12.setText(self.mian_data["keyboard_mode_group"]["name"][11])
            self.ui.keyboard_mode_13.setText(self.mian_data["keyboard_mode_group"]["name"][12])
            self.ui.keyboard_mode_14.setText(self.mian_data["keyboard_mode_group"]["name"][13])
            self.ui.keyboard_mode_15.setText(self.mian_data["keyboard_mode_group"]["name"][14])

            # 加载预设模式工具提示
            self.ui.keyboard_mode_1.setToolTip(self.mian_data["keyboard_mode_group"]["ToolTip"][0])
            self.ui.keyboard_mode_2.setToolTip(self.mian_data["keyboard_mode_group"]["ToolTip"][1])
            self.ui.keyboard_mode_3.setToolTip(self.mian_data["keyboard_mode_group"]["ToolTip"][2])
            self.ui.keyboard_mode_4.setToolTip(self.mian_data["keyboard_mode_group"]["ToolTip"][3])
            self.ui.keyboard_mode_5.setToolTip(self.mian_data["keyboard_mode_group"]["ToolTip"][4])
            self.ui.keyboard_mode_6.setToolTip(self.mian_data["keyboard_mode_group"]["ToolTip"][5])
            self.ui.keyboard_mode_7.setToolTip(self.mian_data["keyboard_mode_group"]["ToolTip"][6])
            self.ui.keyboard_mode_8.setToolTip(self.mian_data["keyboard_mode_group"]["ToolTip"][7])
            self.ui.keyboard_mode_9.setToolTip(self.mian_data["keyboard_mode_group"]["ToolTip"][8])
            self.ui.keyboard_mode_10.setToolTip(self.mian_data["keyboard_mode_group"]["ToolTip"][9])
            self.ui.keyboard_mode_11.setToolTip(self.mian_data["keyboard_mode_group"]["ToolTip"][10])
            self.ui.keyboard_mode_12.setToolTip(self.mian_data["keyboard_mode_group"]["ToolTip"][11])
            self.ui.keyboard_mode_13.setToolTip(self.mian_data["keyboard_mode_group"]["ToolTip"][12])
            self.ui.keyboard_mode_14.setToolTip(self.mian_data["keyboard_mode_group"]["ToolTip"][13])
            self.ui.keyboard_mode_15.setToolTip(self.mian_data["keyboard_mode_group"]["ToolTip"][14])

            # 触摸设置置顶
            self.touch_dialog.setWindowFlags(Qt.WindowStaysOnTopHint)
            # # 追踪鼠标位置
            # self.touch_dialog.setMouseTracking(True)
            # pos = QCursor.pos()
            # print(pos.x(),"  ", pos.y())

            # 获取屏幕分辨率
            self.ui.resolution_X.setValue(self.screenRect.width())
            self.ui.resolution_Y.setValue(self.screenRect.height())
            # 初始化设备
            vendor_id = int((self.ui.vendor_id.text()), 16)
            usage_page = int((self.ui.vendor_page.text()), 16)
            init_usb(vendor_id, usage_page)
            # 读取设备信息
            self.rgb_r_func()
            self.key_r_button_func()

        self.lock_window_size()

    def ping(self):
        # print(hex(int((self.ui.lineEdit.text()), 16)))  # 16进制字符串转16进制
        vendor_id = int((self.ui.vendor_id.text()), 16)
        usage_page = int((self.ui.vendor_page.text()), 16)
        page_id = int(self.ui.usage_id.text())

        info = ping(vendor_id, usage_page, page_id)
        if info == 1:
            self.ui.statusBar().showMessage("未找到设备，请重试")
            self.device_init(1)
        self.ui.statusBar().showMessage(info)

    def reset(self):
        vendor_id = int((self.ui.vendor_id.text()), 16)
        usage_page = int((self.ui.vendor_page.text()), 16)
        page_id = int(self.ui.usage_id.text())

        buffer = [0] * 60
        buffer[0] = page_id  # report_id
        buffer[1] = 0x02  # 读取/写入/复位/测试 0=r 1=w 2=reset 3=test

        info = out_data(vendor_id, usage_page, buffer)
        if info == 1:
            self.ui.statusBar().showMessage("请重试")
            time.sleep(1)
            self.device_init(1)
            return 1
        elif info == -1:
            self.ui.statusBar().showMessage("写入错误")
            return -1

    def reload(self):
        vendor_id = int((self.ui.vendor_id.text()), 16)
        usage_page = int((self.ui.vendor_page.text()), 16)
        page_id = int(self.ui.usage_id.text())
        buffer = [0] * 2
        buffer[0] = page_id  # report_id
        buffer[1] = 0x04  # reload
        out_data(vendor_id, usage_page, buffer)
        print("reload")
        time.sleep(0.6)

    def mian_button_w(self):
        # 进度窗口
        progress = QProgressDialog("Please Wait!", "Cancel", 0, 100, self.ui)
        progress.setWindowModality(Qt.WindowModal)
        progress.setAutoClose(True)
        progress.setWindowTitle("Flash...")
        progress.show()
        time.sleep(0.3)  # 等待窗口显示
        progress.setValue(1)

        vendor_id = int((self.ui.vendor_id.text()), 16)
        usage_page = int((self.ui.vendor_page.text()), 16)
        page_id = int(self.ui.usage_id.text())

        buffer = [0] * 60
        buffer[0] = page_id  # report_id
        buffer[1] = 1  # 读取/写入/复位/测试 0=r 1=w 2=reset 3=test
        buffer[2] = 0  # 单元ID 00=功能设置 01=led 02=简单key 03=多媒体键
        buffer[3] = 0  # 保留位

        if self.key_flag:
            buffer[4] = 0

        if self.ui.keyboard_mode_1.isChecked():  # 预设模式
            buffer[4] = 0
        elif self.ui.keyboard_mode_2.isChecked():
            buffer[4] = 1
        elif self.ui.keyboard_mode_3.isChecked():
            buffer[4] = 2
        elif self.ui.keyboard_mode_4.isChecked():
            buffer[4] = 3
        elif self.ui.keyboard_mode_5.isChecked():
            buffer[4] = 4
        elif self.ui.keyboard_mode_6.isChecked():
            buffer[4] = 5
        elif self.ui.keyboard_mode_7.isChecked():
            buffer[4] = 6
        elif self.ui.keyboard_mode_8.isChecked():
            buffer[4] = 7
        elif self.ui.keyboard_mode_9.isChecked():
            buffer[4] = 8
        elif self.ui.keyboard_mode_10.isChecked():
            buffer[4] = 9
        elif self.ui.keyboard_mode_11.isChecked():
            buffer[4] = 10
        elif self.ui.keyboard_mode_12.isChecked():
            buffer[4] = 11
        elif self.ui.keyboard_mode_13.isChecked():
            buffer[4] = 12
        elif self.ui.keyboard_mode_14.isChecked():
            buffer[4] = 13
        elif self.ui.keyboard_mode_15.isChecked():
            buffer[4] = 14

        if buffer[4] != 0:
            # print(self.mian_data["keyboard_mode_group"][str(buffer[4])])
            for i in range(0, 3):
                mode_group = self.mian_data["keyboard_mode_group"][str(buffer[4])][i].copy()
                info = out_data(vendor_id, usage_page, mode_group)
                time.sleep(0.6)
                if info == 1:
                    self.ui.statusBar().showMessage("未找到设备，请重试")
                    self.device_init(1)
                    progress.setValue(100)
                    return 1
                elif info == -1:
                    self.ui.statusBar().showMessage("写入错误")
                    progress.setValue(100)
                    return -1
                if i == 0:
                    progress.setValue(20)
                if i == 1:
                    progress.setValue(40)
                if i == 2:
                    progress.setValue(60)
                    self.reload()
                    progress.setValue(70)
                    self.key_r_button_func()
                    progress.setValue(75)

        if self.ui.rgb_func.isChecked():  # rgb使能
            buffer[7] = int(self.ui.rgb_comboBox.currentIndex()) + 1  # led模式 0x00-0x06 0为关闭
        else:
            buffer[7] = 0

        buffer[9] = int(self.ui.keyboard_scanSP.value())  # 键盘扫描速度  1ms单位
        buffer[10] = int(self.ui.keyboard_LP.value() / 100)  # 长按识别间隔 100ms单位
        buffer[11] = int(self.ui.resolution_X.value() % 255)
        buffer[12] = int(self.ui.resolution_X.value() / 255)
        buffer[13] = int(self.ui.resolution_Y.value() % 255)
        buffer[14] = int(self.ui.resolution_Y.value() / 255)

        if self.ui.led_effect_radioButton_1.isChecked():  # 灯效
            buffer[15] = 0
        elif self.ui.led_effect_radioButton_2.isChecked():
            buffer[15] = 1
        elif self.ui.led_effect_radioButton_3.isChecked():
            buffer[15] = 2
        elif self.ui.led_effect_radioButton_4.isChecked():
            buffer[15] = 3
        elif self.ui.led_effect_radioButton_5.isChecked():
            buffer[15] = 4

        # 判断是否与之前的数据相同，避免重复写入
        # print(buffer[4:16])
        # print(self.mode_data_FLASH[4:16])
        buffer1 = buffer[4:16].copy()
        buffer2 = self.mode_data_FLASH[4:16].copy()
        if buffer1 == buffer2:
            print("mode数据未改变")
            self.ui.statusBar().showMessage("数据未改变")
            progress.setValue(100)
            return 0
        info = out_data(vendor_id, usage_page, buffer)
        progress.setValue(80)
        if info == 1:
            self.ui.statusBar().showMessage("未找到设备，请重试")
            self.device_init(1)
            progress.setValue(100)
            return 1
        elif info == -1:
            self.ui.statusBar().showMessage("写入错误")
            progress.setValue(100)
            return -1
        else:
            time.sleep(1)
            self.reload()
            progress.setValue(90)
            self.mian_button_r()
            self.ui.statusBar().showMessage("写入完成")
            progress.setValue(100)
            return "ok"

    def mian_button_r(self):

        vendor_id = int((self.ui.vendor_id.text()), 16)
        usage_page = int((self.ui.vendor_page.text()), 16)
        page_id = int(self.ui.usage_id.text())

        buffer = [0] * 60
        buffer[0] = page_id  # report_id
        buffer[1] = 0  # 读取/写入/复位/测试 0=r 1=w 2=reset 3=test
        buffer[2] = 0  # 单元ID 00=功能设置 01=led 02=简单key 03=多媒体键

        info = read_report(vendor_id, usage_page, buffer)
        if info == 1:
            self.ui.statusBar().showMessage("未找到设备，请重试")
            self.device_init(1)
        elif info == 2:
            self.ui.statusBar().showMessage("读取失败")
        elif isinstance(info, list):
            self.ui.statusBar().showMessage("读取完成")
            self.mode_data_FLASH = info.copy()
            # 预设模式
            if info[4] == 0:
                self.ui.keyboard_mode_1.setChecked(True)
            elif info[4] == 1:
                self.ui.keyboard_mode_2.setChecked(True)
            elif info[4] == 2:
                self.ui.keyboard_mode_3.setChecked(True)
            elif info[4] == 3:
                self.ui.keyboard_mode_4.setChecked(True)
            elif info[4] == 4:
                self.ui.keyboard_mode_5.setChecked(True)
            elif info[4] == 5:
                self.ui.keyboard_mode_6.setChecked(True)
            elif info[4] == 6:
                self.ui.keyboard_mode_7.setChecked(True)
            elif info[4] == 7:
                self.ui.keyboard_mode_8.setChecked(True)
            elif info[4] == 8:
                self.ui.keyboard_mode_9.setChecked(True)
            elif info[4] == 9:
                self.ui.keyboard_mode_10.setChecked(True)
            elif info[4] == 10:
                self.ui.keyboard_mode_11.setChecked(True)
            elif info[4] == 11:
                self.ui.keyboard_mode_12.setChecked(True)
            elif info[4] == 12:
                self.ui.keyboard_mode_13.setChecked(True)
            elif info[4] == 13:
                self.ui.keyboard_mode_14.setChecked(True)
            elif info[4] == 14:
                self.ui.keyboard_mode_15.setChecked(True)

            # led模式 0x00-0x06 0为关闭
            if info[7] == 0:
                self.ui.rgb_func.setChecked(False)
            else:
                self.ui.rgb_func.setChecked(True)

            if info[7] == 1:
                self.ui.rgb_comboBox.setCurrentText("灯光组 1")
            elif info[7] == 2:
                self.ui.rgb_comboBox.setCurrentText("灯光组 2")
            elif info[7] == 3:
                self.ui.rgb_comboBox.setCurrentText("灯光组 3")
            elif info[7] == 4:
                self.ui.rgb_comboBox.setCurrentText("灯光组 4")
            elif info[7] == 5:
                self.ui.rgb_comboBox.setCurrentText("灯光组 5")
            elif info[7] == 6:
                self.ui.rgb_comboBox.setCurrentText("灯光组 6")

            self.ui.keyboard_scanSP.setValue(info[9])
            self.ui.keyboard_LP.setValue(info[10] * 100)
            self.ui.resolution_X.setValue(int(info[12] * 255 + info[11]))
            self.ui.resolution_Y.setValue(int(info[14] * 255 + info[13]))

            # 灯效
            if info[15] == 0:
                self.ui.led_effect_radioButton_1.setChecked(True)
            elif info[15] == 1:
                self.ui.led_effect_radioButton_2.setChecked(True)
            elif info[15] == 2:
                self.ui.led_effect_radioButton_3.setChecked(True)
            elif info[15] == 3:
                self.ui.led_effect_radioButton_4.setChecked(True)
            elif info[15] == 4:
                self.ui.led_effect_radioButton_5.setChecked(True)

    # ------------------------------------RGB功能-------------------------------------------

    def colorset_1_1_func(self):
        color = QColorDialog.getColor(QColor("#%02x%02x%02x" % (self.rgb_data[1], self.rgb_data[2], self.rgb_data[0])))
        # color = QColorDialog.getColor()
        if color.isValid():
            print(color.red(), " ", color.green(), " ", color.blue())
            self.rgb_data[0] = color.blue()
            self.rgb_data[1] = color.red()
            self.rgb_data[2] = color.green()
            self.ui.colorset_1_1.setStyleSheet(
                "background-color: #%02x%02x%02x" % (color.red(), color.green(), color.blue()))
            # print("background-color: #%02x%02x%02x" % (color.red(), color.green(), color.blue()))

    def colorset_1_2_func(self):
        color = QColorDialog.getColor(QColor("#%02x%02x%02x" % (self.rgb_data[4], self.rgb_data[5], self.rgb_data[3])))

        if color.isValid():
            print(color.red(), " ", color.green(), " ", color.blue())
            self.rgb_data[3] = color.blue()
            self.rgb_data[4] = color.red()
            self.rgb_data[5] = color.green()
            self.ui.colorset_1_2.setStyleSheet(
                "background-color: #%02x%02x%02x" % (color.red(), color.green(), color.blue()))

    def colorset_1_3_func(self):
        color = QColorDialog.getColor(QColor("#%02x%02x%02x" % (self.rgb_data[7], self.rgb_data[8], self.rgb_data[6])))

        if color.isValid():
            print(color.red(), " ", color.green(), " ", color.blue())
            self.rgb_data[6] = color.blue()
            self.rgb_data[7] = color.red()
            self.rgb_data[8] = color.green()
            self.ui.colorset_1_3.setStyleSheet(
                "background-color: #%02x%02x%02x" % (color.red(), color.green(), color.blue()))

    def colorset_2_1_func(self):
        color = QColorDialog.getColor(
            QColor("#%02x%02x%02x" % (self.rgb_data[10], self.rgb_data[11], self.rgb_data[9])))

        if color.isValid():
            print(color.red(), " ", color.green(), " ", color.blue())
            self.rgb_data[9] = color.blue()
            self.rgb_data[10] = color.red()
            self.rgb_data[11] = color.green()
            self.ui.colorset_2_1.setStyleSheet(
                "background-color: #%02x%02x%02x" % (color.red(), color.green(), color.blue()))

    def colorset_2_2_func(self):
        color = QColorDialog.getColor(
            QColor("#%02x%02x%02x" % (self.rgb_data[13], self.rgb_data[14], self.rgb_data[12])))

        if color.isValid():
            print(color.red(), " ", color.green(), " ", color.blue())
            self.rgb_data[12] = color.blue()
            self.rgb_data[13] = color.red()
            self.rgb_data[14] = color.green()
            self.ui.colorset_2_2.setStyleSheet(
                "background-color: #%02x%02x%02x" % (color.red(), color.green(), color.blue()))

    def colorset_2_3_func(self):
        color = QColorDialog.getColor(
            QColor("#%02x%02x%02x" % (self.rgb_data[16], self.rgb_data[17], self.rgb_data[15])))

        if color.isValid():
            print(color.red(), " ", color.green(), " ", color.blue())
            self.rgb_data[15] = color.blue()
            self.rgb_data[16] = color.red()
            self.rgb_data[17] = color.green()
            self.ui.colorset_2_3.setStyleSheet(
                "background-color: #%02x%02x%02x" % (color.red(), color.green(), color.blue()))

    def colorset_3_1_func(self):
        color = QColorDialog.getColor(
            QColor("#%02x%02x%02x" % (self.rgb_data[19], self.rgb_data[20], self.rgb_data[18])))

        if color.isValid():
            print(color.red(), " ", color.green(), " ", color.blue())
            self.rgb_data[18] = color.blue()
            self.rgb_data[19] = color.red()
            self.rgb_data[20] = color.green()
            self.ui.colorset_3_1.setStyleSheet(
                "background-color: #%02x%02x%02x" % (color.red(), color.green(), color.blue()))

    def colorset_3_2_func(self):
        color = QColorDialog.getColor(
            QColor("#%02x%02x%02x" % (self.rgb_data[22], self.rgb_data[23], self.rgb_data[21])))

        if color.isValid():
            print(color.red(), " ", color.green(), " ", color.blue())
            self.rgb_data[21] = color.blue()
            self.rgb_data[22] = color.red()
            self.rgb_data[23] = color.green()
            self.ui.colorset_3_2.setStyleSheet(
                "background-color: #%02x%02x%02x" % (color.red(), color.green(), color.blue()))

    def colorset_3_3_func(self):
        color = QColorDialog.getColor(
            QColor("#%02x%02x%02x" % (self.rgb_data[25], self.rgb_data[26], self.rgb_data[24])))

        if color.isValid():
            print(color.red(), " ", color.green(), " ", color.blue())
            self.rgb_data[24] = color.blue()
            self.rgb_data[25] = color.red()
            self.rgb_data[26] = color.green()
            self.ui.colorset_3_3.setStyleSheet(
                "background-color: #%02x%02x%02x" % (color.red(), color.green(), color.blue()))

    def colorset_4_1_func(self):
        color = QColorDialog.getColor(
            QColor("#%02x%02x%02x" % (self.rgb_data[28], self.rgb_data[29], self.rgb_data[27])))

        if color.isValid():
            print(color.red(), " ", color.green(), " ", color.blue())
            self.rgb_data[27] = color.blue()
            self.rgb_data[28] = color.red()
            self.rgb_data[29] = color.green()
            self.ui.colorset_4_1.setStyleSheet(
                "background-color: #%02x%02x%02x" % (color.red(), color.green(), color.blue()))

    def colorset_4_2_func(self):
        color = QColorDialog.getColor(
            QColor("#%02x%02x%02x" % (self.rgb_data[31], self.rgb_data[32], self.rgb_data[30])))

        if color.isValid():
            print(color.red(), " ", color.green(), " ", color.blue())
            self.rgb_data[30] = color.blue()
            self.rgb_data[31] = color.red()
            self.rgb_data[32] = color.green()
            self.ui.colorset_4_2.setStyleSheet(
                "background-color: #%02x%02x%02x" % (color.red(), color.green(), color.blue()))

    def colorset_4_3_func(self):
        color = QColorDialog.getColor(
            QColor("#%02x%02x%02x" % (self.rgb_data[34], self.rgb_data[35], self.rgb_data[33])))
        if color.isValid():
            print(color.red(), " ", color.green(), " ", color.blue())
            self.rgb_data[33] = color.blue()
            self.rgb_data[34] = color.red()
            self.rgb_data[35] = color.green()
            self.ui.colorset_4_3.setStyleSheet(
                "background-color: #%02x%02x%02x" % (color.red(), color.green(), color.blue()))

    def colorset_5_1_func(self):
        color = QColorDialog.getColor(
            QColor("#%02x%02x%02x" % (self.rgb_data[37], self.rgb_data[38], self.rgb_data[36])))
        if color.isValid():
            print(color.red(), " ", color.green(), " ", color.blue())
            self.rgb_data[36] = color.blue()
            self.rgb_data[37] = color.red()
            self.rgb_data[38] = color.green()
            self.ui.colorset_5_1.setStyleSheet(
                "background-color: #%02x%02x%02x" % (color.red(), color.green(), color.blue()))

    def colorset_5_2_func(self):
        color = QColorDialog.getColor(
            QColor("#%02x%02x%02x" % (self.rgb_data[40], self.rgb_data[41], self.rgb_data[39])))
        if color.isValid():
            print(color.red(), " ", color.green(), " ", color.blue())
            self.rgb_data[39] = color.blue()
            self.rgb_data[40] = color.red()
            self.rgb_data[41] = color.green()
            self.ui.colorset_5_2.setStyleSheet(
                "background-color: #%02x%02x%02x" % (color.red(), color.green(), color.blue()))

    def colorset_5_3_func(self):
        color = QColorDialog.getColor(
            QColor("#%02x%02x%02x" % (self.rgb_data[43], self.rgb_data[44], self.rgb_data[42])))
        if color.isValid():
            print(color.red(), " ", color.green(), " ", color.blue())
            self.rgb_data[42] = color.blue()
            self.rgb_data[43] = color.red()
            self.rgb_data[44] = color.green()
            self.ui.colorset_5_3.setStyleSheet(
                "background-color: #%02x%02x%02x" % (color.red(), color.green(), color.blue()))

    def colorset_6_1_func(self):
        color = QColorDialog.getColor(
            QColor("#%02x%02x%02x" % (self.rgb_data[46], self.rgb_data[47], self.rgb_data[45])))
        if color.isValid():
            print(color.red(), " ", color.green(), " ", color.blue())
            self.rgb_data[45] = color.blue()
            self.rgb_data[46] = color.red()
            self.rgb_data[47] = color.green()
            self.ui.colorset_6_1.setStyleSheet(
                "background-color: #%02x%02x%02x" % (color.red(), color.green(), color.blue()))

    def colorset_6_2_func(self):
        color = QColorDialog.getColor(
            QColor("#%02x%02x%02x" % (self.rgb_data[49], self.rgb_data[50], self.rgb_data[48])))
        if color.isValid():
            self.rgb_data[48] = color.blue()
            self.rgb_data[49] = color.red()
            self.rgb_data[50] = color.green()
            self.ui.colorset_6_2.setStyleSheet(
                "background-color: #%02x%02x%02x" % (color.red(), color.green(), color.blue()))

    def colorset_6_3_func(self):
        color = QColorDialog.getColor(
            QColor("#%02x%02x%02x" % (self.rgb_data[52], self.rgb_data[53], self.rgb_data[51])))
        if color.isValid():
            self.rgb_data[51] = color.blue()
            self.rgb_data[52] = color.red()
            self.rgb_data[53] = color.green()
            self.ui.colorset_6_3.setStyleSheet(
                "background-color: #%02x%02x%02x" % (color.red(), color.green(), color.blue()))

    def rgb_w_func(self):
        # 进度窗口
        progress = QProgressDialog("Please Wait!", "Cancel", 0, 100, self.ui)
        progress.setWindowModality(Qt.WindowModal)
        progress.setWindowTitle("Flash...")
        progress.setAutoClose(True)
        progress.show()
        time.sleep(0.3)  # 等待窗口显示
        progress.setValue(1)

        vendor_id = int((self.ui.vendor_id.text()), 16)
        usage_page = int((self.ui.vendor_page.text()), 16)
        page_id = int(self.ui.usage_id.text())

        if self.rgb_data_FLASH == self.rgb_data:
            print("rgb数据未改变")
            info1 = 0
        else:
            buffer = self.rgb_data.copy()
            for i in range(0, 4):  # 数组右移4位
                buffer.insert(0, buffer.pop())
            buffer[0] = page_id  # report_id
            buffer[1] = 1  # 读取/写入/复位/测试 0=r 1=w 2=reset 3=test
            buffer[2] = 1  # 单元ID 00=功能设置 01=led 02=简单key 03=多媒体键
            buffer[3] = 0  # 保留位
            self.ui.statusBar().showMessage("写入中 ...")
            info1 = out_data(vendor_id, usage_page, buffer)
            time.sleep(1.6)
            progress.setValue(30)
            # 左移数组
            for i in range(0, 4):
                buffer.insert(len(buffer), buffer[0])
                buffer.remove(buffer[0])
            # 保存数据以进行对比
            self.rgb_data_FLASH = buffer.copy()

        info2 = self.mian_button_w()
        progress.setValue(60)
        if info1 == 1 or info2 == 1:
            self.ui.statusBar().showMessage("未找到设备，请重试")
            self.device_init()
        elif info1 == -1 or info2 == -1:
            self.ui.statusBar().showMessage("写入错误")
        elif info1 == 0 and info2 == 0:
            self.ui.statusBar().showMessage("数据未改变")
        else:
            self.ui.statusBar().showMessage("数据已写入")
            self.reload()
            progress.setValue(80)
        progress.setValue(100)

    def rgb_r_func(self):
        vendor_id = int((self.ui.vendor_id.text()), 16)
        usage_page = int((self.ui.vendor_page.text()), 16)
        page_id = int(self.ui.usage_id.text())

        self.mian_button_r()

        buffer = [0] * 60
        buffer[0] = page_id  # report_id
        buffer[1] = 0  # 读取/写入/复位/测试 0=r 1=w 2=reset 3=test
        buffer[2] = 1  # 单元ID 00=功能设置 01=led 02=简单key 03=多媒体键

        info = read_report(vendor_id, usage_page, buffer)

        if info == 1:
            self.ui.statusBar().showMessage("未找到设备，请重试")
            self.device_init(1)
        elif info == 2:
            self.ui.statusBar().showMessage("读取失败")
        else:
            self.ui.statusBar().showMessage("读取完成")
            # 循环左移4位
            for i in range(0, 4):
                info.insert(len(info), info[0])
                info.remove(info[0])

            # RGB 120 <- BRG 012 修改排列
            self.ui.colorset_1_1.setStyleSheet("background-color: rgb(%d, %d, %d)" % (info[1], info[2], info[0]))
            self.ui.colorset_1_2.setStyleSheet("background-color: rgb(%d, %d, %d)" % (info[4], info[5], info[3]))
            self.ui.colorset_1_3.setStyleSheet("background-color: rgb(%d, %d, %d)" % (info[7], info[8], info[6]))
            self.ui.colorset_2_1.setStyleSheet("background-color: rgb(%d, %d, %d)" % (info[10], info[11], info[9]))
            self.ui.colorset_2_2.setStyleSheet("background-color: rgb(%d, %d, %d)" % (info[13], info[14], info[12]))
            self.ui.colorset_2_3.setStyleSheet("background-color: rgb(%d, %d, %d)" % (info[16], info[17], info[15]))
            self.ui.colorset_3_1.setStyleSheet("background-color: rgb(%d, %d, %d)" % (info[19], info[20], info[18]))
            self.ui.colorset_3_2.setStyleSheet("background-color: rgb(%d, %d, %d)" % (info[22], info[23], info[21]))
            self.ui.colorset_3_3.setStyleSheet("background-color: rgb(%d, %d, %d)" % (info[25], info[26], info[24]))
            self.ui.colorset_4_1.setStyleSheet("background-color: rgb(%d, %d, %d)" % (info[28], info[29], info[27]))
            self.ui.colorset_4_2.setStyleSheet("background-color: rgb(%d, %d, %d)" % (info[31], info[32], info[30]))
            self.ui.colorset_4_3.setStyleSheet("background-color: rgb(%d, %d, %d)" % (info[34], info[35], info[33]))
            self.ui.colorset_5_1.setStyleSheet("background-color: rgb(%d, %d, %d)" % (info[37], info[38], info[36]))
            self.ui.colorset_5_2.setStyleSheet("background-color: rgb(%d, %d, %d)" % (info[40], info[41], info[39]))
            self.ui.colorset_5_3.setStyleSheet("background-color: rgb(%d, %d, %d)" % (info[43], info[44], info[42]))
            self.ui.colorset_6_1.setStyleSheet("background-color: rgb(%d, %d, %d)" % (info[46], info[47], info[45]))
            self.ui.colorset_6_2.setStyleSheet("background-color: rgb(%d, %d, %d)" % (info[49], info[50], info[48]))
            self.ui.colorset_6_3.setStyleSheet("background-color: rgb(%d, %d, %d)" % (info[52], info[53], info[51]))

            self.rgb_data_FLASH = info.copy()
            self.rgb_data = info.copy()

    def rgb_reset(self):
        # 清空界面上的rgb颜色
        info = [0xff] * 64
        self.ui.colorset_1_1.setStyleSheet("background-color: rgb(%d, %d, %d)" % (info[1], info[2], info[0]))
        self.ui.colorset_1_2.setStyleSheet("background-color: rgb(%d, %d, %d)" % (info[4], info[5], info[3]))
        self.ui.colorset_1_3.setStyleSheet("background-color: rgb(%d, %d, %d)" % (info[7], info[8], info[6]))
        self.ui.colorset_2_1.setStyleSheet("background-color: rgb(%d, %d, %d)" % (info[10], info[11], info[9]))
        self.ui.colorset_2_2.setStyleSheet("background-color: rgb(%d, %d, %d)" % (info[13], info[14], info[12]))
        self.ui.colorset_2_3.setStyleSheet("background-color: rgb(%d, %d, %d)" % (info[16], info[17], info[15]))
        self.ui.colorset_3_1.setStyleSheet("background-color: rgb(%d, %d, %d)" % (info[19], info[20], info[18]))
        self.ui.colorset_3_2.setStyleSheet("background-color: rgb(%d, %d, %d)" % (info[22], info[23], info[21]))
        self.ui.colorset_3_3.setStyleSheet("background-color: rgb(%d, %d, %d)" % (info[25], info[26], info[24]))
        self.ui.colorset_4_1.setStyleSheet("background-color: rgb(%d, %d, %d)" % (info[28], info[29], info[27]))
        self.ui.colorset_4_2.setStyleSheet("background-color: rgb(%d, %d, %d)" % (info[31], info[32], info[30]))
        self.ui.colorset_4_3.setStyleSheet("background-color: rgb(%d, %d, %d)" % (info[34], info[35], info[33]))
        self.ui.colorset_5_1.setStyleSheet("background-color: rgb(%d, %d, %d)" % (info[37], info[38], info[36]))
        self.ui.colorset_5_2.setStyleSheet("background-color: rgb(%d, %d, %d)" % (info[40], info[41], info[39]))
        self.ui.colorset_5_3.setStyleSheet("background-color: rgb(%d, %d, %d)" % (info[43], info[44], info[42]))
        self.ui.colorset_6_1.setStyleSheet("background-color: rgb(%d, %d, %d)" % (info[46], info[47], info[45]))
        self.ui.colorset_6_2.setStyleSheet("background-color: rgb(%d, %d, %d)" % (info[50], info[51], info[48]))
        self.ui.colorset_6_3.setStyleSheet("background-color: rgb(%d, %d, %d)" % (info[51], info[52], info[53]))
        self.rgb_data = info.copy()

    # def right_menu_show(self, btn_num):
    #     self.ui.contextMenu = QMenu()
    #     self.ui.action_copy = self.ui.contextMenu.addAction(u'复制')
    #     self.ui.action_paste = self.ui.contextMenu.addAction(u'粘贴')
    #     self.ui.contextMenu.popup(QCursor.pos())  # 菜单显示的位置
    #     self.ui.action_copy.triggered.connect(lambda: self.contextmenu_copy(btn_num))
    #     self.ui.action_paste.triggered.connect(lambda: self.contextmenu_paste(btn_num))
    #     self.ui.contextMenu.show()
    #
    # def contextmenu_copy(self, btn_num):
    #     print('copy', btn_num)
    #
    # def contextmenu_paste(self, btn_num):
    #     print('paste', btn_num)

    # ------------------------------------raw功能按钮-------------------------------------------

    def raw_send_button_func(self):
        vendor_id = int((self.ui.vendor_id.text()), 16)
        usage_page = int((self.ui.vendor_page.text()), 16)

        print(self.ui.raw_data.toPlainText())
        re_list = re.findall(r'(\w+)', self.ui.raw_data.toPlainText())
        print(re_list)
        try:
            for i in range(0, len(re_list)):
                re_list[i] = int(re_list[i], 16)
            print(re_list)
            buffer = re_list.copy()
            info = read_report(vendor_id, usage_page, buffer)

            if info == 1:
                self.ui.statusBar().showMessage("未找到设备，请重试")
                self.device_init(1)
            elif info == 2:
                self.ui.statusBar().showMessage("已发送，无回复")
            else:
                self.ui.statusBar().showMessage("发送完成")
                Str_info = " ".join('0x%02x' % i for i in info)
                print("> " + Str_info)
                self.ui.raw_reply.append("\n" + time.strftime("%H:%M:%S",
                                                              time.localtime()) + "> \n" + Str_info.upper())
        except:
            print("发送数据1失败")
            self.ui.statusBar().showMessage("发送数据1失败，请检查数据")

    def raw_send_button_2_func(self):
        vendor_id = int((self.ui.vendor_id.text()), 16)
        usage_page = int((self.ui.vendor_page.text()), 16)

        print(self.ui.raw_data_2.toPlainText())
        re_list = re.findall(r'(\w+)', self.ui.raw_data_2.toPlainText())
        print(re_list)
        try:
            for i in range(0, len(re_list)):
                re_list[i] = int(re_list[i], 16)
            print(re_list)
            buffer = re_list.copy()
            info = read_report(vendor_id, usage_page, buffer)

            if info == 1:
                self.ui.statusBar().showMessage("未找到设备，请重试")
                self.device_init(1)
            elif info == 2:
                self.ui.statusBar().showMessage("已发送，无回复")
            else:
                self.ui.statusBar().showMessage("发送完成")
                Str_info = " ".join('0x%02x' % i for i in info)
                print("> " + Str_info)
                self.ui.raw_reply.append("\n" + time.strftime("%H:%M:%S",
                                                              time.localtime()) + "> \n" + Str_info.upper())
        except:
            print("发送数据2失败")
            self.ui.statusBar().showMessage("发送数据2失败，请检查数据")

    def tab_change(self, index):
        ui_geometry = self.ui.geometry()
        tabWidget_geometry = self.ui.tabWidget.geometry()
        print("click tab" + "  " + str(index + 1))
        # print(ui_geometry, "\n", tabWidget_geometry)

        # 切换标签卡时重载灯光
        if index + 1 != 2 and self.key_light != 7:
            self.reload()
            self.key_light = 7

        # 动画更改about页窗口大小
        if index + 1 == 6:
            # self.ui.about_group.setVisible(False)
            self.ui.setMinimumSize(ui_geometry.width(), 226)  # 解锁窗口大小
            self.ui.statusBar().setVisible(False)

            self.ui.animation = QPropertyAnimation(self.ui.tabWidget, b'geometry')
            self.ui.animation.setDuration(10)
            self.ui.animation.setStartValue(tabWidget_geometry)
            self.ui.animation.setEndValue(
                QRect(tabWidget_geometry.x(), tabWidget_geometry.y(), tabWidget_geometry.width(), 204))
            self.animation_group.addAnimation(self.ui.animation)

            self.ui.animation = QPropertyAnimation(self.ui, b'geometry')
            self.ui.animation.setDuration(100)
            self.ui.animation.setStartValue(ui_geometry)
            self.ui.animation.setEndValue(QRect(ui_geometry.x(), ui_geometry.y(), ui_geometry.width(), 210))
            self.animation_group.addAnimation(self.ui.animation)

            self.animation_group.start()

        # 动画更改按键页窗口大小
        if index + 1 == 2:
            self.ui.setMinimumSize(ui_geometry.width(), 540)  # 解锁窗口大小
            self.ui.statusBar().setVisible(True)

            self.ui.animation = QPropertyAnimation(self.ui.tabWidget, b'geometry')
            self.ui.animation.setDuration(100)
            self.ui.animation.setStartValue(tabWidget_geometry)
            self.ui.animation.setEndValue(
                QRect(tabWidget_geometry.x(), tabWidget_geometry.y(), tabWidget_geometry.width(), 507))
            self.animation_group.addAnimation(self.ui.animation)

            self.ui.animation = QPropertyAnimation(self.ui, b'geometry')
            self.ui.animation.setDuration(100)
            self.ui.animation.setStartValue(ui_geometry)
            self.ui.animation.setEndValue(QRect(ui_geometry.x(), ui_geometry.y(), ui_geometry.width(), 540))
            self.animation_group.addAnimation(self.ui.animation)

            self.animation_group.start()
        # 动画更改RGB页窗口大小
        if index + 1 == 3:
            self.ui.setMinimumSize(ui_geometry.width(), 460)  # 解锁窗口大小
            self.ui.statusBar().setVisible(True)

            self.ui.animation = QPropertyAnimation(self.ui.tabWidget, b'geometry')
            self.ui.animation.setDuration(100)
            self.ui.animation.setStartValue(tabWidget_geometry)
            self.ui.animation.setEndValue(
                QRect(tabWidget_geometry.x(), tabWidget_geometry.y(), tabWidget_geometry.width(), 427))
            self.animation_group.addAnimation(self.ui.animation)

            self.ui.animation = QPropertyAnimation(self.ui, b'geometry')
            self.ui.animation.setDuration(100)
            self.ui.animation.setStartValue(ui_geometry)
            self.ui.animation.setEndValue(QRect(ui_geometry.x(), ui_geometry.y(), ui_geometry.width(), 460))
            self.animation_group.addAnimation(self.ui.animation)

            self.animation_group.start()
        # 动画更改灯效页窗口大小
        if index + 1 == 4:
            self.ui.setMinimumSize(ui_geometry.width(), 260)  # 解锁窗口大小
            self.ui.statusBar().setVisible(True)

            self.ui.animation = QPropertyAnimation(self.ui.tabWidget, b'geometry')
            self.ui.animation.setDuration(100)
            self.ui.animation.setStartValue(tabWidget_geometry)
            self.ui.animation.setEndValue(
                QRect(tabWidget_geometry.x(), tabWidget_geometry.y(), tabWidget_geometry.width(), 267))
            self.animation_group.addAnimation(self.ui.animation)

            self.ui.animation = QPropertyAnimation(self.ui, b'geometry')
            self.ui.animation.setDuration(100)
            self.ui.animation.setStartValue(ui_geometry)
            self.ui.animation.setEndValue(QRect(ui_geometry.x(), ui_geometry.y(), ui_geometry.width(), 300))
            self.animation_group.addAnimation(self.ui.animation)

            self.animation_group.start()

        # 恢复窗口大小(RAW和设备页)
        if index + 1 == 1 or index + 1 == 5:
            self.ui.setMaximumSize(ui_geometry.width(), 640)  # 解锁窗口大小
            self.ui.statusBar().setVisible(True)

            self.ui.animation = QPropertyAnimation(self.ui.tabWidget, b'geometry')
            self.ui.animation.setDuration(10)
            self.ui.animation.setStartValue(tabWidget_geometry)
            self.ui.animation.setEndValue(
                QRect(tabWidget_geometry.x(), tabWidget_geometry.y(), tabWidget_geometry.width(), 606))
            self.animation_group.addAnimation(self.ui.animation)

            self.ui.animation = QPropertyAnimation(self.ui, b'geometry')
            self.ui.animation.setDuration(90)
            self.ui.animation.setStartValue(ui_geometry)
            self.ui.animation.setEndValue(QRect(ui_geometry.x(), ui_geometry.y(), ui_geometry.width(), 640))
            self.animation_group.addAnimation(self.ui.animation)

            self.animation_group.start()

            # 如果键位被修改则修改预设模式为自定义
            if self.key_flag[0] != 0 or self.key_flag[0] != 0 or self.key_flag[0] != 0:
                self.ui.keyboard_mode_1.setChecked(True)

    def lock_window_size(self):  # 锁定窗口大小
        # print("lock window size")
        ui_geometry = self.ui.geometry()
        self.ui.setMinimumSize(ui_geometry.width(), ui_geometry.height())
        self.ui.setMaximumSize(ui_geometry.width(), ui_geometry.height())
        self.animation_group.clear()
        # self.ui.about_group.setVisible(True)

    def raw_help_button_func(self):
        # 使用QWebEngineView
        # self.helper.webView = QWebEngineView(self.helper.tab_2)
        # self.helper.webView.setGeometry(0, 0, 572, 750)
        # url = QUrl.fromLocalFile('/Help/Help.html')
        # self.helper.webView.load(url)
        # self.helper.webView = QWebEngineView(self.helper.tab_3)
        # self.helper.webView.setGeometry(0, 0, 572, 750)
        # url = 'https://hczhcz.github.io/2048/20ez/'
        # self.helper.webView.load(url)
        # self.helper.show()

        # 使用外部浏览器
        QDesktopServices.openUrl(QUrl('https://github.com/Jackadminx/Keyboard_nano_client/blob/main/Help/report.md'))

    # ------------------------------------按键功能按钮-------------------------------------------

    # ----------------------------LED点亮控制----------------------------
    def k1_button_func(self):  #
        vendor_id = int((self.ui.vendor_id.text()), 16)
        usage_page = int((self.ui.vendor_page.text()), 16)
        page_id = int(self.ui.usage_id.text())

        buffer = [0] * (4 + 9)
        # 更换全部rgb灯光 不写入flash
        buffer[0] = page_id  # report_id
        buffer[1] = 5  # 命令模式
        buffer[2] = 1  # 更改rgb
        buffer[3] = 0  # 保留
        # buffer[4] = 0x1a  # 1-B
        # buffer[5] = 0x1a  # 1-R
        # buffer[6] = 0x1a  # 1-G
        if (self.key_light & 1):
            self.key_light -= 1
            buffer[4] = 0x1a  # 1-B
            buffer[5] = 0x1a  # 1-R
            buffer[6] = 0x1a  # 1-G
        else:
            self.key_light += 1
            buffer[4] = 0xff  # 1-B
            buffer[5] = 0xff  # 1-R
            buffer[6] = 0xff  # 1-G
        buffer[7] = 0  # 2-B
        buffer[8] = 0  # 2-R
        buffer[9] = 0  # 2-G
        buffer[10] = 0  # 3-B
        buffer[11] = 0  # 3-R
        buffer[12] = 0  # 3-G
        out_data(vendor_id, usage_page, buffer)

    def k2_button_func(self):
        vendor_id = int((self.ui.vendor_id.text()), 16)
        usage_page = int((self.ui.vendor_page.text()), 16)
        page_id = int(self.ui.usage_id.text())

        buffer = [0] * (4 + 9)
        # 更换全部rgb灯光 不写入flash
        buffer[0] = page_id  # report_id
        buffer[1] = 5  # 命令模式
        buffer[2] = 1  # 更改rgb
        buffer[3] = 0  # 保留
        buffer[4] = 0  # 1-B
        buffer[5] = 0  # 1-R
        buffer[6] = 0  # 1-G
        # buffer[7] = 0x1a  # 1-B
        # buffer[8] = 0x1a  # 1-R
        # buffer[9] = 0x1a  # 1-G
        if (self.key_light & 2):
            self.key_light -= 2
            buffer[7] = 0x1a  # 1-B
            buffer[8] = 0x1a  # 1-R
            buffer[9] = 0x1a  # 1-G
        else:
            self.key_light += 2
            buffer[7] = 0xff  # 1-B
            buffer[8] = 0xff  # 1-R
            buffer[9] = 0xff  # 1-G
        buffer[10] = 0  # 3-B
        buffer[11] = 0  # 3-R
        buffer[12] = 0  # 3-G
        out_data(vendor_id, usage_page, buffer)

    def k3_button_func(self):
        vendor_id = int((self.ui.vendor_id.text()), 16)
        usage_page = int((self.ui.vendor_page.text()), 16)
        page_id = int(self.ui.usage_id.text())

        buffer = [0] * (4 + 9)
        # 更换全部rgb灯光 不写入flash
        buffer[0] = page_id  # report_id
        buffer[1] = 5  # 命令模式
        buffer[2] = 1  # 更改rgb
        buffer[3] = 0  # 保留
        buffer[4] = 0  # 1-B
        buffer[5] = 0  # 1-R
        buffer[6] = 0  # 1-G
        buffer[7] = 0  # 2-B
        buffer[8] = 0  # 2-R
        buffer[9] = 0  # 2-G
        # buffer[10] = 0x1a  # 1-B
        # buffer[11] = 0x1a  # 1-R
        # buffer[12] = 0x1a  # 1-G
        if (self.key_light & 4):
            self.key_light -= 4
            buffer[10] = 0x1a  # 1-B
            buffer[11] = 0x1a  # 1-R
            buffer[12] = 0x1a  # 1-G
        else:
            self.key_light += 4
            buffer[10] = 0xff  # 1-B
            buffer[11] = 0xff  # 1-R
            buffer[12] = 0xff  # 1-G
        out_data(vendor_id, usage_page, buffer)

    # ----------------------------标准键盘键位输入----------------------------
    def k1_keySequenceEdit_func(self):
        if self.ui.k1_keySequenceEdit.keySequence().count() == 0:
            return
        elif self.ui.k1_keySequenceEdit.keySequence().count() != 1:
            print("暂不支持多个快捷键，保留第一位键位")
            self.ui.statusBar().showMessage("暂不支持多个快捷键，保留第一个快捷键")
            keysequence = self.ui.k1_keySequenceEdit.keySequence().toString().split(",")
            self.ui.k1_keySequenceEdit.setKeySequence(keysequence[0])
        else:
            keysequence = self.ui.k1_keySequenceEdit.keySequence().toString()
        self.key_flag[0] = 1

    def k2_keySequenceEdit_func(self):
        if self.ui.k2_keySequenceEdit.keySequence().count() == 0:
            return
        elif self.ui.k2_keySequenceEdit.keySequence().count() != 1:
            print("暂不支持多个快捷键，保留第一位键位")
            self.ui.statusBar().showMessage("暂不支持多个快捷键，保留第一个快捷键")
            keysequence = self.ui.k2_keySequenceEdit.keySequence().toString().split(",")
            self.ui.k2_keySequenceEdit.setKeySequence(keysequence[0])
        else:
            keysequence = self.ui.k2_keySequenceEdit.keySequence().toString()
        self.key_flag[1] = 1

    def k3_keySequenceEdit_func(self):
        if self.ui.k3_keySequenceEdit.keySequence().count() == 0:
            return
        elif self.ui.k3_keySequenceEdit.keySequence().count() != 1:
            print("暂不支持多个快捷键，保留第一位键位")
            self.ui.statusBar().showMessage("暂不支持多个快捷键，保留第一个快捷键")
            keysequence = self.ui.k3_keySequenceEdit.keySequence().toString().split(",")
            self.ui.k3_keySequenceEdit.setKeySequence(keysequence[0])
        else:
            keysequence = self.ui.k3_keySequenceEdit.keySequence().toString()
        self.key_flag[2] = 1

    # ----------------------------第二下拉菜单改变标志位----------------------------
    def key_comboBox_second_changed(self, comb_num):
        if comb_num == 0:
            if self.ui.k1_comboBox_second.count() != 1 or self.ui.k1_comboBox_second.count() != 0:
                self.key_flag[comb_num] = 1
        elif comb_num == 1:
            if self.ui.k2_comboBox_second.count() != 1 or self.ui.k2_comboBox_second.count() != 0:
                self.key_flag[comb_num] = 1
        elif comb_num == 2:
            if self.ui.k3_comboBox_second.count() != 1 or self.ui.k3_comboBox_second.count() != 0:
                self.key_flag[comb_num] = 1
        # print(self.key_flag)

    # ----------------------------HID读取----------------------------
    def key_r_button_func(self):
        vendor_id = int((self.ui.vendor_id.text()), 16)
        usage_page = int((self.ui.vendor_page.text()), 16)
        page_id = int(self.ui.usage_id.text())

        buffer = [0] * 5
        buffer[0] = page_id  # report_id
        buffer[1] = 0  # 读取/写入/复位/测试 0=r 1=w 2=reset 3=test
        buffer[2] = 0xff  # 单元ID 0=功能 1=led 2=按键1 3=按键2 4=按键3 0xff=全部
        info = read_report(vendor_id, usage_page, buffer)
        if info == 1:
            self.device_init(1)
            self.ui.statusBar().showMessage("未找到设备，请重试")
        elif info == 2:
            self.ui.statusBar().showMessage("读取失败")
        else:
            self.ui.statusBar().showMessage("读取完成")
            # self.key_data_FLASH = info.copy()
            # self.key_data = info.copy()
            self.key_flag = [0, 0, 0]

            if info[4] == 1:
                add_2 = 4 + 3 + 10
            elif info[4] == 2:
                add_2 = 4 + 3 + 8
            elif info[4] == 3:
                add_2 = 4 + 3 + 12
            elif info[4] == 4:
                add_2 = 4 + 3 + 18
            elif info[4] == 5:
                add_2 = 4 + 3 + 12
            else:
                add_2 = 4 + 3 + 10

            if info[5] == 1:
                add_3 = add_2 + 10
            elif info[5] == 2:
                add_3 = add_2 + 8
            elif info[5] == 3:
                add_3 = add_2 + 12
            elif info[5] == 4:
                add_3 = add_2 + 18
            elif info[5] == 5:
                add_3 = add_2 + 12
            else:
                add_3 = add_2 + 10

            if info[4] == 1:
                self.ui.k1_comboBox.setCurrentIndex(0)
                self.ui.k1_keySequenceEdit.setEnabled(True)
                self.ui.k1_keySequenceEdit.setVisible(True)
                keysequence = ""
                if (info[10] & 8) != 0:
                    keysequence = "Meta"
                if (info[10] & 1) != 0:
                    if keysequence == "":
                        pass
                    else:
                        keysequence += "+"
                    keysequence += "Ctrl"
                if (info[10] & 4) != 0:
                    if keysequence == "":
                        pass
                    else:
                        keysequence += "+"
                    keysequence += "Alt"
                if (info[10] & 2) != 0:
                    if keysequence == "":
                        pass
                    else:
                        keysequence += "+"
                    keysequence += "Shift"
                if info[12] != 0:
                    if keysequence == "":
                        pass
                    else:
                        keysequence += "+"
                    keysequence += self.keyboard_map["hid_keyboard"][("0X%02x" % info[12]).upper()]
                # print(keysequence)
                self.ui.k1_keySequenceEdit.setKeySequence(keysequence)
            elif info[4] == 2:
                self.ui.k1_comboBox.setCurrentIndex(1)
                self.ui.k1_comboBox_second.setEnabled(True)
                self.ui.k1_comboBox_second.setVisible(True)
                media_mapcode = "0x" + ("%04x" % (int(info[11] * 255) + info[10])).upper()
                i = 0
                for key in self.mian_data["media_key_list"]:
                    if media_mapcode == self.mian_data["media_key_list"][key]:
                        break
                    i = i + 1
                self.ui.k1_comboBox_second.setCurrentIndex(i)
            elif info[4] == 3:
                self.ui.k1_comboBox.setCurrentIndex(2)
                self.ui.expand_button.setEnabled(True)
                self.ui.expand_button.setVisible(True)
                self.mouse_dialog_data[0]["mouse_btn"] = info[10]
                unsigned_mouse_x = info[11]
                unsigned_mouse_y = info[12]
                unsigned_mouse_scroll = info[13]
                signed_mouse_x = unsigned_mouse_x - 256 if unsigned_mouse_x > 127 else unsigned_mouse_x
                signed_mouse_y = unsigned_mouse_y - 256 if unsigned_mouse_y > 127 else unsigned_mouse_y
                signed_mouse_scroll = unsigned_mouse_scroll - 256 if unsigned_mouse_scroll > 127 else unsigned_mouse_scroll
                self.mouse_dialog_data[0]["mouse_x"] = signed_mouse_x
                self.mouse_dialog_data[0]["mouse_y"] = signed_mouse_y
                self.mouse_dialog_data[0]["mouse_scroll"] = signed_mouse_scroll
            elif info[4] == 4:
                self.ui.k1_comboBox.setCurrentIndex(3)
                flag = info[16]
                print(flag)
                # i = 0
                # for key in self.mian_data["touch_key_list"]:
                #     if flag == self.mian_data["touch_key_list"][key]:
                #         break
                #     i = i + 1
                # self.ui.k1_comboBox_second.setCurrentIndex(i)
                self.ui.k1_comboBox_second.setCurrentIndex(flag)
                if flag == 4:
                    # buffer[6] = 5  # report-id
                    # buffer[7] = 6  # 功能位 多边形边数 n
                    # buffer[8] = 40  # 功能位 边到中心点距离 r
                    # buffer[9] = 0  # x坐标的高八位(保留)
                    # buffer[10] = 0  # y坐标的低八位(保留)
                    # buffer[11] = 0  # y坐标的高八位(保留)
                    # buffer[12] = 10  # 单圈完成时间 单位10ms
                    self.touch_dialog_data[0]["osu_n"] = info[10]
                    self.touch_dialog_data[0]["osu_r"] = info[11]
                    self.touch_dialog_data[0]["osu_finish_ms"] = info[15]
                elif flag == 5:
                    mouse_x = info[11] + info[12] * 0xff
                    mouse_y = info[13] + info[14] * 0xff
                    self.touch_dialog_data[0]["mouse_X"] = mouse_x
                    self.touch_dialog_data[0]["mouse_Y"] = mouse_y
                    self.touch_dialog_data[0]["mouse_ms"] = info[15] * 10
                else:
                    self.touch_dialog_data[0]["slide_ms"] = info[15] * 10
                    px = self.touch_dialog_data[0]["slide_px"]
                    if info[16] == 0:
                        px = (info[11] + info[12] * 0xff) - (info[19] + info[20] * 0xff)
                    elif info[16] == 1:
                        px = (info[19] + info[20] * 0xff) - (info[11] + info[12] * 0xff)
                    elif info[16] == 2:
                        px = (info[21] + info[22] * 0xff) - (info[13] + info[14] * 0xff)
                    elif info[16] == 3:
                        px = (info[13] + info[14] * 0xff) - (info[21] + info[22] * 0xff)
                    # print(px)
                    self.touch_dialog_data[0]["slide_px"] = px
            elif info[4] == 5:
                self.ui.k1_comboBox.setCurrentIndex(4)
                self.ui.k1_comboBox_second.setEnabled(True)
                self.ui.k1_comboBox_second.setVisible(True)
                media_mapcode = "0x" + "%02x" % int(info[10])
                if media_mapcode == "0x01":
                    self.ui.k1_comboBox_second.setCurrentIndex(0)
                elif media_mapcode == "0xc4":
                    self.ui.k1_comboBox_second.setCurrentIndex(1)
                elif media_mapcode == "0x3c":
                    self.ui.k1_comboBox_second.setCurrentIndex(2)
                self.dial_dialog_data[0]["scroll"] = info[12] / 10
                if info[12] % 10 == 1:
                    self.dial_dialog_data[0]["scroll_enable"] = True
                else:
                    self.dial_dialog_data[0]["scroll_enable"] = False
                self.dial_dialog_data[0]["delay"] = info[13]

            if info[5] == 1:
                add_2 = add_2 + 3
                self.ui.k2_comboBox.setCurrentIndex(0)
                self.ui.k2_keySequenceEdit.setEnabled(True)
                self.ui.k2_keySequenceEdit.setVisible(True)
                keysequence = ""
                if (info[add_2] & 8) != 0:
                    keysequence = "Meta"
                if (info[add_2] & 1) != 0:
                    if keysequence == "":
                        pass
                    else:
                        keysequence += "+"
                    keysequence += "Ctrl"
                if (info[add_2] & 4) != 0:
                    if keysequence == "":
                        pass
                    else:
                        keysequence += "+"
                    keysequence += "Alt"
                if (info[add_2] & 2) != 0:
                    if keysequence == "":
                        pass
                    else:
                        keysequence += "+"
                    keysequence += "Shift"
                if info[add_2 + 2] != 0:
                    if keysequence == "":
                        pass
                    else:
                        keysequence += "+"
                    keysequence += self.keyboard_map["hid_keyboard"][("0X%02x" % info[add_2 + 2]).upper()]
                # print(keysequence)
                self.ui.k2_keySequenceEdit.setKeySequence(keysequence)
            elif info[5] == 2:
                add_2 = add_2 + 3
                self.ui.k2_comboBox.setCurrentIndex(1)
                self.ui.k2_comboBox_second.setEnabled(True)
                self.ui.k2_comboBox_second.setVisible(True)
                media_mapcode = "0x" + ("%04x" % (int(info[add_2 + 1] * 255) + info[add_2])).upper()
                i = 0
                for key in self.mian_data["media_key_list"]:
                    if media_mapcode == self.mian_data["media_key_list"][key]:
                        break
                    i = i + 1
                self.ui.k2_comboBox_second.setCurrentIndex(i)
            elif info[5] == 3:
                self.ui.k2_comboBox.setCurrentIndex(2)
                self.ui.expand_button_2.setEnabled(True)
                self.ui.expand_button_2.setVisible(True)
                self.mouse_dialog_data[1]["mouse_btn"] = info[add_2 + 3]
                unsigned_mouse_x = info[add_2 + 4]
                unsigned_mouse_y = info[add_2 + 5]
                unsigned_mouse_scroll = info[add_2 + 6]
                signed_mouse_x = unsigned_mouse_x - 256 if unsigned_mouse_x > 127 else unsigned_mouse_x
                signed_mouse_y = unsigned_mouse_y - 256 if unsigned_mouse_y > 127 else unsigned_mouse_y
                signed_mouse_scroll = unsigned_mouse_scroll - 256 if unsigned_mouse_scroll > 127 else unsigned_mouse_scroll
                self.mouse_dialog_data[1]["mouse_x"] = signed_mouse_x
                self.mouse_dialog_data[1]["mouse_y"] = signed_mouse_y
                self.mouse_dialog_data[1]["mouse_scroll"] = signed_mouse_scroll
            elif info[5] == 4:
                add_2 = add_2 + 9
                self.ui.k2_comboBox.setCurrentIndex(3)
                flag = info[add_2]
                # i = 0
                # for key in self.mian_data["touch_key_list"]:
                #     if flag == self.mian_data["touch_key_list"][key]:
                #         break
                #     i = i + 1
                # self.ui.k2_comboBox_second.setCurrentIndex(i)
                self.ui.k2_comboBox_second.setCurrentIndex(flag)
                if flag == 4:
                    self.touch_dialog_data[1]["osu_n"] = info[add_2 - 6]
                    self.touch_dialog_data[1]["osu_r"] = info[add_2 - 5]
                    self.touch_dialog_data[1]["osu_finish_ms"] = info[add_2 - 1]
                if flag == 5:
                    mouse_x = info[add_2 - 5] + info[add_2 - 4] * 0xff
                    mouse_y = info[add_2 - 3] + info[add_2 - 2] * 0xff
                    self.touch_dialog_data[1]["mouse_X"] = mouse_x
                    self.touch_dialog_data[1]["mouse_Y"] = mouse_y
                    self.touch_dialog_data[1]["mouse_ms"] = info[add_2 - 1] * 10
                else:
                    self.touch_dialog_data[1]["slide_ms"] = info[add_2 - 1] * 10
                    px = self.touch_dialog_data[1]["slide_px"]
                    if info[add_2] == 0:
                        px = (info[add_2 - 5] + info[add_2 - 4] * 0xff) - (info[add_2 + 3] + info[add_2 + 4] * 0xff)
                    elif info[16] == 1:
                        px = (info[add_2 + 3] + info[add_2 + 4] * 0xff) - (info[add_2 - 5] + info[add_2 - 4] * 0xff)
                    elif info[16] == 2:
                        px = (info[add_2 + 5] + info[add_2 + 6] * 0xff) - (info[add_2 - 3] + info[add_2 - 2] * 0xff)
                    elif info[16] == 3:
                        px = (info[add_2 - 3] + info[add_2 - 2] * 0xff) - (info[add_2 + 5] + info[add_2 + 6] * 0xff)
                    # print(px)
                    self.touch_dialog_data[1]["slide_px"] = px
            elif info[5] == 5:
                self.ui.k2_comboBox.setCurrentIndex(4)
                self.ui.k2_comboBox_second.setEnabled(True)
                self.ui.k2_comboBox_second.setVisible(True)
                media_mapcode = "0x" + "%02x" % int(info[add_2 + 3])
                if media_mapcode == "0x01":
                    self.ui.k2_comboBox_second.setCurrentIndex(0)
                elif media_mapcode == "0xc4":
                    self.ui.k2_comboBox_second.setCurrentIndex(1)
                elif media_mapcode == "0x3c":
                    self.ui.k2_comboBox_second.setCurrentIndex(2)
                self.dial_dialog_data[1]["scroll"] = info[add_2 + 5] / 10
                if info[add_2 + 5] % 10 == 1:
                    self.dial_dialog_data[1]["scroll_enable"] = True
                else:
                    self.dial_dialog_data[1]["scroll_enable"] = False
                self.dial_dialog_data[1]["delay"] = info[add_2 + 6]

            if info[6] == 1:
                add_3 = add_3 + 3
                self.ui.k3_comboBox.setCurrentIndex(0)
                self.ui.k3_keySequenceEdit.setEnabled(True)
                self.ui.k3_keySequenceEdit.setVisible(True)
                keysequence = ""
                if (info[add_3] & 8) != 0:
                    keysequence = "Meta"
                if (info[add_3] & 1) != 0:
                    if keysequence == "":
                        pass
                    else:
                        keysequence += "+"
                    keysequence += "Ctrl"
                if (info[add_3] & 4) != 0:
                    if keysequence == "":
                        pass
                    else:
                        keysequence += "+"
                    keysequence += "Alt"
                if (info[add_3] & 2) != 0:
                    if keysequence == "":
                        pass
                    else:
                        keysequence += "+"
                    keysequence += "Shift"
                if info[add_3 + 2] != 0:
                    if keysequence == "":
                        pass
                    else:
                        keysequence += "+"
                    keysequence += self.keyboard_map["hid_keyboard"][("0X%02x" % info[add_3 + 2]).upper()]
                # print(keysequence)
                self.ui.k3_keySequenceEdit.setKeySequence(keysequence)
            elif info[6] == 2:
                add_3 = add_3 + 3
                self.ui.k3_comboBox.setCurrentIndex(1)
                self.ui.k3_comboBox_second.setEnabled(True)
                self.ui.k3_comboBox_second.setVisible(True)
                media_mapcode = "0x" + ("%04x" % (int(info[add_3 + 1] * 255) + info[add_3])).upper()
                i = 0
                for key in self.mian_data["media_key_list"]:
                    if media_mapcode == self.mian_data["media_key_list"][key]:
                        break
                    i = i + 1
                self.ui.k3_comboBox_second.setCurrentIndex(i)
            elif info[6] == 3:
                self.ui.k3_comboBox.setCurrentIndex(2)
                self.ui.expand_button_3.setEnabled(True)
                self.ui.expand_button_3.setVisible(True)
                self.mouse_dialog_data[2]["mouse_btn"] = info[add_3 + 3]
                unsigned_mouse_x = info[add_3 + 4]
                unsigned_mouse_y = info[add_3 + 5]
                unsigned_mouse_scroll = info[add_3 + 6]
                signed_mouse_x = unsigned_mouse_x - 256 if unsigned_mouse_x > 127 else unsigned_mouse_x
                signed_mouse_y = unsigned_mouse_y - 256 if unsigned_mouse_y > 127 else unsigned_mouse_y
                signed_mouse_scroll = unsigned_mouse_scroll - 256 if unsigned_mouse_scroll > 127 else unsigned_mouse_scroll
                self.mouse_dialog_data[2]["mouse_x"] = signed_mouse_x
                self.mouse_dialog_data[2]["mouse_y"] = signed_mouse_y
                self.mouse_dialog_data[2]["mouse_scroll"] = signed_mouse_scroll
            elif info[6] == 4:
                add_3 = add_3 + 9
                self.ui.k3_comboBox.setCurrentIndex(3)
                flag = info[add_3]
                # i = 0
                # for key in self.mian_data["touch_key_list"]:
                #     if flag == self.mian_data["touch_key_list"][key]:
                #         break
                #     i = i + 1
                # self.ui.k3_comboBox_second.setCurrentIndex(i)
                self.ui.k3_comboBox_second.setCurrentIndex(flag)
                if flag == 4:
                    self.touch_dialog_data[2]["osu_n"] = info[add_3 - 6]
                    self.touch_dialog_data[2]["osu_r"] = info[add_3 - 5]
                    self.touch_dialog_data[2]["osu_finish_ms"] = info[add_3 - 1]
                if flag == 5:
                    mouse_x = info[add_3 - 5] + info[add_3 - 4] * 0xff
                    mouse_y = info[add_3 - 3] + info[add_3 - 2] * 0xff
                    self.touch_dialog_data[2]["mouse_X"] = mouse_x
                    self.touch_dialog_data[2]["mouse_Y"] = mouse_y
                    self.touch_dialog_data[2]["mouse_ms"] = info[add_3 - 1] * 10
                else:
                    self.touch_dialog_data[2]["slide_ms"] = info[add_3 - 1] * 10
                    px = self.touch_dialog_data[2]["slide_px"]
                    if info[add_3] == 0:
                        px = (info[add_3 - 5] + info[add_3 - 4] * 0xff) - (info[add_3 + 3] + info[add_3 + 4] * 0xff)
                    elif info[16] == 1:
                        px = (info[add_3 + 3] + info[add_3 + 4] * 0xff) - (info[add_3 - 5] + info[add_3 - 4] * 0xff)
                    elif info[16] == 2:
                        px = (info[add_3 + 5] + info[add_3 + 6] * 0xff) - (info[add_3 - 3] + info[add_3 - 2] * 0xff)
                    elif info[16] == 3:
                        px = (info[add_3 - 3] + info[add_3 - 2] * 0xff) - (info[add_3 + 5] + info[add_3 + 6] * 0xff)
                    # print(px)
                    self.touch_dialog_data[2]["slide_px"] = px
            elif info[6] == 5:
                self.ui.k3_comboBox.setCurrentIndex(4)
                self.ui.k3_comboBox_second.setEnabled(True)
                self.ui.k3_comboBox_second.setVisible(True)
                media_mapcode = "0x" + "%02x" % int(info[add_3 + 3])
                if media_mapcode == "0x01":
                    self.ui.k3_comboBox_second.setCurrentIndex(0)
                elif media_mapcode == "0xc4":
                    self.ui.k3_comboBox_second.setCurrentIndex(1)
                elif media_mapcode == "0x3c":
                    self.ui.k3_comboBox_second.setCurrentIndex(2)
                self.dial_dialog_data[2]["scroll"] = info[add_3 + 5] / 10
                if info[add_3 + 5] % 10 == 1:
                    self.dial_dialog_data[2]["scroll_enable"] = True
                else:
                    self.dial_dialog_data[2]["scroll_enable"] = False
                self.dial_dialog_data[2]["delay"] = info[add_3 + 6]

    # ----------------------------HID写入----------------------------
    def key_w_button_func(self):
        # 进度窗口
        progress = QProgressDialog("Please Wait!", "Cancel", 0, 100, self.ui)
        progress.setWindowModality(Qt.WindowModal)
        progress.setWindowTitle("Flash...")
        progress.setAutoClose(True)
        progress.show()
        time.sleep(0.3)  # 等待窗口显示
        progress.setValue(1)

        vendor_id = int((self.ui.vendor_id.text()), 16)
        usage_page = int((self.ui.vendor_page.text()), 16)
        page_id = int(self.ui.usage_id.text())

        print("change flag: " + str(self.key_flag))

        if self.key_flag[0] == 1:  # 该键被修改
            buffer = [0]
            buffer[0] = page_id
            buffer.append(1)  # 写入
            buffer.append(2)  # 单元ID 0=功能 1=led 2=按键1 3=按键2 4=按键3
            buffer.append(0)  # 保留位
            if self.ui.k1_comboBox.currentIndex() == 0:
                keysequence = self.ui.k1_keySequenceEdit.keySequence().toString()
                for i in range(4, 14):
                    buffer.append(0)
                buffer[4] = 1  # 按键功能 0=停用此键 1=标准按键 2=多媒体键
                buffer[5] = 4  # report所占长度
                # 4字节 按下键盘功能report  Control+X
                buffer[6] = 1  # report-id
                buffer[7] = 0  # Control Shift Alt GUI 键功能
                buffer[8] = 0  # 保留位
                buffer[9] = 0  # 功能位
                # 4字节 按下松开键盘功能
                buffer[10] = 1  # report-id
                buffer[11] = 0  # Control Shift Alt GUI 键功能
                buffer[12] = 0  # 保留位
                buffer[13] = 0  # 功能位
                if self.ui.k1_keySequenceEdit.keySequence().count() == 0:  # 没有输入键位
                    buffer[4] = 1
                    print("未启用该键")
                else:
                    if len(re.findall("\+", keysequence)) == 0:  # 没有匹配到+号，不是组合键
                        mapcode = [key for key, value in self.keyboard_map["hid_keyboard"].items() if
                                   value == keysequence]
                        print(mapcode)
                        buffer[9] = int(mapcode[0], 16)  # 功能位
                    else:  # 组合键
                        keysequence_list = keysequence.split("+").copy()
                        print(keysequence_list)
                        if re.findall(r'Ctrl', keysequence):
                            buffer[7] += 1
                        if re.findall(r'Shift', keysequence):
                            buffer[7] += 2
                        if re.findall(r'Alt', keysequence):
                            buffer[7] += 4
                        if re.findall(r'Meta', keysequence):
                            buffer[7] += 8
                        mapcode = [key for key, value in self.keyboard_map["hid_keyboard"].items() if
                                   value == keysequence_list[-1]]  # 通过值反查key
                        buffer[9] = int(mapcode[0], 16)  # 功能位
            elif self.ui.k1_comboBox.currentIndex() == 1:
                buffer.append(2)  # 按键功能 0=停用此键 1=标准按键 2=多媒体键
                buffer.append(3)  # report所占长度
                # 3字节 按下键盘功能report
                buffer.append(2)  # report-id
                # buffer.append(0)  # 功能位 低位
                # buffer.append(0)  # 功能位 高位
                key_value = self.ui.k1_comboBox_second.currentText()
                buffer.append(int(int(self.mian_data["media_key_list"][key_value], 16) % 255))  # 功能位 低位
                buffer.append(int(int(self.mian_data["media_key_list"][key_value], 16) / 255))  # 功能位 高位
                # 3字节 按下松开键盘功能report
                buffer.append(2)  # report-id
                buffer.append(0)  # 功能位 低位
                buffer.append(0)  # 功能位 高位
                if self.ui.k1_comboBox_second.currentIndex() == 0 or self.ui.k1_comboBox_second.currentIndex() == 1:  # 没有输入键位
                    buffer[4] = 2
                    print("未启用该键")
            elif self.ui.k1_comboBox.currentIndex() == 2:
                buffer.append(3)  # 按键功能 3=鼠标模式
                buffer.append(5)  # report所占长度
                # 5字节 鼠标report
                # buffer[6] = 3  # report-id
                # buffer[7] = 6  # 按键
                # buffer[8] = 40  # X坐标变化量
                # buffer[9] = 0   # Y坐标变化量
                # buffer[10] = 0  # 滚轮变化
                buffer.append(3)  # report-id
                mouse_x = self.mouse_dialog_data[0]["mouse_x"]
                mouse_y = self.mouse_dialog_data[0]["mouse_y"]
                mouse_scroll = self.mouse_dialog_data[0]["mouse_scroll"]
                mouse_btn = self.mouse_dialog_data[0]["mouse_btn"]
                if mouse_btn == 1:
                    buffer.append(1)  # 按键
                elif mouse_btn == 2:
                    buffer.append(2)  # 按键
                elif mouse_btn == 3:
                    buffer.append(4)  # 按键
                else:
                    buffer.append(0)  # 按键
                unsigned_mouse_x = struct.pack("b", mouse_x)[0]
                unsigned_mouse_y = struct.pack("b", mouse_y)[0]
                unsigned_mouse_scroll = struct.pack("b", mouse_scroll)[0]
                buffer.append(unsigned_mouse_x)  # X坐标变化量
                buffer.append(unsigned_mouse_y)  # Y坐标变化量
                buffer.append(unsigned_mouse_scroll)  # 滚轮变化
                buffer.append(3)
                buffer.append(0)  # 松开按键
                buffer.append(0)  # X
                buffer.append(0)  # Y
                buffer.append(0)  # 滚轮
            elif self.ui.k1_comboBox.currentIndex() == 3:
                X = self.ui.resolution_X.value() / 2
                Y = self.ui.resolution_Y.value() / 2
                buffer.append(4)  # 按键功能 0=停用此键 1=标准按键 2=多媒体键 4=触摸
                buffer.append(8)  # report所占长度
                for i in range(6, 8 * 2 + 4 + 2):
                    buffer.append(0)
                slide_ms_v = self.touch_dialog_data[0]["slide_ms"]
                slide_px_v = self.touch_dialog_data[0]["slide_px"]
                osu_finish_ms_v = self.touch_dialog_data[0]["osu_finish_ms"]
                osu_r_v = self.touch_dialog_data[0]["osu_r"]
                osu_n_v = self.touch_dialog_data[0]["osu_n"]
                mouse_X = self.touch_dialog_data[0]["mouse_X"]
                mouse_Y = self.touch_dialog_data[0]["mouse_Y"]
                mouse_ms = self.touch_dialog_data[0]["mouse_ms"]
                if self.ui.k1_comboBox_second.currentIndex() == 0:
                    # buffer[8] = 0   # x坐标的低八位
                    # buffer[9] = 0   # x坐标的高八位
                    # buffer[10] = 0  # y坐标的低八位
                    # buffer[11] = 0  # y坐标的高八位
                    buffer[6] = 5  # report-id
                    buffer[7] = 0x83  # 功能位 0x83=触摸按下 0x82=触摸松开
                    buffer[8] = int((X + slide_px_v / 2) % 255)
                    buffer[9] = int((X + slide_px_v / 2) / 255)
                    buffer[10] = int(Y % 255)
                    buffer[11] = int(Y / 255)
                    buffer[12] = int(slide_ms_v / 10)  # 间隔时间 单位10ms
                    buffer[13] = self.ui.k1_comboBox_second.currentIndex()  # 子功能标记
                    buffer[14] = 5  # report-id
                    buffer[15] = 0x83  # 功能位 0x83=触摸按下 0x82=触摸松开
                    buffer[16] = int((X - slide_px_v / 2) % 255)
                    buffer[17] = int((X - slide_px_v / 2) / 255)
                    buffer[18] = int(Y % 255)
                    buffer[19] = int(Y / 255)
                    buffer[20] = 0  # 间隔时间 单位10ms
                    buffer[21] = self.ui.k1_comboBox_second.currentIndex()  # 子功能标记
                if self.ui.k1_comboBox_second.currentIndex() == 1:
                    buffer[6] = 5  # report-id
                    buffer[7] = 0x83  # 功能位 0x83=触摸按下 0x82=触摸松开
                    buffer[8] = int((X - slide_px_v / 2) % 255)
                    buffer[9] = int((X - slide_px_v / 2) / 255)
                    buffer[10] = int(Y % 255)
                    buffer[11] = int(Y / 255)
                    buffer[12] = int(slide_ms_v / 10)  # 间隔时间 单位10ms
                    buffer[13] = self.ui.k1_comboBox_second.currentIndex()  # 子功能标记
                    buffer[14] = 5  # report-id
                    buffer[15] = 0x83  # 功能位 0x83=触摸按下 0x82=触摸松开
                    buffer[16] = int((X + slide_px_v / 2) % 255)
                    buffer[17] = int((X + slide_px_v / 2) / 255)
                    buffer[18] = int(Y % 255)
                    buffer[19] = int(Y / 255)
                    buffer[20] = 0  # 间隔时间 单位10ms
                    buffer[21] = self.ui.k1_comboBox_second.currentIndex()  # 子功能标记
                if self.ui.k1_comboBox_second.currentIndex() == 2:
                    buffer[6] = 5  # report-id
                    buffer[7] = 0x83  # 功能位 0x83=触摸按下 0x82=触摸松开
                    buffer[8] = int(X % 255)
                    buffer[9] = int(X / 255)
                    buffer[10] = int((Y - slide_px_v / 2) % 255)
                    buffer[11] = int((Y - slide_px_v / 2) / 255)
                    buffer[12] = int(slide_ms_v / 10)  # 间隔时间 单位10ms
                    buffer[13] = self.ui.k1_comboBox_second.currentIndex()  # 子功能标记
                    buffer[14] = 5  # report-id
                    buffer[15] = 0x83  # 功能位 0x83=触摸按下 0x82=触摸松开
                    buffer[16] = int(X % 255)
                    buffer[17] = int(X / 255)
                    buffer[18] = int((Y + slide_px_v / 2) % 255)
                    buffer[19] = int((Y + slide_px_v / 2) / 255)
                    buffer[20] = 0  # 间隔时间 单位10ms
                    buffer[21] = self.ui.k1_comboBox_second.currentIndex()  # 子功能标记
                if self.ui.k1_comboBox_second.currentIndex() == 3:
                    buffer[6] = 5  # report-id
                    buffer[7] = 0x83  # 功能位 0x83=触摸按下 0x82=触摸松开
                    buffer[8] = int(X % 255)
                    buffer[9] = int(X / 255)
                    buffer[10] = int((Y + slide_px_v / 2) % 255)
                    buffer[11] = int((Y + slide_px_v / 2) / 255)
                    buffer[12] = int(slide_ms_v / 10)  # 间隔时间 单位10ms
                    buffer[13] = self.ui.k1_comboBox_second.currentIndex()  # 子功能标记
                    buffer[14] = 5  # report-id
                    buffer[15] = 0x83  # 功能位 0x83=触摸按下 0x82=触摸松开
                    buffer[16] = int(X % 255)
                    buffer[17] = int(X / 255)
                    buffer[18] = int((Y - slide_px_v / 2) % 255)
                    buffer[19] = int((Y - slide_px_v / 2) / 255)
                    buffer[20] = 0  # 间隔时间 单位10ms
                    buffer[21] = self.ui.k1_comboBox_second.currentIndex()  # 子功能标记
                if self.ui.k1_comboBox_second.currentIndex() == 4:
                    buffer[6] = 5  # report-id
                    # buffer[7] = 6  # 功能位 多边形边数
                    # buffer[8] = 40  # 功能位 边到中心点距离
                    buffer[7] = osu_n_v
                    buffer[8] = osu_r_v
                    buffer[12] = osu_finish_ms_v  # 单圈时间 单位1ms
                    buffer[13] = self.ui.k1_comboBox_second.currentIndex()  # 子功能标记
                    buffer[14] = 5  # report-id
                    # buffer[15] = 0x83  # 功能位 0x83=触摸按下 0x82=触摸松开
                    # buffer[16] = int(X % 255)
                    # buffer[17] = int(X / 255)
                    # buffer[18] = int((Y - slide_px_v / 2) % 255)
                    # buffer[19] = int((Y - slide_px_v / 2) / 255)
                    # buffer[20] = 0  # 间隔时间 单位10ms
                    # buffer[21] = 0  # 子功能标记
                if self.ui.k1_comboBox_second.currentIndex() == 5:
                    buffer[6] = 5  # report-id
                    buffer[7] = 0x83  # 功能位 0x83=触摸按下 0x82=触摸松开
                    buffer[8] = int(mouse_X % 255)
                    buffer[9] = int(mouse_X / 255)
                    buffer[10] = int(mouse_Y % 255)
                    buffer[11] = int(mouse_Y / 255)
                    buffer[12] = int(mouse_ms / 10)  # 间隔时间 单位10ms
                    buffer[13] = self.ui.k1_comboBox_second.currentIndex()  # 子功能标记
                    buffer[14] = 5  # report-id
                    buffer[15] = 0x82  # 功能位 0x83=触摸按下 0x82=触摸松开
                    buffer[16] = int(mouse_X % 255)
                    buffer[17] = int(mouse_X / 255)
                    buffer[18] = int(mouse_Y % 255)
                    buffer[19] = int(mouse_Y / 255)
                    buffer[20] = 0  # 间隔时间 单位10ms
                    buffer[21] = self.ui.k1_comboBox_second.currentIndex()  # 子功能标记
            elif self.ui.k1_comboBox.currentIndex() == 4:
                buffer.append(5)  # 按键功能 0=停用此键 1=标准按键 2=多媒体键
                buffer.append(5)  # report所占长度
                # 5字节 按下键盘功能report
                buffer.append(6)  # report-id
                key_value = self.ui.k1_comboBox_second.currentIndex()
                if key_value == 0:
                    buffer.append(int('0x01', 16))  # 功能位 低位 按下
                    buffer.append(int('0x00', 16))  # 功能位 高位
                elif key_value == 1:
                    buffer.append(int('0xC4', 16))  # 功能位 低位 右转
                    buffer.append(int('0xFF', 16))  # 功能位 高位
                elif key_value == 2:
                    buffer.append(int('0x3C', 16))  # 功能位 低位 左转
                    buffer.append(int('0x00', 16))  # 功能位 高位
                else:
                    buffer.append(0)  # 功能位 低位 留空/停用
                    buffer.append(0)  # 功能位 高位

                delay = self.dial_dialog_data[0]["delay"]
                scroll_p = self.dial_dialog_data[0]["scroll"] * 10
                if self.dial_dialog_data[0]["scroll_enable"]:
                    scroll_p = int(scroll_p) + 1
                buffer.append(int(scroll_p))  # 滚动格数/长按 250 -> 25滚动格数/0启用或关闭长按
                buffer.append(delay)  # 滚动间隔 单位1ms
                # 5字节 按下松开键盘功能report
                buffer.append(6)  # report-id
                buffer.append(0)  # 功能位 低位
                buffer.append(0)  # 功能位 高位
                buffer.append(0)  # 滚动格数/长按 可选
                buffer.append(0)  # 滚动间隔 可选
            info = out_data(vendor_id, usage_page, buffer)
            time.sleep(0.6)
            progress.setValue(20)
            print(info)

        if self.key_flag[1] == 1:
            buffer = [0]
            buffer[0] = page_id
            buffer.append(1)  # 写入
            buffer.append(3)  # 单元ID 0=功能 1=led 2=按键1 3=按键2 4=按键3
            buffer.append(0)  # 保留位
            if self.ui.k2_comboBox.currentIndex() == 0:
                keysequence = self.ui.k2_keySequenceEdit.keySequence().toString()
                for i in range(4, 14):
                    buffer.append(0)
                buffer[4] = 1  # 按键功能 0=停用此键 1=标准按键 2=多媒体键
                buffer[5] = 4  # report所占长度
                # 4字节 按下键盘功能report  Control+X
                buffer[6] = 1  # report-id
                buffer[7] = 0  # Control Shift Alt GUI 键功能
                buffer[8] = 0  # 保留位
                buffer[9] = 0  # 功能位
                # 4字节 按下松开键盘功能
                buffer[10] = 1  # report-id
                buffer[11] = 0  # Control Shift Alt GUI 键功能
                buffer[12] = 0  # 保留位
                buffer[13] = 0  # 功能位
                if self.ui.k2_keySequenceEdit.keySequence().count() == 0:  # 没有输入键位
                    buffer[4] = 1
                    print("未启用该键")
                else:
                    if len(re.findall("\+", keysequence)) == 0:  # 没有匹配到+号，不是组合键
                        mapcode = [key for key, value in self.keyboard_map["hid_keyboard"].items() if
                                   value == keysequence]
                        print(mapcode)
                        buffer[9] = int(mapcode[0], 16)  # 功能位
                    else:  # 组合键
                        keysequence_list = keysequence.split("+").copy()
                        print(keysequence_list)
                        if re.findall(r'Ctrl', keysequence):
                            buffer[7] += 1
                        if re.findall(r'Shift', keysequence):
                            buffer[7] += 2
                        if re.findall(r'Alt', keysequence):
                            buffer[7] += 4
                        if re.findall(r'Meta', keysequence):
                            buffer[7] += 8
                        mapcode = [key for key, value in self.keyboard_map["hid_keyboard"].items() if
                                   value == keysequence_list[-1]]  # 通过值反查key
                        buffer[9] = int(mapcode[0], 16)  # 功能位
            elif self.ui.k2_comboBox.currentIndex() == 1:
                buffer.append(2)  # 按键功能 0=停用此键 1=标准按键 2=多媒体键
                buffer.append(3)  # report所占长度
                # 3字节 按下键盘功能report
                buffer.append(2)  # report-id
                # buffer.append(0)  # 功能位 低位
                # buffer.append(0)  # 功能位 高位
                key_value = self.ui.k2_comboBox_second.currentText()
                buffer.append(int(int(self.mian_data["media_key_list"][key_value], 16) % 255))  # 功能位 低位
                buffer.append(int(int(self.mian_data["media_key_list"][key_value], 16) / 255))  # 功能位 高位
                # 3字节 按下松开键盘功能report
                buffer.append(2)  # report-id
                buffer.append(0)  # 功能位 低位
                buffer.append(0)  # 功能位 高位
                if self.ui.k2_comboBox_second.currentIndex() == 0 or self.ui.k2_comboBox_second.currentIndex() == 1:  # 没有输入键位
                    buffer[4] = 2
                    print("未启用该键")
            elif self.ui.k2_comboBox.currentIndex() == 2:
                buffer.append(3)  # 按键功能 3=鼠标模式
                buffer.append(5)  # report所占长度
                # 5字节 鼠标report
                # buffer[6] = 3  # report-id
                # buffer[7] = 6  # 按键
                # buffer[8] = 40  # X坐标变化量
                # buffer[9] = 0   # Y坐标变化量
                # buffer[10] = 0  # 滚轮变化
                buffer.append(3)  # report-id
                mouse_x = self.mouse_dialog_data[1]["mouse_x"]
                mouse_y = self.mouse_dialog_data[1]["mouse_y"]
                mouse_scroll = self.mouse_dialog_data[1]["mouse_scroll"]
                mouse_btn = self.mouse_dialog_data[1]["mouse_btn"]
                if mouse_btn == 1:
                    buffer.append(1)  # 按键
                elif mouse_btn == 2:
                    buffer.append(2)  # 按键
                elif mouse_btn == 3:
                    buffer.append(4)  # 按键
                else:
                    buffer.append(0)  # 按键
                unsigned_mouse_x = struct.pack("b", mouse_x)[0]
                unsigned_mouse_y = struct.pack("b", mouse_y)[0]
                unsigned_mouse_scroll = struct.pack("b", mouse_scroll)[0]
                buffer.append(unsigned_mouse_x)  # X坐标变化量
                buffer.append(unsigned_mouse_y)  # Y坐标变化量
                buffer.append(unsigned_mouse_scroll)  # 滚轮变化
                buffer.append(3)
                buffer.append(0)  # 松开按键
                buffer.append(0)  # X
                buffer.append(0)  # Y
                buffer.append(0)  # 滚轮
            elif self.ui.k2_comboBox.currentIndex() == 3:
                X = self.ui.resolution_X.value() / 2
                Y = self.ui.resolution_Y.value() / 2
                buffer.append(4)  # 按键功能 0=停用此键 1=标准按键 2=多媒体键 4=触摸
                buffer.append(8)  # report所占长度
                for i in range(6, 8 * 2 + 4 + 2):
                    buffer.append(0)
                slide_ms_v = self.touch_dialog_data[1]["slide_ms"]
                slide_px_v = self.touch_dialog_data[1]["slide_px"]
                osu_finish_ms_v = self.touch_dialog_data[1]["osu_finish_ms"]
                osu_r_v = self.touch_dialog_data[1]["osu_r"]
                osu_n_v = self.touch_dialog_data[1]["osu_n"]
                mouse_X = self.touch_dialog_data[1]["mouse_X"]
                mouse_Y = self.touch_dialog_data[1]["mouse_Y"]
                mouse_ms = self.touch_dialog_data[1]["mouse_ms"]
                if self.ui.k2_comboBox_second.currentIndex() == 0:
                    # buffer[8] = 0   # x坐标的低八位
                    # buffer[9] = 0   # x坐标的高八位
                    # buffer[10] = 0  # y坐标的低八位
                    # buffer[11] = 0  # y坐标的高八位
                    buffer[6] = 5  # report-id
                    buffer[7] = 0x83  # 功能位 0x83=触摸按下 0x82=触摸松开
                    buffer[8] = int((X + slide_px_v / 2) % 255)
                    buffer[9] = int((X + slide_px_v / 2) / 255)
                    buffer[10] = int(Y % 255)
                    buffer[11] = int(Y / 255)
                    buffer[12] = int(slide_ms_v / 10)  # 间隔时间 单位10ms
                    buffer[13] = self.ui.k2_comboBox_second.currentIndex()  # 子功能标记
                    buffer[14] = 5  # report-id
                    buffer[15] = 0x83  # 功能位 0x83=触摸按下 0x82=触摸松开
                    buffer[16] = int((X - slide_px_v / 2) % 255)
                    buffer[17] = int((X - slide_px_v / 2) / 255)
                    buffer[18] = int(Y % 255)
                    buffer[19] = int(Y / 255)
                    buffer[20] = 0  # 间隔时间 单位10ms
                    buffer[21] = self.ui.k2_comboBox_second.currentIndex()  # 子功能标记
                if self.ui.k2_comboBox_second.currentIndex() == 1:
                    buffer[6] = 5  # report-id
                    buffer[7] = 0x83  # 功能位 0x83=触摸按下 0x82=触摸松开
                    buffer[8] = int((X - slide_px_v / 2) % 255)
                    buffer[9] = int((X - slide_px_v / 2) / 255)
                    buffer[10] = int(Y % 255)
                    buffer[11] = int(Y / 255)
                    buffer[12] = int(slide_ms_v / 10)  # 间隔时间 单位10ms
                    buffer[13] = self.ui.k2_comboBox_second.currentIndex()  # 子功能标记
                    buffer[14] = 5  # report-id
                    buffer[15] = 0x83  # 功能位 0x83=触摸按下 0x82=触摸松开
                    buffer[16] = int((X + slide_px_v / 2) % 255)
                    buffer[17] = int((X + slide_px_v / 2) / 255)
                    buffer[18] = int(Y % 255)
                    buffer[19] = int(Y / 255)
                    buffer[20] = 0  # 间隔时间 单位10ms
                    buffer[21] = self.ui.k2_comboBox_second.currentIndex()  # 子功能标记
                if self.ui.k2_comboBox_second.currentIndex() == 2:
                    buffer[6] = 5  # report-id
                    buffer[7] = 0x83  # 功能位 0x83=触摸按下 0x82=触摸松开
                    buffer[8] = int(X % 255)
                    buffer[9] = int(X / 255)
                    buffer[10] = int((Y - slide_px_v / 2) % 255)
                    buffer[11] = int((Y - slide_px_v / 2) / 255)
                    buffer[12] = int(slide_ms_v / 10)  # 间隔时间 单位10ms
                    buffer[13] = self.ui.k2_comboBox_second.currentIndex()  # 子功能标记
                    buffer[14] = 5  # report-id
                    buffer[15] = 0x83  # 功能位 0x83=触摸按下 0x82=触摸松开
                    buffer[16] = int(X % 255)
                    buffer[17] = int(X / 255)
                    buffer[18] = int((Y + slide_px_v / 2) % 255)
                    buffer[19] = int((Y + slide_px_v / 2) / 255)
                    buffer[20] = 0  # 间隔时间 单位10ms
                    buffer[21] = self.ui.k2_comboBox_second.currentIndex()  # 子功能标记
                if self.ui.k2_comboBox_second.currentIndex() == 3:
                    buffer[6] = 5  # report-id
                    buffer[7] = 0x83  # 功能位 0x83=触摸按下 0x82=触摸松开
                    buffer[8] = int(X % 255)
                    buffer[9] = int(X / 255)
                    buffer[10] = int((Y + slide_px_v / 2) % 255)
                    buffer[11] = int((Y + slide_px_v / 2) / 255)
                    buffer[12] = int(slide_ms_v / 10)  # 间隔时间 单位10ms
                    buffer[13] = self.ui.k2_comboBox_second.currentIndex()  # 子功能标记
                    buffer[14] = 5  # report-id
                    buffer[15] = 0x83  # 功能位 0x83=触摸按下 0x82=触摸松开
                    buffer[16] = int(X % 255)
                    buffer[17] = int(X / 255)
                    buffer[18] = int((Y - slide_px_v / 2) % 255)
                    buffer[19] = int((Y - slide_px_v / 2) / 255)
                    buffer[20] = 0  # 间隔时间 单位10ms
                    buffer[21] = self.ui.k2_comboBox_second.currentIndex()  # 子功能标记
                if self.ui.k2_comboBox_second.currentIndex() == 4:
                    buffer[6] = 5  # report-id
                    # buffer[7] = 6  # 功能位 多边形边数
                    # buffer[8] = 40  # 功能位 边到中心点距离
                    buffer[7] = osu_n_v
                    buffer[8] = osu_r_v
                    buffer[12] = osu_finish_ms_v  # 单圈时间 单位1ms
                    buffer[13] = self.ui.k2_comboBox_second.currentIndex()  # 子功能标记
                    buffer[14] = 5  # report-id
                    # buffer[15] = 0x83  # 功能位 0x83=触摸按下 0x82=触摸松开
                    # buffer[16] = int(X % 255)
                    # buffer[17] = int(X / 255)
                    # buffer[18] = int((Y - slide_px_v / 2) % 255)
                    # buffer[19] = int((Y - slide_px_v / 2) / 255)
                    # buffer[20] = 0  # 间隔时间 单位10ms
                    # buffer[21] = 0  # 子功能标记
                if self.ui.k2_comboBox_second.currentIndex() == 5:
                    buffer[6] = 5  # report-id
                    buffer[7] = 0x83  # 功能位 0x83=触摸按下 0x82=触摸松开
                    buffer[8] = int(mouse_X % 255)
                    buffer[9] = int(mouse_X / 255)
                    buffer[10] = int(mouse_Y % 255)
                    buffer[11] = int(mouse_Y / 255)
                    buffer[12] = int(mouse_ms / 10)  # 间隔时间 单位10ms
                    buffer[13] = self.ui.k2_comboBox_second.currentIndex()  # 子功能标记
                    buffer[14] = 5  # report-id
                    buffer[15] = 0x82  # 功能位 0x83=触摸按下 0x82=触摸松开
                    buffer[16] = int(mouse_X % 255)
                    buffer[17] = int(mouse_X / 255)
                    buffer[18] = int(mouse_Y % 255)
                    buffer[19] = int(mouse_Y / 255)
                    buffer[20] = 0  # 间隔时间 单位10ms
                    buffer[21] = self.ui.k2_comboBox_second.currentIndex()  # 子功能标记
            elif self.ui.k2_comboBox.currentIndex() == 4:
                buffer.append(5)  # 按键功能 0=停用此键 1=标准按键 2=多媒体键
                buffer.append(5)  # report所占长度
                # 5字节 按下键盘功能report
                buffer.append(6)  # report-id
                key_value = self.ui.k2_comboBox_second.currentIndex()
                if key_value == 0:
                    buffer.append(int('0x01', 16))  # 功能位 低位 按下
                    buffer.append(int('0x00', 16))  # 功能位 高位
                elif key_value == 1:
                    buffer.append(int('0xC4', 16))  # 功能位 低位 右转
                    buffer.append(int('0xFF', 16))  # 功能位 高位
                elif key_value == 2:
                    buffer.append(int('0x3C', 16))  # 功能位 低位 左转
                    buffer.append(int('0x00', 16))  # 功能位 高位
                else:
                    buffer.append(0)  # 功能位 低位 留空/停用
                    buffer.append(0)  # 功能位 高位
                delay = self.dial_dialog_data[1]["delay"]
                scroll_p = self.dial_dialog_data[1]["scroll"] * 10
                if self.dial_dialog_data[1]["scroll_enable"]:
                    scroll_p = int(scroll_p) + 1
                buffer.append(int(scroll_p))  # 滚动格数/长按 250 -> 25滚动格数/0启用或关闭长按
                buffer.append(delay)  # 滚动间隔 单位1ms
                # 5字节 按下松开键盘功能report
                buffer.append(6)  # report-id
                buffer.append(0)  # 功能位 低位
                buffer.append(0)  # 功能位 高位
                buffer.append(0)  # 滚动格数/长按 可选
                buffer.append(0)  # 滚动间隔 可选
            info = out_data(vendor_id, usage_page, buffer)
            time.sleep(0.6)
            progress.setValue(40)
            print(info)

        if self.key_flag[2] == 1:
            buffer = [0]
            buffer[0] = page_id
            buffer.append(1)  # 写入
            buffer.append(4)  # 单元ID 0=功能 1=led 2=按键1 3=按键2 4=按键3
            buffer.append(0)  # 保留位
            if self.ui.k3_comboBox.currentIndex() == 0:
                keysequence = self.ui.k3_keySequenceEdit.keySequence().toString()
                for i in range(4, 14):
                    buffer.append(0)
                buffer[4] = 1  # 按键功能 0=停用此键 1=标准按键 2=多媒体键
                buffer[5] = 4  # report所占长度
                # 4字节 按下键盘功能report  Control+X
                buffer[6] = 1  # report-id
                buffer[7] = 0  # Control Shift Alt GUI 键功能
                buffer[8] = 0  # 保留位
                buffer[9] = 0  # "X"
                # 4字节 按下松开键盘功能
                buffer[10] = 1  # report-id
                buffer[11] = 0  # Control Shift Alt GUI 键功能
                buffer[12] = 0  # 保留位
                buffer[13] = 0  # 功能位
                if self.ui.k3_keySequenceEdit.keySequence().count() == 0:  # 没有输入键位
                    buffer[4] = 1
                    print("未启用该键")
                else:
                    if len(re.findall("\+", keysequence)) == 0:  # 没有匹配到+号，不是组合键
                        mapcode = [key for key, value in self.keyboard_map["hid_keyboard"].items() if
                                   value == keysequence]
                        print(mapcode)
                        buffer[9] = int(mapcode[0], 16)  # 功能位
                    else:  # 组合键
                        keysequence_list = keysequence.split("+").copy()
                        print(keysequence_list)
                        if re.findall(r'Ctrl', keysequence):
                            buffer[7] += 1
                        if re.findall(r'Shift', keysequence):
                            buffer[7] += 2
                        if re.findall(r'Alt', keysequence):
                            buffer[7] += 4
                        if re.findall(r'Meta', keysequence):
                            buffer[7] += 8
                        mapcode = [key for key, value in self.keyboard_map["hid_keyboard"].items() if
                                   value == keysequence_list[-1]]  # 通过值反查key
                        buffer[9] = int(mapcode[0], 16)  # 功能位
            elif self.ui.k3_comboBox.currentIndex() == 1:
                buffer.append(2)  # 按键功能 0=停用此键 1=标准按键 2=多媒体键
                buffer.append(3)  # report所占长度
                # 3字节 按下键盘功能report
                buffer.append(2)  # report-id
                # buffer.append(0)  # 功能位 低位
                # buffer.append(0)  # 功能位 高位
                key_value = self.ui.k3_comboBox_second.currentText()
                buffer.append(int(int(self.mian_data["media_key_list"][key_value], 16) % 255))  # 功能位 低位
                buffer.append(int(int(self.mian_data["media_key_list"][key_value], 16) / 255))  # 功能位 高位
                # 3字节 按下松开键盘功能report
                buffer.append(2)  # report-id
                buffer.append(0)  # 功能位 低位
                buffer.append(0)  # 功能位 高位
                if self.ui.k3_comboBox_second.currentIndex() == 0 or self.ui.k3_comboBox_second.currentIndex() == 1:  # 没有输入键位
                    buffer[4] = 2
                    print("未启用该键")
            elif self.ui.k3_comboBox.currentIndex() == 2:
                buffer.append(3)  # 按键功能 3=鼠标模式
                buffer.append(5)  # report所占长度
                # 5字节 鼠标report
                # buffer[6] = 3  # report-id
                # buffer[7] = 6  # 按键
                # buffer[8] = 40  # X坐标变化量
                # buffer[9] = 0   # Y坐标变化量
                # buffer[10] = 0  # 滚轮变化
                buffer.append(3)  # report-id
                mouse_x = self.mouse_dialog_data[2]["mouse_x"]
                mouse_y = self.mouse_dialog_data[2]["mouse_y"]
                mouse_scroll = self.mouse_dialog_data[2]["mouse_scroll"]
                mouse_btn = self.mouse_dialog_data[2]["mouse_btn"]
                if mouse_btn == 1:
                    buffer.append(1)  # 按键
                elif mouse_btn == 2:
                    buffer.append(2)  # 按键
                elif mouse_btn == 3:
                    buffer.append(4)  # 按键
                else:
                    buffer.append(0)  # 按键
                unsigned_mouse_x = struct.pack("b", mouse_x)[0]
                unsigned_mouse_y = struct.pack("b", mouse_y)[0]
                unsigned_mouse_scroll = struct.pack("b", mouse_scroll)[0]
                buffer.append(unsigned_mouse_x)  # X坐标变化量
                buffer.append(unsigned_mouse_y)  # Y坐标变化量
                buffer.append(unsigned_mouse_scroll)  # 滚轮变化
                buffer.append(3)
                buffer.append(0)  # 松开按键
                buffer.append(0)  # X
                buffer.append(0)  # Y
                buffer.append(0)  # 滚轮
            elif self.ui.k3_comboBox.currentIndex() == 3:
                X = self.ui.resolution_X.value() / 2
                Y = self.ui.resolution_Y.value() / 2
                buffer.append(4)  # 按键功能 0=停用此键 1=标准按键 2=多媒体键 4=触摸
                buffer.append(8)  # report所占长度
                for i in range(6, 8 * 2 + 4 + 2):
                    buffer.append(0)
                slide_ms_v = self.touch_dialog_data[2]["slide_ms"]
                slide_px_v = self.touch_dialog_data[2]["slide_px"]
                osu_finish_ms_v = self.touch_dialog_data[2]["osu_finish_ms"]
                osu_r_v = self.touch_dialog_data[2]["osu_r"]
                osu_n_v = self.touch_dialog_data[2]["osu_n"]
                mouse_X = self.touch_dialog_data[2]["mouse_X"]
                mouse_Y = self.touch_dialog_data[2]["mouse_Y"]
                mouse_ms = self.touch_dialog_data[2]["mouse_ms"]
                if self.ui.k3_comboBox_second.currentIndex() == 0:
                    # buffer[8] = 0   # x坐标的低八位
                    # buffer[9] = 0   # x坐标的高八位
                    # buffer[10] = 0  # y坐标的低八位
                    # buffer[11] = 0  # y坐标的高八位
                    buffer[6] = 5  # report-id
                    buffer[7] = 0x83  # 功能位 0x83=触摸按下 0x82=触摸松开
                    buffer[8] = int((X + slide_px_v / 2) % 255)
                    buffer[9] = int((X + slide_px_v / 2) / 255)
                    buffer[10] = int(Y % 255)
                    buffer[11] = int(Y / 255)
                    buffer[12] = int(slide_ms_v / 10)  # 间隔时间 单位10ms
                    buffer[13] = self.ui.k3_comboBox_second.currentIndex()  # 子功能标记
                    buffer[14] = 5  # report-id
                    buffer[15] = 0x83  # 功能位 0x83=触摸按下 0x82=触摸松开
                    buffer[16] = int((X - slide_px_v / 2) % 255)
                    buffer[17] = int((X - slide_px_v / 2) / 255)
                    buffer[18] = int(Y % 255)
                    buffer[19] = int(Y / 255)
                    buffer[20] = 0  # 间隔时间 单位10ms
                    buffer[21] = self.ui.k3_comboBox_second.currentIndex()  # 子功能标记
                if self.ui.k3_comboBox_second.currentIndex() == 1:
                    buffer[6] = 5  # report-id
                    buffer[7] = 0x83  # 功能位 0x83=触摸按下 0x82=触摸松开
                    buffer[8] = int((X - slide_px_v / 2) % 255)
                    buffer[9] = int((X - slide_px_v / 2) / 255)
                    buffer[10] = int(Y % 255)
                    buffer[11] = int(Y / 255)
                    buffer[12] = int(slide_ms_v / 10)  # 间隔时间 单位10ms
                    buffer[13] = self.ui.k3_comboBox_second.currentIndex()  # 子功能标记
                    buffer[14] = 5  # report-id
                    buffer[15] = 0x83  # 功能位 0x83=触摸按下 0x82=触摸松开
                    buffer[16] = int((X + slide_px_v / 2) % 255)
                    buffer[17] = int((X + slide_px_v / 2) / 255)
                    buffer[18] = int(Y % 255)
                    buffer[19] = int(Y / 255)
                    buffer[20] = 0  # 间隔时间 单位10ms
                    buffer[21] = self.ui.k3_comboBox_second.currentIndex()  # 子功能标记
                if self.ui.k3_comboBox_second.currentIndex() == 2:
                    buffer[6] = 5  # report-id
                    buffer[7] = 0x83  # 功能位 0x83=触摸按下 0x82=触摸松开
                    buffer[8] = int(X % 255)
                    buffer[9] = int(X / 255)
                    buffer[10] = int((Y - slide_px_v / 2) % 255)
                    buffer[11] = int((Y - slide_px_v / 2) / 255)
                    buffer[12] = int(slide_ms_v / 10)  # 间隔时间 单位10ms
                    buffer[13] = self.ui.k3_comboBox_second.currentIndex()  # 子功能标记
                    buffer[14] = 5  # report-id
                    buffer[15] = 0x83  # 功能位 0x83=触摸按下 0x82=触摸松开
                    buffer[16] = int(X % 255)
                    buffer[17] = int(X / 255)
                    buffer[18] = int((Y + slide_px_v / 2) % 255)
                    buffer[19] = int((Y + slide_px_v / 2) / 255)
                    buffer[20] = 0  # 间隔时间 单位10ms
                    buffer[21] = self.ui.k3_comboBox_second.currentIndex()  # 子功能标记
                if self.ui.k3_comboBox_second.currentIndex() == 3:
                    buffer[6] = 5  # report-id
                    buffer[7] = 0x83  # 功能位 0x83=触摸按下 0x82=触摸松开
                    buffer[8] = int(X % 255)
                    buffer[9] = int(X / 255)
                    buffer[10] = int((Y + slide_px_v / 2) % 255)
                    buffer[11] = int((Y + slide_px_v / 2) / 255)
                    buffer[12] = int(slide_ms_v / 10)  # 间隔时间 单位10ms
                    buffer[13] = self.ui.k3_comboBox_second.currentIndex()  # 子功能标记
                    buffer[14] = 5  # report-id
                    buffer[15] = 0x83  # 功能位 0x83=触摸按下 0x82=触摸松开
                    buffer[16] = int(X % 255)
                    buffer[17] = int(X / 255)
                    buffer[18] = int((Y - slide_px_v / 2) % 255)
                    buffer[19] = int((Y - slide_px_v / 2) / 255)
                    buffer[20] = 0  # 间隔时间 单位10ms
                    buffer[21] = self.ui.k3_comboBox_second.currentIndex()  # 子功能标记
                if self.ui.k3_comboBox_second.currentIndex() == 4:
                    buffer[6] = 5  # report-id
                    # buffer[7] = 6  # 功能位 多边形边数
                    # buffer[8] = 40  # 功能位 边到中心点距离
                    buffer[7] = osu_n_v
                    buffer[8] = osu_r_v
                    buffer[12] = osu_finish_ms_v  # 单圈时间 单位1ms
                    buffer[13] = self.ui.k3_comboBox_second.currentIndex()  # 子功能标记
                    buffer[14] = 5  # report-id
                    # buffer[15] = 0x83  # 功能位 0x83=触摸按下 0x82=触摸松开
                    # buffer[16] = int(X % 255)
                    # buffer[17] = int(X / 255)
                    # buffer[18] = int((Y - slide_px_v / 2) % 255)
                    # buffer[19] = int((Y - slide_px_v / 2) / 255)
                    # buffer[20] = 0  # 间隔时间 单位10ms
                    # buffer[21] = 0  # 子功能标记
                if self.ui.k3_comboBox_second.currentIndex() == 5:
                    buffer[6] = 5  # report-id
                    buffer[7] = 0x83  # 功能位 0x83=触摸按下 0x82=触摸松开
                    buffer[8] = int(mouse_X % 255)
                    buffer[9] = int(mouse_X / 255)
                    buffer[10] = int(mouse_Y % 255)
                    buffer[11] = int(mouse_Y / 255)
                    buffer[12] = int(mouse_ms / 10)  # 间隔时间 单位10ms
                    buffer[13] = self.ui.k3_comboBox_second.currentIndex()  # 子功能标记
                    buffer[14] = 5  # report-id
                    buffer[15] = 0x82  # 功能位 0x83=触摸按下 0x82=触摸松开
                    buffer[16] = int(mouse_X % 255)
                    buffer[17] = int(mouse_X / 255)
                    buffer[18] = int(mouse_Y % 255)
                    buffer[19] = int(mouse_Y / 255)
                    buffer[20] = 0  # 间隔时间 单位10ms
                    buffer[21] = self.ui.k3_comboBox_second.currentIndex()  # 子功能标记
            elif self.ui.k3_comboBox.currentIndex() == 4:
                buffer.append(5)  # 按键功能 0=停用此键 1=标准按键 2=多媒体键
                buffer.append(5)  # report所占长度
                # 5字节 按下键盘功能report
                buffer.append(6)  # report-id
                key_value = self.ui.k3_comboBox_second.currentIndex()
                if key_value == 0:
                    buffer.append(int('0x01', 16))  # 功能位 低位 按下
                    buffer.append(int('0x00', 16))  # 功能位 高位
                elif key_value == 1:
                    buffer.append(int('0xC4', 16))  # 功能位 低位 右转
                    buffer.append(int('0xFF', 16))  # 功能位 高位
                elif key_value == 2:
                    buffer.append(int('0x3C', 16))  # 功能位 低位 左转
                    buffer.append(int('0x00', 16))  # 功能位 高位
                else:
                    buffer.append(0)  # 功能位 低位 留空/停用
                    buffer.append(0)  # 功能位 高位
                delay = self.dial_dialog_data[2]["delay"]
                scroll_p = self.dial_dialog_data[2]["scroll"] * 10
                if self.dial_dialog_data[2]["scroll_enable"]:
                    scroll_p = int(scroll_p) + 1
                buffer.append(int(scroll_p))  # 滚动格数/长按 250 -> 25滚动格数/0启用或关闭长按
                buffer.append(delay)  # 滚动间隔 单位1ms
                # 5字节 按下松开键盘功能report
                buffer.append(6)  # report-id
                buffer.append(0)  # 功能位 低位
                buffer.append(0)  # 功能位 高位
                buffer.append(0)  # 滚动格数/长按 可选
                buffer.append(0)  # 滚动间隔 可选
            info = out_data(vendor_id, usage_page, buffer)
            time.sleep(0.6)
            progress.setValue(60)
            print(info)

        if self.key_flag[0] == 0 and self.key_flag[1] == 0 and self.key_flag[2] == 0:
            self.ui.statusBar().showMessage("键位未更改")
        else:
            self.reload()
            progress.setValue(70)
            self.key_r_button_func()
            progress.setValue(85)
        progress.setValue(100)

    # ----------------------------第一下拉菜单功能----------------------------
    def k1_comboBox_func(self):
        if self.ui.k1_comboBox.currentIndex() == 0:
            self.ui.k1_keySequenceEdit.setVisible(True)
            self.ui.k1_keySequenceEdit.setEnabled(True)
            self.ui.k1_button_attribute.setVisible(True)
            self.ui.k1_button_attribute.setEnabled(True)
            self.ui.expand_button.setVisible(False)
            self.ui.expand_button.setEnabled(False)
            self.ui.k1_comboBox_second.setVisible(False)
        elif self.ui.k1_comboBox.currentIndex() == 1:
            self.ui.k1_keySequenceEdit.setVisible(False)

            self.ui.k1_comboBox_second.clear()
            for i in self.mian_data["media_key_list"]:
                self.ui.k1_comboBox_second.addItem(i)

            self.ui.k1_comboBox_second.setVisible(True)
            self.ui.k1_comboBox_second.setEnabled(True)
            self.ui.k1_button_attribute.setVisible(False)
            self.ui.expand_button.setVisible(False)
        elif self.ui.k1_comboBox.currentIndex() == 2:
            self.ui.k1_keySequenceEdit.setVisible(False)
            self.ui.k1_comboBox_second.setVisible(False)
            self.ui.k1_button_attribute.setVisible(False)
            self.ui.expand_button.setEnabled(True)
            self.ui.expand_button.setVisible(True)
        elif self.ui.k1_comboBox.currentIndex() == 3:
            self.ui.k1_keySequenceEdit.setVisible(False)
            self.ui.k1_comboBox_second.clear()
            for i in self.mian_data["touch_key_list"]:
                self.ui.k1_comboBox_second.addItem(i)
            self.ui.k1_comboBox_second.setVisible(True)
            self.ui.k1_comboBox_second.setEnabled(True)
            self.ui.k1_button_attribute.setVisible(True)
            self.ui.expand_button.setVisible(False)
        elif self.ui.k1_comboBox.currentIndex() == 4:
            self.ui.k1_keySequenceEdit.setVisible(False)
            self.ui.k1_comboBox_second.clear()
            for i in self.mian_data["dial_key_list"]:
                self.ui.k1_comboBox_second.addItem(i)
            self.ui.k1_comboBox_second.setVisible(True)
            self.ui.k1_comboBox_second.setEnabled(True)
            self.ui.k1_button_attribute.setVisible(True)
            self.ui.expand_button.setVisible(False)
        else:
            self.ui.k1_keySequenceEdit.setEnabled(False)
            self.ui.k1_keySequenceEdit.setVisible(False)
            self.ui.k1_comboBox_second.setVisible(False)
            self.ui.k1_comboBox_second.setEnabled(False)
            self.ui.k1_button_attribute.setVisible(False)

    def k2_comboBox_func(self):
        if self.ui.k2_comboBox.currentIndex() == 0:
            self.ui.k2_keySequenceEdit.setEnabled(True)
            self.ui.k2_keySequenceEdit.setVisible(True)
            self.ui.expand_button_2.setVisible(False)
            self.ui.expand_button_2.setEnabled(False)
            self.ui.k2_comboBox_second.setVisible(False)
            self.ui.k2_comboBox_second.setEnabled(False)
            self.ui.k2_button_attribute.setEnabled(True)
            self.ui.k2_button_attribute.setVisible(True)
        elif self.ui.k2_comboBox.currentIndex() == 1:
            self.ui.k2_keySequenceEdit.setEnabled(False)
            self.ui.k2_keySequenceEdit.setVisible(False)
            self.ui.k2_comboBox_second.clear()
            for i in self.mian_data["media_key_list"]:
                self.ui.k2_comboBox_second.addItem(i)

            self.ui.expand_button_2.setVisible(False)
            self.ui.k2_comboBox_second.setVisible(True)
            self.ui.k2_comboBox_second.setEnabled(True)
            self.ui.expand_button_2.setVisible(False)
            self.ui.k2_button_attribute.setVisible(False)
        elif self.ui.k2_comboBox.currentIndex() == 2:
            self.ui.k2_keySequenceEdit.setVisible(False)
            self.ui.k2_comboBox_second.setVisible(False)
            self.ui.expand_button_2.setEnabled(True)
            self.ui.expand_button_2.setVisible(True)
        elif self.ui.k2_comboBox.currentIndex() == 3:
            self.ui.k2_keySequenceEdit.setVisible(False)
            self.ui.k2_comboBox_second.clear()
            for i in self.mian_data["touch_key_list"]:
                self.ui.k2_comboBox_second.addItem(i)
            self.ui.k2_comboBox_second.setVisible(True)
            self.ui.k2_comboBox_second.setEnabled(True)
            self.ui.k2_button_attribute.setVisible(True)
            self.ui.expand_button_2.setVisible(False)
        elif self.ui.k2_comboBox.currentIndex() == 4:
            self.ui.k2_keySequenceEdit.setVisible(False)
            self.ui.k2_comboBox_second.clear()
            for i in self.mian_data["dial_key_list"]:
                self.ui.k2_comboBox_second.addItem(i)
            self.ui.k2_comboBox_second.setVisible(True)
            self.ui.k2_comboBox_second.setEnabled(True)
            self.ui.k2_button_attribute.setVisible(True)
            self.ui.expand_button_2.setVisible(False)

        else:
            self.ui.k2_keySequenceEdit.setEnabled(False)
            self.ui.k2_keySequenceEdit.setVisible(False)
            self.ui.k2_comboBox_second.setVisible(False)
            self.ui.k2_comboBox_second.setEnabled(False)
            self.ui.k2_button_attribute.setVisible(False)

    def k3_comboBox_func(self):
        if self.ui.k3_comboBox.currentIndex() == 0:
            self.ui.k3_keySequenceEdit.setEnabled(True)
            self.ui.k3_keySequenceEdit.setVisible(True)
            self.ui.expand_button_3.setVisible(False)
            self.ui.expand_button_3.setEnabled(False)
            self.ui.k3_comboBox_second.setVisible(False)
            self.ui.k3_comboBox_second.setEnabled(False)
            self.ui.k3_button_attribute.setEnabled(True)
            self.ui.k3_button_attribute.setVisible(True)
        elif self.ui.k3_comboBox.currentIndex() == 1:
            self.ui.k3_keySequenceEdit.setEnabled(False)
            self.ui.k3_keySequenceEdit.setVisible(False)
            self.ui.k3_comboBox_second.clear()
            for i in self.mian_data["media_key_list"]:
                self.ui.k3_comboBox_second.addItem(i)
            self.ui.expand_button_3.setVisible(False)
            self.ui.k3_comboBox_second.setVisible(True)
            self.ui.k3_comboBox_second.setEnabled(True)
            self.ui.k3_button_attribute.setVisible(False)
        elif self.ui.k3_comboBox.currentIndex() == 2:
            self.ui.k3_keySequenceEdit.setVisible(False)
            self.ui.k3_comboBox_second.setVisible(False)
            self.ui.k3_button_attribute.setVisible(False)
            self.ui.expand_button_3.setEnabled(True)
            self.ui.expand_button_3.setVisible(True)
        elif self.ui.k3_comboBox.currentIndex() == 3:
            self.ui.k3_keySequenceEdit.setVisible(False)
            self.ui.k3_comboBox_second.clear()
            for i in self.mian_data["touch_key_list"]:
                self.ui.k3_comboBox_second.addItem(i)
            self.ui.k3_comboBox_second.setVisible(True)
            self.ui.k3_comboBox_second.setEnabled(True)
            self.ui.k3_button_attribute.setVisible(True)
            self.ui.expand_button_3.setVisible(False)
        elif self.ui.k3_comboBox.currentIndex() == 4:
            self.ui.k3_keySequenceEdit.setVisible(False)
            self.ui.k3_comboBox_second.clear()
            for i in self.mian_data["dial_key_list"]:
                self.ui.k3_comboBox_second.addItem(i)
            self.ui.k3_comboBox_second.setVisible(True)
            self.ui.k3_comboBox_second.setEnabled(True)
            self.ui.k3_button_attribute.setVisible(True)
            self.ui.expand_button_3.setVisible(False)

        else:
            self.ui.k3_keySequenceEdit.setEnabled(False)
            self.ui.k3_keySequenceEdit.setVisible(False)
            self.ui.k3_comboBox_second.setVisible(False)
            self.ui.k3_comboBox_second.setEnabled(False)
            self.ui.k3_button_attribute.setVisible(False)

    # ----------------------------属性按钮功能----------------------------
    def k1_button_attribute_func(self):
        if self.ui.k1_comboBox.currentIndex() == 0:
            info = self.key_dialog.exec()
            if info == 1:
                if self.key_dialog.checkBox_21.isChecked():
                    keysequence = "Tab"
                else:
                    keysequence = self.key_dialog.keySequenceEdit.keySequence().toString()
                if self.key_dialog.checkBox_3.isChecked():
                    keysequence = "Shift+" + keysequence
                if self.key_dialog.checkBox_2.isChecked():
                    keysequence = "Alt+" + keysequence
                if self.key_dialog.checkBox_1.isChecked():
                    keysequence = "Ctrl+" + keysequence
                if self.key_dialog.checkBox_4.isChecked():
                    keysequence = "Meta+" + keysequence
                print(keysequence)
                self.ui.k1_keySequenceEdit.setKeySequence(keysequence)
                self.key_flag[0] = 1
        elif self.ui.k1_comboBox.currentIndex() == 3:
            self.touch_dialog.osu_r.setValue(self.touch_dialog_data[0]["osu_r"])
            self.touch_dialog.osu_n.setValue(self.touch_dialog_data[0]["osu_n"])
            self.touch_dialog.slide_ms.setValue(self.touch_dialog_data[0]["slide_ms"])
            self.touch_dialog.slide_px.setValue(self.touch_dialog_data[0]["slide_px"])
            self.touch_dialog.osu_finish_ms.setValue(self.touch_dialog_data[0]["osu_finish_ms"])
            self.touch_dialog.mouse_X.setValue(self.touch_dialog_data[0]["mouse_X"])
            self.touch_dialog.mouse_Y.setValue(self.touch_dialog_data[0]["mouse_Y"])
            self.touch_dialog.mouse_ms.setValue(self.touch_dialog_data[0]["mouse_ms"])

            info = self.touch_dialog.exec()
            if info == 1:
                self.touch_dialog_data[0]["slide_ms"] = self.touch_dialog.slide_ms.value()
                self.touch_dialog_data[0]["slide_px"] = self.touch_dialog.slide_px.value()
                self.touch_dialog_data[0]["osu_finish_ms"] = self.touch_dialog.osu_finish_ms.value()
                self.touch_dialog_data[0]["osu_r"] = self.touch_dialog.osu_r.value()
                self.touch_dialog_data[0]["osu_n"] = self.touch_dialog.osu_n.value()
                self.touch_dialog_data[0]["mouse_X"] = self.touch_dialog.mouse_X.value()
                self.touch_dialog_data[0]["mouse_Y"] = self.touch_dialog.mouse_Y.value()
                self.touch_dialog_data[0]["mouse_ms"] = self.touch_dialog.mouse_ms.value()

                # print(self.touch_dialog_data[0]["mouse_X"], "  ", self.touch_dialog_data[0]["mouse_Y"])
                self.key_flag[0] = 1
        elif self.ui.k1_comboBox.currentIndex() == 4:
            self.dial_dialog.delay.setValue(self.dial_dialog_data[0]["delay"])
            self.dial_dialog.dial_scroll.setValue(self.dial_dialog_data[0]["scroll"])
            self.dial_dialog.checkBox.setChecked(self.dial_dialog_data[0]["scroll_enable"])
            info = self.dial_dialog.exec()
            if info == 1:
                self.dial_dialog_data[0]["delay"] = self.dial_dialog.delay.value()
                self.dial_dialog_data[0]["scroll"] = self.dial_dialog.dial_scroll.value()
                if self.dial_dialog.checkBox.isChecked():
                    self.dial_dialog_data[0]["scroll_enable"] = True
                else:
                    self.dial_dialog_data[0]["scroll_enable"] = False
                self.key_flag[0] = 1

    def k2_button_attribute_func(self):
        if self.ui.k2_comboBox.currentIndex() == 0:
            info = self.key_dialog.exec()
            if info == 1:
                if self.key_dialog.checkBox_21.isChecked():
                    keysequence = "Tab"
                else:
                    keysequence = self.key_dialog.keySequenceEdit.keySequence().toString()
                if self.key_dialog.checkBox_3.isChecked():
                    keysequence = "Shift+" + keysequence
                if self.key_dialog.checkBox_2.isChecked():
                    keysequence = "Alt+" + keysequence
                if self.key_dialog.checkBox_1.isChecked():
                    keysequence = "Ctrl+" + keysequence
                if self.key_dialog.checkBox_4.isChecked():
                    keysequence = "Meta+" + keysequence
                print(keysequence)
                self.ui.k2_keySequenceEdit.setKeySequence(keysequence)
                self.key_flag[1] = 1
        elif self.ui.k2_comboBox.currentIndex() == 3:
            self.touch_dialog.osu_r.setValue(self.touch_dialog_data[1]["osu_r"])
            self.touch_dialog.osu_n.setValue(self.touch_dialog_data[1]["osu_n"])
            self.touch_dialog.slide_ms.setValue(self.touch_dialog_data[1]["slide_ms"])
            self.touch_dialog.slide_px.setValue(self.touch_dialog_data[1]["slide_px"])
            self.touch_dialog.osu_finish_ms.setValue(self.touch_dialog_data[1]["osu_finish_ms"])
            self.touch_dialog.mouse_X.setValue(self.touch_dialog_data[1]["mouse_X"])
            self.touch_dialog.mouse_Y.setValue(self.touch_dialog_data[1]["mouse_Y"])
            self.touch_dialog.mouse_ms.setValue(self.touch_dialog_data[1]["mouse_ms"])
            self.touch_dialog.exec()
            info = self.key_flag[1] = 1
            if info == 1:
                self.touch_dialog_data[1]["slide_ms"] = self.touch_dialog.slide_ms.value()
                self.touch_dialog_data[1]["slide_px"] = self.touch_dialog.slide_px.value()
                self.touch_dialog_data[1]["osu_finish_ms"] = self.touch_dialog.osu_finish_ms.value()
                self.touch_dialog_data[1]["osu_r"] = self.touch_dialog.osu_r.value()
                self.touch_dialog_data[1]["osu_n"] = self.touch_dialog.osu_n.value()
                self.touch_dialog_data[1]["mouse_X"] = self.touch_dialog.mouse_X.value()
                self.touch_dialog_data[1]["mouse_Y"] = self.touch_dialog.mouse_Y.value()
                self.touch_dialog_data[1]["mouse_ms"] = self.touch_dialog.mouse_ms.value()
                self.key_flag[1] = 1
        elif self.ui.k2_comboBox.currentIndex() == 4:
            self.dial_dialog.delay.setValue(self.dial_dialog_data[1]["delay"])
            self.dial_dialog.dial_scroll.setValue(self.dial_dialog_data[1]["scroll"])
            self.dial_dialog.checkBox.setChecked(self.dial_dialog_data[1]["scroll_enable"])
            info = self.dial_dialog.exec()
            if info == 1:
                self.dial_dialog_data[1]["delay"] = self.dial_dialog.delay.value()
                self.dial_dialog_data[1]["scroll"] = self.dial_dialog.dial_scroll.value()
                if self.dial_dialog.checkBox.isChecked():
                    self.dial_dialog_data[1]["scroll_enable"] = True
                else:
                    self.dial_dialog_data[1]["scroll_enable"] = False
                self.key_flag[1] = 1

    def k3_button_attribute_func(self):
        if self.ui.k3_comboBox.currentIndex() == 0:
            info = self.key_dialog.exec()
            if info == 1:
                self.key_flag[2] = 1
                if self.key_dialog.checkBox_21.isChecked():
                    keysequence = "Tab"
                else:
                    keysequence = self.key_dialog.keySequenceEdit.keySequence().toString()
                if self.key_dialog.checkBox_3.isChecked():
                    keysequence = "Shift+" + keysequence
                if self.key_dialog.checkBox_2.isChecked():
                    keysequence = "Alt+" + keysequence
                if self.key_dialog.checkBox_1.isChecked():
                    keysequence = "Ctrl+" + keysequence
                if self.key_dialog.checkBox_4.isChecked():
                    keysequence = "Meta+" + keysequence
                print(keysequence)
                self.ui.k3_keySequenceEdit.setKeySequence(keysequence)
                self.key_flag[2] = 1
        elif self.ui.k3_comboBox.currentIndex() == 3:
            self.touch_dialog.osu_r.setValue(self.touch_dialog_data[2]["osu_r"])
            self.touch_dialog.osu_n.setValue(self.touch_dialog_data[2]["osu_n"])
            self.touch_dialog.slide_ms.setValue(self.touch_dialog_data[2]["slide_ms"])
            self.touch_dialog.slide_px.setValue(self.touch_dialog_data[2]["slide_px"])
            self.touch_dialog.osu_finish_ms.setValue(self.touch_dialog_data[2]["osu_finish_ms"])
            self.touch_dialog.mouse_X.setValue(self.touch_dialog_data[2]["mouse_X"])
            self.touch_dialog.mouse_Y.setValue(self.touch_dialog_data[2]["mouse_Y"])
            self.touch_dialog.mouse_ms.setValue(self.touch_dialog_data[2]["mouse_ms"])
            info = self.touch_dialog.exec()
            if info == 1:
                self.touch_dialog_data[2]["slide_ms"] = self.touch_dialog.slide_ms.value()
                self.touch_dialog_data[2]["slide_px"] = self.touch_dialog.slide_px.value()
                self.touch_dialog_data[2]["osu_finish_ms"] = self.touch_dialog.osu_finish_ms.value()
                self.touch_dialog_data[2]["osu_r"] = self.touch_dialog.osu_r.value()
                self.touch_dialog_data[2]["osu_n"] = self.touch_dialog.osu_n.value()
                self.touch_dialog_data[2]["mouse_X"] = self.touch_dialog.mouse_X.value()
                self.touch_dialog_data[2]["mouse_Y"] = self.touch_dialog.mouse_Y.value()
                self.touch_dialog_data[2]["mouse_ms"] = self.touch_dialog.mouse_ms.value()
                self.key_flag[2] = 1
        elif self.ui.k3_comboBox.currentIndex() == 4:
            self.dial_dialog.delay.setValue(self.dial_dialog_data[2]["delay"])
            self.dial_dialog.dial_scroll.setValue(self.dial_dialog_data[2]["scroll"])
            self.dial_dialog.checkBox.setChecked(self.dial_dialog_data[2]["scroll_enable"])
            info = self.dial_dialog.exec()
            if info == 1:
                self.dial_dialog_data[2]["delay"] = self.dial_dialog.delay.value()
                self.dial_dialog_data[2]["scroll"] = self.dial_dialog.dial_scroll.value()
                if self.dial_dialog.checkBox.isChecked():
                    self.dial_dialog_data[2]["scroll_enable"] = True
                else:
                    self.dial_dialog_data[2]["scroll_enable"] = False
                self.key_flag[2] = 1

    # ----------------------------第二按钮功能----------------------------
    def expand_button_func(self):
        if self.ui.k1_comboBox.currentIndex() == 2:
            self.mouse_dialog.mouse_x.setValue(self.mouse_dialog_data[0]["mouse_x"])
            self.mouse_dialog.mouse_y.setValue(self.mouse_dialog_data[0]["mouse_y"])
            self.mouse_dialog.mouse_scroll.setValue(self.mouse_dialog_data[0]["mouse_scroll"])
            self.mouse_dialog.mouse_btn_comboBox.setCurrentIndex(self.mouse_dialog_data[0]["mouse_btn"])
            info = self.mouse_dialog.exec()
            if info == 1:
                self.mouse_dialog_data[0]["mouse_x"] = self.mouse_dialog.mouse_x.value()
                self.mouse_dialog_data[0]["mouse_y"] = self.mouse_dialog.mouse_y.value()
                self.mouse_dialog_data[0]["mouse_scroll"] = self.mouse_dialog.mouse_scroll.value()
                self.mouse_dialog_data[0]["mouse_btn"] = self.mouse_dialog.mouse_btn_comboBox.currentIndex()
                self.key_flag[0] = 1

    def expand_button_2_func(self):
        if self.ui.k2_comboBox.currentIndex() == 2:
            self.mouse_dialog.mouse_x.setValue(self.mouse_dialog_data[1]["mouse_x"])
            self.mouse_dialog.mouse_y.setValue(self.mouse_dialog_data[1]["mouse_y"])
            self.mouse_dialog.mouse_scroll.setValue(self.mouse_dialog_data[1]["mouse_scroll"])
            self.mouse_dialog.mouse_btn_comboBox.setCurrentIndex(self.mouse_dialog_data[1]["mouse_btn"])
            info = self.mouse_dialog.exec()
            if info == 1:
                self.mouse_dialog_data[1]["mouse_x"] = self.mouse_dialog.mouse_x.value()
                self.mouse_dialog_data[1]["mouse_y"] = self.mouse_dialog.mouse_y.value()
                self.mouse_dialog_data[1]["mouse_scroll"] = self.mouse_dialog.mouse_scroll.value()
                self.mouse_dialog_data[1]["mouse_btn"] = self.mouse_dialog.mouse_btn_comboBox.currentIndex()
                self.key_flag[1] = 1

    def expand_button_3_func(self):
        if self.ui.k3_comboBox.currentIndex() == 2:
            self.mouse_dialog.mouse_x.setValue(self.mouse_dialog_data[2]["mouse_x"])
            self.mouse_dialog.mouse_y.setValue(self.mouse_dialog_data[2]["mouse_y"])
            self.mouse_dialog.mouse_scroll.setValue(self.mouse_dialog_data[2]["mouse_scroll"])
            self.mouse_dialog.mouse_btn_comboBox.setCurrentIndex(self.mouse_dialog_data[2]["mouse_btn"])
            info = self.mouse_dialog.exec()
            if info == 1:
                self.mouse_dialog_data[2]["mouse_x"] = self.mouse_dialog.mouse_x.value()
                self.mouse_dialog_data[2]["mouse_y"] = self.mouse_dialog.mouse_y.value()
                self.mouse_dialog_data[2]["mouse_scroll"] = self.mouse_dialog.mouse_scroll.value()
                self.mouse_dialog_data[2]["mouse_btn"] = self.mouse_dialog.mouse_btn_comboBox.currentIndex()
                self.key_flag[2] = 1

    # ----------------------------标准键盘弹出窗口----------------------------
    def key_dialog_keySequenceEdit_func(self):
        if self.key_dialog.keySequenceEdit.keySequence().count() == 0:  # 去除多个复合键
            keysequence = ""
        elif self.key_dialog.keySequenceEdit.keySequence().count() == 1:
            keysequence = self.key_dialog.keySequenceEdit.keySequence().toString()
        else:
            keysequence = self.key_dialog.keySequenceEdit.keySequence().toString().split(",")
            self.key_dialog.keySequenceEdit.setKeySequence(keysequence[0])
            keysequence = keysequence[0]
        if len(re.findall("\+", keysequence)) == 0:  # 没有匹配到+号，不是组合键
            self.key_dialog.keySequenceEdit.setKeySequence(keysequence)
        else:
            keysequence_list = keysequence.split("+").copy()  # 将复合键转换为功能键
            self.key_dialog.keySequenceEdit.setKeySequence(keysequence_list[-1])

    def get_resolution_func(self):
        # 获取屏幕分辨率
        self.ui.resolution_X.setValue(self.screenRect.width())
        self.ui.resolution_Y.setValue(self.screenRect.height())

    def mouse_position(self):
        pos = QCursor.pos()
        # print(pos.x(),"  ", pos.y())
        self.touch_dialog.mouse_X.setValue(pos.x())
        self.touch_dialog.mouse_Y.setValue(pos.y())


def main():
    configfile_init()
    app = QApplication([])
    stats = Stats()
    # apply_stylesheet(app, theme='dark_teal.xml') # qt_material主题
    stats.ui.show()
    app.exec_()
    h.close()
    print("exit")
    sys.exit(0)


if __name__ == '__main__':
    main()
