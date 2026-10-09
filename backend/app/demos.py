"""Three carefully composed, deterministic lessons for the private prototype.

Each lesson is one immutable scene, introduced in six small groups. Curves are
authored in a fixed 1000-unit drawing space; no SVG markup or assets are stored.
The sample scenes are deliberately identified as demos, never photo results.
"""

from math import cos, pi, sin
from typing import Any

from .models import Lesson

XY = tuple[float, float]
Segment = tuple[XY, XY, XY]


def _point(value: XY) -> dict[str, float]:
    return {"x": round(float(value[0]), 2), "y": round(float(value[1]), 2)}


def _base(identifier: str, kind: str, color: str, width: float, opacity: float) -> dict[str, Any]:
    return {"id": identifier, "kind": kind, "color": color, "width": width, "opacity": opacity}


def _curve(
    identifier: str,
    start: XY,
    segments: list[Segment],
    *,
    closed: bool = False,
    fill: str = "none",
    color: str = "graphite",
    width: float = 7,
    opacity: float = 1,
) -> dict[str, Any]:
    return {
        **_base(identifier, "bezier", color, width, opacity),
        "start": _point(start),
        "segments": [
            {"control1": _point(first), "control2": _point(second), "end": _point(end)}
            for first, second, end in segments
        ],
        "closed": closed,
        "fill": fill,
    }


def _line(
    identifier: str, start: XY, end: XY, *, color: str = "graphite", width: float = 6
) -> dict[str, Any]:
    return {
        **_base(identifier, "line", color, width, 1),
        "start": _point(start),
        "end": _point(end),
    }


def _polyline(identifier: str, points: list[XY], *, width: float = 7) -> dict[str, Any]:
    return {
        **_base(identifier, "polyline", "graphite", width, 1),
        "points": [_point(point) for point in points],
    }


def _ellipse(
    identifier: str,
    center: XY,
    rx: float,
    ry: float,
    *,
    fill: str = "none",
    color: str = "graphite",
    width: float = 6,
    opacity: float = 1,
) -> dict[str, Any]:
    return {
        **_base(identifier, "ellipse", color, width, opacity),
        "center": _point(center),
        "rx": rx,
        "ry": ry,
        "fill": fill,
    }


def _polygon(identifier: str, points: list[XY], *, width: float = 7) -> dict[str, Any]:
    return {
        **_base(identifier, "polygon", "graphite", width, 1),
        "points": [_point(point) for point in points],
        "fill": "none",
    }


def _wash(stroke: dict[str, Any], identifier: str, color: str) -> dict[str, Any]:
    """A pale color shape immediately followed by its dark, teachable contour."""
    return {**stroke, "id": identifier, "color": color, "fill": color, "opacity": 0.25}


def _group(
    identifier: str, title: str, instruction: str, strokes: list[dict[str, Any]]
) -> dict[str, Any]:
    return {"id": identifier, "title": title, "instruction": instruction, "strokes": strokes}


def _lesson(
    identifier: str,
    title: str,
    subject: str,
    description: str,
    features: list[str],
    proportions: str,
    groups: list[dict[str, Any]],
) -> Lesson:
    return Lesson.model_validate(
        {
            "schema_version": "1",
            "id": identifier,
            "source": "demo",
            "title": title,
            "subject": subject,
            "description": description,
            "analysis": {
                "subject": subject,
                "recognizable_features": features,
                "simplifications": [
                    "Use a few rounded outlines.",
                    "Leave out texture, shading, and tiny details.",
                ],
                "proportions": proportions,
                ("composition"): (
                    "One centered subject with generous paper space around it; the finished "
                    "scene is shared by every step."
                ),
                "difficulty": "easy",
                "suitable": True,
                "reason": "A hand-authored sample lesson, independent of uploaded photographs.",
            },
            "groups": groups,
        }
    )


