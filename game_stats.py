import json

class GameStats:
    
    def __init__(self, ai_game):
        self.settings = ai_game.settings
        self.game_active = False 
        
        self._load_high_score() 
        
        self.reset_stats()

    def _load_high_score(self):
        filename = 'high_score.json' 
        self.high_score = 0 
        try:
            with open(filename) as f:
                self.high_score = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            pass 

    def reset_stats(self):
        self.ships_left = self.settings.ship_limit 
        self.score = 0   
        self.level = 1   
        self.settings.initialize_dynamic_settings()