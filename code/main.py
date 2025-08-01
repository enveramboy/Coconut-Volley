import pygame
import pymunk
import pymunk.pygame_util
import random

# Screen Initialization
WIDTH, HEIGHT = 840, 640
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))

# Game Mechanics Initialization
running = True
clock = pygame.time.Clock()
delta_time = 0.1
frm_cnt = 0
space = pymunk.Space()
space.gravity = (0, 981)
font = pygame.font.Font('midorima.ttf', size=100)

# Audio Initialization
bg_themes = [pygame.mixer.Sound('audio/Carnival Kerfuffle.mp3'), pygame.mixer.Sound('audio/Clip Joint Calamity.mp3'), pygame.mixer.Sound('audio/Pyramid Peril.mp3')]
hit_sfxs = [pygame.mixer.Sound('audio/hit1.mp3'), pygame.mixer.Sound('audio/hit2.mp3'), pygame.mixer.Sound('audio/hit3.mp3')]
score_sfx = pygame.mixer.Sound('audio/hit4.mp3')
bg_themes[random.randint(0, len(bg_themes)-1)].play(-1)

# Functions
def Init_Sprite(sprite_path, width, height):
    """
    Initializes sprite for blit functionality to game window.

    Args:
        sprite_path (str): path to image associated with sprite.
        width (int): width of sprite.
        height (int): height of sprite.

    Returns:
        Surface: resulting surface object of newly initialized sprite.
    """
    ret = pygame.image.load(sprite_path).convert()
    ret = pygame.transform.scale(ret, (width, height))
    ret.set_colorkey((0, 0, 0))
    return ret

def Create_Ball_Rb(x, y, radius, mass):
    """
    Creates a pymunk body for the volleyball.

    Args:
        x (int): x location to initialize body at.
        y (int): y location to initialize body at.
        radius (float): radius of circle.
        mass (float): mass of circle.

    Returns:
        Circle: pymunk Circle object associated with body.
    """

    body = pymunk.Body()
    body.position = (x, y)
    shape = pymunk.Circle(body, radius)
    shape.mass = mass
    shape.elasticity = 2
    shape.friction = 0.4
    shape.color = (0, 0, 0, 0)
    space.add(body, shape)
    return shape

def Create_Wall(x, y, width, height, collision_type):
    """
    Creates a static pymunk body in the shape of a rectangle.

    Args:
        x (int): x location to initialize body at.
        y (int): y location to initialize body at.
        width (int): width of rectangular body.
        height (int): height of rectangular body.
        collision_type: id for collision handling.

    Returns:
        Poly: pymunk Poly object associated with the created body.
    """

    body = pymunk.Body(body_type = pymunk.Body.STATIC)
    body.position = (x, y)
    shape = pymunk.Poly.create_box(body, (width, height))
    shape.elasticity = 0.4
    shape.friction = 0.5
    shape.color = (0, 0, 0, 0)
    shape.collision_type = collision_type
    space.add(body, shape)
    return shape

def Create_Bird_Rb(x, y, vertices, mass):
    """
    Creates a pymunk body for a bird. Trapezoidal shape with a pointed top.

    Args:
        x (int): x location to initialize body at.
        y (int): y location to initialize body at.

    Returns:
        Poly: pymunk Poly object associated with the created body.
    """

    body = pymunk.Body()
    body.position = x, y
    shape = pymunk.Poly(body, vertices)
    shape.mass = mass
    shape.elasticity = 0.4
    shape.friction = 0.5
    shape.color = (0, 0, 0, 0)
    space.add(body, shape)
    return shape

# Collision Callbacks
def p1_ground_callback(arbiter, space, data): p1.isGrounded = True

def p1_score(arbiter, space, data):
    ball.rb.body.position = (WIDTH*3/4, 70)
    ball.rb.body.velocity = (0, 0)
    score_board.Inc_P1()
    score_sfx.play()

def p1_pole_callback(arbiter, space, data): p1.moving_right = False