def _puppy() -> Lesson:
    head = _curve(
        "puppy-head",
        (500, 235),
        [
            ((400, 214), (333, 244), (305, 333)),
            ((285, 390), (308, 462), (352, 500)),
            ((393, 549), (445, 567), (500, 566)),
            ((563, 565), (622, 546), (660, 500)),
            ((701, 459), (718, 389), (696, 329)),
            ((668, 253), (603, 222), (500, 235)),
        ],
        closed=True,
        width=8,
    )
    left_ear = _curve(
        "puppy-ear-left",
        (326, 290),
        [
            ((266, 280), (231, 323), (208, 396)),
            ((185, 462), (194, 528), (231, 549)),
            ((259, 566), (292, 531), (307, 475)),
            ((320, 414), (307, 353), (326, 290)),
        ],
        closed=True,
    )
    right_ear = _curve(
        "puppy-ear-right",
        (674, 290),
        [
            ((734, 280), (769, 323), (792, 396)),
            ((815, 462), (806, 528), (769, 549)),
            ((741, 566), (708, 531), (693, 475)),
            ((680, 414), (693, 353), (674, 290)),
        ],
        closed=True,
    )
    left_paw = _curve(
        "puppy-paw-left",
        (365, 772),
        [
            ((365, 747), (397, 740), (425, 746)),
            ((449, 749), (472, 772), (465, 796)),
            ((457, 816), (379, 820), (365, 798)),
            ((361, 790), (362, 779), (365, 772)),
        ],
        closed=True,
    )
    right_paw = _curve(
        "puppy-paw-right",
        (535, 796),
        [
            ((528, 772), (551, 749), (575, 746)),
            ((603, 740), (635, 747), (635, 772)),
            ((638, 793), (639, 806), (620, 812)),
            ((594, 820), (543, 816), (535, 796)),
        ],
        closed=True,
    )
    nose = _curve(
        "puppy-nose",
        (482, 426),
        [
            ((491, 419), (509, 419), (518, 426)),
            ((525, 435), (510, 447), (500, 449)),
            ((490, 447), (475, 435), (482, 426)),
        ],
        closed=True,
        fill="graphite",
        width=5,
    )
    return _lesson(
        "puppy",
        "A floppy-eared friend",
        "A friendly seated puppy",
        (
            "Meet Pip: floppy ears, soft paws, and a little wagging tail. Build this "
            "friendly puppy one gentle shape at a time."
        ),
        [
            "Two long floppy ears",
            "Rounded head and little nose",
            "Seated body with four soft paws",
            "A curved wagging tail",
        ],
        (
            "A large, round head above a smaller seated body. The ears hang beside the "
            "cheeks and the front paws sit together below the chest."
        ),
        [
            _group(
                "puppy-round-head",
                "A soft, round head",
                (
                    "Start with a big, soft shape like a squishy apple. Leave plenty of paper "
                    "underneath for your puppy's body."
                ),
                [
                    head,
                    _curve(
                        "puppy-tuft",
                        (464, 237),
                        [
                            ((470, 222), (479, 217), (486, 215)),
                            ((487, 224), (491, 232), (500, 237)),
                            ((506, 225), (513, 218), (517, 216)),
                            ((520, 227), (526, 234), (533, 239)),
                        ],
                        width=5,
                    ),
                ],
            ),
            _group(
                "puppy-floppy-ears",
                "Two floppy ears",
                (
                    "Add a long, floppy ear on each side. Let them droop down like soft socks, "
                    "then add a little fold inside each one."
                ),
                [
                    _wash(left_ear, "puppy-ear-wash-left", "peach"),
                    left_ear,
                    _wash(right_ear, "puppy-ear-wash-right", "peach"),
                    right_ear,
                    _curve(
                        "puppy-ear-fold-left",
                        (274, 335),
                        [((237, 380), (220, 470), (244, 509))],
                        width=5,
                    ),
                    _curve(
                        "puppy-ear-fold-right",
                        (726, 335),
                        [((763, 380), (780, 470), (756, 509))],
                        width=5,
                    ),
                ],
            ),
            _group(
                "puppy-seated-body",
                "A cuddly body",
                (
                    "Draw two gently curved sides below the head. Add the round back legs and "
                    "a little fluffy patch on the chest."
                ),
                [
                    _curve("puppy-body-left", (381, 529), [((330, 580), (330, 664), (356, 717))]),
                    _curve("puppy-body-right", (628, 530), [((677, 580), (670, 664), (644, 717))]),
                    _curve(
                        "puppy-haunch-left",
                        (347, 677),
                        [
                            ((285, 675), (279, 780), (333, 799)),
                            ((344, 803), (351, 801), (365, 798)),
                        ],
                    ),
                    _curve(
                        "puppy-haunch-right",
                        (653, 677),
                        [
                            ((715, 675), (721, 780), (667, 799)),
                            ((656, 803), (649, 801), (635, 798)),
                        ],
                    ),
                    _curve(
                        "puppy-chest",
                        (455, 582),
                        [
                            ((465, 597), (476, 603), (485, 598)),
                            ((491, 610), (499, 615), (505, 602)),
                            ((518, 610), (534, 597), (544, 582)),
                        ],
                        width=5,
                    ),
                ],
            ),
            _group(
                "puppy-paws-tail",
                "Paws and a wag",
                (
                    "Bring two front legs down to soft little paws. Finish with a curved tail "
                    "peeking out from the side—it's happy to see you!"
                ),
                [
                    _curve(
                        "puppy-leg-left",
                        (393, 631),
                        [((387, 670), (389, 716), (390, 748))],
                        width=6,
                    ),
                    _curve(
                        "puppy-leg-right",
                        (607, 631),
                        [((613, 670), (611, 716), (610, 748))],
                        width=6,
                    ),
                    left_paw,
                    right_paw,
                    _curve(
                        "puppy-tail",
                        (695, 728),
                        [
                            ((755, 730), (800, 689), (785, 647)),
                            ((778, 625), (749, 630), (754, 650)),
                            ((770, 683), (735, 696), (697, 695)),
                        ],
                        width=7,
                    ),
                    _curve(
                        "puppy-belly-base",
                        (470, 802),
                        [((486, 807), (514, 807), (530, 802))],
                        width=5,
                    ),
                ],
            ),
            _group(
                "puppy-kind-face",
                "A friendly face",
                (
                    "Place two eyes above a little nose. Add the round muzzle and a smile; "
                    "your puppy is starting to say hello."
                ),
                [
                    _ellipse("puppy-eye-left", (423, 381), 11, 15, fill="graphite", width=5),
                    _ellipse("puppy-eye-right", (577, 381), 11, 15, fill="graphite", width=5),
                    _curve(
                        "puppy-brow-left",
                        (405, 351),
                        [((418, 342), (431, 342), (441, 351))],
                        width=5,
                    ),
                    _curve(
                        "puppy-brow-right",
                        (559, 351),
                        [((569, 342), (582, 342), (595, 351))],
                        width=5,
                    ),
                    _curve(
                        "puppy-muzzle",
                        (445, 440),
                        [
                            ((429, 454), (436, 487), (462, 497)),
                            ((484, 509), (516, 509), (538, 497)),
                            ((564, 487), (571, 454), (555, 440)),
                        ],
                        width=5,
                    ),
                    nose,
                    _line("puppy-nose-stem", (500, 449), (500, 459), width=5),
                    _curve(
                        "puppy-smile-left",
                        (500, 459),
                        [((488, 476), (473, 476), (463, 459))],
                        width=5,
                    ),
                    _curve(
                        "puppy-smile-right",
                        (500, 459),
                        [((512, 476), (527, 476), (537, 459))],
                        width=5,
                    ),
                ],
            ),
            _group(
                "puppy-finishing-love",
                "Little happy details",
                (
                    "Give your puppy a tiny tongue and a few toe marks. Add a soft ground "
                    "line, then give your new drawing friend a name!"
                ),
                [
                    _curve(
                        "puppy-tongue",
                        (487, 474),
                        [
                            ((485, 502), (512, 505), (513, 474)),
                            ((505, 480), (495, 480), (487, 474)),
                        ],
                        closed=True,
                        color="peach",
                        fill="peach",
                        opacity=0.8,
                        width=5,
                    ),
                    _curve(
                        "puppy-cheek-left",
                        (364, 429),
                        [((375, 436), (386, 436), (396, 430))],
                        color="peach",
                        width=6,
                        opacity=0.7,
                    ),
                    _curve(
                        "puppy-cheek-right",
                        (604, 430),
                        [((614, 436), (625, 436), (636, 429))],
                        color="peach",
                        width=6,
                        opacity=0.7,
                    ),
                    _curve(
                        "puppy-toe-left-a",
                        (392, 779),
                        [((388, 790), (390, 800), (393, 806))],
                        width=5,
                    ),
                    _curve(
                        "puppy-toe-left-b",
                        (420, 778),
                        [((416, 790), (419, 801), (422, 807))],
                        width=5,
                    ),
                    _curve(
                        "puppy-toe-right-a",
                        (580, 778),
                        [((584, 790), (581, 801), (578, 807))],
                        width=5,
                    ),
                    _curve(
                        "puppy-toe-right-b",
                        (608, 779),
                        [((612, 790), (610, 800), (607, 806))],
                        width=5,
                    ),
                    _curve(
                        "puppy-ground",
                        (286, 834),
                        [((397, 847), (602, 847), (714, 834))],
                        color="lavender",
                        width=5,
                        opacity=0.6,
                    ),
                ],
            ),
        ],
    )


