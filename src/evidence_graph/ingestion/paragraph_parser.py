import re

class ParagraphParser:

    def parse(self,text:str)->list[str]:
        ...

    def split_paragraph(self,text:str)->list[str]:
        return re.split(r"\n\s*\n",text)

    def clean_paragraph(self,text:str)->str:
        lines = text.splitlines()

        lines = [
            line.strip()
            for line in lines
            if line.strip()
        ]
        return " ".join(lines)