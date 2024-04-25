from groq import Groq


import os
from os.path import join, dirname
from dotenv import load_dotenv
import pandas as pd
from utils import inference_logger

input_sql_mapping_filename = '20240402_CUSTOMER360_CI_DIFA_LOG_AND_CGY(EDIT).xlsx'
input_sql_mapping_filepath = join(dirname(__file__), input_sql_mapping_filename)
inference_logger.info(f"loading mapping data from {input_sql_mapping_filename}")
df = pd.read_excel(input_sql_mapping_filepath, sheet_name='CI_SMY_DAILY_APP')

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

model_name = "llama3-70b-8192"
inference_logger.info(f'Setup {model_name} from groq')
GROQ_API_KEY = os.environ.get('GROQ_API_KEY')

client = Groq(
    api_key=GROQ_API_KEY,
)


def check_none(value):
  if value == None:
    return True
  if value.strip() == '':
    return True
  return False


def check_none_entry(entry):
  key_cols = ['Phân vùng', 'Target Field', 'Source Table', 'Source Field', 'Mapping Rule']
  for key in key_cols:
    if check_none(entry[key]):
      return True
  return False 


def extract_fields(text):
  fields = text.split('\n')
  return '\n'.join([f"- '{field.strip()}'" for field in fields])



import json

selected_df = df[['Phân vùng', 'Target Field', 'Source Table', 'Source Field', 'Mapping Rule', 'NOTE']][3:]
# Convert the selected DataFrame to a JSON string
json_data = selected_df.to_json(orient='records')

# Convert the JSON string to a Python dictionary
data_dict = json.loads(json_data)

refined_data_dict = [entry for entry in data_dict if not check_none_entry(entry) and entry['Mapping Rule'] != 'MAP 1-1']


REFINED_SQL_TEST_CASE_GENERATION_PROMPT = """
The source table is created using the following SQL query:
```sql
{source_table_sql}
```
The source fields are:
{source_field}

The target field is:
{target_field}

The mapping rule to create the target field 'SERVICE' from the source fields 'SERVICE' and 'TRANS_TYPE' is:
```sql
{mapping_rule}
```

Could you design sql test cases to validate this mapping process? The final output MUST BE in this format:
Test case n
'description': describe the test case and expected output,
'sql': the sql for testing,

"""

def create_prompt(entry):
  return REFINED_SQL_TEST_CASE_GENERATION_PROMPT.format(
      source_table_sql = entry['Source Table'],
      source_field = extract_fields(entry['Source Field']),
      target_field = extract_fields(entry['Target Field']),
      mapping_rule = entry['Mapping Rule']
  )



def generate_test_case(prompt, stream=False):
    completion = client.chat.completions.create(
        model=model_name,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0,
        max_tokens=1024,
        stream=stream,
        stop=None,
    )
    inference_logger.info(completion.choices[0].message.content)


for i in range(len(refined_data_dict))[0:1]:
    generate_test_case(create_prompt(refined_data_dict[i]))