def _petal(index: int) -> dict[str, Any]:
    # Seven broad, slightly asymmetric petals. Their open roots meet the center
    # circle, so no hidden geometry or renderer-specific clipping is required.
    angle = -pi / 2 + index * 2 * pi / 7

    def position(point: XY) -> XY:
        tangent, radial = point
        return (
            500 + radial * cos(angle) - tangent * sin(angle),
            315 + radial * sin(angle) + tangent * cos(angle),
        )

    return _curve(
        f"flower-petal-{index + 1}",
        position((-28, 62)),
        [
            (position((-34, 90)), position((-54, 131)), position((-32, 158))),
            (position((-13, 184)), position((20, 185)), position((39, 155))),
            (position((58, 130)), position((40, 90)), position((28, 62))),
        ],
        width=7,
    )


def _flower() -> Lesson:
    left_leaf = _curve(
        "flower-leaf-left",
        (486, 511),
        [
            ((416, 467), (327, 477), (357, 541)),
            ((380, 572), (447, 551), (486, 511)),
        ],
        closed=True,
    )
    right_leaf = _curve(
        "flower-leaf-right",
        (505, 567),
        [
            ((548, 501), (644, 496), (629, 541)),
            ((616, 591), (555, 604), (505, 567)),
        ],
        closed=True,
    )
    return _lesson(
        "flower",
        "A little sunshine flower",
        "A cheerful seven-petaled flower in a pot",
        (
            "A round flower, seven soft petals, and two leafy arms. This sunny little "
            "plant is ready to brighten your paper."
        ),
        [
            "Seven rounded petals around a round center",
            "A gently bending stem",
            "Two broad leaves",
            "A small tapered flowerpot",
        ],
        (
            "A large flower head above a slender stem, with two broad leaves and a "
            "small pot to balance the drawing."
        ),
        [
            _group(
                "flower-sunny-middle",
                "A sunny middle",
                (
                    "Draw a round middle near the top of your paper. It can be a little "
                    "wobbly—that gives your flower its own personality."
                ),
                [
                    _ellipse(
                        "flower-center-wash",
                        (500, 315),
                        68,
                        66,
                        fill="peach",
                        color="peach",
                        width=5,
                        opacity=0.25,
                    ),
                    _ellipse("flower-center", (500, 315), 68, 66, width=7),
                ],
            ),
            _group(
                "flower-soft-petals",
                "Petals all around",
                (
                    "Add seven big, soft petals around the middle. Make each one like a "
                    "rounded spoon, and let them be slightly different."
                ),
                [_petal(index) for index in range(7)],
            ),
            _group(
                "flower-stem-leaves",
                "A stem and leafy arms",
                (
                    "Bring a gently bending stem down from your flower. Add one leaf on each "
                    "side, like two little hands waving hello."
                ),
                [
                    _curve(
                        "flower-stem-left",
                        (499, 383),
                        [
                            ((499, 409), (498, 434), (497, 451)),
                            ((495, 469), (490, 480), (487, 490)),
                            ((481, 546), (479, 609), (486, 666)),
                        ],
                        width=5,
                    ),
                    _curve(
                        "flower-stem-right",
                        (501, 383),
                        [
                            ((501, 409), (502, 434), (503, 451)),
                            ((505, 469), (510, 480), (511, 490)),
                            ((508, 546), (504, 609), (508, 666)),
                        ],
                        width=5,
                    ),
                    _wash(left_leaf, "flower-leaf-wash-left", "mint"),
                    left_leaf,
                    _wash(right_leaf, "flower-leaf-wash-right", "mint"),
                    right_leaf,
                    _curve(
                        "flower-leaf-vein-left",
                        (476, 517),
                        [((438, 524), (403, 533), (375, 531))],
                        width=5,
                    ),
                    _curve(
                        "flower-leaf-vein-right",
                        (516, 566),
                        [((551, 555), (580, 537), (611, 529))],
                        width=5,
                    ),
                ],
            ),
            _group(
                "flower-cozy-pot",
                "A cozy flowerpot",
                (
                    "Make a wide oval for the top of the pot. Draw the sides gently inward and "
                    "join them with a curved bottom."
                ),
                [
                    _ellipse("flower-pot-rim", (500, 677), 136, 25, width=7),
                    _curve(
                        "flower-pot",
                        (369, 685),
                        [
                            ((378, 736), (387, 801), (399, 832)),
                            ((455, 850), (545, 850), (601, 832)),
                            ((613, 801), (622, 736), (631, 685)),
                        ],
                        width=7,
                    ),
                    _curve(
                        "flower-pot-stripe",
                        (383, 754),
                        [((453, 777), (547, 777), (617, 754))],
                        color="lavender",
                        width=6,
                        opacity=0.8,
                    ),
                ],
            ),
            _group(
                "flower-friendly-smile",
                "A sunshine smile",
                (
                    "Give your flower two little eyes and a happy smile. Add tiny peach cheeks "
                    "if you would like an extra sunny friend."
                ),
                [
                    _ellipse("flower-eye-left", (478, 306), 5, 7, fill="graphite", width=5),
                    _ellipse("flower-eye-right", (522, 306), 5, 7, fill="graphite", width=5),
                    _curve(
                        "flower-smile", (481, 327), [((490, 344), (510, 344), (519, 327))], width=5
                    ),
                    _ellipse(
                        "flower-cheek-left",
                        (454, 326),
                        8,
                        5,
                        fill="peach",
                        color="peach",
                        width=5,
                        opacity=0.7,
                    ),
                    _ellipse(
                        "flower-cheek-right",
                        (546, 326),
                        8,
                        5,
                        fill="peach",
                        color="peach",
                        width=5,
                        opacity=0.7,
                    ),
                ],
            ),
            _group(
                "flower-little-love",
                "A little love",
                (
                    "Decorate your pot with a tiny heart. Add a few small marks in the soil "
                    "and a ground line—your sunshine flower is ready to grow!"
                ),
                [
                    _curve(
                        "flower-pot-heart",
                        (500, 797),
                        [
                            ((481, 783), (473, 770), (484, 765)),
                            ((491, 761), (497, 766), (500, 771)),
                            ((505, 765), (513, 762), (518, 768)),
                            ((527, 779), (509, 792), (500, 797)),
                        ],
                        closed=True,
                        color="mint",
                        fill="mint",
                        opacity=0.7,
                        width=5,
                    ),
                    _curve(
                        "flower-soil-left",
                        (406, 679),
                        [((424, 674), (443, 674), (461, 678))],
                        width=5,
                    ),
                    _curve(
                        "flower-soil-right",
                        (540, 678),
                        [((559, 674), (578, 674), (595, 679))],
                        width=5,
                    ),
                    _curve(
                        "flower-ground",
                        (345, 861),
                        [((440, 873), (560, 873), (655, 861))],
                        color="lavender",
                        width=5,
                        opacity=0.6,
                    ),
                ],
            ),
        ],
    )


