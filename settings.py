class Settings:
    """存储游戏所有设置的类"""
    
    def __init__(self):
        """初始化游戏的静态设置"""
        # 屏幕设置
        self.screen_width = 1200
        self.screen_height = 800
        self.bg_color = (230, 230, 230)

        # 飞船设置
        self.ship_limit = 3  # 玩家拥有的飞船数量

        # 普通子弹设置
        self.bullet_width = 3
        self.bullet_height = 15
        self.bullet_color = (60, 60, 60)  # 灰色
        self.bullets_allowed = 3  # 同时允许存在的普通子弹数量

        # 外星人子弹设置
        self.alien_bullet_width = 5
        self.alien_bullet_height = 15
        self.alien_bullet_color = (255, 60, 60)  # 红色
        self.alien_bullets_allowed = 2  # 同时允许存在的外星人子弹数量

        # 升级子弹设置（必须包含的核心属性）
        self.upgrade_bullets_reward_score = 600  # 每600分奖励升级子弹（关键属性！）
        self.upgrade_bullet_width = 15
        self.upgrade_bullet_height = 15
        self.upgrade_bullet_color = (255, 255, 0)  # 黄色
        self.upgrade_bullet_speed = 3.6  # 升级子弹速度

        # 外星人舰队设置
        self.fleet_drop_speed = 10
        self.fleet_direction = 1  # 1表示向右，-1表示向左

        # 难度提升设置
        self.speedup_scale = 1.1
        self.score_scale = 1.5

        # 初始化动态设置（必须保留这个方法调用）
        self.initialize_dynamic_settings()

    def initialize_dynamic_settings(self):
        """初始化随游戏进行而变化的设置（被game_stats调用）"""
        self.ship_speed = 1.5
        self.bullet_speed = 3.0
        self.alien_speed = 1.0
        self.alien_bullet_speed = 1.5

        self.alien_points = 50  # 击中外星人基础得分

    def increase_speed(self):
        """提高游戏速度（随关卡升级）"""
        self.ship_speed *= self.speedup_scale
        self.bullet_speed *= self.speedup_scale
        self.alien_speed *= self.speedup_scale
        self.alien_bullet_speed *= self.speedup_scale
        self.upgrade_bullet_speed *= self.speedup_scale

        self.alien_points = int(self.alien_points * self.score_scale)