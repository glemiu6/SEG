from dataclasses import dataclass

@dataclass
class Page:
    text: str
    number: int


@dataclass
class Paragraph:
    id: str
    text: str
    pages: list[Page]
    section:str

@dataclass
class Section:
    title:str
    paragraphs:list[Paragraph]

@dataclass
class Paper:
    id:str
    title:str
    authors:list[str]
    pages:list[Page]
    sections:list[Section]