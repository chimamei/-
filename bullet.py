import pygame
from pygame.sprite import Sprite

class Bullet(Sprite):
    """管理飞船和外星人发射的子弹，包括普通子弹、外星人子弹和升级子弹"""
    
    def __init__(self, ai_game, is_alien_bullet=False, is_upgrade_bullet=False):
        super().__init__()
        self.screen = ai_game.screen
        self.settings = ai_game.settings
        self.is_alien_bullet = is_alien_bullet  # 是否是外星人子弹
        self.is_upgrade_bullet = is_upgrade_bullet  # 是否是升级子弹

        # 根据子弹类型设置不同属性
        if self.is_upgrade_bullet:
            # 升级子弹：黄色宽子弹，可穿透
            self.color = self.settings.upgrade_bullet_color
            self.width = self.settings.upgrade_bullet_width
            self.height = self.settings.upgrade_bullet_height
            self.speed = self.settings.upgrade_bullet_speed
            
            # 升级子弹位置（飞船顶部中央）
            self.rect = pygame.Rect(0, 0, self.width, self.height)
            self.rect.midtop = ai_game.ship.rect.midtop
            
        elif self.is_alien_bullet:
            # 外星人子弹：红色子弹，向下发射
            self.color = self.settings.alien_bullet_color
            self.width = self.settings.alien_bullet_width
            self.height = self.settings.alien_bullet_height
            self.speed = self.settings.alien_bullet_speed
            
            # 外星人子弹位置（选中的外星人底部中央）
            alien = ai_game.current_shooter
            self.rect = pygame.Rect(0, 0, self.width, self.height)
            self.rect.midbottom = alien.rect.midbottom
            
        else:
            # 普通飞船子弹：灰色细子弹
            self.color = self.settings.bullet_color
            self.width = self.settings.bullet_width
            self.height = self.settings.bullet_height
            self.speed = self.settings.bullet_speed
            
            # 普通子弹位置（飞船顶部中央）
            self.rect = pygame.Rect(0, 0, self.width, self.height)
            self.rect.midtop = ai_game.ship.rect.midtop

        # 存储子弹的精确y坐标（用于平滑移动）
        self.y = float(self.rect.y)

    def update(self):
        """更新子弹位置"""
        if self.is_alien_bullet:
            # 外星人子弹向下移动（y坐标增加）
            self.y += self.speed
        else:
            # 飞船子弹（普通/升级）向上移动（y坐标减少）
            self.y -= self.speed
        
        # 将精确坐标同步到rect属性
        self.rect.y = self.y

    def draw_bullet(self):
        """在屏幕上绘制子弹"""
        pygame.draw.rect(self.screen, self.color, self.rect)