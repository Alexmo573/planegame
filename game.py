from abc import abstractmethod

import pygame
import cv2

from mediapipe_gesture_helper import mediapipe_gesture_helper

# 设置游戏屏幕大小
SCREEN_WIDTH = 480
SCREEN_HEIGHT = 800


def text_objects(text, font):
    # 将字符串转换为pygame的文本框
    textSurface = font.render(text, True, (0, 0, 0))
    return textSurface, textSurface.get_rect()


def mid(a, b, c):
    if c < a and c < b:
        return b if b < a else a
    r = a if a > b else b
    return r if r < c else c


fontDict = dict()


def getFont(size: int) -> pygame.font.Font:
    if size not in fontDict:
        newFont = pygame.font.Font('resources/font/MiSans-Medium.ttf', size)
        fontDict[size] = newFont
        return newFont
    else:
        return fontDict[size]


class Scene:
    def __init__(self, gameManager: 'GameManager'):
        self.gameManager = gameManager
        # 控制是否显示食指鼠标
        self.showPointer = True

    @abstractmethod
    def drawFrame(self):
        pass


class GameManager:
    def __init__(self, screen: pygame.display):
        self.screen = screen
        self.gesture_helper = mediapipe_gesture_helper()
        self.levelStack: list[Scene] = []
        self.last_x = -1
        self.last_y = -1
        self.dx = 0
        self.dy = 0
        self.move = False
        self.gesture = ""

        self.indexFingerTipLandmark = None
        ptrImg = pygame.image.load('resources/image/hand-point-up-solid.png')
        self.pointerImage = pygame.transform.scale(ptrImg, (24, 32))
        self.pointerImageRect = self.pointerImage.get_rect()

        self.thumbUpCoolDown = 0

    def switchScene(self, newScene: Scene, isCurrentSceneEnd: bool):
        # 表示当前level已经结束，切换到上一个level
        if isCurrentSceneEnd:
            self.endScene()
        self.levelStack.append(newScene)

    def endScene(self):
        self.levelStack.pop()

    def tick(self):
        if len(self.levelStack) > 0:
            self.updateHand()
            if self.thumbUpCoolDown > 0:
                self.thumbUpCoolDown -= 1
            self.levelStack[-1].drawFrame()
        if len(self.levelStack) > 0:
            if self.levelStack[-1].showPointer:
                self._drawPointer()
        else:
            pygame.quit()
            exit()

    def _drawPointer(self):
        if self.indexFingerTipLandmark is not None:
            self.pointerImageRect.x = self.indexFingerTipLandmark.x * SCREEN_WIDTH
            self.pointerImageRect.y = self.indexFingerTipLandmark.y * SCREEN_HEIGHT
            self.screen.blit(self.pointerImage, self.pointerImageRect)

    def getHandGesture(self):
        return self.gesture

    # 返回食指指针空间位置转换到的ui位置
    def getPointerPos(self):
        if self.indexFingerTipLandmark is not None:
            return self.indexFingerTipLandmark.x * SCREEN_WIDTH, self.indexFingerTipLandmark.y * SCREEN_HEIGHT
        else:
            return -1, -1

    # 判断是否为点赞手势
    def getIsThumbUp(self):
        # 两次点击判断之中需要延迟30frame
        return self.gesture == "Thumb_Up" and self.thumbUpCoolDown == 0

    # 成功执行点击事件后需要调这个方法来重置点击冷却
    def resetThumbCoolDown(self):
        self.thumbUpCoolDown = 30

    def getHandDeltaPos(self):
        return self.dx, self.dy, self.move

    def updateHand(self):
        self.gesture_helper.take_photo()
        detect_result = self.gesture_helper.get_last_hand_info()
        if detect_result is not None:
            self.gesture, x, y, z, indexLandMark = detect_result
            if self.last_x != -1:
                self.dx = (x - self.last_x) * 5
                self.dy = (y - self.last_y) * 5
            self.last_x = x
            self.last_y = y

            if self.gesture == "Pointing_Up":
                self.move = True
                self.indexFingerTipLandmark = indexLandMark
            else:
                self.move = False
        else:
            self.move = False
            self.gesture = ""
        cv2.imshow('frame', self.gesture_helper.last_image)  # 显示摄像头画面
        # cv2.waitKey(int(1000 / fps))