def p1_left_wall_callback(arbiter, space, data): p1.moving_left = False

def p1_ball_callback(arbiter, space, data): hit_sfxs[random.randint(0, len(hit_sfxs)-1)].play()

def p2_ground_callback(arbiter, space, data): p2.isGrounded = True

def p2_score(arbiter, space, data):
    ball.rb.body.position = (WIDTH/4, 70)
    ball.rb.body.velocity = (0, 0)
    score_board.Inc_P2()
    score_sfx.play()

def p2_pole_callback(arbiter, space, data): p2.moving_left = False

def p2_right_wall_callback(arbiter, space, data): p2.moving_right = False

def p2_ball_callback(arbiter, space, data): hit_sfxs[random.randint(0, len(hit_sfxs)-1)].play()

# Classes
class Ball:
    """
    A volleyball object.

    Attributes:
        x (int): x coordinate of initial object location.
        y (int): y coordinate of initial object location.
        collision_type (int): id for collision handling
    """
    def __init__(self, x, y, collision_type):
        self.idle = Init_Sprite('images/ball.png', 100, 100)
        self.rb = Create_Ball_Rb(x, y, 44, 10)
        self.rb.collision_type = collision_type
    
    def Display(self):
        """
        Displays ball in game window.
        """
        screen.blit(self.idle, (self.rb.body.position.x-50, self.rb.body.position.y-50))
        self.rb.body.velocity = (self.rb.body.velocity.x, self.rb.body.velocity.y*0.97)

class Bird:
    """
    A bird object.

    Attributes:
        x (int): x coordinate of initial object location.
        y (int): y coordinate of initial object location.
        sprites (list): paths of associated sprites. Formatted as [idle, jump, run_1, run_2]
        adjustment_x (int): x value to adjust sprite overlay of pymunk body, in the case sprite is not centered
        adjustment_y (int): y value to adjust sprite overlay of pymunk body, in the case sprite is not centered
        collision_type (int): id for collision handling
    """
    def __init__(self, x, y, sprites, adjustment_x, adjustment_y, collision_type):
        self.idle = Init_Sprite(sprites[0], 200, 150)
        self.jmp = Init_Sprite(sprites[1], 200, 150)
        self.sprite_sheet_run = [Init_Sprite(sprites[2], 200, 150), Init_Sprite(sprites[3], 200, 150)]
        self.run_idx = 0
        self.moving_right = False
        self.moving_left = False
        self.rb = Create_Bird_Rb(x, y, [(0, 640), (100, 640), (100, 590), (60, 540), (50, 538), (40, 540), (0, 590)], 100)
        self.rb.body.moment = float('inf')
        self.isGrounded = True
        self.rb.collision_type = collision_type
        self.adjustment_x = adjustment_x
        self.adjustment_y = adjustment_y
    
    def __Handle_Animations(self):
        """
        Displays appropriate animations according to in-game actions.
        """
        if self.moving_right ^ self.moving_left:
            if frm_cnt % 8 == 0:
                self.run_idx = ((self.run_idx) + 1) % len(self.sprite_sheet_run)
            screen.blit(self.sprite_sheet_run[self.run_idx], (self.rb.body.position.x+self.adjustment_x, self.rb.body.position.y+self.adjustment_y))
        elif not self.isGrounded:
            screen.blit(self.jmp, (self.rb.body.position.x+self.adjustment_x, self.rb.body.position.y+self.adjustment_y))
        else: screen.blit(self.idle, (self.rb.body.position.x+self.adjustment_x, self.rb.body.position.y+self.adjustment_y))

    def __Handle_Move(self):
        """
        Sets velocity of the associated body of bird according to moving_right and moving_left values.
        """
        self.rb.body.velocity = (20000 * delta_time * (self.moving_right - self.moving_left), self.rb.body.velocity.y)

    def Handle_Jmp(self):
        """
        When called, if bird is grounded execute a jump. Jump actuated through impulse force.
        """
        if self.isGrounded:
            self.isGrounded = False
            self.rb.body.apply_impulse_at_local_point((0, -70000.0), (0, 0))


    def Display(self):
        """
        Displays bird in game window.
        """
        self.__Handle_Animations()
        self.__Handle_Move()

