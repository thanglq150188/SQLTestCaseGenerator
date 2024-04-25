from langchain_fireworks import ChatFireworks
from langchain_core.messages import HumanMessage, SystemMessage

import os
from os.path import join, dirname
from dotenv import load_dotenv

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

FIREWORKS_API_KEY = os.environ.get('FIREWORKS_API_KEY')

fw_dbrx = ChatFireworks(
    model="accounts/fireworks/models/dbrx-instruct",
    temperature=0,
    max_tokens=1000,
    fireworks_api_key=FIREWORKS_API_KEY
)

human_message = HumanMessage(content="""Write a fucking horror story for me!!""")

for text in fw_dbrx.stream([human_message]):
  print(text.content, end='')