__author__ = 'Kovrizhnykh Alexey'

import math
import pygame
import geometry
from geometry import Vector
import random
import time


RESOURCES = 'resources'
MUSIC_AMOUNT = 4
END_MUSIC_EVENT = 42

class StaticGameObject:
    """Обобщенный статический игровой объект.
    """
    def __init__(self, x, y, h, w, parent):
        self.parent = parent
        self.visible = False
        self.x = x
        self.y = y
        self.height = h
        self.width = w
        # Создаем поверхность объекта
        # Флаг SRCALPHA включает попиксельный режим отрисовки
        self.surface = pygame.Surface((w, h), pygame.SRCALPHA)

    def refresh(self):
        pass

    def repaint(self):
        if self.visible:
            self.parent.screen.blit(self.surface, (self.x, self.y))

    def set_coord(self, x, y):
        self.x = x
        self.y = y

    def set_size(self, h, w):
        self.height = h
        self.width = w

    def show(self):
        self.visible = True

    def hide(self):
        self.visible = False

    def set_color(self, r, g, b):
        self.surface.fill((r, g, b))


class DynamicGameObject (StaticGameObject):
    """Обобщенный динамический игровой объект.
    """

    def __init__(self, x, y, h, w, parent, speed_x, speed_y):
        super().__init__(x, y, h, w, parent)
        self.speed_x = speed_x
        self.speed_y = speed_y

    def set_speed(self, speed_x, speed_y):  
        self.speed_x = speed_x
        self.speed_y = speed_y

    def increase_speed(self, mul):
        self.speed_x *= mul
        self.speed_y *= mul

    def get_speed(self):
        return math.sqrt(self.speed_x ** 2 + self.speed_y ** 2)

    def refresh(self):
        """ Метод, обновляющий положение динамического
        объекта в пространстве
        """
        # print(self.x, self.y, self.speed_x, self.speed_y)
        new_x = self.x + self.speed_x
        if new_x + self.width >= self.parent.WIDTH:
            self.speed_x *= -1
            self.x = self.parent.WIDTH - self.width
        elif new_x < 0:
            self.speed_x *= -1
            self.x = 0
        else:
            self.x = new_x

        new_y = self.y + self.speed_y
        if new_y + self.height >= self.parent.HEIGHT:
            self.speed_y *= -1
            self.y = self.parent.HEIGHT - self.height
        elif new_y < 0:
            self.speed_y *= -1
            self.y = 0
        else:
            self.y = new_y
        super().refresh()


