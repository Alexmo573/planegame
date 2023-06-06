import pygame

from game import Scene, GameManager, SCREEN_HEIGHT, SCREEN_WIDTH, text_objects, getFont


class GameWinScene(Scene):
    def __init__(self, gameManager: 'GameManager', score, maxScore):
        super().__init__(gameManager)
        self.max_score = maxScore
        self.score = score
        largeText = getFont(80)
        self.TextSurf, self.TextRect = text_objects('恭喜过关', largeText)  # 通关标识
        self.TextRect.center = ((SCREEN_WIDTH / 2), (SCREEN_HEIGHT / 3))
        # 设置按钮的尺寸和其他属性
        width, height = 200, 50
        self.button_color = (0, 255, 0)
        self.text_color = (255, 255, 255)
        font = getFont(30)
        # 创建按钮的rect对象，居中
        self.rect = pygame.Rect(0, 0, width, height)

        self.msg_image = font.render("竖起大拇指回到开始菜单.", True, (100, 100, 100))
        self.msg_image_rect = self.msg_image.get_rect()

        self.score_font = getFont(20)

    def drawFrame(self):
        screen_rect = self.gameManager.screen.get_rect()
        self.gameManager.screen.blit(self.TextSurf, self.TextRect)
        self.rect.center = screen_rect.center

        self.msg_image_rect.center = self.rect.center
        self.gameManager.screen.blit(self.msg_image, self.msg_image_rect)
        # 绘制得分
        score_text = self.score_font.render(
            'score: {} best score: {}'.format(str(self.score), self.max_score), True, (128, 128, 128))
        text_rect = score_text.get_rect()
        text_rect.topleft = [10, 10]
        self.gameManager.screen.blit(score_text, text_rect)

        if self.gameManager.getIsThumbUp():
            self.gameManager.resetThumbCoolDown()
            self.gameManager.endScene()
