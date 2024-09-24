import argparse
from application.app import Application
from tools.admin import useAdminRun

def main(config_path):
    app = Application(config_path)
    app.run()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="启动应用程序并指定配置文件")
    parser.add_argument('-c', '--config', type=str, default='conf/config.json', help='配置文件的路径')
    args = parser.parse_args()
    
    useAdminRun()  # 如果需要管理员权限，取消注释这一行
    
    main(args.config)
