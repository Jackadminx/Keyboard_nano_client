## HID通信

多设备是使用多个HID Report Descriptor实现，HID收发数据的第一位为该数据的 Report-Id

上网机与键盘通信使用`Vendor-Defined`

```
Report ID (4)
Report Size (8) 
Report Count (60) 
```


## 模式设置
```
# buffer[0] = 4  # report_id
# buffer[1] = 1  
# 读取/写入/复位/测试 0=r 1=w 2=reset 3=test 4=reload 5=命令模式 6=echo模式 7=操作FLASH
# buffer[2] = 0  # 单元ID 0=功能 1=led 2=按键1 3=按键2 4=按键3
# buffer[3] = 0  # 保留/单元功能

# buffer[4] = 0  # 预设键盘模式
# buffer[5] = 0  # 保留
# buffer[6] = 0  # 保留
# buffer[7] = 2  # led模式组 0x00-0x06 0为关闭
# buffer[8] = 10  # 按键扫描速度 单位1ms
# buffer[9] = 10  # 按键长按检测时间 单位100ms
# buffer[10] = 0xff   # 屏幕分辨率 X 低位
# buffer[11] = 0xff   # 屏幕分辨率 X 高位
# buffer[12] = 0xff   # 屏幕分辨率 Y 低位
# buffer[13] = 0xff   # 屏幕分辨率 Y 高位
```

### 重启单片机

```
# 重启单片机
# buffer[0] = 4  # report_id
# buffer[1] = 3  #  4=reset
```

### 重载配置 

从FLASH中重载灯光 键位 模式

```
# 重载配置 不重启单片机
# buffer[0] = 4  # report_id
# buffer[1] = 4  #  4=reload
```

### ECHO模式

可以用在上位机宏，可以设置延迟时间，

将上位机发送的HID去掉前4位，然后返回到电脑

```
# echo模式 前4位
# buffer[1] = 6  # 6=虚拟键盘
# buffer[2] = 0xff  # 延迟时间 高8位
# buffer[3] = 0xff  # 延迟时间 低8位
# buffer[4-60] # 数据报文单片机将直接发送此部分
```

## RGB

WS2812B 是以BRG读取灯光的

### 读写灯光组

写入全部6组灯光

```
buffer[0] = 4  # report_id
buffer[1] = 1  # 读取/写入/ 0=r 1=w
buffer[2] = 1  # 单元ID 00=功能设置 01=led 02=简单key 03=多媒体键
buffer[3] = 0  # 保留位
# buffer[4] = 0  # 1-B #第一组
# buffer[5] = 0  # 1-R
# buffer[6] = 0  # 1-G
# buffer[7] = 0  # 2-B
# buffer[8] = 0  # 2-R
# buffer[9] = 0  # 2-G
# buffer[7] = 0  # 3-B
# buffer[8] = 0  # 3-R
# buffer[9] = 0  # 3-G

......


# buffer[50] = 0  # 1-B #第六组
...
```

读取全部6组灯光

```
...
buffer[1] = 0  # 读取/写入/ 0=r 1=w
...
```

### 临时灯光

更改当前3个键的灯光，reload或reset后丢失

可以用上位机实现多种灯效

```
# 更换全部rgb灯光 不写入flash
# buffer[1] = 5  # 命令模式
# buffer[2] = 1  # 更改rgb
# buffer[3] = 0  # 保留
# buffer[4] = 0  # 1-B
# buffer[5] = 0  # 1-R
# buffer[6] = 0  # 1-G
# buffer[7] = 0  # 2-B
# buffer[8] = 0  # 2-R
# buffer[9] = 0  # 2-G
# buffer[7] = 0  # 3-B
# buffer[8] = 0  # 3-R
# buffer[9] = 0  # 3-G
```



## 键位

### 查询键位

```
# 查询按键
# buffer[0] = page_id  # report_id
# buffer[1] = 0  # 读取/写入/复位/测试 0=r 1=w 2=reset 3=test
# buffer[2] = 0xff  # 单元ID 0=功能 1=led 2=按键1 3=按键2 4=按键3 0xff=全部
# 当buffer[2] = 0xff时[4][5][6]为按键类型
```

### 标准键盘

```
# 标准按键
# buffer[1] = 1  # 写入
# buffer[2] = 2  # 单元ID 0=功能 1=led 2=按键1 3=按键2 4=按键3
# buffer[3] = 0  # 保留位
# buffer[4] = 1  # 按键功能 1=标准按键 2=多媒体键
# buffer[5] = 4  # report所占长度
# 4字节 按下键盘功能report  Control+X
# buffer[6] = 1  # report-id
# buffer[7] = 0x01  # Control Shift Alt GUI 键功能
# buffer[8] = 0  # 保留位
# buffer[9] = 0x1B  # "X"
# 4字节 按下松开键盘功能
# buffer[12] = 1  # report-id
# buffer[13] = 0  # Control Shift Alt GUI 键功能
# buffer[14] = 0  # 保留位
# buffer[15] = 0  # 功能位
```

### 多媒体键

