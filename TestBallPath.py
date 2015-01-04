__author__ = 'Kovrizhnykh Alexey'

import arkanoid
import pygame
import sys

fig1 = [
    (93, 266),
    (191, 234),
    (140, 173),
    (234, 199),
    (212, 111),
    (277, 194),
    (318, 87),
    (325, 187),
    (449, 114),
    (387, 213),
    (498, 232),
    (410, 262),
    (488, 296),
    (376, 324),
    (431, 398),
    (363, 364),
    (339, 444),
    (274, 360),
    (248, 404),
    (225, 361),
    (131, 414),
    (179, 311),
]

fig2 = [
    (514, 84),
    (553, 72),
    (562, 31),
    (576, 69),
    (604, 87),
    (576, 98),
    (571, 140),
    (548, 102),
]

fig3 = [
    (629, 470),
    (564, 472),
    (632, 406),
]

fig4 = [
    (10, 19),
    (56, 42),
    (5, 62),
    (68, 77),
    (9, 123),
    (68, 150),
    (6, 184),
    (53, 203),
    (4, 247),
    (47, 255),
    (9, 285),
    (55, 313),
    (7, 351),
    (63, 371),
    (13, 401),
    (83, 433),
    (8, 469),
    (0, 413),
    (2, 56),
]

fig5 = [
    (639, 449),
    (0, 342),
    (0, 104),
    (639, 21),
    (638, 88),
    (0, 230),
    (639, 391),
]

polygons = (fig1, fig2, fig3, fig4)
polygons = (fig5,)


class TestingBall(arkanoid.Ball):

    def refresh(self):
        for polygon in polygons:
            self.intersect_with_polygon(polygon.copy())
        arkanoid.DynamicGameObject.refresh(self)


class TestBallPath:

    WIDTH = 640
    HEIGHT = 480

    def __init__(self):
        pygame.display.set_caption('Ball Path Testing')
        self.bg_color = (0, 0, 255)
        self.screen = pygame.display.set_mode(
            (self.WIDTH, self.HEIGHT)
        )
        speed = -20
        #self.ball = TestingBall(600, 400, 7, speed, speed, self)
        self.ball = TestingBall(
            614.8704199262805, 232.3800416326503,
            7,
            28.258470778887805, -1.2078200357437066,
            self
        )
        self.debug = False
        self.ball.show()


    def run(self):
        clock = pygame.time.Clock()

        while True:
            self.screen.fill(self.bg_color)
            for polygon in polygons:
                pygame.draw.polygon(self.screen, (255, 0, 0), polygon)
            self.ball.refresh()
            self.f()
            # print(self.ball.x, self.ball.y, self.ball.speed_x, self.ball.speed_y)
            pygame.display.flip()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    print(str(event.pos) + ',')

            # clock.tick(60)

    def f(self):
        x0 = self.ball.x + self.ball.radius
        y0 = self.ball.y + self.ball.radius
        x1 = x0 + self.ball.speed_x
        y1 = y0 + self.ball.speed_y
        pygame.draw.line(self.screen, (0, 255, 0), (x0, y0), (x1, y1))

if __name__ == '__main__':
    test = TestBallPath()
    test.run()