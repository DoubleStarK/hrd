import sys
from copy import deepcopy
import pygame
from pygame.locals import *

RED = (255, 0, 0)
RED2 = (255, 0, 100)
RED3 = (255, 100, 0)
GREEN = (0, 255, 0)
GREEN2 = (0, 100, 0)
BLUE = (0, 100, 255)
YELLOW = (255, 255, 0)
YELLOW2 = (100, 100, 0)
PURPLE = (0, 255, 255)
PURPLE2 = (0, 100, 100)
WHITE = (255, 255, 255)
movable_heros = []


class HStatus:
    """存储当前棋盘状态， 并获取下一步所有可能的状态。
    初始化参数：某个棋盘状态。
    初始化之前，一定要先调用movable_check_4d更新每个英雄的可移动列表。
    初始化之后，需要调用get_nextstatus才能获取到接下来的状态。"""

    def __init__(self, game_box: list):
        self.status = deepcopy(game_box)
        self.next_status = []

    def __eq__(self, other):
        if self.status == other.status:
            return True
        else:
            return False

    def print_info(self):
        """输出当前棋盘状态和所有下一步状态， 测试用"""
        for each in self.status:
            print(each)
        for each in self.next_status:
            for i in each:
                print(i)

    def _move_by_name(self, name: str, direction: str):
        """根据名字和方向， 移动某一个英雄"""
        temp = deepcopy(self.status)
        for hero in temp:
            if hero.name == name:
                hero.move(direction)
        return temp

    def get_nextstatus(self) -> list:
        """根据当前棋盘状态， 获取所有下一步可能状态"""
        for hero in self.status:
            # print(hero.name)
            if hero.movable:
                for next_move in hero.movable:
                    # print(next_move)
                    self.next_status.append(self._move_by_name(hero.name, next_move))

        return self.next_status


class Hero:
    """英雄类"""

    def __init__(self, pos: tuple, size: tuple, _color: tuple, name):
        self.unit = 80
        self.color = _color
        self.name = name
        self.rect = pygame.Rect((pos[0] * self.unit, pos[1] * self.unit), (size[0] * self.unit, size[1] * self.unit))
        self.movable = []

    def __eq__(self, other):
        if self.rect == other.rect and self.name == other.name:
            return True
        else:
            return False

    def __str__(self):
        return str({'name': self.name, 'rect': self.rect})

    def move(self, direction: str):
        if direction == 'r':
            self.rect = pygame.Rect.move(self.rect, self.unit, 0)
        elif direction == 'l':
            self.rect = pygame.Rect.move(self.rect, -self.unit, 0)
        elif direction == 'u':
            self.rect = pygame.Rect.move(self.rect, 0, -self.unit)
        elif direction == 'd':
            self.rect = pygame.Rect.move(self.rect, 0, self.unit)
        # 移动一次就重置列表

    def draw(self, screen):
        # screen.fill(WHITE)
        pygame.draw.rect(screen, self.color, self.rect, 0)
        text = pygame.font.SysFont('华文仿宋', 15)
        text_fmt = text.render(self.name, True, (0, 0, 0))
        screen.blit(text_fmt, (self.rect.centerx - text_fmt.get_rect().width / 2,
                               self.rect.centery - text_fmt.get_rect().height / 2))


def movable_check_1d(game_box: list, direction: str, screen: pygame.Surface):
    """检查可以移动的英雄(针对某一个方向), 并将每个英雄可移动的方向添加到英雄的属性中"""
    flag = 0
    for hero in game_box:
        _index = game_box.index(hero)
        temp_hero = game_box.pop(_index)  # 取出一个英雄
        # after move still in screen and not collided with others
        temp_rect = None
        temp_rect_r = pygame.Rect.move(temp_hero.rect, temp_hero.unit, 0)
        temp_rect_l = pygame.Rect.move(temp_hero.rect, -temp_hero.unit, 0)
        temp_rect_u = pygame.Rect.move(temp_hero.rect, 0, -temp_hero.unit)
        temp_rect_d = pygame.Rect.move(temp_hero.rect, 0, temp_hero.unit)
        if direction == 'r':
            temp_rect = temp_rect_r
        elif direction == 'l':
            temp_rect = temp_rect_l
        elif direction == 'u':
            temp_rect = temp_rect_u
        elif direction == 'd':
            temp_rect = temp_rect_d

        for each in game_box:  # 与未取出的进行碰撞比较
            if each.rect.colliderect(temp_rect):
                # 如果这个英雄移动后发生碰撞, 则跳过
                flag = 1
                break
        if flag == 0 and screen.get_rect().contains(temp_rect):
            # 进行到这里, 说明这个英雄移动后没有发生碰撞, 再判断其是否在棋盘内
            # 若在棋盘内, 则英雄移动没有问题, 把此方向添加到movable中
            # 并且, 将这个可移动的英雄记录下来
            temp_hero.movable.append(direction)
            movable_heros.append(temp_hero)
        game_box.insert(_index, temp_hero)  # 放回英雄
        flag = 0


