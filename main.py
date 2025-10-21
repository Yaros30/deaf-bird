from pygame import *
from random import *
import sounddevice as sd
import numpy as np
init()
window = display.set_mode((700, 500))
display.set_caption("Deaf Bird (Voice Flappy Bird)")
clock = time.Clock()

sr = 16000
block = 256
mic_level = 0.0
def audio_cb(indata, frames, time, status):
    global mic_level
    if status:
        return
    rms = float(np.sqrt(np.mean(indata**2)))
    mic_level = 0.85 * mic_level + 0.15 * rms



class Bird(sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = transform.scale(image.load("bird.png"), (34, 24))
        self.rect = self.image.get_rect(center=(x, y))



class Pipe(sprite.Sprite):
    def __init__(self, x, y, is_top=False):
        super().__init__()
        self.is_top = is_top
        pipe_image = image.load("pipe.png").convert_alpha()
        pipe_image_bottom = transform.scale(pipe_image, (80, 320))
        pipe_image_top = transform.flip(pipe_image_bottom, False, True)
        self.image = pipe_image_top if is_top else pipe_image_bottom
        self.rect = self.image.get_rect(topleft=(x, y))
def generate_pipes(count, gap_height=140, distance=300):
    pipes = sprite.Group()
    for i in range(count):
        height = randint(50, 500 - gap_height - 50)
        x = 300 + i * distance
        top_y = height - 320
        bottom_y = height + gap_height
        top_pipe = Pipe(x, top_y, is_top=True)
        bottom_pipe = Pipe(x, bottom_y, is_top=False)
        pipes.add(top_pipe, bottom_pipe)
    return pipes

pipes = generate_pipes(5)
pipe_speed = 3
bg_image = transform.scale(image.load("background.png"), (700, 500))
bird = Bird(100, 250)
gravity = 0.6
THRESH = 0.0001
IMPULSE = -8.0
y_vel = 0.0
with sd.InputStream(channels=1, samplerate=sr, blocksize=block, callback=audio_cb):    
    running = True
    while running:
        for e in event.get():
            if e.type == QUIT:
                running = False
        if mic_level > THRESH:
            y_vel = IMPULSE
        y_vel += gravity
        bird.rect.y += int(y_vel)

        if bird.rect.bottom > 500:
            bird.rect.bottom = 500
            y_vel = 0
        if bird.rect.top < 0:
            bird.rect.top = 0
            y_vel = 0

        

        for p in pipes:
            p.rect.x -= pipe_speed
            if bird.rect.colliderect(p.rect):
                bird.rect.x -= 150
            if p.rect.right < 0:
                max_x = max(pipe.rect.x for pipe in pipes)
                if p.is_top:
                    height = randint(50, 500 - 280 - 50)
                    p.rect.x = max_x + 300
                    p.rect.y = height - 320
                    for b in pipes:
                        if not b.is_top and abs(b.rect.x - p.rect.x) < 5:
                            b.rect.x = p.rect.x
                            b.rect.y = height + 280
                
        window.blit(bg_image, (0, 0))
        pipes.draw(window)
        window.blit(bird.image, bird.rect)
        display.update()
        clock.tick(60)
quit()