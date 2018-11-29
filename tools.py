import math
from vectors import Vector2
from vectors import Vector3

def get_car_facing_vector(car):
    pitch = float(car.physics.rotation.pitch)
    yaw = float(car.physics.rotation.yaw)

    facing_x = math.cos(pitch) * math.cos(yaw)
    facing_y = math.cos(pitch) * math.sin(yaw)

    return Vector2(facing_x, facing_y)

def get_own_goal(self, packet):
    my_car = packet.game_cars[self.index]
    field_info = self.get_field_info()
    team = 0
    if field_info.goals[team].team_num != my_car.team: team = 1
    return Vector3(field_info.goals[team].location)

def get_opponents_goal(self, packet):
    my_car = packet.game_cars[self.index]
    field_info = self.get_field_info()
    goal = Vector2(0, 0)
    team = 1
    if field_info.goals[team].team_num == my_car.team: team = 0
    return Vector3(field_info.goals[team].location)

def get_ball_prediction(self, num):
    ball_prediction = self.get_ball_prediction_struct()
    return ball_prediction.slices[num]

def time_needed_for_car(agent, packet, car_to):
    car = agent.car.pos
    difference = Vector2(car.x-car_to.x, car.y-car_to.y)
    length = difference.magnitude()
    speed = get_xy_speed(agent, packet)
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

def get_xy_speed(self, packet):
    my_car = packet.game_cars[self.index]
    car_xy_velocity = Vector2(my_car.physics.velocity.x, my_car.physics.velocity.y)
    car_xy_velocity_magnitude = car_xy_velocity.magnitude()
    return car_xy_velocity_magnitude

def difference_angles(angle1, angle2):
    angle1 = normalize_angle(angle1)
    angle2 = normalize_angle(angle2)
    difference = angle1 - angle2
    if difference > 180: difference = 360 - difference
    return difference

def is_angle_inbetween(n, a, b):
    n = normalize_angle(n)
    a = normalize_angle(a)
    b = normalize_angle(b)
    if a < b: 
        return a <= n and n <= b
    return a <= n and n <= b

def normalize_angle(angle):
    while angle < 0: angle += 360
    while angle >= 360: angle -= 360
    return angle

def get_car_speed(self, packet):
    my_car = packet.game_cars[self.index]

def aim_to(agent, packet, to, plus=0):
    my_car = packet.game_cars[agent.index]
    car = agent.car
    car_direction = get_car_facing_vector(my_car)
    magnitude = Vector3(car.pos - to).magnitude()
    steer_correction = car_direction.correction_to(to.get_2d() - car.pos.get_2d())
    z_correction = Vector3(car.pos - to).get_angle('z')
    draw_text(agent, str(math.degrees(z_correction)), 100)
    steer_correction *= -5
    steer_correction += plus
    # z correction
    draw_text(agent, 'z-diff: '+str(to.z - car.pos.z), 130)
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
    elif math.degrees(z_correction) > 4 and to.z - car.pos.z > 500:
        agent.controller_state.boost = False
    # Drift if needs to steer much
    if abs(steer_correction) > 7:
        agent.controller_state.handbrake = True

    agent.controller_state.steer = cap_num(steer_correction, -1, 1)

def double_jump(self, packet):
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