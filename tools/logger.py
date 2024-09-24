import logging
from logging.handlers import RotatingFileHandler

class LogManager:
    def __init__(self, name="logger", debug_path='log/debug.log', error_path='log/error.log'):
        self.error_messages_logged = {}
        self.debug_messages_logged = {}
        self.log_debug_filename = debug_path
        self.log_error_filename = error_path
        self.logger = logging.getLogger(name)
        if not self.logger.handlers:  # 检查是否已经存在处理器
            self.setup_logging()

    def setup_logging(self):
        self.logger.setLevel(logging.DEBUG)  # 确保日志级别为 DEBUG

        # 创建控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)

        # 创建调试日志处理器，使用 RotatingFileHandler
        debug_handler = RotatingFileHandler(
            self.log_debug_filename, maxBytes=10 * 1024 * 1024, backupCount=5, encoding='utf-8')
        debug_handler.setLevel(logging.DEBUG)

        # 创建错误日志处理器，使用 RotatingFileHandler
        error_handler = RotatingFileHandler(
            self.log_error_filename, maxBytes=10 * 1024 * 1024, backupCount=5, encoding='utf-8')
        error_handler.setLevel(logging.ERROR)

        # 设置日志格式
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(formatter)
        debug_handler.setFormatter(formatter)
        error_handler.setFormatter(formatter)

        # 添加处理器到 logger
        self.logger.addHandler(console_handler)
        self.logger.addHandler(debug_handler)
        self.logger.addHandler(error_handler)


    def log_error_once(self, message):
        """
        记录一条错误消息，如果这条消息之前没有被记录过。
        """
        if message not in self.error_messages_logged:
            self.logger.error(message)  # 使用特定 logger 记录错误
            self.error_messages_logged[message] = True

    def clear_error_message(self, message):
        """
        清除已记录的错误消息，允许这条消息在未来被重新记录。
        """
        if message in self.error_messages_logged:
            del self.error_messages_logged[message]

    def log_debug_once(self, message):
        """
        记录一条调试消息，如果这条消息之前没有被记录过。
        """
        if message not in self.debug_messages_logged:
            self.logger.debug(message)  # 使用特定 logger 记录调试信息
            self.debug_messages_logged[message] = True

    def clear_debug_message(self, message):
        """
        清除已记录的调试消息，允许这条消息在未来被重新记录。
        """
        if message in self.debug_messages_logged:
            del self.debug_messages_logged[message]

    def info(self, message, *args, **kwargs):
        """
        记录一条信息消息
        """
        self.logger.info(message, *args, **kwargs)  # 使用特定 logger

    def error(self, message, *args, **kwargs):
        """
        记录一条错误消息
        """
        self.logger.error(message, *args, **kwargs)  # 使用特定 logger

    def debug(self, message, *args, **kwargs):
        """
        记录一条调试消息
        """
        self.logger.debug(message, *args, **kwargs)  # 使用特定 logger

    def warn(self, message, *args, **kwargs):
        """
        记录一条警告消息
        """
        self.logger.warning(message, *args, **kwargs)  # 使用特定 logger
