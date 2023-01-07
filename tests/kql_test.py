from unittest import TestCase

from parsimonious.nodes import Node

from kibana_ql import KqlParser

tests = [
    ("A", {"value": ("A",)}),
    ('"A"', {"value": "A"}),
    ('"A:B"', {"value": "A:B"}),
    ("A\\:B", {"value": ("A:B",)}),
    ("A or B", {"left": {"value": ("A",)}, "op": "or", "right": {"value": ("B",)}}),
    ("A and B", {"left": {"value": ("A",)}, "op": "and", "right": {"value": ("B",)}}),
    (
        "A or B or C",
        {"left": {"value": ("A",)}, "op": "or", "right": {"exprs": [{"value": ("B",)}, {"value": ("C",)}], "op": "or"}},
    ),
    (
        "A and B and C",
        {
            "left": {"value": ("A",)},
            "op": "and",
            "right": {"exprs": [{"value": ("B",)}, {"value": ("C",)}], "op": "and"},
        },
    ),
    (
        "A or B and C",
        {
            "left": {"value": ("A",)},
            "op": "or",
            "right": {"left": {"value": ("B",)}, "op": "and", "right": {"value": ("C",)}},
        },
    ),
    (
        "A and B or C",
        {
            "left": {"left": {"value": ("A",)}, "op": "and", "right": {"value": ("B",)}},
            "op": "or",
            "right": {"value": ("C",)},
        },
    ),
    ("A: B", {"field": "A", "value": ("B",)}),
    ('A: "B:C"', {"field": "A", "value": "B:C"}),
    ("A: B\\:C", {"field": "A", "value": ("B:C",)}),
    ("A: B C", {"field": "A", "value": ("B", "C")}),
    ('A: "B C"', {"field": "A", "value": "B C"}),
    ("  A  :  B  ", {"field": "A", "value": ("B",)}),
    ("A or B: C", {"left": {"value": ("A",)}, "op": "or", "right": {"field": "B", "value": ("C",)}}),
    ("A: B or C: D", {"left": {"field": "A", "value": ("B",)}, "op": "or", "right": {"field": "C", "value": ("D",)}}),
    ("A: B and C: D", {"left": {"field": "A", "value": ("B",)}, "op": "and", "right": {"field": "C", "value": ("D",)}}),
    (
        "A: B or C: D or E: F",
        {
            "left": {"field": "A", "value": ("B",)},
            "op": "or",
            "right": {"exprs": [{"field": "C", "value": ("D",)}, {"field": "E", "value": ("F",)}], "op": "or"},
        },
    ),
    (
        "A: B and C: D and E: F",
        {
            "left": {"field": "A", "value": ("B",)},
            "op": "and",
            "right": {"exprs": [{"field": "C", "value": ("D",)}, {"field": "E", "value": ("F",)}], "op": "and"},
        },
    ),
    (
        "A: B or C: D and E: F",
        {
            "left": {"field": "A", "value": ("B",)},
            "op": "or",
            "right": {"left": {"field": "C", "value": ("D",)}, "op": "and", "right": {"field": "E", "value": ("F",)}},
        },
    ),
    (
        "A: B and C: D or E: F",
        {
            "left": {"left": {"field": "A", "value": ("B",)}, "op": "and", "right": {"field": "C", "value": ("D",)}},
            "op": "or",
            "right": {"field": "E", "value": ("F",)},
        },
    ),
    (
        "A: B and (C: D and E: F)",
        {
            "left": {"field": "A", "value": ("B",)},
            "op": "and",
            "right": {"left": {"field": "C", "value": ("D",)}, "op": "and", "right": {"field": "E", "value": ("F",)}},
        },
    ),
    (
        "(A: B and C: D) and E: F",
        {
            "left": {"left": {"field": "A", "value": ("B",)}, "op": "and", "right": {"field": "C", "value": ("D",)}},
            "op": "and",
            "right": {"field": "E", "value": ("F",)},
        },
    ),
    ("A < B", {"field": "A", "op": "<", "value": ("B",)}),
    (
        "A.B > C.D and E <= F",
        {
            "left": {"field": "A.B", "op": ">", "value": ("C.D",)},
            "op": "and",
            "right": {"field": "E", "op": "<=", "value": ("F",)},
        },
    ),
    ("@A < B-C", {"field": "@A", "op": "<", "value": ("B-C",)}),
    ("NOT A", {"op": "not", "expr": {"value": ("A",)}}),
    ("NOT A: B", {"op": "not", "expr": {"field": "A", "value": ("B",)}}),
    (
        "A: (B OR C)",
        {
            "field": "A",
            "value": {"left": ("B",), "op": "or", "right": ("C",)},
        },
    ),
    (
        "A: (B OR C OR D)",
        {
            "field": "A",
            "value": {"left": ("B",), "op": "or", "right": {"exprs": [("C",), ("D",)], "op": "or"}},
        },
    ),
    (
        "A:{ B: C and D: E }",
        {
            "field": "A",
            "value": {
                "left": {"field": "B", "value": ("C",)},
                "op": "and",
                "right": {"field": "D", "value": ("E",)},
            },
        },
    ),
]


class KqlTest(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.kql = KqlParser()

    def test_parse(self):
        for test, truth in tests:
            with self.subTest(test=test):
                result = self.kql.parse(test)
                self.assertIsInstance(result, Node)
                ast = self.kql.ast(result)
                self.assertEqual(truth, ast)


if __name__ == "__main__":
    import unittest

    unittest.main()
