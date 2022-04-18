import ast
import _ast

import astor

scopes: "list[Scope]" = []

def parse_file(filename: str, dump: bool = False) -> "tuple[str, list[Scope]]":
    """
    Parses a python file and returns the code and the scopes within it
    """
    global scopes
    code = ""
    with open(f'./{filename}', 'r') as s:
        code = s.read()

    tree = ast.parse(code)
    if dump:
        print(astor.dump_tree(tree))

    scopes.append(Scope("global", 0))
    Scope.global_scope = scopes[0]

    visitor = AnalyzerVisitor()
    visitor.visit(tree)

    if dump:
        for scope in scopes:
            print(scope)
            print(scope.childrens)
            print(scope.identifiers)
            print()

    return code, scopes

class AnalyzerVisitor(ast.NodeTransformer):

    def visit_Assign(self, node: _ast.Assign):
        if node.col_offset == 0:
            # Global Scope
            if isinstance(node.value, _ast.Constant):
                Scope.global_scope.add_identifier(tuple(targ.id for targ in node.targets), node.value.value)

            elif isinstance(node.value, (_ast.List, _ast.Tuple)):
                Scope.global_scope.add_identifier(tuple(targ.id for targ in node.targets), node.value.elts)

            else:
                Scope.global_scope.add_identifier(tuple(targ.id for targ in node.targets), node.value)
        else:
            scope = Scope.get_scope_by_col(node.col_offset)

            if isinstance(node.value, _ast.Constant):
                scope.add_identifier(tuple(targ.id for targ in node.targets), node.value.value)

            elif isinstance(node.value, (_ast.List, _ast.Tuple)):
                scope.add_identifier(tuple(targ.id for targ in node.targets), node.value.elts)

            else:
                scope.add_identifier(tuple(targ.id for targ in node.targets), node.value)

        self.generic_visit(node)

    def visit_FunctionDef(self, node: _ast.FunctionDef):

        if node.col_offset == 0:
            new_scope = Scope(node.name, 4, Scope.global_scope)
            scopes.append(new_scope)

            Scope.global_scope.childrens.append(new_scope)
            Scope.global_scope.add_identifier(node.name, new_scope)
        else:
            parent = Scope.get_scope_by_col(node.col_offset)
            new_scope = Scope(node.name, node.col_offset + 4, parent)
            scopes.append(new_scope)

            parent.childrens.append(new_scope)
            parent.add_identifier(node.name, new_scope)

        self.generic_visit(node)

    def visit_Constant(self, node: _ast.Constant):
        self.generic_visit(node)
        return node

class Scope:
    def __init__(self, scope_name: str, col_offset: int, parent: "Scope" = None):
        self.parent = parent
        self.scope_name = scope_name
        self.col_offset = col_offset
        self.childrens: "list[Scope]" = []

        self.identifiers = {}

    def __repr__(self) -> str:
        return f"<Scope: {self.scope_name} offset: {self.col_offset}>"# parent: {self.parent}>"

    @classmethod
    def get_scope_by_name(self, name: str) -> "Scope":
        matches = []

        for scope in scopes:
            if scope.scope_name == name: matches.append(scope)

        return matches[-1]

    @classmethod
    def get_scope_by_col(self, col: int) -> "Scope":
        matches = []
        # for scope in scopes.values():
        #     if isinstance(scope, list):
        #         for _scope in scope:
        #             if _scope.col_offset == col: matches.append(_scope)
        #     else:        
        #         if scope.col_offset == col: matches.append(scope)
        for scope in scopes:
            if scope.col_offset == col: matches.append(scope)

        return matches[-1]

    def add_identifier(self, name: str, val):
        self.identifiers[name] = val

if __name__ == "__main__":
    parse_file('script.py', True)