import pygame.font  

class Button:
    """按钮类：创建和管理游戏中的按钮（如Play按钮）"""
    
    def __init__(self, ai_game, msg):
        """初始化按钮的属性和文本内容"""
        self.screen = ai_game.screen 
        self.screen_rect = self.screen.get_rect()  
        # 设置按钮的尺寸和颜色
        self.width, self.height = 200, 50  # 按钮宽度200像素，高度50像素
        self.button_color = (0, 135, 0)    # 按钮背景色：绿色
        self.text_color = (255, 255, 255)  # 文本颜色：白色
        self.font = pygame.font.SysFont(None, 48)  
        # 创建按钮的矩形对象并居中显示
        self.rect = pygame.Rect(0, 0, self.width, self.height)  # 创建矩形按钮
        self.rect.center = self.screen_rect.center  # 将按钮置于屏幕中央

        # 渲染按钮文本（只需要渲染一次，除非文本改变）
        self._prep_msg(msg)

    def _prep_msg(self, msg):
        """将按钮文本渲染为图像，并居中显示在按钮上（私有方法）"""
        # 渲染文本为图像：msg为文本内容，True表示抗锯齿，文本颜色，背景色
        self.msg_image = self.font.render(msg, True, self.text_color,
                                          self.button_color)
        self.msg_image_rect = self.msg_image.get_rect()  # 获取文本图像的矩形对象
        self.msg_image_rect.center = self.rect.center    # 将文本图像居中于按钮

    def draw_button(self):
        """在屏幕上绘制按钮和文本"""
        self.screen.fill(self.button_color, self.rect)  # 绘制按钮背景（填充矩形）
        self.screen.blit(self.msg_image, self.msg_image_rect)  # 绘制按钮文本图像