import random
import pygame
import pygame.font
import os
from sys import exit

# 设置游戏屏幕大小
SCREEN_WIDTH = 480
SCREEN_HEIGHT = 800
# 初始化 pygame
pygame.init()

# 设置游戏界面大小、背景图片及标题
# 游戏界面像素大小
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
# 创建时钟对象
clock = pygame.time.Clock()
# 背景图
background = pygame.image.load('resources/image/background.png').convert()

#障碍原始图片
obstacle_raw_img = pygame.image.load('resources/image/obstacle.PNG')
done = False


class Player(pygame.sprite.Sprite):
    def __init__(self, plane_img, player_rect, init_pos):
        pygame.sprite.Sprite.__init__(self)
        self.image = []                                 # 用来存储玩家飞机图片的列表
        for i in range(len(player_rect)):
            self.image.append(plane_img.subsurface(
                player_rect[i]).convert_alpha())
        self.rect =self.image[0].get_rect()              # 初始化图片所在的矩形
        self.rect.topleft = init_pos                    # 初始化矩形的左上角坐标
        self.speed = 8                                  # 初始化玩家飞机速度，这里是一个确定的值
        self.bullets = pygame.sprite.Group()            # 玩家飞机所发射的子弹的集合
        self.is_hit = False                             # 玩家是否被击中


#障碍组成部分
class obstacle_brick(pygame.sprite.Sprite):
    def __init__(self,image,init_pos):
        pygame.sprite.Sprite.__init__(self)
        self.image=image
        self.rect=self.image.get_rect()
        self.rect.topleft=init_pos
        self.speed=1
    def move(self):
        self.rect.top +=self.speed
#障碍物类
class obstacle(pygame.sprite.Sprite):
    def __init__(self,obstacle_img,gap_pos,gap_len,screen):
        pygame.sprite.Sprite.__init__(self)
        self.image=obstacle_img
        #左边障碍
        self.left_obstacle=pygame.sprite.Group()
        #左边障碍终点
        self.left_end=gap_pos
        self.left_len=0
        #右边障碍
        self.right_obstacle=pygame.sprite.Group()
        #右边障碍长度
        self.right_len=gap_pos+gap_len
        self.img_rect=self.image.get_rect()
        #self.rect.topleft=gap_pos
        self.speed=1
        self.screen=screen
        self.arrange()
    #排列障碍，形成一列障碍
    def arrange(self):
        #生成左边障碍
        while self.img_rect[2] + self.left_len< self.left_end:
            self.left_obstacle.add(obstacle_brick(self.image,[self.left_len,0]))
            self.left_len+=self.img_rect[2]
        #生成右边障碍
        while self.right_len<SCREEN_WIDTH:
            self.right_obstacle.add(obstacle_brick(self.image,[self.right_len,0]))
            self.right_len+=self.img_rect[2]
        # 画出障碍
        self.left_obstacle.draw(self.screen)
        self.right_obstacle.draw(self.screen)

    def move(self):
        #画出障碍，然后移动
        for brick in self.left_obstacle:
            brick.move()
            #障碍离开屏幕，删除
            if brick.rect.top<0:
                self.left_obstacle.remove()
                break
        for brick in self.right_obstacle:
            brick.move()
            if brick.rect.top<0:
                self.right_obstacle.remove()
                break
        #画出障碍
        self.left_obstacle.draw(self.screen)
        self.right_obstacle.draw(self.screen)

#障碍图，从障碍原始图中取出一部分
obstacle_img=obstacle_raw_img.subsurface(pygame.Rect(10,10,35,35))
#存储障碍，管理多个对象
obstacles=pygame.sprite.Group()
#obstacle生成频率
obstacle_frequency=0
#随机频率的标志
time_isused=False
times=200


# 飞机及子弹图片集合
plane_img = pygame.image.load('resources/image/shoot.png')

# 设置玩家飞机不同状态的图片列表，多张图片展示为动画效果
player_rect = []
player_rect.append(pygame.Rect(0, 99, 102, 126))        # 玩家飞机图片
player_rect.append(pygame.Rect(165, 234, 102, 126))     # 玩家爆炸图片

player_pos = [200, 600]
player = Player(plane_img, player_rect, player_pos)
player_g=pygame.sprite.Group()
player_g.add(player)


while not done:
    screen.fill(0)
    #循环50次生成一个障碍
    if time_isused:
        #从新生成一个随机频率，标志改变
        times = random.randint(100, 300)
        time_isused = False
    if obstacle_frequency % times==0:
        #标志为已使用
        time_isused=True
        #频率计数为0
        obstacle_frequency = 0

        gap_len=random.randint(0,25)+25
        gap_start=random.randint(0,SCREEN_WIDTH-gap_len)
        obstacle_1=obstacle(obstacle_img,gap_start,gap_len,screen)
        obstacles.add(obstacle_1)
    obstacle_frequency+=1

    # 绘制玩家飞机
    if not player.is_hit:
        screen.blit(player.image[0], player.rect)  # 将正常飞机画出来
    else:
        # 玩家飞机被击中后的效果处理
        screen.blit(player.image[1], player.rect)  # 将爆炸的飞机画出来
        done = True
    for ob in obstacles:
        #移动障碍
        ob.move()
        #障碍与飞机碰撞
        if pygame.sprite.groupcollide(ob.left_obstacle,player_g,False,False) \
                or pygame.sprite.groupcollide(ob.right_obstacle,player_g,False,False):
            player.is_hit=True
            break


    # screen.blit(, (0, 0))
    # screen.blit(obstacle_img,(5,52))
    # 更新窗口
    pygame.display.update()

    # 控制游戏帧率
    clock.tick(60)
    # 处理事件
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True
        elif event.type == pygame.MOUSEBUTTONDOWN:
            print("鼠标点击")
# 游戏 Game Over 后显示最终得分
font = pygame.font.Font(None, 64)
# 显示得分并处理游戏退出
while 1:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
    pygame.display.update()