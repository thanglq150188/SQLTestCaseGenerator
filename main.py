from langchain_fireworks import ChatFireworks
from langchain_core.messages import HumanMessage, SystemMessage

import os
from os.path import join, dirname
from dotenv import load_dotenv

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

FIREWORKS_API_KEY = os.environ.get('FIREWORKS_API_KEY')