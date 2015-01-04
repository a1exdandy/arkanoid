__author__ = 'Kovrizhnykh Alexey'
import math


# Geometry functional tools
class Vector:

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __add__(self, other):
        return Vector(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Vector(self.x - other.x, self.y - other.y)

    def __abs__(self):
        return math.sqrt(self.x ** 2 + self.y ** 2)

    def __mul__(self, other):
        return Vector(self.x * other, self.y * other)

    def __truediv__(self, other):
        return Vector(self.x / other, self.y / other)

    def scalar_mul(self, other):
        return self.x * other.x + self.y * other.y

    def vector_mul(self, other):
        return self.x * other.y - self.y * other.x

    def rotate(self, angle):
        angle = angle / 180 * math.pi
        return Vector(
            self.x * math.cos(angle) - self.y * math.sin(angle),
            self.x * math.sin(angle) + self.y * math.cos(angle)
        )

    def __repr__(self):
        return str((self.x, self.y))


def diff_sign(a, b):
    return (min(a, b) <= 0) and (max(a, b) >= 0)


def intersect_sector_sector(a, b, c, d):
    """Проверка на пересечение отрезков (a, b) и (c, d)
    Возвращает точку пересечения
    """
    if not diff_sign((b - a).vector_mul(c - a), (b - a).vector_mul(d - a)):
        return False, None
    if not diff_sign((d - c).vector_mul(a - c), (d - c).vector_mul(b - c)):
        return False, None
    s1 = -1 * (c - a).vector_mul(d - a)
    s2 = (c - b).vector_mul(d - b)
    if s1 + s2 == 0:
        return False, None
    return True, a + (b - a) * (s1 / (s1 + s2))


def intersect_line_line(a, b, c, d):
    """Проверка на пересечение прямых (a, b) и (c, d)
    Возвращает точку пересечения
    """
    s1 = -1 * (c - a).vector_mul(d - a)
    s2 = (c - b).vector_mul(d - b)
    if s1 + s2 == 0:
        return False, None
    return True, a + (b - a) * (s1 / (s1 + s2))


def intersect_line_circle(line_point, path, center, radius):
    """ Получить точку пересечения прямой и окружности
    line_point - точка прямой
    path - направляющий вектор прямой
    center - центер окружнсоти
    radius - радиус окружности

    Для нахожденя точки пересечения необходимо решить систему уравнений:
    {
        r^2 = x^2 + y^2
        x = x_0 + tu
        y = y_0 + tv
    }
    (u, v - координаты направляющего вектора)
    Подставив x и y в первое уравнение, получим:
        r^2 = (x_0 + tu)^2 + (y_0 + tv)^2
    Приведем к квадратному уравнению:
        t^2(u^2 + v^2) + t(2*u*x_0 + 2*v*y_0) + (x_0)^2 + (y_0)^2 - r^2 = 0
    Переобозначим коэффициенты при x как a, b и c и найдем решение уравнения
        a * t^2 + b * t + c = 0
    Точки пересечения будут равны a + s * t_1 и a + s * t_2
    """

    u = path.x
    v = path.y
    x_0 = line_point.x - center.x
    y_0 = line_point.y - center.y

    a = u ** 2 + v ** 2
    b = 2 * u * x_0 + 2 * v * y_0
    c = x_0 ** 2 + y_0 ** 2 - radius ** 2
    # Дискременант
    D = b ** 2 - 4 * a * c
    if D < 0:
        return ()
    t_1 = (-b + math.sqrt(D)) / (2 * a)
    t_2 = (-b - math.sqrt(D)) / (2 * a)

    return line_point + path * t_1, line_point + path * t_2

