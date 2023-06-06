import pygame

from scenes.PlaneFightScene import PlaneFightScene
from scenes.PlaneObstacleScene import PlaneObstacleScene
from scenes.PlaneMusicScene import PlaneMusicScene
from game import Scene, GameManager, SCREEN_HEIGHT, SCREEN_WIDTH, text_objects, getFont


class Button:
    # rect:中心的坐标
    def __init__(self, width, height, rectCenter, color, text, mouseDownEvent, scene):
        self.width = width
        self.visibleWidth = width
        self.height = height
        self.visibleHeight = height
        self.center = rectCenter
        self.color = color
        font = getFont(30)
        self.msg_image = font.render(text, True, (255, 255, 255), self.color)
        self.scene = scene
        self.mouseDownEvent = mouseDownEvent

    def draw(self, screen):
        r = pygame.Rect(0, 0, self.visibleWidth, self.visibleHeight)
        r.center = self.center
        screen.fill(self.color, r)
        r = self.msg_image.get_rect()
        r.center = self.center
        screen.blit(self.msg_image, r)

    def testMouse(self):
        x, y = self.scene.gameManager.getPointerPos()
        inside = (x > self.center[0] - self.width / 2) and (x < self.center[0] + self.width / 2) and \
                 (y > self.center[1] - self.height / 2) and (y < self.center[1] + self.height / 2)
        if inside:
            self.visibleWidth = self.width * 1.1
            self.visibleHeight = self.height * 1.1
            if self.scene.gameManager.getIsThumbUp():
                self.scene.gameManager.resetThumbCoolDown()
                self.mouseDownEvent()
        else:
            self.visibleWidth = self.width
            self.visibleHeight = self.height


class StartMenuScene(Scene):
    def __init__(self, gameManager: 'GameManager'):
        super().__init__(gameManager)
        # 绘制“飞机大战”文本框
        largeText = getFont(80)
        self.TextSurf, self.TextRect = text_objects('飞机大战', largeText)
        self.TextRect.center = ((SCREEN_WIDTH / 2), (SCREEN_HEIGHT / 3) - 100)
        # 设置按钮的尺寸和其他属性
        width, height = 200, 50

        # 创建按钮的rect对象，居中
        screen_rect = self.gameManager.screen.get_rect()
        self.rect = pygame.Rect(0, 0, width, height)
        cx, cy = screen_rect.center
        self.btn1 = Button(200, 50, (cx, cy - 130), (0, 255, 0), "飞机空战", self.startPlaneFight, self)
        self.btn2 = Button(200, 50, (cx, cy - 60), (255, 0, 0), "飞机避障", self.startPlaneAvoidObstacle, self)
        self.btn3 = Button(200, 50, (cx, cy + 10), (0, 0, 255), "飞机音游", self.startPlaneRhythm, self)
        self.btn4 = Button(200, 50, (cx, cy + 80), (0, 0, 0), "退出游戏", self.quit, self)

    def drawFrame(self):
        # 开始界面
        self.gameManager.screen.blit(self.TextSurf, self.TextRect)

        # self.gameManager.screen.blit(self.msg_image, self.msg_image_rect)
        self.btn1.draw(self.gameManager.screen)
        self.btn2.draw(self.gameManager.screen)
        self.btn3.draw(self.gameManager.screen)
        self.btn4.draw(self.gameManager.screen)
        self.btn1.testMouse()
        self.btn2.testMouse()
        self.btn3.testMouse()
        self.btn4.testMouse()

    def startPlaneFight(self):
        self.gameManager.switchScene(PlaneFightScene(self.gameManager), False)

    def startPlaneAvoidObstacle(self):
        self.gameManager.switchScene(PlaneObstacleScene(self.gameManager), False)

    def startPlaneRhythm(self):
        self.gameManager.switchScene(PlaneMusicScene(self.gameManager), False)

    def quit(self):
        self.gameManager.endScene()