def movable_check_4d(game_box: list, screen: pygame.Surface):
    """检查可以移动的英雄(针对四个方向), 并将每个英雄可移动的方向添加到英雄的属性中"""
    directions = ['d', 'l', 'u', 'r']
    # 先清除每个英雄可移动的方向
    for hero in game_box:
        hero.movable.clear()
    # 再清除所有可移动英雄
    movable_heros.clear()

    for direction in directions:
        movable_check_1d(game_box, direction, screen)


def print_info(game_box: list):
    for hero in game_box:
        print(hero.name, hero.movable)


def deep_first_search(game_box: list, screen: pygame.Surface):
    """深度优先搜索，解谜华容道"""
    stack = [[], []]  # 状态栈[[状态][深度]], 左低右顶
    record = [[], []]  # 出栈记录， 用于回溯
    deep = 0  # 搜索深度
    flag = 0
    movable_check_4d(game_box, screen)
    current_status = game_box
    while True:
        current_status = HStatus(current_status)
        movable_check_4d(current_status.status, screen)
        next_status = current_status.get_nextstatus()
        temp = []
        for s in next_status:
            if s not in stack[0] and s not in record[0]:
                temp.append(s)
                flag = 1  # 发生入栈
            else:
                print('有重复！')
        if flag:
            # 如果发生入栈
            flag = 0
            if deep + 1 <= 300:
                deep += 1
                print('入栈！', deep)
                for t in temp:
                    stack[0].append(t)
                    stack[1].append(deep)

        current_status = stack[0].pop()
        record[0].append(current_status)
        record[1].append(deep)
        deep = stack[1].pop()
        print('出栈！', deep)
        print(len(record[0]), len(record[1]), len(stack[0]), len(stack[1]))
        yield current_status


def main():
    # 一些初始化
    pygame.init()
    pygame.font.init()
    screen = pygame.display.set_mode((320, 400))
    pygame.display.set_caption('华容道')
    clock = pygame.time.Clock()
    # 英雄
    cc = Hero((1, 0), (2, 2), RED, '曹操0')
    zy = Hero((0, 0), (1, 2), GREEN, '赵云1')
    mc = Hero((3, 0), (1, 2), BLUE, '马超2')
    hz = Hero((0, 2), (1, 2), PURPLE, '黄忠3')
    gy = Hero((1, 2), (2, 1), YELLOW, '关羽4')
    zf = Hero((3, 2), (1, 2), PURPLE2, '张飞5')
    a = Hero((0, 4), (1, 1), RED2, '甲6')
    b = Hero((1, 3), (1, 1), GREEN2, '乙7')
    c = Hero((2, 3), (1, 1), YELLOW2, '丙8')
    d = Hero((3, 4), (1, 1), RED3, '丁9')
    game_box = [cc, zy, mc, hz, gy, zf, a, b, c, d]  # 棋盘
    hero_index = 0  # 当前英雄序号
    game_box = deep_first_search(game_box, screen)
    # 主循环
    run = True
    while run:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                # movable_check_4d(game_box, screen)
                # print_info(heros)
                if event.key == K_DOWN and 'd' in game_box[hero_index].movable:
                    game_box[hero_index].move('d')
                elif event.key == K_UP and 'u' in game_box[hero_index].movable:
                    game_box[hero_index].move('u')
                elif event.key == K_LEFT and 'l' in game_box[hero_index].movable:
                    game_box[hero_index].move('l')
                elif event.key == K_RIGHT and 'r' in game_box[hero_index].movable:
                    game_box[hero_index].move('r')
                elif event.key == K_z:
                    if hero_index == 9:
                        hero_index = 0
                    else:
                        hero_index += 1
                    print('当前英雄序号：', hero_index)
                elif event.key == K_SPACE:
                    pass

        screen.fill(WHITE)
        for hero in next(game_box):
            hero.draw(screen)
            if hero.name == '丁9' and hero.rect.topleft == (0, 320):
                pygame.quit()
                sys.exit()
        pygame.display.flip()
        clock.tick(3)


if __name__ == '__main__':
    main()
