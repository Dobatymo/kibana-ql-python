from unittest import TestCase

from parsimonious.nodes import Node

from kibana_ql import KqlParser

tests = [
    "asd: qwe",
    "http.request.method: *",
    "http.request.method: GET",
    "Hello",
    '(a: "b" AND c: "d") OR (e: "f" AND g: "h")',
    'a: "b" AND e: "f" AND g: "h"',
    '(a: "b" AND (e: "f" AND g: "h"))',
    "http.request.body.content: null pointer",
    'http.request.body.content: "null pointer"',
    'http.request.body.content: "null pointer" and *',
    'http.request.referrer: "https://example.com"',
    r"http.request.referrer: https\://example.com",
    "http.response.bytes < 10000",
    "http.response.bytes > 10000 and http.response.bytes <= 20000",
    "@timestamp < now-2w",
    "http.response.status_code: 4*",
    "NOT http.request.method: GET",
    "http.request.method: GET OR http.response.status_code: 400",
    "http.request.method: GET AND http.response.status_code: 400",
    "(http.request.method: GET AND http.response.status_code: 200) OR (http.request.method: POST AND http.response.status_code: 400)",
    "http.request.method: (GET OR POST OR DELETE)",
    "http.response.*: error",
    'user:{ first: "Alice" and last: "White" }',
    'user.names:{ first: "Alice" and last: "White" }',
]


class KqlTest(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.kql = KqlParser()

    def test_parse(self):
        for test in tests:
            with self.subTest(test=test):
                result = self.kql.parse(test)
                self.assertIsInstance(result, Node)


if __name__ == "__main__":
    import unittest

    unittest.main()
