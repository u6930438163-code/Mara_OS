"""Syntax-only Python compilation for the browser editor.

Never executes submitted code. Privileged execution remains local CLI only.
"""
import ast

MAX_SOURCE = 100_000

def check_source(source):
    if not isinstance(source, str) or not 1 <= len(source.encode("utf-8")) <= MAX_SOURCE:
        raise ValueError("Source must be 1..100000 UTF-8 bytes")
    try:
        tree = ast.parse(source, filename="<mara-editor>", mode="exec")
        compile(tree, "<mara-editor>", "exec")
    except SyntaxError as exc:
        return {"ok": False, "line": exc.lineno, "column": exc.offset,
                "error": exc.msg, "state": "syntax_error"}
    return {"ok": True, "state": "compiled", "statements": len(tree.body)}
