import pkgutil

from parsimonious.grammar import Grammar
from parsimonious.nodes import Node


class KqlParser:
    def __init__(self) -> None:
        data = pkgutil.get_data(__name__, "kql.parsimonious")
        assert data is not None
        self.grammar = Grammar(data.decode("utf-8"))

    def parse(self, text: str) -> Node:
        return self.grammar.parse(text)
