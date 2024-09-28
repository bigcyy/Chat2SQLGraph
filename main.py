import logging
import sys
import os
import django
from django.core import management

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.join(BASE_DIR, 'backend')

# 改变当前工作目录到 BASE_DIR。后续的相对路径操作将以 BASE_DIR 为基准。
os.chdir(BASE_DIR)
# 将 BACKEND_DIR 插入到 Python 的系统路径的开头。
sys.path.insert(0, BACKEND_DIR)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project.settings")
django.setup()

def perform_db_migrate():
    """
    初始化数据库表
    """
    try:
        management.call_command('migrate')
    except Exception as e:
        logging.error('Perform migrate failed, exit', exc_info=True)
        sys.exit(11)

def dev():
    management.call_command('runserver')
        
if __name__ == "__main__":
    perform_db_migrate()
    dev()

