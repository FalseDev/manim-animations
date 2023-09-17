from manim import *

from custom_mobjects import CodeExec


def for_loop_circumscribes(code: "CodeExec", line_no: int, *, run_time: float = 2):
    line = code.contents[line_no]
    index = len(line)
    line = line.lstrip().lstrip("for").lstrip().lstrip("(")
    index -= len(line)

    (init, cond, incr) = line[: line.rfind(")")].split(";")
    init_inds = (index + (len(init) - len(init.lstrip())), index + len(init))
    index = init_inds[1] + 1
    cond_inds = (index + (len(cond) - len(cond.lstrip())), index + len(cond))
    index = cond_inds[1] + 1
    incr_inds = (index + (len(incr) - len(incr.lstrip())), index + len(incr))

    kwargs = {"run_time": run_time, "fade_out": True}
    for_init = code.circumscribe(line_no, *init_inds, color=YELLOW, **kwargs)
    for_cond_true = code.circumscribe(line_no, *cond_inds, color=GREEN, **kwargs)
    for_cond_false = code.circumscribe(line_no, *cond_inds, color=RED, **kwargs)
    for_decr = code.circumscribe(
        line_no, *incr_inds, color=YELLOW, run_time=2, fade_out=True
    )

    return (for_init, for_cond_true, for_cond_false, for_decr)