def _house() -> Lesson:
    roof = _curve(
        "house-roof",
        (258, 415),
        [
            ((330, 342), (393, 283), (504, 211)),
            ((608, 279), (677, 342), (748, 415)),
            ((592, 409), (414, 409), (258, 415)),
        ],
        closed=True,
        width=8,
    )
    door = _curve(
        "house-door",
        (445, 713),
        [
            ((444, 658), (444, 600), (445, 551)),
            ((445, 521), (466, 501), (500, 501)),
            ((532, 501), (554, 521), (554, 551)),
            ((556, 600), (556, 658), (554, 713)),
            ((518, 713), (481, 713), (445, 713)),
        ],
        closed=True,
        width=7,
    )
    return _lesson(
        "house",
        "A cozy little cottage",
        "A small house with a peaked roof and garden",
        (
            "A peach-tinted roof, bright windows, and a welcoming curved door. Follow "
            "the path to your very own little cottage."
        ),
        [
            "A broad peaked roof",
            "Two windows divided into four panes",
            "A rounded front door",
            "A chimney and a short garden path",
        ],
        (
            "A broad triangle roof above a squat house. Two windows balance a centered "
            "arched door, and a curved path leads toward the viewer."
        ),
        [
            _group(
                "house-peaked-roof",
                "A cozy peaked roof",
                (
                    "Draw a big roof like a gentle mountain. Join the two slopes with a long "
                    "line across the bottom."
                ),
                [
                    _wash(roof, "house-roof-wash", "peach"),
                    roof,
                ],
            ),
            _group(
                "house-solid-walls",
                "Walls to call home",
                (
                    "Bring two sides down from under the roof. Join them at the bottom to make "
                    "a sturdy little home."
                ),
                [
                    _curve(
                        "house-walls",
                        (305, 415),
                        [
                            ((304, 512), (304, 630), (306, 709)),
                            ((413, 719), (585, 719), (694, 709)),
                            ((696, 630), (696, 512), (695, 415)),
                        ],
                        width=7,
                    ),
                    _curve(
                        "house-ground", (250, 725), [((345, 731), (398, 729), (435, 725))], width=5
                    ),
                    _curve(
                        "house-ground-right",
                        (565, 725),
                        [((632, 731), (705, 731), (753, 725))],
                        width=5,
                    ),
                ],
            ),
            _group(
                "house-bright-windows",
                "Two bright windows",
                (
                    "Add a window on each side. A line down and a line across turn each window "
                    "into four little panes."
                ),
                [
                    _polygon(
                        "house-window-left",
                        [(337, 458), (417, 458), (417, 553), (337, 553)],
                        width=6,
                    ),
                    _line("house-window-left-vertical", (377, 458), (377, 553), width=5),
                    _line("house-window-left-horizontal", (337, 505), (417, 505), width=5),
                    _line("house-sill-left", (329, 563), (425, 563), width=6),
                    _polygon(
                        "house-window-right",
                        [(583, 458), (663, 458), (663, 553), (583, 553)],
                        width=6,
                    ),
                    _line("house-window-right-vertical", (623, 458), (623, 553), width=5),
                    _line("house-window-right-horizontal", (583, 505), (663, 505), width=5),
                    _line("house-sill-right", (575, 563), (671, 563), width=6),
                ],
            ),
            _group(
                "house-welcome-path",
                "A door and a path",
                (
                    "Draw a rounded door in the middle and add a tiny handle. Let two curved "
                    "lines make a path that gets wider as it comes toward you."
                ),
                [
                    _wash(door, "house-door-wash", "lavender"),
                    door,
                    _ellipse("house-doorknob", (535, 608), 5, 5, fill="graphite", width=5),
                    _line("house-doorstep", (434, 722), (566, 722), width=6),
                    _curve(
                        "house-path-left",
                        (463, 730),
                        [((449, 781), (430, 832), (414, 879))],
                        width=6,
                    ),
                    _curve(
                        "house-path-right",
                        (537, 730),
                        [((552, 781), (578, 832), (594, 879))],
                        width=6,
                    ),
                    _ellipse("house-path-stone-one", (500, 780), 27, 7, width=5),
                    _ellipse("house-path-stone-two", (501, 832), 35, 9, width=5),
                ],
            ),
            _group(
                "house-chimney-garden",
                "A chimney and a garden",
                (
                    "Add a little chimney above one roof slope. Draw a few round bushes beside "
                    "the house, like soft green clouds."
                ),
                [
                    _polyline(
                        "house-chimney", [(612, 306), (612, 239), (659, 239), (659, 343)], width=6
                    ),
                    _polygon(
                        "house-chimney-cap",
                        [(603, 230), (668, 230), (668, 246), (603, 246)],
                        width=5,
                    ),
                    _curve(
                        "house-bush-left",
                        (246, 713),
                        [
                            ((227, 690), (231, 670), (250, 674)),
                            ((248, 652), (280, 648), (286, 672)),
                            ((307, 655), (326, 676), (320, 695)),
                            ((341, 692), (344, 710), (326, 714)),
                            ((290, 726), (261, 722), (246, 713)),
                        ],
                        closed=True,
                        color="mint",
                        width=7,
                    ),
                    _curve(
                        "house-bush-right",
                        (713, 715),
                        [
                            ((693, 680), (722, 660), (738, 679)),
                            ((752, 650), (782, 667), (778, 685)),
                            ((802, 675), (822, 701), (807, 715)),
                            ((775, 724), (741, 724), (713, 715)),
                        ],
                        closed=True,
                        color="mint",
                        width=7,
                    ),
                ],
            ),
            _group(
                "house-homely-details",
                "Make it your home",
                (
                    "Add a few short roof marks and a tiny round attic window. A little curl "
                    "above the chimney gives your cottage a storybook finish."
                ),
                [
                    _ellipse("house-attic-window", (504, 334), 26, 26, width=6),
                    _line("house-attic-window-cross", (478, 334), (530, 334), width=5),
                    _line("house-attic-window-vertical", (504, 308), (504, 360), width=5),
                    _curve(
                        "house-roof-mark-left",
                        (362, 361),
                        [((376, 358), (390, 358), (404, 361))],
                        width=5,
                    ),
                    _curve(
                        "house-roof-mark-right",
                        (587, 377),
                        [((602, 374), (617, 374), (632, 377))],
                        width=5,
                    ),
                    _curve(
                        "house-chimney-curl",
                        (638, 210),
                        [
                            ((617, 201), (615, 183), (635, 176)),
                            ((653, 169), (653, 154), (637, 144)),
                        ],
                        color="lavender",
                        width=5,
                        opacity=0.65,
                    ),
                ],
            ),
        ],
    )


DEMO_LESSONS: list[Lesson] = [_puppy(), _flower(), _house()]
DEMOS: dict[str, Lesson] = {lesson.id: lesson for lesson in DEMO_LESSONS}


def get_demo(identifier: str) -> Lesson | None:
    """Return a validated deterministic lesson, or None for an unknown ID."""
    return DEMOS.get(identifier)
