# 新·阴阳师 挂机助手

## 目的

- 用opencv进行简单的模板匹配，起到对游戏场景进行识别的功能，并根据策略进行控制



## 模板

### 生成

- 用截取到的截图手动截取出模板图片，截图保存路径: [static/images/cap/screenshot.png](static/images/cap/screenshot.png)
- 用[img2json.py](tools-box/img2json.py)将模板保存为json文件，并将目标匹配区域的左上角坐标也保存进去

### 使用

- 读取json文件，根据所需位置，截取待匹配图片
- 匹配模板

## 未实现

- 鼠标控制与输入
- 游戏状态更新 -> 施工中
- 策略构建与解析系统
- UI


## 项目结构

```
├── application/
│   ├── app.py
│   ├── app_state.py
│   ├── detector.py
│   ├── Readme.md
│   ├── scene_context.py
│   └── scenes/
│       ├── base.py
│       ├── battle.py
│       ├── explore.py
│       ├── index.py
│       ├── index2.py
│       ├── login.py
│       ├── scene_registry.py
│       └── unknown.py
├── conf/
│   └── config.json
├── log/
│   ├── debug.log
│   └── error.log
├── main.py
├── Readme.md
├── static/
│   ├── data/
│   │   ├── template/
│   │   │   ├── json files...
│   │   └── template.json
│   └── images/
│       ├── cap/
│       │   ├── cap image files...
│       └── template/
│           ├── template image files...
├── tools/
│   ├── admin.py
│   ├── config_loader.py
│   ├── grabscreen.py
│   ├── image_processing.py
│   ├── key_listener.py
│   ├── logger.py
│   └── window.py
└── tools-box/
    ├── img.ico
    ├── img2json.py
    └── test.py
```