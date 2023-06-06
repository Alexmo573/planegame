import pygame
import pygame.display
import random
import pygame.font
import os
from game import Scene, GameManager, SCREEN_HEIGHT, SCREEN_WIDTH, mid, getFont
from scenes.GameOverScene import GameOverScene
from scenes.GameWinScene import GameWinScene


# 玩家飞机类
class Player(pygame.sprite.Sprite):
    def __init__(self, plane_img, player_rect, init_pos):
        pygame.sprite.Sprite.__init__(self)
        self.image = []  # 用来存储玩家飞机图片的列表
        for i in range(len(player_rect)):
            self.image.append(plane_img.subsurface(
                player_rect[i]).convert_alpha())
        self.rect = player_rect[0]  # 初始化图片所在的矩形
        self.rect.topleft = init_pos  # 初始化矩形的左上角坐标
        self.speed = 8  # 初始化玩家飞机速度，这里是一个确定的值
        self.bullets = pygame.sprite.Group()  # 玩家飞机所发射的子弹的集合
        self.is_hit = False  # 玩家是否被击中

    def move(self, dx, dy):
        self.rect.left = mid(0, self.rect.left + dx * self.speed * 20, SCREEN_WIDTH - self.rect.width)
        self.rect.top = mid(0, self.rect.top + dy * self.speed * 20, SCREEN_HEIGHT - self.rect.height)


class Enemy(pygame.sprite.Sprite):
    def __init__(self, enemy_img, enemy_down_imgs, init_pos,note: int):
        pygame.sprite.Sprite.__init__(self)
        self.image = enemy_img
        self.rect = self.image.get_rect()
        self.rect.topleft = init_pos
        self.rect.top -= self.rect.height
        self.down_imgs = enemy_down_imgs
        self.speed = 10
        self.note = note

    # 敌机移动，边界判断及删除在游戏主循环里处理
    def move(self):
        self.rect.top += self.speed


little_star = [1, 1, 5, 5, 6, 6, 5, 4, 4, 3, 3, 2, 2, 1, 5, 5, 4, 4, 3, 3, 2, 5, 5, 4, 4, 3, 3, 2, 1, 1, 5, 5, 6, 6,
               5, 4, 4, 3, 3, 2, 2, 1]  # 小星星简谱


class PlaneMusicScene(Scene):
    def __init__(self, gameManager: 'GameManager'):
        # 初始化射击及敌机移动频率
        super().__init__(gameManager)
        self.showPointer = False
        self.shoot_frequency = 0
        self.enemy_frequency = 0

        # 总音符数
        self.noteCount = len(little_star)
        # 初始化分数
        self.score = 0
        # 总共发射了多少音符
        self.notePlayed = 0
        # 多少音符被玩家击中或到底部消失
        self.noteCompleted = 0
        if os.path.exists('data1.txt'):
            with open('data1.txt', 'r') as f:
                self.max_score = eval(f.read())
        else:
            self.max_score = 0

        # 飞机及子弹图片集合
        plane_img = pygame.image.load('resources/image/shoot.png')

        # 设置玩家飞机不同状态的图片列表，多张图片展示为动画效果
        player_rect = [pygame.Rect(0, 99, 102, 126), pygame.Rect(165, 234, 102, 126)]

        player_pos = [200, 600]
        self.player = Player(plane_img, player_rect, player_pos)

        # 子弹图片
        bullet_rect = pygame.Rect(1004, 987, 9, 21)
        self.bullet_img = plane_img.subsurface(bullet_rect)

        # 敌机不同状态的图片列表，包括正常敌机，爆炸的敌机图片
        self.enemy1_rect = pygame.Rect(534, 612, 57, 43)
        self.enemy1_img = plane_img.subsurface(self.enemy1_rect)
        self.enemy1_down_imgs = plane_img.subsurface(pygame.Rect(267, 347, 57, 43))

        # 存储敌机，管理多个对象
        self.enemies1 = pygame.sprite.Group()

        # 存储被击毁的飞机
        self.enemies_down = pygame.sprite.Group()
        self.isMoving = False
        self.timeTillShowGameOver = 5

        self.score_font = getFont(20)

        self.enemy_frequency = 0

        # 音乐处理
        s = 'resources/sound'
        self.sounds = [
            pygame.mixer.Sound(os.path.join(s, '1.mp3')),
            pygame.mixer.Sound(os.path.join(s, '2.mp3')),
            pygame.mixer.Sound(os.path.join(s, '3.mp3')),
            pygame.mixer.Sound(os.path.join(s, '4.mp3')),
            pygame.mixer.Sound(os.path.join(s, '5.mp3')),
            pygame.mixer.Sound(os.path.join(s, '6.mp3')),
            pygame.mixer.Sound(os.path.join(s, '7.mp3')),
            pygame.mixer.Sound(os.path.join(s, '8.mp3'))
        ]

    def playNote(self, note: int):
        if 0 < note <= len(self.sounds):
            pygame.mixer.Sound.play(self.sounds[note - 1])

    def drawFrame(self):
        self.gameManager.screen.blit(self.player.image[0], self.player.rect)  # 将正常飞机画出来

        if self.score >= self.noteCount or self.noteCompleted >= self.noteCount:
            if self.score > self.max_score:
                max_score = self.score
                with open('data1.txt', 'w') as f:
                    f.write(str(max_score))
            self.gameManager.switchScene(GameWinScene(self.gameManager, self.score, self.max_score), True)
            return

        # 生成敌机，需要控制生成频率
        # 循环50次生成一架敌机
        if self.enemy_frequency % 20 == 0 and self.notePlayed < self.noteCount:
            enemy1_pos = [random.randint(0, SCREEN_WIDTH - self.enemy1_rect.width), 0]
            enemy1 = Enemy(self.enemy1_img, self.enemy1_down_imgs, enemy1_pos, little_star[self.notePlayed])
            self.enemies1.add(enemy1)
            self.notePlayed += 1
        self.enemy_frequency += 1
        if self.enemy_frequency >= 100:
            self.enemy_frequency = 0

        for enemy in self.enemies1:
            # 2. 移动敌机
            enemy.move()
            # 3. 敌机与玩家飞机碰撞效果处理
            if pygame.sprite.collide_circle(enemy, self.player):
                self.enemies_down.add(enemy)
                self.enemies1.remove(enemy)
                self.player.is_hit = False
                break
            # 4. 移动出屏幕后删除敌人
            if enemy.rect.top > SCREEN_HEIGHT:
                self.enemies1.remove(enemy)
                self.noteCompleted += 1
            # TODO 没打中要扣分？

        # 敌机被子弹击中效果显示
        for enemy_down in self.enemies_down:
            self.enemies_down.remove(enemy_down)
            self.score += 1
            self.noteCompleted += 1
            self.playNote(little_star[self.score])
            self.gameManager.screen.blit(enemy_down.down_imgs, enemy_down.rect)  # 将爆炸的敌机画出来

        # 显示敌机
        self.enemies1.draw(self.gameManager.screen)

        dx, dy, move = self.gameManager.getHandDeltaPos()
        if move:
            self.player.move(dx, dy)

        score_text = self.score_font.render('score: {}/42 max score: {}'.format(str(self.score), self.max_score), True,
                                            (128, 128, 128))
        text_rect = score_text.get_rect()
        text_rect.topleft = [10, 10]
        self.gameManager.screen.blit(score_text, text_rect)
