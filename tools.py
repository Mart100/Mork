import math
from vectors import Vector2
from vectors import Vector3

def get_car_facing_vector(car):
    pitch = float(car.rotation.pitch)
    yaw = float(car.rotation.yaw)

    facing_x = math.cos(pitch) * math.cos(yaw)
    facing_y = math.cos(pitch) * math.sin(yaw)

    return Vector2(facing_x, facing_y)

def get_own_goal(agent):
    car = agent.car
    field_info = agent.get_field_info()
    team = 0
    if field_info.goals[team].team_num != car.team: team = 1
    return Vector3(field_info.goals[team].location)

def get_opponents_goal(agent):
    car = agent.car
    field_info = agent.get_field_info()
    goal = Vector2(0, 0)
    team = 1
    if field_info.goals[team].team_num == car.team: team = 0
    return Vector3(field_info.goals[team].location)

def time_needed_for_car(agent, car_to):
    car = agent.car
    difference = car.pos - car_to
    length = difference.magnitude()
    speed = get_xy_speed(agent)
    if speed == 0: speed = 0.00000000000000001
    duration = length/speed
    return duration
def predict_time_needed_for_car(self, packet, car_from, car_to):
    difference = Vector2(car_from.x-car_to.x, car_from.y-car_to.y)
    length = difference.magnitude()
    speed = 1400
    if speed == 0: speed = 0.00000000000000001
    duration = length/speed
    return duration

def own_color(self, packet): 
    # get right color
    if packet.game_cars[self.index].team:
        color = self.renderer.create_color(255, 255, 127, 80)
    else:
        color = self.renderer.create_color(255, 22, 138, 255)
    return color

def get_xy_speed(agent):
    car = agent.car
    car_xy_velocity = Vector3(car.velocity).to_2d()
    car_xy_velocity_magnitude = car_xy_velocity.magnitude()
    return car_xy_velocity_magnitude

def difference_angles(angle1, angle2):
    angle1 = math.degrees(angle1)
    angle2 = math.degrees(angle2)
    angle1 = normalize_angle(angle1)
    angle2 = normalize_angle(angle2)
    difference = angle1 - angle2
    if difference > 180: difference = 360 - difference
    return math.radians(difference)

def normalize_angle(angle):
    while angle < 0: angle += 360
    while angle >= 360: angle -= 360
    return angle

def get_car_speed(self, packet):
    my_car = packet.game_cars[self.index]



def aim_to(agent, to, plus=0):
    car = agent.car
    car_direction = get_car_facing_vector(car)
    magnitude = Vector3(car.pos - to).magnitude()
    steer_correction = car_direction.correction_to(to.to_2d() - car.pos.to_2d())
    z_correction = Vector3(car.pos - to).angle('z')
    draw_text(agent, str(math.degrees(z_correction)), 100)
    steer_correction *= -5
    steer_correction += plus

    # aerial
    if to.z - car.pos.z > 500 and car.boost > 50 and agent.car_status != 'dribble':
        if math.degrees(z_correction) > 10 and to.z - car.pos.z > 500:
            # jump if still on ground
            if car.pos.z < 17.1:
                agent.jumps.append(1)
                print(car.pos.x, car.pos.y)
            # enable boost
            agent.controller_state.boost = True
            # sigmoid and correct
            agent.controller_state.pitch = cap_num((z_correction-car.rotation.pitch)+0.9, -1, 1)
        # if close to going to fly stop boost
        elif math.degrees(z_correction) > 4:
            agent.controller_state.boost = False

    # Drift if needs to steer much
    if abs(steer_correction) > 7:
        agent.controller_state.handbrake = True
    agent.controller_state.steer = cap_num(steer_correction, -1, 1)

def double_jump(self):
    self.jumps.append(1)
    self.jumps.append(3)
    return self

def more_colors(agent, color):
    if color == 'black': color = [255,255,255]
    if color == 'white': color = [0,0,0]
    if color == 'red': color = [255,0,0]
    if color == 'blue': color = [0,0,255]
    if color == 'green': color = [0,255,0]
    if color == 'own':
        if agent.car.team:
            color = [255, 127, 80]
        else:
            color = [22, 138, 255]
    return color

def draw_text(agent, text, y):
    agent.renderer.draw_string_2d(0, y, 1, 1, text,agent.renderer.create_color(255, 255, 255, 255))

def sigmoid(x):
    return (1 / (1 + math.exp(-x)))*2 - 1

def cap_num(x, mini, maxi):
    if x > maxi: x = maxi
    if x < mini: x = mini
    return x

def black(agent):
    return agent.renderer.create_color(255, 0, 0, 0)
def white(agent):
    return agent.renderer.create_color(255, 255, 255, 255)
