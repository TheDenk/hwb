# -*- coding: utf-8 -*-
import numpy as np

from .utils import unpack_mm_params, generate_parameter
from .configs import blot_rect_config, blot_params


def generate_rect_coordinates(img_h: int, img_w: int,
                              min_x: int = None, min_y: int = None,
                              max_x: int = None, max_y: int = None,
                              min_h: int = None, min_w: int = None,
                              max_h: int = None, max_w: int = None):
    """
    Description:
    Generation of coordinates by which the rectangle will be cut.

    Parameters:
    img_h (int), img_w (int) - Image parameters used to calculate the maximum value of a rectangle
    min_x (int), min_y (int) - Minimum allowed coordinates of the upper left point
    max_x (int), max_y (int) - Maximum allowed coordinates of the upper left point
    min_h (int), min_w (int) - Minimum allowed width and height of a rectangle
    max_h (int), max_w (int) - Maximum allowed width and height of a rectangle

    Returns:
    (x1, y1, x2, y2) (tuple of ints) -  Rectangle coordinates
    """

    min_h = 1 if min_h is None else min_h
    min_w = 1 if min_w is None else min_w

    max_h = img_h if max_h is None else max_h
    max_w = img_w if max_w is None else max_w

    rect_h = generate_parameter(min_h, max_h)
    rect_w = generate_parameter(min_w, max_w)

    min_x = 0 if min_x is None or min_x < 0 else min_x
    min_y = 0 if min_y is None or min_y < 0 else min_y

    max_x = img_w - rect_w if max_x is None else max_x
    max_y = img_h - rect_h if max_y is None else max_y

    x1 = generate_parameter(min_x, max_x)
    x2 = x1 + rect_w if x1 + rect_w <= img_w else img_w

    y1 = generate_parameter(min_y, max_y)
    y2 = y1 + rect_h if y1 + rect_h <= img_h else img_h

    return x1, y1, x2, y2