class Ball(DynamicGameObject):
    """Игровой мяч.
    """
    def __init__(self, x, y, r, speed_x, speed_y, parent):
        super().__init__(
            x - r, y - r,
            2 * r, 2 * r,
            parent,
            speed_x, speed_y,
        )
        self.radius = r
        self.color = (246, 255, 0)
        pygame.draw.ellipse(
            self.surface,
            self.color,
            (0, 0, self.width, self.height)
        )
        # self.set_color(*self.color)

    def intersect_with_polygon(self, pts):
        current_pos = Vector(self.x + self.radius, self.y + self.radius)
        speed = Vector(self.speed_x, self.speed_y)
        new_pos = current_pos + speed

        min_dist = 1e9
        result_speed = None
        result_position = None

        # Проверяем пересечения со сторонами
        pts.append(pts[0])
        for i in range(len(pts) - 1):
            # Делаем сдвиг стороны наружу на радиус шара
            # Шар сжимаем до точки
            line = Vector(*pts[i]) - Vector(*pts[i + 1])
            norm = line.rotate(90) / abs(line)
            # a и b - новые точки сдвинутой прямой
            a = Vector(*pts[i]) + norm * self.radius
            b = Vector(*pts[i + 1]) + norm * self.radius
            intersect, intersect_point = geometry.intersect_sector_sector(
                a, b,
                current_pos,
                new_pos
            )
            if intersect and abs(intersect_point - current_pos) < min_dist:
                min_dist = abs(intersect_point - current_pos)
                if self.parent.debug:
                    self.parent.debug_line(
                        a.x, a.y, b.x, b.y
                    )
                    self.parent.debug_point(
                        intersect_point.x, intersect_point.y
                    )
                line = Vector(*pts[i]) - Vector(*pts[i + 1])
                angle_cos = speed.scalar_mul(line) / \
                    (abs(speed) * abs(line))
                angle = math.acos(angle_cos)
                angle = angle / math.pi * 180
                result_speed = speed.rotate(2 * angle)
                result_position = intersect_point

        # Проверка пересечения с углами
        for x, y in pts:
            point = Vector(x, y)
            # Ищем точки пересечения вектора скорости мяча
            # с окружностью в точке прямоугольника и радиуса мяча
            intersect_points = geometry.intersect_line_circle(
                current_pos, speed,
                point, self.radius
            )
            # Перебираем точки пересечения и выбираем нужную
            for intersect_point in intersect_points:
                if abs(intersect_point - current_pos) > abs(speed):
                    continue
                if (intersect_point - current_pos).scalar_mul(speed) <= 0:
                    continue
                if abs(intersect_point - current_pos) >= min_dist:
                    continue
                min_dist = abs(intersect_point - current_pos)
                if self.parent.debug:
                    self.parent.debug_point(
                        intersect_point.x, intersect_point.y
                    )
                # Получаем направляющий вектор касательной
                # к окружности в найенной точке
                tangent = (point - intersect_point).rotate(90)
                # Найдем косинус угла между вектором скорости и
                # касательной
                angle_cos = speed.scalar_mul(tangent) /\
                    (abs(speed) * abs(tangent))
                # Переведем угол в градусы
                angle = math.acos(angle_cos)
                angle = angle / math.pi * 180
                result_speed = speed.rotate(2 * angle)
                result_position = intersect_point

        if result_speed and result_position:
            self.speed_x = result_speed.x
            self.speed_y = result_speed.y
            self.x = result_position.x - self.radius - self.speed_x * 0.9
            self.y = result_position.y - self.radius - self.speed_y * 0.9
            return True
        return False

    def intersect_with_react(self, react):
        x = react.x
        y = react.y
        w = react.width
        h = react.height
        return self.intersect_with_polygon(
            [(x, y), (x + w, y), (x + w, y + h), (x, y + h)]
        )

    def refresh(self):

        for obj in self.parent.blocks:
            if obj.lives == 0:
                continue
            if self.intersect_with_react(obj):
                obj.hit()
                if self.parent.debug:
                    self.parent.debug_line(
                        self.x + self.radius,
                        self.y + self.radius,
                        self.x + 25 * self.speed_x + self.radius,
                        self.y + 25 * self.speed_y + self.radius
                    )
                break

        # panel
        if self.intersect_with_react(self.parent.panel):
            self.y += self.speed_y
            self.x += self.speed_x
            speed = self.parent.panel.speed_x
            if speed != 0:
                ball_speed_vec = Vector(self.speed_x, self.speed_y)
                rotate_angle = random.randint(1, 15)
                ball_speed_vec = ball_speed_vec.rotate(
                    speed / 3 * rotate_angle
                )
                self.speed_x = ball_speed_vec.x
                self.speed_y = ball_speed_vec.y

        if self.y + self.speed_y + 2 * self.radius > self.parent.HEIGHT:
            self.parent.lose_ball()

        # super refreshing
        super().refresh()


class Block (StaticGameObject):
    """Игровой блок. Статический объект, который разрушается
    после нескольких ударов мячем по нему.
    """
    def __init__(self, x, y, h, w, parent, lives):
        super().__init__(x, y, h, w, parent)
        self.lives = lives
        self.set_color(0, 255, 0)

    def hit(self):
        self.lives -= 1
        if self.lives == 3:
            self.surface.fill((0, 200, 0))
        elif self.lives == 2:
            self.surface.fill((0, 150, 0))
        elif self.lives == 1:
            self.surface.fill((0, 100, 0))
        else:
            self.hide()


class Panel (DynamicGameObject):
    """Панель, урпвляемая пользователем.
    """
    def __init__(self, x, y, h, w, parent):
        super().__init__(x, y, h, w, parent, 0, 0)
        self.set_color(255, 0, 0)

    def refresh(self):
        # print(self.x, self.y, self.speed_x, self.speed_y)
        self.x += self.speed_x
        self.y += self.speed_y
        if self.x + self.width >= self.parent.WIDTH or self.x < 0:
            self.speed_x = 0
        super().refresh()


