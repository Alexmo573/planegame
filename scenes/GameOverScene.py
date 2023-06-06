import pygame

from game import Scene, GameManager, getFont


class GameOverScene(Scene):
    def __init__(self, gameManager: 'GameManager', score):
        super().__init__(gameManager)
        self.score = score
        # Game Over 的背景图
        self.game_over = pygame.image.load('resources/image/gameover.png')

    def drawFrame(self):
        # 游戏 Game Over 后显示最终得分
        font = getFont(30)
        text = font.render('总分: ' + str(self.score) + "\n竖起大拇指回到开始菜单.", True, (255, 0, 0))
        text_rect = text.get_rect()
        text_rect.centerx = self.gameManager.screen.get_rect().centerx
        text_rect.centery = self.gameManager.screen.get_rect().centery + 24
        self.gameManager.screen.blit(self.game_over, (0, 0))
        self.gameManager.screen.blit(text, text_rect)

        if self.gameManager.getIsThumbUp():
            self.gameManager.resetThumbCoolDown()
            self.gameManager.endScene()
