from pathlib import Path

from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser




def load_prompt(prompt_file_name: str) -> str:


    prompt_file_path = Path(__file__).resolve().parents[0] / 'jinja2' / f'{prompt_file_name}.jinja2'

    return prompt_file_path.read_text(encoding='utf-8')



if __name__ == "__main__":
    print(load_prompt('turn_plan'))