class HandWrittenBlot:
    """
    Description:
    This class for make some blots on image.

    Init Parameters:

    rect_config (dict) - Config with blot parameters (size and position)
    params (dict) - Config with blot parameters (incline, transparency, intensivity, count)
    """

    def __init__(self, rect_config: dict = None, params: dict = None):
        try:
            import cv2
        except ImportError:
            raise Exception('''OpenCV library not found. Please install it.
                Run command: pip install opencv-python>=4.1.1''')

        try:
            import bezier
        except ImportError:
            raise Exception('''Bezier library not found. Please install it.
                Run command: pip install bezier>=2020.5.19''')

        self.cv2 = cv2
        self.bezier = bezier

        self.rect_config = blot_rect_config if rect_config is None else rect_config
        self.params = blot_params if params is None else params

        for def_key, def_val in blot_rect_config.items():
            if def_key not in self.rect_config.keys() or self.rect_config[def_key] is None:
                self.rect_config[def_key] = def_val

        for def_key, def_val in blot_params.items():
            if def_key not in self.params.keys() or self.params[def_key] is None:
                self.params[def_key] = def_val

        self.min_x, self.max_x = unpack_mm_params(self.rect_config['x'])
        self.min_y, self.max_y = unpack_mm_params(self.rect_config['y'])
        self.min_h, self.max_h = unpack_mm_params(self.rect_config['h'])
        self.min_w, self.max_w = unpack_mm_params(self.rect_config['w'])

        self.min_incline, self.max_incline = unpack_mm_params(self.params['incline'])
        self.min_intens, self.max_intens = unpack_mm_params(self.params['intensivity'])
        self.min_transp, self.max_transp = unpack_mm_params(self.params['transparency'])
        self.min_count, self.max_count = unpack_mm_params(self.params['count'])
        self.min_thick, self.max_thick = unpack_mm_params(self.params['thickness'])


    def generate_points(self, mask_x: int, mask_y: int,
                        mask_w: int, mask_h: int, intensivity: float, incline: int):
        """
        Description:
        Method for points generation. Points using for draw lines between them.

        Parameters:
        mask_x (int) - Blot position X
        mask_y (int) - Blot position Y
        mask_w (int) - Max Blot width
        mask_h (int) - Max Blot height
        intensivity (float) - Blot intensivity. Max points count.
        incline (int) - Shift point by Y-axes.

        Return:
        points ([X, Y], Where X, Y - lists of int) - points for drawing lines
        """

        points_count = int(intensivity * 20)

        point_prer_pixel = points_count / mask_h
        step_size = int(1 / point_prer_pixel) if 1 / point_prer_pixel > 1 else 1

        lp_min, lp_max = int(mask_w*0.01), int(mask_w*0.20)
        rp_min, rp_max = int(mask_w*0.8), int(mask_w*0.99)

        points = [[], []]

        if lp_min == lp_max or rp_min == rp_max:
            return points

        for i, step in enumerate(range(0, points_count*step_size, step_size)):

            if i < points_count // 10:
                x = np.random.randint(mask_x, mask_x + mask_w)
                y = np.random.randint(mask_y, mask_y + mask_h)
                points[0].append(x)
                points[1].append(y)
            else:
                l_att = np.random.randint(10, 80)
                r_att = 80 - l_att

                if i % 2 == 0:
                    for _ in range(l_att):
                        x = np.random.randint(lp_min, lp_max)
                        y = np.random.randint(step + incline, step + step_size + incline)

                        points[0].append(x + mask_x)
                        points[1].append(y + mask_y)
                else:
                    for _ in range(r_att):
                        x = np.random.randint(rp_min, rp_max)
                        y = np.random.randint(step - incline, step + step_size - incline)

                        points[0].append(x + mask_x)
                        points[1].append(y + mask_y)

        return points

    def draw_bezier_curve(self, image: np.array, points: list, thickness: int):
        """
        Description:
        Method for drawing bezier line, using generated points.

        Parameters:
        image (np.array) - image on wich the blot will be drawn
        points (list) - list of points for drawing

        Return:
        image (np.array) - the same image as on input but with blot
        """
        img = image.copy()

        curve = self.bezier.Curve(points, degree=len(points[0]) - 1)

        x, y = curve.evaluate(0.01)

        if x is None or y is None or np.isnan(x) or np.isnan(y):
            return img

        x1, y1 = np.uint16(x)[0], np.uint16(y)[0]

        for point in np.arange(0.01, 0.99, 0.02):
            x, y = curve.evaluate(point)

            if x is None or y is None or np.isnan(x) or np.isnan(y):
                return img

            x2, y2 = np.uint16(x)[0], np.uint16(y)[0]

            img = self.cv2.line(img, (x1, y1), (x2, y2), (0, 0, 0), thickness)
            x1, y1 = x2, y2

        return img

    def make_handwriting(self, image: np.array, configs: dict):
        """
        Description:
        Method for creating bezier lines and drawing them.

        Parameters:
        image (np.array) - image on wich the blots will be drawn
        configs (dict) - config with blot parameters (x, y, h, w, incline, ...)

        Return:
        bg_img (np.array) - the same image as on input but with blots
        """
        bg_img = image.copy()
        fg_img = image.copy()

        for config in configs:
            for _ in range(config['repeat']):
                points = self.generate_points(
                    config['x'],
                    config['y'],
                    config['w'],
                    config['h'],
                    config['points_intensivity'],
                    config['incline'],
                )
                if not points:
                    continue
                fg_img = self.draw_bezier_curve(fg_img, points, config['thickness'])

            bg_img = self.cv2.addWeighted(bg_img, config['transparency'], fg_img, 1 - config['transparency'], 0)

        return bg_img

    def generate_configs(self, img_h: int, img_w: int):
        """
        Description:
        Method fog configs generating. Configs contains parameters for blots generating.

        Parameters:
        img_h (int) - image height
        img_w (int) - image width

        Return:
        configs (list of dict) - configs with blots parameters (x, y, h, w, incline, ...)
        """
        configs = []

        count = generate_parameter(self.min_count, self.max_count, 'count')

        for _ in range(count):

            x1, y1, x2, y2 = generate_rect_coordinates(
                img_h=img_h, img_w=img_w,
                min_x=self.min_x, min_y=self.min_y,
                max_x=self.max_x, max_y=self.max_y,
                min_h=self.min_h, min_w=self.min_w,
                max_h=self.max_h, max_w=self.max_w,)

            incline = generate_parameter(self.min_incline, self.max_incline, 'incline')
            intensivity = generate_parameter(self.min_intens, self.max_intens, 'intensivity')
            transp = generate_parameter(self.min_transp, self.max_transp, 'transparency')
            thick = generate_parameter(self.min_thick, self.max_thick, 'thickness')

            configs.append({
                'x': x1,
                'y': y1,
                'w': x2 - x1,
                'h': y2 - y1,
                'points_intensivity': intensivity,
                'repeat': int(intensivity * 5),
                'transparency': transp,
                'incline': incline,
                'thickness': thick,
            })

        return configs

    def apply(self, image):
        """
        Description:
        Main method for adding blots on image.

        Parameters:
        image (np.array) - image on wich the blots will be drawn

        Return:
        image (np.array) - the same image as on input but with blots
        """
        img_h, img_w, _ = image.shape
        shades_configs = self.generate_configs(img_h, img_w)
        img = self.make_handwriting(image, shades_configs)
        return img

    def __call__(self, image):
        return self.apply(image)
