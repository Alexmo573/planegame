import pygame
from sys import exit

import pygame.display
import cv2

from scenes.StartMenuScene import StartMenuScene
import pygame.font
import os
from game import Scene, GameManager, SCREEN_WIDTH, SCREEN_HEIGHT


# 初始化 pygame
pygame.init()

# 设置游戏界面大小、背景图片及标题
# 游戏界面像素大小
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

# 游戏界面标题
pygame.display.set_caption('打飞机大战')
# 读取前置摄像头
camera = cv2.VideoCapture(0)
# 游戏循环帧率设置
clock = pygame.time.Clock()

# 判断游戏循环退出的参数
running = True

# 移动方向（初始化）
move = True

fps = 60
# 背景图
background = pygame.image.load('resources/image/background.png').convert()
gameManager = GameManager(screen)
gameManager.switchScene(StartMenuScene(gameManager), False)

# 游戏主循环
while True:
    # 控制游戏最大帧率
    clock.tick(fps)
    # 绘制背景
    screen.fill(0)
    screen.blit(background, (0, 0))

    # 更新屏幕
    gameManager.tick()
    # 处理游戏退出
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

    pygame.display.update()



