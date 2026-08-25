import re
import networkx as nx
from .code_parser import EXTENSIONS, SKIP_DIRS

IMPORT_RE = re.compile(r'''(?:import\s+(?:[^'"]+\s+from\s+)?|from\s+|require\(\s*|import\(\s*)['"]([^'"]+)['"]''')

class DependencyAnalyzer:
    def build_graph(self, root):
        graph = nx.DiGraph()
        files = [p for p in root.rglob("*") if p.is_file() and not any(x in SKIP_DIRS for x in p.parts) and p.suffix.lower() in EXTENSIONS]
        module_map = {self.module_name(root, p): p for p in files}
        for path in files:
            source = self.module_name(root, path)
            graph.add_node(source)
            text = path.read_text(encoding="utf-8", errors="ignore")
            for target in IMPORT_RE.findall(text):
                local = self.resolve(root, path, target, module_map)
                if local:
                    graph.add_edge(source, local)
        return graph

    def module_name(self, root, path):
        return str(path.relative_to(root).with_suffix(""))

    def resolve(self, root, source, target, module_map):
        if target.startswith("."):
            base = source.parent
            dots = len(target) - len(target.lstrip("."))
            target = target[dots:]
            for _ in range(max(dots - 1, 0)):
                base = base.parent
            candidate = (base / target).resolve()
        elif target.startswith("@/") or target.startswith("~/"):
            candidate = (root / target[2:]).resolve()
        else:
            candidate = (root / target).resolve()
        candidates = [candidate]
        candidates += [candidate.with_suffix(ext) for ext in EXTENSIONS]
        candidates += [candidate / f"index{ext}" for ext in EXTENSIONS]
        for item in candidates:
            try:
                name = self.module_name(root, item)
            except ValueError:
                continue
            if name in module_map:
                return name
        return None

    def cycle_count(self, graph):
        return sum(1 for _ in nx.simple_cycles(graph))