class Option:

    def __init__(self, name):
        self.normal_image = pygame.image.load(
            RESOURCES + '/menu/' + name + '_normal.png'
        )
        self.hover_image = pygame.image.load(
            RESOURCES + '/menu/' + name + '_hover.png'
        )
        self.rect = self.normal_image.get_rect()
        self.handler = None
        self.enabled = False

    def set_handler(self, handler):
        self.handler = handler

    def onclick(self):
        if callable(self.handler):
            self.handler()


class Menu (StaticGameObject):

    def __init__(self, parent):
        super().__init__(0, 0, parent.HEIGHT, parent.WIDTH, parent)
        self.parent = parent
        self.visible = True
        resume_opt = Option('resume')
        resume_opt.set_handler(self.resume)
        new_game_opt = Option('new_game')
        new_game_opt.set_handler(self.new_game)
        quit_opt = Option('quit')
        quit_opt.set_handler(self.quit)
        self.options = [
            resume_opt,
            new_game_opt,
            quit_opt
        ]
        self.up_padding = 100

    def refresh(self):
        if not self.visible:
            return
        self.surface.fill((0, 0, 0, 100))
        mouse_pos_x, mouse_pos_y = pygame.mouse.get_pos()
        left_pressed = pygame.mouse.get_pressed()[0]
        pos_x = self.parent.WIDTH // 2 - 150
        for i, option in enumerate(self.options):
            pos_y = 100 * i + self.up_padding
            if pos_x < mouse_pos_x < pos_x + 300 and \
                    100 * i < mouse_pos_y - self.up_padding < 100 * (i + 1):
                if left_pressed:
                    option.onclick()
                self.surface.blit(option.hover_image, (pos_x, pos_y))
            else:
                self.surface.blit(option.normal_image, (pos_x, pos_y))
        super().refresh()

    def new_game(self):
        self.hide()
        self.parent.start_game()

    def quit(self):
        exit()

    def resume(self):
        if self.parent.pause:
            self.hide()
            self.parent.pause = False
            self.parent.runnable = True


class LiveIndicator(StaticGameObject):

    def __init__(self, parent):
        super().__init__(0, 0, 25, 75, parent)
        self.heart_image = pygame.image.load(
            RESOURCES + '/heart.png'
        )

    def refresh(self):
        self.surface.fill((0, 0, 0, 0))
        for i in range(self.parent.lives):
            self.surface.blit(self.heart_image, (i * 25, 0))


class Label(StaticGameObject):

    def __init__(self, name, parent):
        super().__init__(0, 0, parent.HEIGHT, parent.WIDTH, parent)
        image_number = random.randint(0, 5)
        directory = RESOURCES + '/' + name + '/'
        image = pygame.image.load(
            directory + name + '_' + str(image_number) + '.png'
        )
        self.surface.blit(image, (0, 0))
        self.show()

    def refresh(self):
        if any(pygame.mouse.get_pressed()):
            pygame.mouse.set_pos((0, 0))
            self.parent.label = None


class LoseLabel(Label):

    def __init__(self, parent):
        super().__init__('lose', parent)


class WinLabel(Label):

    def __init__(self, parent):
        super().__init__('win', parent)


