from manim import *  # noqa: F403

from custom_mobjects import Array, ChangingParagraph, CodeExec, CodeOutput
from manim_utils import for_loop, from_range


class ArrayInsert(Scene):
    def construct(self):
        title_p1 = Paragraph(
            "Inserting an element into an",
            font="JetBrainsMono Nerd Font",
            weight="BOLD",
        ).shift(UP * 2)
        title_p2 = Text(
            "array at given position",
            font="JetBrainsMono Nerd Font",
            weight="BOLD",
        ).shift(UP)
        lang = Text(
            "Language: C",
            font="JetBrainsMono Nerd Font",
            weight="LIGHT",
            color=LIGHTER_GREY,
        ).next_to(title_p2, DOWN * 3)

        self.play(
            LaggedStart(
                Create(title_p1),
                Create(title_p2),
                Create(lang),
                lag_ratio=0.15,
                run_time=3,
            )
        )
        self.wait(2)
        self.play(
            LaggedStart(
                Uncreate(title_p1),
                Uncreate(title_p2),
                Uncreate(lang),
                lag_ratio=0.15,
                run_time=3,
            )
        )

        code = CodeExec(
            "./code/array_insert.c",
            language="c",
        )

        # Shift to left half of screen
        code.shift(np.array([-self.camera.frame_width / 4, 0, 0]))

        # Scale to fit within screen
        code.scale(0.8)

        self.play(Create(code, name="Create code executor", run_time=3))

        self.play(code.highlight(0))
        self.play(code.highlight(2))
        self.wait(1)
        self.play(code.highlight(3))

        size = 4
        arr = Array(
            size=size,
            texts=[str(i) for i in range(size)],
            box_height=1.25,
            box_width=2.0,
            vertical=True,
        )

        # Shift to right half of screen
        arr.shift(np.array([self.camera.frame_width * 3 / 8, 0, 0]))

        self.play(arr.animate.lagged_creation(run_time=1.5))

        self.play(code.highlight(4))

        pos = 1
        val = str(10)

        def vars_text(i):
            return f"n = {arr.size}\nval = {val}\npos = {pos}\ni = {i}"

        var_view = ChangingParagraph(vars_text(""))
        var_view.shift(np.array([self.camera.frame_width * 1 / 8, 0, 0]))
        self.play(Write(var_view))

        self.play(code.highlight(5))
        self.play(arr.shift_space())
        self.play(arr.append(), var_view.update_text(vars_text("")))
        self.wait(1)

        i_text = Text("i").next_to(arr.objects[-1], RIGHT, buff=0.5)

        update_vars = lambda i: var_view.update_text(vars_text(i))
        update_i = lambda i: i_text.animate.next_to(arr.objects[i], RIGHT, buff=0.5)

        @for_loop(
            self,
            code,
            (6, 8),
            **from_range(range(arr.size - 1, pos, -1)),
            post_init=[Create(i_text), update_vars],
            with_incr=[update_vars, update_i],
        )
        def shift_loop(i: int):
            self.wait(1)
            arr.shift_val(self, i - 1, i, create=i == arr.size - 1)
            self.wait(1)

        shift_loop()

        self.play(code.highlight(9))
        self.play(arr.set_text(pos, val), var_view.update_text(vars_text(pos)))

        self.wait(2)

        top = code.get_top()
        bottom = code.get_bottom()

        hor_array = (
            Array(
                size=arr.size,
                texts=arr.texts.copy(),
                box_height=arr.box_height,
                box_width=arr.box_width,
                vertical=False,
            )
            .scale(0.6)
            .to_edge(RIGHT)
            .set_y(top[1] - 0.5, UP)
        )

        self.play(
            ReplacementTransform(arr, hor_array),
            var_view.animate.scale(0.6).set_y(bottom[1] + 0.3, DOWN),
            i_text.animate.next_to(hor_array.objects[pos], DOWN, buff=0.3).scale(0.6),
        )

        output = (
            CodeOutput("./code-output/array_insert_output.txt", "c", char_width=6)
            .to_corner(DR)
            .set_y(bottom[1], DOWN)
        )
        self.play(Create(output, run_time=3))

        n = len(output.code.code)
        update_vars = lambda i: var_view.update_text(vars_text(i), 0.6)
        update_i = lambda i: i_text.animate.next_to(
            hor_array.objects[i - 1 * (i == n)],
            DOWN + RIGHT * (i == n),
            buff=0.3,
        )

        @for_loop(
            self,
            code,
            (11, 13),
            **from_range(range(n)),
            with_init=[update_vars, update_i],
            with_incr=[update_vars, update_i],
        )
        def output_loop(i: int):
            self.play(output.show_line(i))

        output_loop()

        self.play(code.highlight(14))
        self.wait(3)
