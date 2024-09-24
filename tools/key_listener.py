from pynput.keyboard import Key, Listener
from tools.logger import LogManager

class KeyListener:
    def __init__(self, interface):
        self.interface = interface
        self.logger = LogManager(name="key_listener")
        
    def on_press(self, key):
        """
        处理按键按下的事件
        """
        try:
            char = key.char.lower()
        except AttributeError:
            char = key
        try:
            if char == 'a':
                self.interface.decrease_index()
            elif char == 'd':
                self.interface.increase_index()
            elif char == 'j':
                self.interface.save_current_image()
            elif char == 's':
                self.interface.toggle_state()
            elif char == Key.esc:
                self.interface.stop()
                return False  # 停止监听
        except Exception as e:
            self.logger.error("按键处理错误: %s", e)

    def listener_start(self):
        """
        启动按键监听
        """
        with Listener(on_press=self.on_press) as listener:
            listener.join()
