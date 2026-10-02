from dataclasses import dataclass


@dataclass
class TextSpan:
    text: str
    font: str
    size: float


@dataclass
class TextLine:
    bbox: tuple[float, float, float, float]
    spans: list[TextSpan]


@dataclass
class TextBox:
    bbox: tuple[float, float, float, float]
    lines: list[TextLine]


@dataclass
class Page:
    number: int
    blocks: list[TextBox]


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