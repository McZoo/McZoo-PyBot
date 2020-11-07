import os
from utils import source

yaml_path: str = os.path.join(os.getcwd(), 'config.yaml')
mirai = source.Mirai(yaml_path)
