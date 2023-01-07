import pkgutil
from typing import Any, Dict, List

from genutility.string import backslashquote_unescape, build_multiple_replace
from parsimonious.grammar import Grammar
from parsimonious.nodes import Node, NodeVisitor

_unescape = build_multiple_replace(
    {
        "\\\\": "\\",
        "\\(": "(",
        "\\)": ")",
        "\\:": ":",
        "\\<": "<",
        "\\>": ">",
        '\\"': '"',
        "\\*": "*",
        "\\{": "{",
        "\\}": "}",
    }
)


def unescape(s: str) -> str:
    return _unescape(s)


class Visitor(NodeVisitor):
    passthrough = (str, tuple, dict)

    def _parse_op(self, node: Node, visited_children: List[Any], op: str):
        assert len(visited_children) == 1, visited_children

        if isinstance(visited_children[0], self.passthrough):
            return visited_children[0]
        elif isinstance(visited_children[0], list):
            num_children = len(visited_children[0])
            if num_children == 1:
                return visited_children[0][0]
            elif num_children == 2:
                if isinstance(visited_children[0][1], self.passthrough):
                    right = visited_children[0][1]
                elif isinstance(visited_children[0][1], list):
                    right = {"op": op, "exprs": visited_children[0][1]}
                else:
                    assert False, visited_children[0]
                return {"op": op, "left": visited_children[0][0], "right": right}
            else:
                assert False, visited_children[0]
        else:
            assert False, visited_children[0]

    def _parse_not(self, node: Node, visited_children: List[Any]):
        assert len(visited_children) == 1, visited_children

        if isinstance(visited_children[0], self.passthrough):
            if node.text.lower().startswith("not "):
                return {"op": "not", "expr": visited_children[0]}
            else:
                return visited_children[0]
        else:
            assert False, visited_children[0]

    def visit_start(self, node: Node, visited_children: List[Any]):
        assert len(visited_children) == 3, visited_children

        return visited_children[1]

    def visit_OrQuery(self, node: Node, visited_children: List[Any]):
        return self._parse_op(node, visited_children, "or")

    def visit_AndQuery(self, node: Node, visited_children: List[Any]):
        return self._parse_op(node, visited_children, "and")

    def visit_NotQuery(self, node: Node, visited_children: List[Any]):
        return self._parse_not(node, visited_children)

    def visit_SubQuery(self, node: Node, visited_children: List[Any]):
        assert len(visited_children) == 1, visited_children

        return visited_children[0]

    def visit_NestedQuery(self, node: Node, visited_children: List[Any]):
        assert len(visited_children) == 1, visited_children

        if isinstance(visited_children[0], self.passthrough):
            return visited_children[0]
        elif isinstance(visited_children[0], list):
            num_children = len(visited_children[0])
            if num_children == 1:
                return visited_children[0][0]
            elif num_children == 2:
                return {"field": visited_children[0][0], "value": visited_children[0][1]}
            else:
                assert False, visited_children[0]
        else:
            assert False, visited_children[0]

    def visit_Expression(self, node: Node, visited_children: List[Any]):
        assert len(visited_children) == 1, visited_children
        assert isinstance(visited_children[0], dict), visited_children[0]

        return visited_children[0]

    def visit_Field(self, node: Node, visited_children: List[Any]):
        assert len(visited_children) == 1, visited_children

        if isinstance(visited_children[0], str):
            return visited_children[0]
        elif isinstance(visited_children[0], tuple):
            assert len(visited_children[0]) == 1, visited_children[0]
            return visited_children[0][0]
        else:
            assert False, visited_children[0]

    def visit_FieldRangeExpression(self, node: Node, visited_children: List[Any]):
        assert len(visited_children) == 5, visited_children

        return {"field": visited_children[0], "op": visited_children[2], "value": visited_children[4]}

    def visit_FieldValueExpression(self, node: Node, visited_children: List[Any]):
        assert len(visited_children) == 5, visited_children

        return {"field": visited_children[0], "value": visited_children[4]}

    def visit_ValueExpression(self, node: Node, visited_children: List[Any]):
        assert len(visited_children) == 1, visited_children
        assert isinstance(visited_children[0], (str, tuple)), visited_children[0]

        return {"value": visited_children[0]}

    def visit_ListOfValues(self, node: Node, visited_children: List[Any]):
        assert len(visited_children) == 1, visited_children

        return visited_children[0]

    def visit_OrListOfValues(self, node: Node, visited_children: List[Any]):
        return self._parse_op(node, visited_children, "or")

    def visit_AndListOfValues(self, node: Node, visited_children: List[Any]):
        return self._parse_op(node, visited_children, "and")

    def visit_NotListOfValues(self, node: Node, visited_children: List[Any]):
        return self._parse_not(node, visited_children)

    def visit_Value(self, node: Node, visited_children: List[Any]):
        assert len(visited_children) == 1, visited_children

        return visited_children[0]

    def visit_Or(self, node: Node, visited_children: List[Any]):
        return None

    def visit_And(self, node: Node, visited_children: List[Any]):
        return None

    def visit_Not(self, node: Node, visited_children: List[Any]):
        return None

    def visit_Literal(self, node: Node, visited_children: List[Any]):
        assert len(visited_children) == 1, visited_children

        return visited_children[0]

    def visit_QuotedString(self, node: Node, visited_children: List[Any]):
        return backslashquote_unescape(node.text.strip()[1:-1])

    def visit_QuotedCharacter(self, node: Node, visited_children: List[Any]):
        return None

    def visit_UnquotedLiteral(self, node: Node, visited_children: List[Any]):
        return tuple(unescape(node.text.strip()).split())

    def visit_UnquotedCharacter(self, node: Node, visited_children: List[Any]):
        return None

    def visit_Wildcard(self, node: Node, visited_children: List[Any]):
        return None

    def visit_OptionalSpace(self, node: Node, visited_children: List[Any]):
        return None

    def visit_EscapedWhitespace(self, node: Node, visited_children: List[Any]):
        return None

    def visit_EscapedSpecialCharacter(self, node: Node, visited_children: List[Any]):
        return None

    def visit_EscapedKeyword(self, node: Node, visited_children: List[Any]):
        return None

    def visit_Keyword(self, node: Node, visited_children: List[Any]):
        return None

    def visit_SpecialCharacter(self, node: Node, visited_children: List[Any]):
        return None

    def visit_EscapedUnicodeSequence(self, node: Node, visited_children: List[Any]):
        return None

    def visit_UnicodeSequence(self, node: Node, visited_children: List[Any]):
        return None

    def visit_HexDigit(self, node: Node, visited_children: List[Any]):
        return None

    def visit_RangeOperator(self, node: Node, visited_children: List[Any]):
        return node.text

    def visit_Space(self, node: Node, visited_children: List[Any]):
        return None

    def generic_visit(self, node: Node, visited_children: List[Any]):
        """The generic visit method."""

        if node.expr_name:
            assert False, node.expr_name

        ret = [child for child in visited_children if child]
        if len(ret) == 1:
            return ret[0]
        else:
            return ret


class KqlParser:
    def __init__(self) -> None:
        data = pkgutil.get_data(__name__, "kql.parsimonious")
        assert data is not None
        self.grammar = Grammar(data.decode("utf-8"))
        self.visitor = Visitor()

    def parse(self, text: str) -> Node:
        return self.grammar.parse(text)

    def ast(self, node: Node) -> Dict[str, Any]:
        return self.visitor.visit(node)