class ArkanoidGame:
    """Основной игровой класс, который инициализирует игровое
    поле и все динамические и статические объекты на нем, а
    также отвечает за обновление состояния игры
    """

    WIDTH = 640
    HEIGHT = 480

    def __init__(self, debug=False):
        pygame.init()
        pygame.display.set_caption('Arkanoid')
        self.bg_color = (39, 15, 157)
        # self.bg_color = (255, 255, 255)
        self.debug = debug
        self.runnable = False
        self.pause = False
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        self.label = None
        self.live_indicator = LiveIndicator(self)
        self.live_indicator.show()

        self.music_list = []
        for i in range(MUSIC_AMOUNT):
            music_name = RESOURCES + '/music/sound_' + str(i) + '.mp3'
            self.music_list.append(music_name)
        self.play_random_music()

        self.blocks = []
        self.stars = []
        self.debug_obj = []
        self.panel = None
        self.ball = None
        self.game_menu = Menu(self)
        self.lives = 0

        # Генерация звезд
        for i in range(30):
            r = random.randint(3, 5)
            obj = DynamicGameObject(
                random.randint(0, self.WIDTH),
                random.randint(0, self.HEIGHT),
                r, r,
                self,
                10 * random.random(),
                10 * random.random(),
            )
            pygame.draw.ellipse(
                obj.surface,
                (255, 255, 0),
                (0, 0, obj.width, obj.height)
            )
            obj.show()
            self.stars.append(obj)

    def play_random_music(self):
        pygame.mixer.music.load(random.choice(self.music_list))
        pygame.mixer.music.play()
        pygame.mixer.music.set_endevent(END_MUSIC_EVENT)

    def start_game(self):

        self.blocks = []
        self.debug_obj = []
        self.panel = None
        self.ball = None
        self.lives = 3

        # Добавление игровой панели

        # Генерация блоков
        for i in range(5):
            for j in range(10):
                self.blocks.append(
                    Block(
                        50 + j * 55,
                        50 + i * 25,
                        20, 50, self,
                        3
                    )
                )

        self.drop_ball()
        self.drop_panel()

        # Показать все блоки
        for obj in self.blocks:
            obj.show()
        self.runnable = True

    def drop_ball(self):
        self.ball = Ball(self.WIDTH // 2, self.HEIGHT // 2, 5, 0, 4, self)
        self.ball.show()

    def drop_panel(self):
        self.panel = Panel(
            self.WIDTH / 2 - 50,
            self.HEIGHT - 20,
            10, 100, self
        )
        self.panel.show()

    def lose_ball(self):
        self.lives -= 1
        if self.lives > 0:
            self.drop_ball()
            self.drop_panel()
        else:
            self.lose()

    def lose(self):
        self.label = LoseLabel(self)
        self.runnable = False
        self.game_menu.show()

    def win(self):
        self.label = WinLabel(self)
        self.runnable = False
        self.game_menu.show()

    def run(self):
        """Основной цикл игры, в котором происходит отрисовка всех элементов.
        """
        clock = pygame.time.Clock()
        while True:

            self.screen.fill(self.bg_color)

            # Обновление положений объектов
            for obj in self.stars:
                obj.refresh()
            if self.runnable:
                for obj in self.blocks:
                    obj.refresh()
                self.panel.refresh()
                self.ball.refresh()
                for obj in self.blocks:
                    if obj.lives == 0:
                        self.blocks.remove(obj)
                if not self.blocks:
                    self.win()

            # Отрисовка объектов
            for obj in self.stars:
                obj.repaint()
            for obj in self.blocks:
                obj.repaint()
            if self.panel:
                self.panel.repaint()
            if self.ball:
                self.ball.repaint()

            if self.debug:
                if len(self.debug_obj) > 3:
                    self.debug_obj = self.debug_obj[-25:]
                for obj in self.debug_obj:
                    obj.refresh()

            self.live_indicator.refresh()
            self.live_indicator.repaint()

            if self.label:
                self.label.repaint()
                self.label.refresh()
            else:
                self.game_menu.refresh()
                self.game_menu.repaint()

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        self.panel.speed_x = -3
                    elif event.key == pygame.K_RIGHT:
                        self.panel.speed_x = 3
                    elif event.key == pygame.K_ESCAPE:
                        self.runnable = False
                        self.pause = True
                        self.game_menu.show()
                    elif event.key == pygame.K_x:
                        if len(self.blocks) > 0:
                            obj = random.choice(self.blocks)
                            obj.hit()
                elif event.type == pygame.KEYUP:
                    if event.key in (pygame.K_LEFT, pygame.K_RIGHT):
                        self.panel.speed_x = 0
                elif event.type == END_MUSIC_EVENT:
                    self.play_random_music()

            clock.tick(60)

    def debug_point(self, x, y):
        obj = StaticGameObject(x - 4, y - 4, 8, 8, self)
        pygame.draw.line(obj.surface, (255, 0, 0), (0, 0), (7, 7))
        pygame.draw.line(obj.surface, (255, 0, 0), (0, 7), (7, 0))
        obj.show()
        self.debug_obj.append(obj)

    def debug_line(self, x0, y0, x1, y1):
        w = abs(x0 - x1)
        h = abs(y0 - y1)
        x = min(x0, x1)
        y = min(y0, y1)
        x0 -= x
        x1 -= x
        y0 -= y
        y1 -= y
        obj = StaticGameObject(x, y, h + 1, w + 1, self)
        obj.show()
        pygame.draw.line(obj.surface, (255, 0, 0), (x0, y0), (x1, y1))
        self.debug_obj.append(obj)


if __name__ == '__main__':
    game = ArkanoidGame(debug=True)
    game.run()
