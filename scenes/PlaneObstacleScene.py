import random

import pygame
from game import Scene, GameManager, SCREEN_HEIGHT, SCREEN_WIDTH, mid, getFont
from scenes.GameOverScene import GameOverScene


class Player(pygame.sprite.Sprite):
    def __init__(self, plane_img, player_rect, init_pos):
        pygame.sprite.Sprite.__init__(self)
        self.image = []  # 用来存储玩家飞机图片的列表
        for i in range(len(player_rect)):
            img = (plane_img.subsurface(
                player_rect[i]).convert_alpha())
            imgRect: 'pygame.Rect' = img.get_rect()
            self.image.append(pygame.transform.scale(img, (imgRect.w, imgRect.h)))
        self.rect = self.image[0].get_rect()  # 初始化图片所在的矩形
        self.rect.height -= 20
        self.rect.topleft = init_pos  # 初始化矩形的左上角坐标
        self.speed = 9  # 初始化玩家飞机速度，这里是一个确定的值
        self.bullets = pygame.sprite.Group()  # 玩家飞机所发射的子弹的集合
        self.is_hit = False  # 玩家是否被击中

    def move(self, dx, dy):
        self.rect.left = mid(0, self.rect.left + dx * self.speed * 10, SCREEN_WIDTH - self.rect.width)
        self.rect.top = mid(0, self.rect.top + dy * self.speed * 10, SCREEN_HEIGHT - self.rect.height)


# 障碍组成部分
class obstacle_brick(pygame.sprite.Sprite):
    def __init__(self, image, init_pos):
        pygame.sprite.Sprite.__init__(self)
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.topleft = init_pos
        self.rect.top -= self.rect.height
        self.speed = 5

    def move(self):
        self.rect.top += self.speed


# 障碍物类
class obstacle(pygame.sprite.Sprite):
    def __init__(self, obstacle_img, gap_pos, gap_len, screen):
        pygame.sprite.Sprite.__init__(self)
        self.image = obstacle_img
        # 左边障碍
        self.left_obstacle = pygame.sprite.Group()
        # 左边障碍终点
        self.left_end = gap_pos
        self.left_len = 0
        # 右边障碍
        self.right_obstacle = pygame.sprite.Group()
        # 右边障碍长度
        self.right_len = gap_pos + gap_len
        self.img_rect = self.image.get_rect()
        # self.rect.topleft=gap_pos
        #self.speed = 1
        self.screen = screen
        self.arrange()
        # 记录飞机是否已经越过本障碍物
        self.isPassed = False

    # 排列障碍，形成一列障碍
    def arrange(self):
        # 生成左边障碍
        while self.img_rect[2] + self.left_len < self.left_end:
            self.left_obstacle.add(obstacle_brick(self.image, [self.left_len, 0]))
            self.left_len += self.img_rect[2]
        # 生成右边障碍
        while self.right_len < SCREEN_WIDTH:
            self.right_obstacle.add(obstacle_brick(self.image, [self.right_len, 0]))
            self.right_len += self.img_rect[2]
        # 画出障碍
        self.left_obstacle.draw(self.screen)
        self.right_obstacle.draw(self.screen)

    # 返回是否已经离开屏幕
    def move(self) -> bool:
        # 画出障碍，然后移动
        for brick in self.left_obstacle:
            brick.move()
            # 障碍离开屏幕，删除
            if brick.rect.top > SCREEN_HEIGHT:
                self.left_obstacle.remove()
                return True
        for brick in self.right_obstacle:
            brick.move()
            if brick.rect.top > SCREEN_HEIGHT:
                self.right_obstacle.remove()
                return True
        # 画出障碍
        self.left_obstacle.draw(self.screen)
        self.right_obstacle.draw(self.screen)
        return False

    def getTop(self) -> int:
        s = self.left_obstacle.sprites()
        if len(s) > 0:
            return self.left_obstacle.sprites()[0].rect.top
        else:
            return -1


class PlaneObstacleScene(Scene):
    def __init__(self, gameManager: 'GameManager'):
        super().__init__(gameManager)
        self.showPointer = False

        # 障碍原始图片
        obstacle_raw_img = pygame.image.load('resources/image/obstacle.PNG')
        # 障碍图，从障碍原始图中取出一部分
        self.obstacle_img = obstacle_raw_img.subsurface(pygame.Rect(10, 10, 35, 35))
        plane_img = pygame.image.load('resources/image/shoot.png')

        # 随机频率的标志
        self.time_isUsed = False
        self.times = 0
        # 存储障碍，管理多个对象
        self.obstacles = pygame.sprite.Group()
        # obstacle生成频率
        self.obstacle_frequency = 0

        # 设置玩家飞机不同状态的图片列表，多张图片展示为动画效果
        # 玩家飞机图片
        # 玩家爆炸图片
        self.player_rect = [pygame.Rect(0, 99, 102, 126), pygame.Rect(165, 234, 102, 126)]

        self.player_pos = [200, 600]
        self.player = Player(plane_img, self.player_rect, self.player_pos)
        self.player_g = pygame.sprite.Group()
        self.player_g.add(self.player)

        self.timeTillShowGameOver = 5

        self.score = 0

        self.score_font = getFont(20)

    def drawFrame(self):

        # 绘制玩家飞机
        if not self.player.is_hit:
            self.gameManager.screen.blit(self.player.image[0], self.player.rect)  # 将正常飞机画出来
        else:
            # 玩家飞机被击中后的效果处理
            self.gameManager.screen.blit(self.player.image[1], self.player.rect)  # 将爆炸的飞机画出来
            self.timeTillShowGameOver -= 1
            if self.timeTillShowGameOver == 0:
                self.gameManager.switchScene(GameOverScene(self.gameManager, self.score), True)
            return

        for ob in self.obstacles:
            # 移动障碍
            isOut = ob.move()
            if isOut:
                self.obstacles.remove(ob)
            else:
                # 障碍与飞机碰撞
                if pygame.sprite.groupcollide(ob.left_obstacle, self.player_g, False, False) \
                        or pygame.sprite.groupcollide(ob.right_obstacle, self.player_g, False, False):
                    self.player.is_hit = True
                    break
                if not ob.isPassed and ob.getTop() > self.player.rect.top:
                    ob.isPassed = True
                    self.score += 1

        dx, dy, move = self.gameManager.getHandDeltaPos()
        if move:
            self.player.move(dx, dy)

        # 循环50次生成一个障碍
        if self.time_isUsed:
            # 从新生成一个随机频率，标志改变
            self.times = random.randint(55, 85)
            self.time_isUsed = False
        if self.obstacle_frequency == self.times:
            # 标志为已使用
            self.time_isUsed = True
            # 频率计数为0
            self.obstacle_frequency = 0

            # gap_len = random.randint(10, 55) + 65
            # gap_start = random.randint(0, SCREEN_WIDTH - gap_len)
            gap_len = random.randint(20, self.player.rect.width) + self.player.rect.width
            gap_start = random.randint(0, SCREEN_WIDTH - gap_len)
            obstacle_1 = obstacle(self.obstacle_img, gap_start, gap_len, self.gameManager.screen)
            self.obstacles.add(obstacle_1)
        self.obstacle_frequency += 1

        # 绘制得分
        score_text = self.score_font.render(
            'score: {}'.format(str(self.score)), True, (128, 128, 128))
        text_rect = score_text.get_rect()
        text_rect.topleft = [10, 10]
        self.gameManager.screen.blit(score_text, text_rect)