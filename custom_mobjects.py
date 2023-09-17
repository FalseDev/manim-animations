from manim import *
from manim.mobject.text.text_mobject import remove_invisible_chars


class Cell(VGroup):
    def __init__(self, index: int, text: Text, height, width):
        super().__init__()
        self.rect = Rectangle(height=height, width=width)
        self.text = text
        self.index = index
        text.move_to(self.rect.get_center())
        self.index_text = (
            Text(f"[{index}]", color=GREY)
            .scale(0.5)
            .move_to(
                self.rect.get_center()
                + [self.rect.width * 5 / 16, -self.rect.height * 5 / 16, 0]
            )
        )
        self.add(self.rect, self.text, self.index_text)


class Array(VGroup):
    def __init__(
        self,
        size: int,
        texts: list,
        box_height: float = 2.0,
        box_width: float = 4.0,
        vertical: bool = False,
    ):
        super().__init__()
        self.size = size
        self.box_height = box_height
        self.box_width = box_width
        self.texts = texts
        self.vertical = vertical

        self.objects: list[Cell] = []
        for i in range(self.size):
            rect = Cell(
                index=i,
                text=Text(str(texts[i])),
                height=self.box_height,
                width=self.box_width,
            )
            rect.shift(
                np.array(
                    [(not vertical) * self.box_width, vertical * -self.box_height, 0.0]
                )
                * (i - self.size / 2 + 0.5)
            )
            self.objects.append(rect)

        self.add(*self.objects)

    def lagged_creation(self):
        pass

    @override_animate(lagged_creation)
    def _lagged_creation_animation(
        self, *, anim_args=None, lag_ratio=0.05, run_time=1.5
    ):
        anims = []
        for obj in self.objects:
            # TODO: This has to be manually updated when new
            # attributes/Mobjects are added to the Array or Cells
            anims += (Create(obj.rect), Write(obj.text), Write(obj.index_text))

        if anim_args is None:
            anim_args = {}
        anim_args = {"lag_ratio": lag_ratio, "run_time": run_time, **anim_args}
        return LaggedStart(*anims, **anim_args)

    def shift_space(self):
        # Move half cell width distance to left or up to
        # make room for new cell and center array
        return self.animate.shift(
            ((not self.vertical) * LEFT * self.box_width / 2)
            + (self.vertical * UP * self.box_height / 2)
        )

    def append(self):
        text = ""
        c = Cell(self.size, Text(text), height=self.box_height, width=self.box_width)
        # Calculate which direction the next cell must be
        # attached to
        next_dir = (not self.vertical) * RIGHT + self.vertical * DOWN
        c.next_to(self, next_dir, buff=0)
        self.objects.append(c)
        self.texts.append(text)
        self.size += 1
        self.add(c)

        return Create(c)

    def shift_val(self, scene, from_index, to_index, *, create=False):
        self.texts[to_index] = self.texts[from_index]
        prev_text = self.objects[from_index].text
        changing_obj = self.objects[to_index]
        new_text = prev_text.copy().move_to(changing_obj.get_center())
        old_text = changing_obj.text
        changing_obj.text = new_text

        arrow_start = self.objects[from_index].get_center() - np.array(
            [
                self.vertical * self.box_width / 2,
                (not self.vertical) * self.box_height / 2,
                0,
            ]
        )
        arrow_end = arrow_start + np.array(
            [
                (not self.vertical) * self.box_width,
                self.vertical * -self.box_height,
                0,
            ]
            * (to_index - from_index)
        )
        arrow = CurvedArrow(arrow_start, arrow_end)
        scene.play(Create(arrow))

        if create:
            self.add(new_text)
            scene.play(FadeTransform(old_text, new_text))
        else:
            scene.play(ReplacementTransform(old_text, new_text))

        scene.play(Uncreate(arrow, run_time=0.2))

    def set_text(self, pos: int, text: str):
        self.texts[pos] = text
        changing_obj = self.objects[pos]
        new_text = Text(text).move_to(changing_obj.get_center())
        old_text = changing_obj.text
        changing_obj.text = new_text
        return ReplacementTransform(old_text, new_text)


class ChangingParagraph(VGroup):
    def __init__(self, text: str):
        super().__init__()
        self.text = [l + "\n" for l in text.splitlines()]
        self.para = Paragraph(*self.text)
        self.add(self.para)

    def update_text(self, text: str, scale: float = 1):
        self.text = [l + "\n" for l in text.splitlines()]
        old_para = self.para
        self.para = Paragraph(*self.text).move_to(old_para.get_center()).scale(scale)
        # self.add(self.para)
        return ReplacementTransform(old_para, self.para)


class CodeExec(VGroup):
    def __init__(self, filename: str = None, language: str = None, *, code: str = None):
        super().__init__()
        if code is None:
            if filename is None:
                raise Exception("One of filename and code must be given")
            with open(filename) as f:
                code = f.read()

        self.contents = code.splitlines()

        self.code = Code(
            code=code,
            language=language,
            background="window",
            line_spacing=1,
            style=Code.styles_list[15],
        )
        self.add(self.code)

        # Remove invisible characters
        self.code.code = remove_invisible_chars(self.code.code)

        self.sliding_windows = VGroup()
        for line in self.code.code:
            self.sliding_windows.add(
                SurroundingRectangle(line)
                .set_fill(YELLOW)
                .set_opacity(0)
                .stretch_to_fit_width(self.code.background_mobject.width)
                .align_to(self.code.background_mobject, LEFT)
            )
        self.add(self.sliding_windows)

        self.highlighted = None

    def highlight(self, index: int):
        if self.highlighted is not None:
            true_pos = self.sliding_windows[index].get_center()
            self.sliding_windows[index].move_to(
                self.sliding_windows[self.highlighted].get_center()
            )
            self.sliding_windows[index].set_opacity(0.3)
            self.sliding_windows[self.highlighted].set_opacity(0.0)
            anim = self.sliding_windows[index].animate.move_to(true_pos)

        else:
            anim = self.sliding_windows[index].animate.set_opacity(0.3)

        self.highlighted = index

        return anim

    def remove_highlight(self):
        if self.highlighted is not None:
            anims = [self.sliding_windows[self.highlighted].animate.set_opacity(0.0)]
            self.highlighted = None
            return anims

        return []

    def circumscribe(self, line_no, start, finish, **kwargs):
        line = self.contents[line_no]
        new_start = 0
        new_finish = 0
        for i, c in enumerate(line):
            if c.isspace():
                continue
            if start > i:
                new_start += 1
            if finish <= i:
                break
            new_finish += 1

        return Circumscribe(self.code.code[line_no][new_start:new_finish], **kwargs)


class CodeOutput(CodeExec):
    def __init__(
        self,
        filename: str = None,
        language: str = None,
        *,
        code: str = None,
        char_width=None,
    ):
        if code is None:
            if filename is None:
                raise Exception("One of filename and code must be given")
            with open(filename) as f:
                code = f.read()

        if char_width is not None:
            lines = code.splitlines()
            char_width = max([char_width - 2, *[len(l) for l in lines]]) + 2
            code = "\u23CE\n".join([l + (char_width - len(l)) * " " for l in lines])

        super().__init__(language=language, code=code)

        for line in self.code.code:
            line.set_opacity(0.0)

    def show_line(self, index: int):
        return LaggedStart(
            self.highlight(index),
            self.code.code[index].animate.set_opacity(1.0),
            lag_ratio=1,
            run_time=2,
        )
