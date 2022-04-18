from manim import *

from script_parser import parse_file, Scope

class PythonVisializer(Scene):

    def prepare_code(self):
        self._code, self._scopes = parse_file('simple.py')
        self.scopes = []
        self._heap = []
        self._stack = []

        for scope in self._scopes:
            scope_code_text = f"-------------\nScope: {scope.scope_name}\nparent: {scope.parent.scope_name if scope.parent else None}"
            scope_vars_codes = []

            for iden in scope.identifiers.items():
                if isinstance(iden[0], tuple):
                    for i in iden[0]:
                        # scope_code += f"{i}\n\n"
                        scope_vars_codes.append(Code(code=f"{i}", language='Python', font_size=18, insert_line_no=False, background_stroke_width=0))
                else:
                    # scope_code += f"{iden[0]}\n\n"
                    scope_vars_codes.append(Code(code=f"{iden[0]}", language='Python', font_size=18, insert_line_no=False, background_stroke_width=0))

                heap_code = f"{iden[1] if not isinstance(iden[1], Scope) else 'func: ' + iden[1].scope_name}"

                self._heap.append(Code(code=f"{heap_code}", language='Python', font_size=18, insert_line_no=False, background_stroke_width=0))

                scope_vars_codes[-1].var_val = self._heap[-1]
                self._heap[-1].val_var = scope_vars_codes[-1]

            scope_code = Code(code=f'{scope_code_text}', background_stroke_width=0, language='Python', insert_line_no=False, font_size=18)

            for scope_var in scope_vars_codes:
                scope_var.move_to(scope_code.submobjects[-1].get_bottom()).shift(DOWN * 0.4)
                scope_code.add(scope_var)

            self.scopes.append(scope_code)

    def construct(self):
        self.prepare_code()
        self.connection_arrows = []

        self.rendered_code = Code(code=self._code, tab_width=4, background="window", language="Python", font="Monospace")

        # self.heap = Code(code='heap', language='Python', insert_line_no=False)
        self.heap = Rectangle()

        # self.heap.match_height(self.rendered_code)
        self.heap.stretch_to_fit_height(7)
        self.heap.stretch_to_fit_width(3.5)

        self.heap.to_edge(RIGHT)

        # self.stack = Code(code='stack', language='Python', insert_line_no=False)
        self.stack = Rectangle()

        # self.stack.match_height(self.rendered_code)
        self.stack.stretch_to_fit_height(7)
        self.stack.stretch_to_fit_width(3.5)

        self.stack.next_to(self.heap, LEFT)

        for scope in self.scopes:
            scope.move_to(self.stack.get_top()).shift(DOWN*1.5)
            self.stack.add(scope)

        for hp in self._heap:
            hp.move_to(self.heap.get_top()).shift(DOWN*1)
            self.heap.add(hp)

        for hp in self._heap:
            self.connection_arrows.append(Arrow(start=hp.val_var, end=hp))
        
        # self.stack.arrange_submobjects(direction=DOWN)
        self.stack.arrange(direction=DOWN, center=False)
        self.heap.arrange(direction=DOWN, center=False)

        self.rendered_code.to_edge(LEFT).shift(RIGHT*0.5)
        self.play(Create(self.rendered_code))
        self.play(Create(self.stack), Create(self.heap))

        self.wait(2)

        for arrow in self.connection_arrows:
            self.play(Create(arrow))

        self.wait(5)