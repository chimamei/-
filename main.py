import sys
import pygame
import random
from time import sleep 
import json

from settings import Settings
from ship import Ship 
from bullet import Bullet 
from alien import Alien 
from game_stats import GameStats 
from button import Button 
from scoreboard import Scoreboard 

class AlienInvasion:
    """管理游戏资源和行为的主类"""
    
    def __init__(self):
        """初始化游戏并创建游戏资源"""
        pygame.init()
        self.settings = Settings()
        
        # 创建游戏窗口
        self.screen = pygame.display.set_mode(
            (self.settings.screen_width, self.settings.screen_height))
        pygame.display.set_caption("Alien Invasion")
        
        # 创建游戏统计信息、记分板
        self.stats = GameStats(self) 
        self.sb = Scoreboard(self) 

        # 创建飞船、子弹组、外星人组
        self.ship = Ship(self) 
        self.bullets = pygame.sprite.Group() 
        self.alien_bullets = pygame.sprite.Group()  # 外星人子弹组
        self.aliens = pygame.sprite.Group() 

        # 创建外星人舰队
        self._create_fleet() 

        # 创建Play按钮
        self.play_button = Button(self, "Play") 

        # 外星人发射子弹的计时器
        self.alien_shoot_timer = 0
        self.alien_shoot_interval = 2000  # 初始发射间隔（毫秒）
        
        # 升级子弹奖励标记（明确初始化为0）
        self.last_upgrade_score = 0

    def run_game(self):
        """开始游戏的主循环"""
        while True:
            self._check_events()

            if self.stats.game_active: 
                self.ship.update()
                self._update_bullets()
                self._update_aliens()
                self._update_alien_bullets()
                self._alien_shoot_logic()  # 外星人发射子弹逻辑

            self._update_screen()

    # --- 退出游戏处理 ---
    def _close_game(self):
        """保存最高分并退出游戏"""
        filename = 'high_score.json'
        high_score = self.stats.high_score
        
        try:
            with open(filename, 'w') as f:
                json.dump(high_score, f)
        except Exception as e:
            print(f"警告: 无法保存最高得分到 {filename}. 错误: {e}")
            
        sys.exit()

    # --- 事件处理 ---
    def _check_events(self):
        """响应按键和鼠标事件"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self._close_game() 
            elif event.type == pygame.MOUSEBUTTONDOWN: 
                mouse_pos = pygame.mouse.get_pos()
                self._check_play_button(mouse_pos)
            elif event.type == pygame.KEYDOWN:
                self._check_keydown_events(event)
            elif event.type == pygame.KEYUP:
                self._check_keyup_events(event)

    def _check_play_button(self, mouse_pos): 
        """在玩家点击Play按钮时开始新游戏"""
        button_clicked = self.play_button.rect.collidepoint(mouse_pos)
        
        if button_clicked and not self.stats.game_active:
            # 重置游戏设置
            self.settings.initialize_dynamic_settings()
            self.stats.reset_stats() 
            self.stats.game_active = True
            
            # 重置升级子弹奖励标记（关键修复）
            self.last_upgrade_score = 0
            
            # 重置记分板
            self.sb.prep_score()
            self.sb.prep_level()
            self.sb.prep_ships()
            
            # 清空外星人和子弹
            self.aliens.empty()
            self.bullets.empty()
            self.alien_bullets.empty()

            # 创建新舰队并居中飞船
            self._create_fleet()
            self.ship.center_ship()

            # 隐藏鼠标光标
            pygame.mouse.set_visible(False) 

    def _check_keydown_events(self, event):
        """响应按键按下"""
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = True
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = True
        elif event.key == pygame.K_q: 
            self._close_game() 
        elif event.key == pygame.K_SPACE and self.stats.game_active: 
            self._fire_bullet()

    def _check_keyup_events(self, event):
        """响应按键松开"""
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = False
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = False

    # --- 子弹管理 ---
    def _fire_bullet(self):
        """创建新子弹并添加到子弹组"""
        if len(self.bullets) < self.settings.bullets_allowed * 2:  # 放宽子弹限制
            new_bullet = Bullet(self)
            self.bullets.add(new_bullet)

    def _fire_upgrade_bullets(self):
        """发射三发升级子弹（分散发射）"""
        try:
            # 确保飞船存在且游戏处于激活状态
            if not self.stats.game_active or not hasattr(self, 'ship'):
                return
            
            # 限制同时存在的升级子弹数量
            upgrade_bullets = [b for b in self.bullets if b.is_upgrade_bullet]
            if len(upgrade_bullets) >= 3:
                return
            
            # 发射三发升级子弹，分散排列
            for i in range(3):
                new_bullet = Bullet(self, is_upgrade_bullet=True)
                # 调整子弹位置，避免重叠
                new_bullet.rect.centerx = self.ship.rect.centerx + (i - 1) * 20
                new_bullet.rect.top = self.ship.rect.top
                self.bullets.add(new_bullet)
        except Exception as e:
            print(f"发射升级子弹时出错: {e}")

    def _update_bullets(self):
        """更新子弹位置并删除消失的子弹"""
        self.bullets.update()
        
        # 删除飞出屏幕的普通子弹和升级子弹
        for bullet in self.bullets.copy():
            if bullet.rect.bottom <= 0:
                self.bullets.remove(bullet)
        
        # 检查子弹与外星人的碰撞
        self._check_bullet_alien_collisions()

    def _update_alien_bullets(self):
        """更新外星人子弹位置并检测碰撞"""
        self.alien_bullets.update()
        
        # 删除飞出屏幕的外星人子弹
        for bullet in self.alien_bullets.copy():
            if bullet.rect.top >= self.settings.screen_height:
                self.alien_bullets.remove(bullet)
        
        # 检查外星人子弹是否击中飞船
        if pygame.sprite.spritecollideany(self.ship, self.alien_bullets):
            self._ship_hit()

    def _check_bullet_alien_collisions(self):
        """响应子弹与外星人的碰撞"""
        # 普通子弹击中后消失，升级子弹可穿透
        collisions = pygame.sprite.groupcollide(
            self.bullets, self.aliens, 
            False,  # 先不销毁子弹，后续手动处理
            True    # 外星人被击中后销毁
        )

        # 手动处理子弹销毁：只有普通子弹需要销毁
        bullets_to_remove = []
        for bullet in self.bullets:
            if not bullet.is_upgrade_bullet and bullet in collisions:
                bullets_to_remove.append(bullet)
        for bullet in bullets_to_remove:
            self.bullets.remove(bullet)

        # 处理得分
        if collisions:
            for aliens in collisions.values():
                self.stats.score += self.settings.alien_points * len(aliens)
            self.sb.prep_score()
            self.sb.check_high_score()

            # 优化奖励分数判断
            current_score = self.stats.score
            reward_score = self.settings.upgrade_bullets_reward_score
            
            # 计算当前应奖励的次数
            current_reward_count = current_score // reward_score
            last_reward_count = self.last_upgrade_score // reward_score
            
            # 只有当奖励次数增加时才触发
            if current_reward_count > last_reward_count:
                self._fire_upgrade_bullets()
                # 更新为当前奖励次数对应的分数（避免重复触发）
                self.last_upgrade_score = current_reward_count * reward_score

        # 检查是否消灭了所有外星人
        if not self.aliens: 
            self.settings.increase_speed() 
            self.stats.level += 1 
            self.sb.prep_level() 
            
            # 清空子弹并创建新舰队
            self.bullets.empty() 
            self.alien_bullets.empty()
            self._create_fleet() 

    # --- 外星人管理 ---
    def _alien_shoot_logic(self):
        """外星人随机发射子弹的逻辑"""
        if not self.aliens:
            return
            
        current_time = pygame.time.get_ticks()
        # 随机调整发射间隔（1-3秒）
        random_interval = random.randint(1000, 3000)
        
        if current_time - self.alien_shoot_timer > random_interval:
            # 随机选择一个外星人发射子弹
            random_alien = random.choice(list(self.aliens))
            self.current_shooter = random_alien  # 设置当前发射的外星人
            
            # 创建外星人子弹并添加到组中
            if len(self.alien_bullets) < self.settings.alien_bullets_allowed:
                new_bullet = Bullet(self, is_alien_bullet=True)
                self.alien_bullets.add(new_bullet)
            
            # 更新计时器
            self.alien_shoot_timer = current_time

    def _create_alien(self, x_position, y_position):
        """创建一个外星人并将其放在当前行"""
        new_alien = Alien(self)
        new_alien.x = x_position
        new_alien.rect.x = x_position
        new_alien.rect.y = y_position 
        self.aliens.add(new_alien)

    def _create_fleet(self):
        """创建外星人舰队"""
        alien = Alien(self)
        alien_width, alien_height = alien.rect.size 

        # 计算每行可容纳的外星人数量和行数
        current_x = alien_width 
        current_y = alien_height 
        
        while current_y < (self.settings.screen_height - (3 * alien_height)):
            while current_x < (self.settings.screen_width - (2 * alien_width)):
                self._create_alien(current_x, current_y) 
                current_x += 2 * alien_width 
            
            # 换行重置x坐标，增加y坐标
            current_x = alien_width 
            current_y += 2 * alien_height 

    def _check_fleet_edges(self):
        """当有外星人到达边缘时采取相应措施"""
        for alien in self.aliens.sprites():
            if alien.check_edges(): 
                self._change_fleet_direction() 
                break
    
    def _change_fleet_direction(self):
        """将整支舰队下移并改变方向"""
        for alien in self.aliens.sprites():
            alien.rect.y += self.settings.fleet_drop_speed 
        self.settings.fleet_direction *= -1

    def _update_aliens(self):
        """检查舰队是否到达边缘，然后更新所有外星人的位置"""
        self._check_fleet_edges() 
        self.aliens.update() 

        # 检测外星人与飞船的碰撞
        if pygame.sprite.spritecollideany(self.ship, self.aliens):
            self._ship_hit()
        
        # 检测外星人是否到达屏幕底部
        self._check_aliens_bottom()

    def _check_aliens_bottom(self):
        """检查是否有外星人到达屏幕底部"""
        screen_rect = self.screen.get_rect()
        for alien in self.aliens.sprites():
            if alien.rect.bottom >= screen_rect.bottom: 
                # 像飞船被击中一样处理
                self._ship_hit() 
                break

    # --- 游戏状态管理 ---
    def _ship_hit(self):
        """响应飞船被外星人击中"""
        if self.stats.ships_left > 0: 
            # 减少剩余飞船数量并更新记分板
            self.stats.ships_left -= 1
            self.sb.prep_ships() 
            
            # 清空外星人和子弹
            self.aliens.empty()
            self.bullets.empty()
            self.alien_bullets.empty()
            
            # 创建新舰队并将飞船居中
            self._create_fleet() 
            self.ship.center_ship() 
            
            # 暂停
            sleep(0.5)
        else:
            # 游戏结束
            self.stats.game_active = False 
            pygame.mouse.set_visible(True) 
    
    # --- 屏幕更新 ---
    def _update_screen(self):
        """更新屏幕上的图像，并切换到新屏幕"""
        # 填充背景色
        self.screen.fill(self.settings.bg_color)
        
        # 绘制飞船
        self.ship.blitme() 
        
        # 绘制所有子弹
        for bullet in self.bullets.sprites():
            bullet.draw_bullet() 
        for bullet in self.alien_bullets.sprites():
            bullet.draw_bullet()

        # 绘制外星人舰队
        self.aliens.draw(self.screen) 
        
        # 显示得分信息
        self.sb.show_score() 

        # 如果游戏处于非活动状态，绘制Play按钮
        if not self.stats.game_active: 
            self.play_button.draw_button()

        # 让最近绘制的屏幕可见
        pygame.display.flip()

if __name__ == '__main__':
    # 创建游戏实例并运行游戏
    ai = AlienInvasion()
    ai.run_game()