```
# 多媒体键
# buffer[1] = 1  # 写入
# buffer[2] = 2  # 单元ID 0=功能 1=led 2=按键1 3=按键2 4=按键3
# buffer[3] = 0  # 保留位
# buffer[4] = 2  # 按键功能 1=标准按键 2=多媒体键
# buffer[5] = 3  # report所占长度
# 3字节 按下键盘功能report
# buffer[6] = 1  # report-id
# buffer[7] = 0  # 功能位 低位
# buffer[8] = 0  # 功能位 高位
# 3字节 按下松开键盘功能
# buffer[9] = 1  # report-id
# buffer[10] = 0  # 功能位 低位
# buffer[11] = 0  # 功能位 高位
```

###  触摸模式

```
# 触摸模式
# buffer[1] = 1  # 写入
# buffer[2] = 2  # 单元ID 0=功能 1=led 2=按键1 3=按键2 4=按键3
# buffer[3] = 0  # 保留位
# buffer[4] = 4  # 按键功能 1=标准按键 2=多媒体键 3=鼠标模式 4=触摸按键
# buffer[5] = 8  # report所占长度
# 8字节 触摸A点
# buffer[6] = 5  # report-id
# buffer[7] = 0x83  # 功能位 0x83=触摸按下 0x82=触摸松开
# buffer[8] = 0   # x坐标的低八位
# buffer[9] = 0   # x坐标的高八位
# buffer[10] = 0  # y坐标的低八位
# buffer[11] = 0  # y坐标的高八位
# buffer[12] = 1  # 间隔时间 单位10ms
# buffer[13] = 0  # 子功能标记
# 8字节 触摸B点
# buffer[14] = 5  # report-id
# buffer[15] = 0x82  # 功能位 0x83=触摸按下 0x82=触摸松开
# buffer[16] = 0  # x坐标的低八位
# buffer[17] = 0  # x坐标的高八位
# buffer[18] = 0  # y坐标的低八位
# buffer[19] = 0  # y坐标的高八位
# buffer[20] = 0  # 间隔时间 单位10ms 可选
# buffer[21] = 0  # 子功能标记 可选
```

### 触摸画圈

```
# 触摸画圈
# buffer[1] = 1  # 写入
# buffer[2] = 2  # 单元ID 0=功能 1=led 2=按键1 3=按键2 4=按键3
# buffer[3] = 0  # 保留位
# buffer[4] = 4  # 按键功能 1=标准按键 2=多媒体键 3=鼠标模式 4=触摸按键
# buffer[5] = 8  # report所占长度
# 8字节 按下触摸功能
# buffer[6] = 5  # report-id
# buffer[7] = 6  # 功能位 多边形边数 n
# buffer[8] = 40  # 功能位 边到中心点距离 r
# buffer[9] = 0  # x坐标的高八位(保留)
# buffer[10] = 0  # y坐标的低八位(保留)
# buffer[11] = 0  # y坐标的高八位(保留)
# buffer[12] = 10  # 单圈完成时间 单位10ms
# buffer[13] = 5  # 子功能标记 画圈
# 8字节 松开触摸功能 （可选）
# buffer[14] = 5  # report-id
# buffer[15] = 0x82  # 功能位 画圈大小 1 2 3
# buffer[16] = 0  # x坐标的低八位(保留)
# buffer[17] = 0  # x坐标的高八位(保留)
# buffer[18] = 0  # y坐标的低八位(保留)
# buffer[19] = 0  # y坐标的高八位(保留)
# buffer[20] = 0  # 间隔时间 单位10ms
# buffer[21] = 5  # 子功能标记 画圈
```

### 模拟鼠标

```
# 鼠标
# buffer[1] = 1  # 写入
# buffer[2] = 2  # 单元ID 0=功能 1=led 2=按键1 3=按键2 4=按键3
# buffer[3] = 0  # 保留位
# buffer[4] = 3  # 按键功能 1=标准按键 2=多媒体键 3=鼠标模式 4=触摸按键
# buffer[5] = 5  # report所占长度
# 5字节 鼠标report
# buffer[6] = 3  # report-id
# buffer[7] = 6  # 按键
# buffer[8] = 40  # X坐标变化量
# buffer[9] = 0   # Y坐标变化量
# buffer[10] = 0  # 滚轮变化
# 5字节 鼠标report 松开按键
# buffer[11] = 3  # report-id
# buffer[12] = 0  # 按键
# buffer[13] = 0  # X坐标变化量
# buffer[14] = 0  # Y坐标变化量
# buffer[15] = 0  # 滚轮变化
```

### 模拟dial

```
# 模拟dial
# buffer[1] = 1  # 写入
# buffer[2] = 2  # 单元ID 0=功能 1=led 2=按键1 3=按键2 4=按键3
# buffer[3] = 0  # 保留位
# buffer[4] = 5  # 按键功能 1=标准按键 2=多媒体键 3=鼠标模式 4=触摸按键 5=dial
# buffer[5] = 3  # report所占长度
# 3字节 按下键盘功能report
# buffer[6] = 6  # report-id
# buffer[7] = 0  # 功能位 低位
# buffer[8] = 0  # 功能位 高位
# buffer[9] = 151  # 滚动格数/长按 250 -> 25滚动格数/0启用或关闭长按
# buffer[10] = 0  # 滚动间隔 单位1ms
# 3字节 按下松开键盘功能
# buffer[11] = 6  # report-id
# buffer[12] = 0  # 功能位 低位
# buffer[13] = 0  # 功能位 高位
# buffer[14] = 0  # 功能位 低位
# buffer[15] = 0  # 功能位 高位
```

