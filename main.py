import pygame as pg
from random import choice

pg.mixer.pre_init(frequency=44100, size=16, channels=1, buffer=512)
pg.init()
screen = pg.display.set_mode((552, 980))
pg.display.set_caption('Flappy Bird by: github.com/JT-1337')

class Background:
    def __init__(self):
        self.bg_surface = pg.transform.scale2x(pg.image.load('img/background.png')).convert()
        #672x224
        self.floor_surface = pg.transform.scale2x(pg.image.load('img/floor.png')).convert()
        self.floor_surface2 = self.floor_surface
        self.floor_x = 0
        
    def scroll_floor(self): 
        if self.floor_x <= -672: self.floor_x = 0
        self.floor_x -= 1
        
    def draw(self): screen.blit(self.bg_surface, (0, 0))
    
    def draw_floor(self):
        screen.blit(self.floor_surface, (self.floor_x, 756))
        screen.blit(self.floor_surface2, (self.floor_x + self.floor_surface.get_width(), 756))
        
        
class Bird:
    def __init__(self):
        self.bird_downflap_surface = pg.transform.scale2x(pg.image.load('img/yellowbird-downflap.png')).convert_alpha()
        self.bird_surface = pg.transform.scale2x(pg.image.load('img/yellowbird-midflap.png')).convert_alpha()
        self.bird_upflap_surface = pg.transform.scale2x(pg.image.load('img/yellowbird-upflap.png')).convert_alpha()
        self.bird_surface_list = [self.bird_downflap_surface, self.bird_surface, self.bird_upflap_surface]
        
        self.bird_surface_index = 0
        self.BIRD_FLAP = pg.USEREVENT + 1
        pg.time.set_timer(self.BIRD_FLAP, 200)
        
        self.bird_rect = self.bird_surface.get_rect(center=(100, 490))
        self.bird_speed = 0
        
        self.flap_sound = pg.mixer.Sound('sounds/sfx_wing.wav')
        self.flap_sound.set_volume(0.2)
        self.die_sound = pg.mixer.Sound('sounds/sfx_hit.wav')
        self.die_sound.set_volume(0.1)
        
    def move(self, grav):
        self.bird_speed += grav
        self.bird_rect.centery += self.bird_speed
        
    def fly_up(self): 
        self.bird_speed = 0
        self.bird_speed -= 8
        
    def draw(self): screen.blit(self.rotate(), self.bird_rect)
    
    def rotate(self): return pg.transform.rotozoom(self.bird_surface, -self.bird_speed * 4, 1)
    
    def animation(self):
        return self.bird_surface_list[self.bird_surface_index], self.bird_surface_list[self.bird_surface_index].get_rect(center=(100, self.bird_rect.centery))


class Pipe:
    def __init__(self):
        self.bottom_pipe_surface = pg.transform.scale2x(pg.image.load('img/pipe.png')).convert()
        self.top_pipe_surface = pg.transform.flip(pg.transform.scale2x(pg.image.load('img/pipe.png')).convert(), False, True)
        self.pipe_heights = [-500, -400, -300]
        self.pipes = []
        self.SPAWN_PIPE = pg.USEREVENT
        pg.time.set_timer(self.SPAWN_PIPE, 3000)
        
    def spawn_pipe(self):
        random_pos = choice(self.pipe_heights)
        self.bottom_pipe_rect = self.bottom_pipe_surface.get_rect(midtop=(700, random_pos + 900))
        self.top_pipe_rect = self.top_pipe_surface.get_rect(midtop=(700, random_pos))
        return self.bottom_pipe_rect, self.top_pipe_rect
           
    def move(self): 
        for pipe in self.pipes: pipe.centerx -= 1
        
    def draw(self):
        for index, pipe in enumerate(self.pipes): 
            if index % 2 == 0: screen.blit(self.bottom_pipe_surface, pipe)
            else: screen.blit(self.top_pipe_surface, pipe)
            
    def remove_pipe(self):
        for pipe in self.pipes:
            if pipe.centerx < -42: self.pipes.remove(pipe)
            
            
class App:
    def __init__(self):
        self.run = True
        self.game_active = False
        self.clock = pg.time.Clock()
        self.gravity = 0.25
        self.background = Background()
        self.bird = Bird()
        self.pipe = Pipe()
        self.font = pg.font.Font('04B_19.TTF', 36)
        self.score = 0
        self.highest_score = self.get_highest_score()
        self.message_surface = pg.image.load('img/message.png').convert()
        self.message_rect = self.message_surface.get_rect(center=(276, 490))
        self.score_sound = pg.mixer.Sound('sounds/sfx_point.wav')
        self.score_sound.set_volume(0.2)
    
    def draw(self):
        self.background.draw()
        self.pipe.draw()
        self.background.draw_floor()
        self.bird.draw()
        
        score_text = self.font.render(str(self.score), True, (255, 255, 255))
        score_rect = score_text.get_rect(center=(screen.get_width()//2, 100))
        screen.blit(score_text, score_rect)
        
        highest_score_text = self.font.render(str(self.highest_score), True, (255, 255, 255))
        highest_score_rect = highest_score_text.get_rect(center=(screen.get_width()//2, 880))
        screen.blit(highest_score_text, highest_score_rect)
        
        if not self.game_active: screen.blit(self.message_surface, self.message_rect)
        
        pg.display.update()
        
    def check_collision(self): 
        for pipe in self.pipe.pipes: 
            if self.bird.bird_rect.colliderect(pipe): 
                self.save_highest_score()
                return True
        
    def check_bird_pos(self): return self.bird.bird_rect.bottom >= 756 or self.bird.bird_rect.top <= 0
    
    def scoring(self): 
        if self.pipe.pipes != []: 
            if self.bird.bird_rect.centerx == self.pipe.pipes[0].centerx + 60: 
                self.score_sound.play()
                self.score += 1
            
    def get_highest_score(self):
        import os
        path = os.getcwd() + '\\highest_score.txt'
        if os.path.exists(path):
            with open(path) as f: highest_score = int(f.read())
        else: return 0
        
        return highest_score
    
    def save_highest_score(self):
        if self.highest_score < self.score:
            import os 
            path = os.getcwd() + '\\highest_score.txt'
            with open(path, 'w') as f: f.write(str(self.score))
        
    def main(self):
        while self.run:
            for event in pg.event.get(): 
                if event.type == pg.QUIT: self.run = False 
                
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_SPACE: 
                        self.game_active = True
                        self.bird.fly_up()
                        self.bird.flap_sound.play()
                    
                if event.type == pg.MOUSEBUTTONDOWN:
                    if event.button == 1: 
                        self.game_active = True
                        self.bird.fly_up()
                        self.bird.flap_sound.play()
                    
                if event.type == self.pipe.SPAWN_PIPE and self.game_active: self.pipe.pipes.extend(self.pipe.spawn_pipe())
                
                if event.type == self.bird.BIRD_FLAP: 
                    if self.bird.bird_surface_index < 2: self.bird.bird_surface_index += 1
                    else: self.bird.bird_surface_index = 0
             
            self.bird.bird_surface, self.bird.bird_rect = self.bird.animation()
            
            if self.game_active:
                self.bird.move(self.gravity)
                self.pipe.move()
                self.pipe.remove_pipe()
                self.scoring()
                if self.check_collision() or self.check_bird_pos():
                    self.bird.die_sound.play()
                    self.__init__()
            
            self.save_highest_score()
            self.background.scroll_floor()
            self.draw()   
            
            self.clock.tick(120)


if __name__ == '__main__':          
    app = App()
    app.main()