import pygame
import random

WIDTH= 800
HEIGHT= 600


def line_segments_cross(p1, p2, p3, p4):
    x1, y1 = p1
    x2, y2 = p2
    x3, y3 = p3
    x4, y4 = p4
    den = (x1-x2)*(y3-y4) - (y1-y2)*(x3-x4)
    if den == 0:
        return False
    t = ((x1-x3)*(y3-y4) - (y1-y3)*(x3-x4))/den
    u = -((x1-x2)*(y1-y3) - (y1-y2)*(x1-x3))/den
    if 0<=t<=1 and 0<=u<=1:
        return True
    return False

def point_distance(p1, p2):
    return ((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2)**0.5

def point_dot_product(p1, p2):
    return p1[0]*p2[0] + p1[1]*p2[1]

def point_subtraction(p1, p2):
    return (p1[0]-p2[0], p1[1]-p2[1])

def triangle_area(p1, p2, p3):
    return abs((p1[0]*(p2[1]-p3[1]) + p2[0]*(p3[1]-p1[1]) + p3[0]*(p1[1]-p2[1]))/2)

def circle_line_collision(p1, p2, c, r):
    max_dist = max(point_distance(p1, c), point_distance(p2, c))
    if point_dot_product(point_subtraction(c, p1), point_subtraction(p2, p1)) > 0 \
            and point_dot_product(point_subtraction(c, p2), point_subtraction(p1, p2)) > 0:
        min_dist = triangle_area(p1, p2, c)*2/point_distance(p1, p2)
    else:
        min_dist = min(point_distance(p1, c), point_distance(p2, c))
    if min_dist < r and max_dist > r:
        return True
    return False

class Sticks:

    def __init__(self):
        self.c = (200.0, 200.0)
        self.step_size=2
        self.step_change_factor_increase=1.01
        self.step_change_factor_decrease=0.8
        self.r = (0.0, 0.0)
        self.tail = []

    def update(self, walls, player):
        r0 = (random.uniform(-self.step_size, self.step_size), random.uniform(-self.step_size, self.step_size))
        self.r = (self.r[0]*0.9 + r0[0]*0.1, self.r[1] * 0.9 + r0[1] * 0.1)
        new_c = (self.c[0]+self.r[0], self.c[1]+self.r[1])

        if not any(line_segments_cross(new_c, self.c, wall[0], wall[1]) for wall in walls)\
                and not any(circle_line_collision(wall[0], wall[1], new_c, 5) for wall in walls):
            self.c = new_c
            self.step_size = self.step_size*self.step_change_factor_increase
        else:
            self.step_size = max(10, self.step_size*self.step_change_factor_decrease)
            self.r = (-self.r[0], -self.r[1])
            self.update(walls, player)
        self.tail.insert(0, self.c)
        self.tail = self.tail[:10]

        for i in range(len(self.tail)-1):
            if any(line_segments_cross(self.tail[i], self.tail[i+1], carving_wall[0], carving_wall[1]) for carving_wall in player.carving_walls):
                return True
        return False

    def draw(self, screen):
        c = 0
        for i in range(len(self.tail)-1):
            pygame.draw.line(screen, (c, c, c), (int(self.tail[i][0]), int(self.tail[i][1])), (int(self.tail[i+1][0]), int(self.tail[i+1][1])), 4)
            c += 20
        pygame.draw.circle(screen, (0, 0, 0), (int(self.c[0]), int(self.c[1])), 5)


class Player:

    def __init__(self, current_wall, position, direction):
        self.current_wall = current_wall
        self.position = position
        self.direction = direction
        self.speed=5
        self.carving = False
        self.carving_walls = []

    def update(self, walls_object, sticks):
        walls = walls_object.walls
        keys = pygame.key.get_pressed()
        if self.carving and walls_object.point_on_wall(self.position):
            self.carving = False
            walls_object.add_walls(self.carving_walls, sticks.c)
            self.carving_walls = []

        elif keys[pygame.K_SPACE] or self.carving:

            # carving
            if keys[pygame.K_DOWN] and walls_object.point_in_open_field((self.position[0], self.position[1]+self.speed)):
                if not self.carving and (self.current_wall[0][1] == self.current_wall[1][1] or len([wall for wall in walls if wall[1][0]==self.position[0] and wall[1][1]==self.position[1] and wall[0][0]==wall[1][0]])==1):
                    self.direction = 1
                    self.position = (self.position[0], self.position[1]+self.speed)
                    self.current_wall = ((self.position[0], self.position[1]-self.speed), (self.position[0], self.position[1]))
                    self.carving_walls.append(self.current_wall)
                    self.carving = True
                elif self.carving and self.current_wall[0][0] == self.current_wall[1][0] and self.direction == 1:
                    self.position = (self.position[0], self.position[1] + self.speed)
                    self.current_wall = ((self.current_wall[0][0], self.current_wall[0][1]), (self.position[0], self.position[1]))
                    self.carving_walls[-1] = self.current_wall
                elif self.carving and self.current_wall[0][1] == self.current_wall[1][1]:
                    self.direction = 1
                    self.position = (self.position[0], self.position[1]+self.speed)
                    self.current_wall =  ((self.position[0], self.position[1]-self.speed), (self.position[0], self.position[1]))
                    self.carving_walls.append(self.current_wall)
            elif keys[pygame.K_UP] and (walls_object.point_in_open_field((self.position[0], self.position[1]-self.speed)) or walls_object.point_on_wall((self.position[0], self.position[1]-self.speed))):
                if not self.carving and (self.current_wall[0][1] == self.current_wall[1][1] or len([wall for wall in walls if wall[0][0]==self.position[0] and wall[0][1]==self.position[1] and wall[0][0]==wall[1][0]])==1):
                    self.direction = -1
                    self.position = (self.position[0], self.position[1]-self.speed)
                    self.current_wall = ((self.position[0], self.position[1]), (self.position[0], self.position[1]+self.speed))
                    self.carving_walls.append(self.current_wall)
                    self.carving = True
                elif self.carving and self.current_wall[0][0] == self.current_wall[1][0] and self.direction == -1:
                    self.position = (self.position[0], self.position[1] - self.speed)
                    self.current_wall = ((self.position[0], self.position[1]), (self.current_wall[1][0], self.current_wall[1][1]))
                    self.carving_walls[-1] = self.current_wall
                elif self.carving and self.current_wall[0][1] == self.current_wall[1][1]:
                    self.direction = -1
                    self.position = (self.position[0], self.position[1]-self.speed)
                    self.current_wall = ((self.position[0], self.position[1]), (self.position[0], self.position[1]+self.speed))
                    self.carving_walls.append(self.current_wall)
            elif keys[pygame.K_RIGHT] and (walls_object.point_in_open_field((self.position[0]+self.speed, self.position[1])) or (walls_object.point_on_wall((self.position[0]+self.speed, self.position[1])))):
                if not self.carving and (self.current_wall[0][0] == self.current_wall[1][0] or len([wall for wall in walls if wall[1][1]==self.position[1] and wall[1][0]==self.position[0] and wall[0][1]==wall[1][1]])==1):
                    self.direction = 1
                    self.position = (self.position[0]+self.speed, self.position[1])
                    self.current_wall = ((self.position[0]-self.speed, self.position[1]), (self.position[0], self.position[1]))
                    self.carving_walls.append(self.current_wall)
                    self.carving = True
                elif self.carving and self.current_wall[0][1] == self.current_wall[1][1] and self.direction == 1:
                    self.position = (self.position[0]+self.speed, self.position[1])
                    self.current_wall = ((self.current_wall[0][0], self.current_wall[0][1]), (self.position[0], self.position[1]))
                    self.carving_walls[-1] = self.current_wall
                elif self.carving and self.current_wall[0][0] == self.current_wall[1][0]:
                    self.direction = 1
                    self.position = (self.position[0]+self.speed, self.position[1])
                    self.current_wall = ((self.position[0]-self.speed, self.position[1]), (self.position[0], self.position[1]))
                    self.carving_walls.append(self.current_wall)
            elif keys[pygame.K_LEFT] and (walls_object.point_in_open_field((self.position[0]-self.speed, self.position[1])) or (walls_object.point_on_wall((self.position[0]-self.speed, self.position[1])))):
                if not self.carving and (self.current_wall[0][0] == self.current_wall[1][0] or len([wall for wall in walls if wall[0][1]==self.position[1] and wall[0][0]==self.position[0] and wall[0][1]==wall[1][1]])==1):
                    self.direction = -1
                    self.position = (self.position[0]-self.speed, self.position[1])
                    self.current_wall = ((self.position[0], self.position[1]), (self.position[0]+self.speed, self.position[1]))
                    self.carving_walls.append(self.current_wall)
                    self.carving = True
                elif self.carving and self.current_wall[0][1] == self.current_wall[1][1] and self.direction == -1:
                    self.position = (self.position[0]-self.speed, self.position[1])
                    self.current_wall = ((self.position[0], self.position[1]), (self.current_wall[1][0], self.current_wall[1][1]))
                    self.carving_walls[-1] = self.current_wall
                elif self.carving and self.current_wall[0][0] == self.current_wall[1][0]:
                    self.direction = -1
                    self.position = (self.position[0]-self.speed, self.position[1])
                    self.current_wall = ((self.position[0], self.position[1]), (self.position[0]+self.speed, self.position[1]))
                    self.carving_walls.append(self.current_wall)




        else:
            if keys[pygame.K_LEFT]:
                if self.current_wall[0][1] == self.current_wall[1][1] and self.position[0] > self.current_wall[0][0]:
                    self.position = (max(self.position[0]-self.speed, self.current_wall[0][0]), self.position[1])
                    self.direction = -1
                else:
                    filtered_walls = [wall for wall in walls if wall[1][0]==self.position[0] and wall[1][1]==self.position[1] == wall[0][1]]
                    if len(filtered_walls) == 1:
                        self.current_wall = filtered_walls[0]
                        self.direction = -1
                        self.position = (self.current_wall[1][0], self.current_wall[1][1])

            elif keys[pygame.K_DOWN]:
                if self.current_wall[0][0] == self.current_wall[1][0] and self.position[1] < self.current_wall[1][1]:
                    self.position = (self.position[0], min(self.position[1]+self.speed, self.current_wall[1][1]))
                    self.direction = 1
                else:
                    filtered_walls = [wall for wall in walls if wall[0][0]==self.position[0] and wall[0][1]==self.position[1] and wall[0][0]==wall[1][0]]
                    if len(filtered_walls) == 1:
                        self.current_wall = filtered_walls[0]
                        self.direction = 1
                        self.position = (self.current_wall[0][0], self.current_wall[0][1])
            elif keys[pygame.K_RIGHT]:
                if self.current_wall[0][1] == self.current_wall[1][1] and self.position[0] < self.current_wall[1][0]:
                    self.position = (min(self.position[0]+self.speed, self.current_wall[1][0]), self.position[1])
                    self.direction = 1
                else:
                    filtered_walls = [wall for wall in walls if wall[0][0]==self.position[0] and wall[0][1]==self.position[1] and wall[0][1]==wall[1][1]]
                    if len(filtered_walls) == 1:
                        self.current_wall = filtered_walls[0]
                        self.direction = 1
                        self.position = (self.current_wall[0][0], self.current_wall[0][1])
            elif keys[pygame.K_UP]:
                if self.current_wall[0][0] == self.current_wall[1][0] and self.position[1] > self.current_wall[0][1]:
                    self.position = (self.position[0], max(self.position[1]-self.speed, self.current_wall[0][1]))
                    self.direction = -1
                else:
                    filtered_walls = [wall for wall in walls if wall[1][0]==self.position[0] and wall[1][1]==self.position[1] and wall[0][0]==wall[1][0]]
                    if len(filtered_walls) == 1:
                        self.current_wall = filtered_walls[0]
                        self.direction = -1
                        self.position = (self.current_wall[1][0], self.current_wall[1][1])

    def draw(self, screen):
        if self.current_wall[0][0] == self.current_wall[1][0]:
            top_point = (self.position[0], self.position[1]+self.direction*6)
            wings = ((self.position[0]+6, self.position[1]-self.direction*6), (self.position[0]-6, self.position[1]-self.direction*6))
        else:
            top_point = (self.position[0]+self.direction*6, self.position[1])
            wings = ((self.position[0]-self.direction*6, self.position[1]+6), (self.position[0]-self.direction*6, self.position[1]-6))
        pygame.draw.line(screen, (0, 200, 50), (self.position[0], self.position[1]), (wings[0][0], wings[0][1]), 4)
        pygame.draw.line(screen, (0, 200, 50), (self.position[0], self.position[1]), (wings[1][0], wings[1][1]), 4)
        pygame.draw.line(screen, (0, 200, 50), (top_point[0], top_point[1]), (wings[0][0], wings[0][1]), 4)
        pygame.draw.line(screen, (0, 200, 50), (top_point[0], top_point[1]), (wings[1][0], wings[1][1]), 4)

        for wall in self.carving_walls:
            pygame.draw.line(screen, (200, 60, 60), (wall[0][0], wall[0][1]), (wall[1][0], wall[1][1]), 2)




class Walls:

    def __init__(self):
        self.walls = []
        eps=10
        self.walls.append(((eps,eps), (WIDTH-eps, eps)))
        self.walls.append(((eps,eps), (eps, HEIGHT-eps)))
        self.walls.append(((eps, HEIGHT-eps), (WIDTH-eps, HEIGHT-eps)))
        self.walls.append(((WIDTH-eps, eps), (WIDTH-eps, HEIGHT-eps)))

        self.open_fields = [(eps+1, eps+1, WIDTH-eps, HEIGHT-eps)]
        self.carved_fields = []
        self.current_area = 0


    def draw(self, window):
        for open_field in self.open_fields:
            pygame.draw.rect(window, (200, 200, 200), (open_field[0], open_field[1], open_field[2]-open_field[0], open_field[3]-open_field[1]))
        for wall in self.walls:
            pygame.draw.line(window, (0, 0, 0), (wall[0][0], wall[0][1]), (wall[1][0], wall[1][1]), 2)

    def add_walls(self, additional_walls, sticks_position):
        double_points = list(sum(additional_walls, ()))
        for p in set(double_points):
            double_points.remove(p)
        split_points = set(sum(additional_walls, ())) - set(double_points)
        start_walls = self.walls
        for split_point in split_points:
            new_walls = []
            for wall in start_walls:
                if wall[0][0] == wall[1][0] == split_point[0] and wall[0][1] < split_point[1] < wall[1][1]:
                    new_walls.append((wall[0], (wall[1][0], split_point[1])))
                    new_walls.append(((wall[0][0], split_point[1]), wall[1]))
                elif wall[0][1] == wall[1][1] == split_point[1] and wall[0][0] < split_point[0] < wall[1][0]:
                    new_walls.append((wall[0], (split_point[0], wall[1][1])))
                    new_walls.append(((split_point[0], wall[0][1]), wall[1]))
                else:
                    new_walls.append(wall)
            start_walls = new_walls

        self.walls = start_walls + additional_walls
        xs = sorted(set([wall[0][0] for wall in self.walls] + [wall[1][0] for wall in self.walls]))
        ys = sorted(set([wall[0][1] for wall in self.walls] + [wall[1][1] for wall in self.walls]))
        fields = {}
        for i in range(len(xs)-1):
            for j in range(len(ys)-1):
                fields[i,j] = (xs[i], ys[j], xs[i+1], ys[j+1])
        stick_field = [field for field in fields.items() if field[1][0] <= sticks_position[0] < field[1][2] and field[1][1] < sticks_position[1] <= field[1][3]][0]
        new_open_fields = set()

        splitted_walls = set()
        for wall in self.walls:
            if wall[0][0] == wall[1][0]:
                for i in range(len(ys)-1):
                    if wall[0][1] <= ys[i] and wall[1][1] >= ys[i+1]:
                        splitted_walls.add(((wall[0][0], ys[i]), (wall[1][0], ys[i+1])))
            else:
                for i in range(len(xs)-1):
                    if wall[0][0] <= xs[i] and wall[1][0] >= xs[i+1]:
                        splitted_walls.add(((xs[i], wall[0][1]), (xs[i+1], wall[1][1])))


        fill_ij_list = [stick_field[0]]
        while len(fill_ij_list) > 0:
            field_ij = fill_ij_list.pop()
            field_xy = fields[field_ij]
            new_open_fields.add(field_xy)
            # check left
            if field_ij[0]>0 and fields[(field_ij[0]-1, field_ij[1])] not in new_open_fields and ((field_xy[0], field_xy[1]), (field_xy[0], field_xy[3])) not in splitted_walls:
                fill_ij_list.append((field_ij[0]-1, field_ij[1]))
            # check right
            if field_ij[0]<len(xs)-2 and fields[(field_ij[0]+1, field_ij[1])] not in new_open_fields and ((field_xy[2], field_xy[1]), (field_xy[2], field_xy[3])) not in splitted_walls:
                fill_ij_list.append((field_ij[0]+1, field_ij[1]))
            # check up
            if field_ij[1]>0 and fields[(field_ij[0], field_ij[1]-1)] not in new_open_fields and ((field_xy[0], field_xy[1]), (field_xy[2], field_xy[1])) not in splitted_walls:
                fill_ij_list.append((field_ij[0], field_ij[1]-1))
            # check down
            if field_ij[1]<len(ys)-2 and fields[(field_ij[0], field_ij[1]+1)] not in new_open_fields and ((field_xy[0], field_xy[3]), (field_xy[2], field_xy[3])) not in splitted_walls:
                fill_ij_list.append((field_ij[0], field_ij[1]+1))
        self.open_fields = list(new_open_fields)
        self.current_area = 100 - 100 * sum((field[2]- field[0])*(field[3]-field[1]) for field in self.open_fields) /((WIDTH-20) * (HEIGHT-20))

    def point_in_open_field(self, p):
        return any(field[0]<=p[0]<field[2] and field[1]<p[1]<=field[3] for field in self.open_fields)

    def point_on_wall(self, p):
        return any(((wall[0][0]==p[0]==wall[1][0] and wall[0][1]<=p[1]<=wall[1][1])
                    or (wall[0][1]==p[1]==wall[1][1] and wall[0][0]<=p[0] <= wall[1][0])) for wall in self.walls)



class Game:
    def __init__(self):
        self.width = WIDTH
        self.height = HEIGHT
        self.screen = pygame.display.set_mode((self.width, self.height+60))
        self.running = True
        self.clock = pygame.time.Clock()
        self.FPS = 60
        self.sticks = Sticks()
        self.walls = Walls()
        self.player = Player(self.walls.walls[1], (self.walls.walls[1][0][0], self.walls.walls[1][0][1]), 1)
        self.time_left = 100
        self.time_step = 0.03
        self.target_area = 80
        self.current_area = 0

    def draw(self):
        # time left
        font = pygame.font.Font(None, 32)
        text = font.render("Time left:", 1, (10, 10, 10))
        self.screen.blit(text, (20, HEIGHT+10))
        pygame.draw.rect(self.screen, (125, 125, 125), (120, HEIGHT+ 10, 100, 20))
        time_color = (255, 0, 0) if self.time_left<20 else (0, 255, 0)
        pygame.draw.rect(self.screen, time_color, (122, HEIGHT+12, int(self.time_left*96/100), 16))
        # target area
        text = font.render("Area:", 1, (10, 10, 10))
        self.screen.blit(text, (260, HEIGHT+10))
        pygame.draw.rect(self.screen, (125, 125, 125), (320, HEIGHT+10, 100, 20))
        pygame.draw.rect(self.screen, (255, 100, 100), (322, HEIGHT+12, int(self.target_area*96/100), 16))
        pygame.draw.rect(self.screen, (100, 255, 100), (322+int(self.target_area * 96 / 100), HEIGHT+12, int(96-self.target_area * 96 / 100), 16))
        pygame.draw.rect(self.screen, (0, 0, 255), (322, HEIGHT+12, int(self.current_area*96/100), 16))


    def show_start_screen(self):
        while True:
            self.screen.fill((255, 255, 255))
            font = pygame.font.Font(None, 38)
            text = font.render("Press space to start", 1, (10, 10, 10))
            self.screen.blit(text, (WIDTH/2-100, HEIGHT/2))
            pygame.display.flip()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return False

            keys = pygame.key.get_pressed()
            if keys[pygame.K_SPACE]:
                self.running = True
                self.clock = pygame.time.Clock()
                self.FPS = 60
                self.sticks = Sticks()
                self.walls = Walls()
                self.player = Player(self.walls.walls[1], (self.walls.walls[1][0][0], self.walls.walls[1][0][1]), 1)
                self.time_left = 100
                self.time_step = 0.03
                self.target_area = 80
                self.current_area = 0
                self.run()


    def run(self):
        dead = False
        while self.running and self.time_left>=0 and self.current_area < self.target_area:
            self.clock.tick(self.FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
            self.screen.fill((255, 255, 255))
            self.walls.draw(self.screen)
            dead = self.sticks.update(self.walls.walls, self.player)
            if dead:
                self.running = False
                break
            self.sticks.draw(self.screen)
            self.player.update(self.walls, self.sticks)
            self.player.draw(self.screen)
            self.time_left -= self.time_step
            self.draw()
            self.current_area = self.walls.current_area
            pygame.display.flip()
        if dead:
            self.sticks.draw(self.screen)
            self.player.draw(self.screen)
            self.draw()
            font = pygame.font.Font(None, 38)
            text = font.render("You died", 1, (10, 10, 10))
            self.screen.blit(text, (WIDTH/2-50, HEIGHT/2))
            pygame.display.flip()
            pygame.time.wait(2000)
            self.show_start_screen()
        elif self.time_left<=0:
            self.sticks.draw(self.screen)
            self.player.draw(self.screen)
            self.draw()
            font = pygame.font.Font(None, 38)
            text = font.render("Time's up", 1, (10, 10, 10))
            self.screen.blit(text, (WIDTH / 2 - 50, HEIGHT / 2))
            pygame.display.flip()
            pygame.time.wait(2000)
            self.show_start_screen()
        elif self.current_area >= self.target_area:
            self.sticks.draw(self.screen)
            self.player.draw(self.screen)
            self.draw()
            font = pygame.font.Font(None, 38)
            text = font.render("You win", 1, (10, 10, 10))
            self.screen.blit(text, (WIDTH / 2 - 50, HEIGHT / 2))
            pygame.display.flip()
            pygame.time.wait(2000)
            self.show_start_screen()
        pygame.quit()

if __name__ == "__main__":
    pygame.init()
    game = Game()
    game.run()
