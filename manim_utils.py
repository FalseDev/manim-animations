from typing import Callable, Generic, TypedDict, TypeVar

from manim import GREEN, RED, YELLOW, Animation, Scene
from manim.mobject.mobject import _AnimationBuilder

from custom_mobjects import CodeExec


def for_loop_circumscribes(code: "CodeExec", line_no: int, *, run_time: float = 2):
    line = code.contents[line_no]
    index = len(line)
    line = line.lstrip().lstrip("for").lstrip().lstrip("(")
    index -= len(line)

    init, cond, incr = line[: line.rfind(")")].split(";")
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


_T = TypeVar("_T")
_R = TypeVar("_R")
AnimType = Animation | _AnimationBuilder
ZeroPlusAnim = list[AnimType] | AnimType
AnimSrc = Callable[[_T], ZeroPlusAnim] | AnimType
Anim = list[AnimSrc[_T]] | AnimSrc[_T] | None


def play_anims(
    scene: Scene,
    elem: _T,
    extra_anims: Anim[_T] | None,
    *default_anims: Animation | _AnimationBuilder,
    delay: float = 1.0,
):
    all_anims: list[Animation | _AnimationBuilder] = [*default_anims]
    if extra_anims is None:
        extra_anims = []
    elif not isinstance(extra_anims, list):
        extra_anims = [extra_anims]

    for anims in extra_anims:
        if callable(anims) and not isinstance(anims, _AnimationBuilder):
            anims = anims(elem)
        if isinstance(anims, list):
            all_anims.extend(anims)
        else:
            all_anims.append(anims)

    if all_anims:
        scene.play(*all_anims)
        scene.wait(delay)


def for_loop(
    scene: Scene,
    code: CodeExec,
    line_boundary: tuple[int, int],
    *,
    initialize: Callable[[], _T],
    condition: Callable[[_T], bool],
    mutate: Callable[[_T], _T],
    with_init: Anim[_T] = None,
    post_init: Anim[_T] = None,
    with_incr: Anim[_T] = None,
):
    cond_line, end_line = line_boundary
    for_init, cond_true, cond_false, for_incr = for_loop_circumscribes(code, cond_line)

    def decorator(func: Callable[[_T], _R]) -> Callable[[], list[tuple[_T, _R]]]:
        def wrapper():
            scene.play(code.highlight(cond_line))
            scene.wait(1)
            elem = initialize()
            play_anims(scene, elem, with_init, for_init)
            play_anims(scene, elem, post_init)
            rets = []

            while condition(elem):
                scene.play(cond_true)

                scene.play(code.highlight(cond_line + 1))

                rets.append((elem, func(elem)))

                scene.play(code.highlight(end_line))
                scene.wait(1)

                scene.play(code.highlight(cond_line))
                scene.wait(1)

                elem = mutate(elem)

                play_anims(scene, elem, with_incr, for_incr)

            scene.play(cond_false)

            return rets

        return wrapper

    return decorator


class ForParts(TypedDict, Generic[_T]):
    initialize: Callable[[], _T]
    condition: Callable[[_T], bool]
    mutate: Callable[[_T], _T]


def from_range(r: range) -> ForParts[int]:
    return {
        "initialize": lambda: r.start,
        "condition": lambda i: (i < r.stop, i > r.stop)[r.step < 0],
        "mutate": lambda i: i + r.step,
    }
