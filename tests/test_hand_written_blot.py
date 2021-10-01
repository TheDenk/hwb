# -*- coding: utf-8 -*-
import numpy as np
import pytest

from hwb.blots import generate_rect_coordinates, HandWrittenBlot
from hwb.configs import blot_rect_config, blot_params


@pytest.mark.parametrize('params',
                         [(500, 500, 0, 0, 500, 500, 100, 100, 300, 300),
                          (1000, 2000, 0, 0, 2000, 1000, 300, 300, 600, 600),
                             (500, 1000, 0, 0, 500, 500, None, None, None, None),
                             (500, 700, None, None, None, None, None, None, None, None),
                             (300, 300, None, None, None, None, 100, 100, 300, 300)])
def test_generate_rect_coordinates(params):
    img_h, img_w, min_x, min_y, max_x, max_y, min_h, min_w, max_h, max_w = params
    rect = generate_rect_coordinates(img_h, img_w, min_x, min_y, max_x, max_y, min_h, min_w, max_h, max_w)
    x1, y1, x2, y2 = rect

    assert x1 < x2 and y1 < y2
    assert x1 >= 0 and y1 >= 0
    assert x2 <= img_w and y2 <= img_h


@pytest.mark.parametrize('params', [(10, 10, 50, 100, 0.5, 10, 323), ])
def test_generate_points(params):
    mask_x, mask_y, mask_w, mask_h, intensivity, incline, p_count = params

    hand_written_blot = HandWrittenBlot(blot_rect_config, blot_params)
    p = hand_written_blot.generate_points(mask_x, mask_y, mask_w, mask_h, intensivity, incline)

    assert isinstance(p, list)
    assert len(p) == 2


@pytest.mark.parametrize('params', [(np.ones((100, 100, 3), dtype=np.uint8),
                                     [[10, 20, 30, 40, 50], [10, 40, 50, 30, 40]]), ])
def test_draw_bezier_curve(params):
    img, points = params
    hand_written_blot = HandWrittenBlot(blot_rect_config, blot_params)
    p = hand_written_blot.draw_bezier_curve(img, points)

    assert type(img) == type(p)


@pytest.mark.parametrize('params', [(np.ones((100, 100, 3), dtype=np.uint8),
                                     [{'x': 10, 'y': 10, 'w': 50, 'h': 50, 'points_intensivity': 0.9,
                                       'incline': 0, 'transparency': 0.1, 'repeat': 5}]), ])
def test_make_handwriting(params):
    img, configs = params
    hand_written_blot = HandWrittenBlot(blot_rect_config, blot_params)
    p = hand_written_blot.make_handwriting(img, configs)

    assert type(img) == type(p)


@pytest.mark.parametrize('params', [(100, 100), ])
def test_generate_configs(params):
    img_h, img_w = params
    hand_written_blot = HandWrittenBlot(blot_rect_config, blot_params)
    configs = hand_written_blot.generate_configs(img_h, img_w)

    assert isinstance(configs, list)


@pytest.mark.parametrize('params', [(np.ones((100, 100, 3), dtype=np.uint8)), ])
def test_apply(params):
    img = params
    hand_written_blot = HandWrittenBlot(blot_rect_config, blot_params)
    out_img = hand_written_blot.apply(img)

    assert type(img) == type(out_img)
    assert img.shape == out_img.shape


@pytest.mark.parametrize('params', [(np.ones((100, 100, 3), dtype=np.uint8), {}, {}),
                                    (np.ones((100, 100, 3), dtype=np.uint8), {
                                     'x': 10, }, {'points_intensivity': 0.9, }),
                                    (np.ones((100, 100, 3), dtype=np.uint8), None, None), ])
def test_apply_no_params(params):
    img, b_r, b_p = params
    hand_written_blot = HandWrittenBlot(b_r, b_p)
    out_img = hand_written_blot.apply(img)

    assert type(img) == type(out_img)
    assert img.shape == out_img.shape