class Pole:
    """
    A pole object.

    Attributes:
        collision_type (int): id for collision handling
    """
    def __init__(self, collision_type):
        self.idle = Init_Sprite('images/pole.png', 46, 564)
        self.rb = Create_Wall(420, 425, 26, 364, collision_type)

    def Display(self):
        """
        Displays pole in game window.
        """
        screen.blit(self.idle, (395, 210))

class Score_Board:
    """
    Object for keeping track of scores.
    """
    def __init__(self):
        self.p1 = 0
        self.p2 = 0
    
    def Inc_P1(self): 
        """
        Increments Player 1's score.
        """
        self.p1 += 1
    def Inc_P2(self): 
        """
        Increments Player 2's score.
        """
        self.p2 += 1

    def Display(self):
        """
        Displays scores in game window.
        """
        screen.blit(font.render(str(self.p1), True, (0, 0, 0)), (WIDTH/4-20, 120))
        screen.blit(font.render(str(self.p2), True, (0, 0, 0)), (WIDTH*3/4-20, 120))

# Object Initialization
p1_ground = Create_Wall(WIDTH/4, HEIGHT-75, WIDTH/2, 1, 3)
p2_ground = Create_Wall(WIDTH*3/4, HEIGHT-75, WIDTH/2, 1, 7)
left_wall = Create_Wall(-20, HEIGHT/2, 40, 5*HEIGHT, 4)
right_wall = Create_Wall(WIDTH+30, HEIGHT/2, 50, 5*HEIGHT, 5)
ball = Ball(WIDTH/4, 70, 2)
p1 = Bird(140, -76, ['images/player/idle.png', 'images/player/jmp.png', 'images/player/run_1.png', 'images/player/run_2.png'], -33, 520, 1)
p2 = Bird(590, -76, ['images/computer/idle.png', 'images/computer/jmp.png', 'images/computer/run_1.png', 'images/computer/run_2.png'], -66, 520, 8)
pole = Pole(6)
score_board = Score_Board()

# Collision Handling Initialization
space.on_collision(1, 3, p1_ground_callback)
space.on_collision(2, 7, p1_score)
space.on_collision(1, 6, None, p1_pole_callback)
space.on_collision(1, 4, None, p1_left_wall_callback)
space.on_collision(1, 2, p1_ball_callback)

space.on_collision(8, 7, p2_ground_callback)
space.on_collision(2, 3, p2_score)
space.on_collision(8, 6, None, p2_pole_callback)
space.on_collision(8, 5, None, p2_right_wall_callback)
space.on_collision(8, 2, p2_ball_callback)

while running:
    frm_cnt += 1

    screen.blit(Init_Sprite('images/bg_1.png', 840, 640), (0, 0))

    score_board.Display()

    # space.debug_draw(pymunk.pygame_util.DrawOptions(screen))

    ball.Display()
    p1.Display()
    p2.Display()
    pole.Display()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_d:
                p1.moving_right = True
            if event.key == pygame.K_a:
                p1.moving_left = True
            if event.key == pygame.K_w:
                p1.Handle_Jmp()

            if event.key == pygame.K_RIGHT:
                p2.moving_right = True
            if event.key == pygame.K_LEFT:
                p2.moving_left = True
            if event.key == pygame.K_UP:
                p2.Handle_Jmp()

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_d:
                p1.moving_right = False
            if event.key == pygame.K_a:
                p1.moving_left = False

            if event.key == pygame.K_RIGHT:
                p2.moving_right = False
            if event.key == pygame.K_LEFT:
                p2.moving_left = False
    
    pygame.display.flip()

    delta_time = clock.tick(60)/1000
    delta_time = max(0.001, min(0.1, delta_time))
    space.step(1/60)

pygame.quit()