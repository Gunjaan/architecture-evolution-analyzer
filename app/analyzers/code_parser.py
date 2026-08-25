from collections import Counter
from collections.abc import Iterator
from pathlib import Path

import tree_sitter_java
import tree_sitter_javascript
import tree_sitter_kotlin
import tree_sitter_python
import tree_sitter_typescript
from tree_sitter import Language, Node, Parser

from app.models import FileMetrics

SKIP_DIRS = {
    ".git",
    ".venv",
    "venv",
    "node_modules",
    "__pycache__",
    ".next",
    "dist",
    "build",
    "coverage",
    ".gradle",
}


EXTENSIONS = {
    ".py": "python",
    ".js": "javascript",
    ".jsx": "javascript",
    ".ts": "typescript",
    ".tsx": "tsx",
    ".java": "java",
    ".kt": "kotlin",
    ".kts": "kotlin",
}


class CodeParser:
    def __init__(self) -> None:

        self.languages = {
            "python": Language(tree_sitter_python.language()),
            "javascript": Language(tree_sitter_javascript.language()),
            "typescript": Language(tree_sitter_typescript.language_typescript()),
            "tsx": Language(tree_sitter_typescript.language_tsx()),
            "java": Language(tree_sitter_java.language()),
            "kotlin": Language(tree_sitter_kotlin.language()),
        }

    def analyze_file(self, path: Path, root: Path) -> FileMetrics:

        language = EXTENSIONS[path.suffix.lower()]

        source = path.read_bytes()

        parser = Parser(self.languages[language])

        tree = parser.parse(source)

        function_nodes = {
            "function_definition",
            "function_declaration",
            "method_definition",
            "arrow_function",
            "function_expression",
            "constructor_declaration",
            "function",
            "secondary_constructor",
        }

        class_nodes = {
            "class_definition",
            "class_declaration",
            "interface_declaration",
            "enum_declaration",
            "object_declaration",
        }

        import_nodes = {
            "import_statement",
            "import_declaration",
        }

        branch_nodes = {
            "if_statement",
            "for_statement",
            "for_in_statement",
            "while_statement",
            "try_statement",
            "switch_statement",
            "when_expression",
            "conditional_expression",
            "catch_clause",
        }

        counts: Counter[str] = Counter()

        for node in self._walk(tree.root_node):
            if node.type in function_nodes:
                counts["functions"] += 1

            if node.type in class_nodes:
                counts["classes"] += 1

            if node.type in import_nodes:
                counts["imports"] += 1

            if node.type in branch_nodes:
                counts["branches"] += 1

        text = source.decode("utf-8", errors="ignore")

        return FileMetrics(
            path=str(path.relative_to(root)),
            language=language,
            lines=len(text.splitlines()),
            functions=counts["functions"],
            classes=counts["classes"],
            imports=counts["imports"],
            branches=counts["branches"],
            max_nesting=self._max_depth(tree.root_node, branch_nodes),
        )

    def analyze_repo(self, root: Path) -> tuple[list[FileMetrics], dict[str, int]]:

        results = []

        unsupported: Counter[str] = Counter()

        for path in root.rglob("*"):
            if not path.is_file():
                continue

            if any(part in SKIP_DIRS for part in path.parts):
                continue

            suffix = path.suffix.lower()

            if suffix not in EXTENSIONS:
                if suffix:
                    unsupported[suffix] += 1

                continue

            try:
                results.append(self.analyze_file(path, root))

            except Exception as exc:
                print(f"Could not parse {path}: {exc}")

        return (results, dict(unsupported))

    def _walk(self, node: Node) -> Iterator[Node]:

        yield node

        for child in node.children:
            yield from self._walk(child)

    def _max_depth(self, root: Node, branch_nodes: set[str]) -> int:

        maximum = 0

        def visit(node: Node, depth: int) -> None:

            nonlocal maximum

            if node.type in branch_nodes:
                depth += 1

                maximum = max(maximum, depth)

            for child in node.children:
                visit(child, depth)

        visit(root, 0)

        return maximum
