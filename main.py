import math

from rlbot.agents.base_agent import BaseAgent, SimpleControllerState
from rlbot.utils.structures.game_data_struct import GameTickPacket
from rlbot.utils.structures.quick_chats import QuickChats
import rlbot.utils.game_state_util #import GameState, BallState, CarState, Physics, Rotator
from random import *
import winsound
from vectors import Vector2
from vectors import Vector3
from kick_ball import kick_ball
from tools import *


class main(BaseAgent):

    def initialize_agent(self):
        #This runs once before the bot starts up
        self.controller_state = SimpleControllerState()
        self.car_status = 'none'
        self.jumps = []
        self.average_xy_speed = 0
        self.testing = 'none'


    def get_output(self, packet: GameTickPacket) -> SimpleControllerState:

        #print(difference_angles(Vector2(1, 1).get_angle(), Vector2(-1, 1).get_angle()))
        #return self.controller_state
        
        self.testing = 'ground_shot'
        self.ball = Ball(packet.game_ball)
        self.car = Car(packet.game_cars[self.index])

        self.renderer.begin_rendering()
        self.controller_state.jump = False
        self.controller_state.boost = False
        self.controller_state.handbrake = False
        self.controller_state.throttle = 0
        self.controller_state.steer = 0
        self.controller_state.pitch = -1
        
        draw_ball_prediction(self, packet)
        jumping(self, packet)
        decide_car_status(self, packet)
        draw(self, packet)
        quickchat.check(self, packet)
        calculate_average_xy_speed(self, packet)
        on_wall_jump(self, packet)
        game_state.main(self)
        # run function what car status is
        if self.car_status == 'get_boost':
            get_boost(self, packet)
        if self.car_status == 'kick_ball':
            kick_ball.main(self, packet)
        if self.car_status == 'wrong_side':
            wrong_side(self, packet)
        if self.car_status == 'kickoff':
            kickoff(self, packet)
        if self.car_status == 'clear_ball':
            clear_ball.main(self, packet)

        # If jumps planned stop boosting
        if self.jumps != []:
            self.controller_state.boost = False
        
        draw_text(self, 'throttle:  '+str(self.controller_state.throttle), 120)
        self.renderer.end_rendering()
        print(round(random()*10), self.controller_state.boost)
        return self.controller_state

class game_state:
    timer = 7
    def main(agent):
        # if ball going in goal. reset ball
        if abs(agent.ball.pos.y) > 5050 or abs(get_ball_prediction(agent, 30).physics.location.y) > 5050:
            game_state.timer = 0
            winsound.Beep(100, 100)
        if agent.testing == 'aerial_shot':
            game_state.timer -= 1/60
            if game_state.timer > 0: return
            game_state.timer = 7
            a = rlbot.utils.game_state_util
            state = a.GameState()
            kick_ball.prediction_timer = 0
            agent.car_status = 'kick_ball'
            ball_state = a.BallState(a.Physics(
                                                location=a.Vector3(-3050, 3000, 0),  
                                                velocity=a.Vector3(1500, 1500, 100),
                                                rotation=a.Rotator(math.pi / 2, 0, 0), angular_velocity=a.Vector3(0, 0, 0)
                                                ))
            car_state = a.CarState(boost_amount=100,
                                        physics=a.Physics(
                                                location=a.Vector3(1000, -2100, 20),  
                                                velocity=a.Vector3(0, 0, 0),
                                                rotation=a.Rotator(0, math.pi / 2, 0), angular_velocity=a.Vector3(0, 0, 0)
                                                ))
            agent.jumps = []
            state = a.GameState(ball=ball_state, cars={agent.index: car_state})
            agent.set_game_state(state)
        if agent.testing == 'ground_shot':
            game_state.timer -= 1/60
            if game_state.timer > 0: return
            game_state.timer = 6
            a = rlbot.utils.game_state_util
            state = a.GameState()
            kick_ball.prediction_timer = 0
            kick_ball.ball_prediction = 0
            agent.car_status = 'kick_ball'
            ball_state = a.BallState(a.Physics(
                                                location=a.Vector3(3100, 3000, 0),  
                                                velocity=a.Vector3(-1500, 500, 0),
                                                rotation=a.Rotator(math.pi / 2, 0, 0), angular_velocity=a.Vector3(0, 0, 0)
                                                ))
            car_state = a.CarState(boost_amount=100,
                                        physics=a.Physics(
                                                location=a.Vector3(-1000, -2000, 20),  
                                                velocity=a.Vector3(0, 0, 0),
                                                rotation=a.Rotator(0, math.pi / 2, 0), angular_velocity=a.Vector3(0, 0, 0)
                                                ))
            agent.jumps = []
            state = a.GameState(ball=ball_state, cars={agent.index: car_state})
            agent.set_game_state(state)

class Car:
    def __init__(self, car):
        self.pos = Vector3(car.physics.location)
        self.rotation = car.physics.rotation
        self.velocity = Vector3(car.physics.velocity)
        self.ang_velocity = Vector3(car.physics.angular_velocity)
        self.is_demolished = car.is_demolished
        self.has_wheel_contact = car.has_wheel_contact
        self.is_super_sonic = car.is_super_sonic
        self.jumped = car.jumped
        self.double_jumped = car.double_jumped
        self.name = car.name
        self.boost = car.boost
        self.score_info = car.score_info
        self.team = car.team

class Ball:
    def __init__(self, ball):
        self.pos = Vector3(ball.physics.location)
        self.rotation = ball.physics.rotation
        self.velocity = Vector3(ball.physics.velocity)
        self.ang_velocity = Vector3(ball.physics.angular_velocity)
        self.latest_touch = ball.latest_touch

def draw_ball_prediction(agent, packet):
    ball_prediction = agent.get_ball_prediction_struct()
    ball_predicts = []
    for idx, ball in enumerate(ball_prediction.slices):
        if idx % 20: continue
        loc = ball.physics.location
        if loc.x == 0 and loc.y == 0: continue
        ball_predicts.append(Vector3(loc).get_array())
    if len(ball_predicts) <= 2: return
    agent.renderer.draw_polyline_3d(ball_predicts, agent.renderer.create_color(255, 0, 255, 0))
def calculate_average_xy_speed(self, packet):
    self.average_xy_speed -= self.average_xy_speed/100
    self.average_xy_speed += get_xy_speed(self, packet)/100

class quickchat:
    own_goals = 0
    goals = 0
    saves = 0
    opponent_saves = 0
    opponent_own_goals = 0
    opponent_goals = 0
    demolitions = 0
    def check(self, packet):
        my_car = packet.game_cars[self.index]
        opponent = packet.game_cars[abs(self.index-1)]
        if quickchat.goals != my_car.score_info.goals:
            quickchat.goals = my_car.score_info.goals
            self.send_quick_chat(QuickChats.CHAT_EVERYONE, QuickChats.Compliments_WhatASave)

        if quickchat.saves != my_car.score_info.saves:
            quickchat.saves = my_car.score_info.saves
            self.send_quick_chat(QuickChats.CHAT_EVERYONE, QuickChats.Reactions_CloseOne)
        
        if quickchat.opponent_saves != opponent.score_info.saves:
            quickchat.opponent_saves = opponent.score_info.saves
            self.send_quick_chat(QuickChats.CHAT_EVERYONE, QuickChats.Reactions_CloseOne)

        if quickchat.opponent_goals != opponent.score_info.goals:
            quickchat.opponent_goals = opponent.score_info.goals
            self.send_quick_chat(QuickChats.CHAT_EVERYONE, QuickChats.Compliments_NiceShot)

def on_wall_jump(self, packet):
    my_car = packet.game_cars[self.index]
    if my_car.physics.location.z > 1000: double_jump(self, packet)

def draw(self, packet):
    my_car = packet.game_cars[self.index]
    car_location = Vector2(my_car.physics.location.x, my_car.physics.location.y)
    ball_location = Vector2(packet.game_ball.physics.location.x, packet.game_ball.physics.location.y)

    
    # color
    color = self.renderer.create_color(255, 255, 255, 255)
    white_color = self.renderer.create_color(255, 255, 255, 255)
    x = 5
    y = 10
    text_size = 1
    if my_car.team == 0:
        x = 5
        color = self.renderer.create_color(255, 22, 138, 255) # blue
    else:
        x = 150
        color = self.renderer.create_color(255, 255, 127, 80) # orange
        

    # drawing
    self.renderer.draw_string_2d(x, y, text_size, text_size, self.car_status, color)
    self.renderer.draw_string_2d(x, y+10, text_size, text_size, str(Vector2(car_location.x - ball_location.x, car_location.y - ball_location.y).magnitude()), color)
    self.renderer.draw_string_2d(x, y+20, text_size, text_size, 'boost: '+str(my_car.boost), color)
    self.renderer.draw_string_2d(x, y+30, text_size, text_size, 'Jumps: '+str(self.jumps), color)
    self.renderer.draw_string_2d(x, y+40, text_size, text_size, 'Z: '+str(my_car.physics.location.z), color)
    self.renderer.draw_string_2d(x, y+50, text_size, text_size, 'speed: '+str(self.average_xy_speed), color)
    if self.car_status == 'kick_ball': self.renderer.draw_string_2d(x, y+60, text_size, text_size, 'TimeTillHit: '+str(kick_ball.prediction_timer), color)
    if self.car_status == 'clear_ball': self.renderer.draw_string_2d(x, y+60, text_size, text_size, 'TimeTillHit: '+str(clear_ball.prediction_timer), color)

def wrong_side(agent, packet):
    my_car = packet.game_cars[agent.index]
    car_location = Vector2(my_car.physics.location.x, my_car.physics.location.y)
    car_direction = get_car_facing_vector(my_car)
    ball_location = Vector2(packet.game_ball.physics.location.x, packet.game_ball.physics.location.y)
    goal = get_own_goal(agent, packet)
    difference = abs(difference_angles(Vector3(goal).get_2d().get_angle(), car_location.get_angle()))
    # double jump if on ground and straight and going good direction
    if agent.jumps == [] and my_car.physics.location.z < 17.1 and difference < 10 and get_xy_speed(agent, packet) > 1000 and my_car.boost > 50: agent.controller_state.boost = True
    if agent.jumps == [] and my_car.physics.location.z < 17.1 and difference < 10 and get_xy_speed(agent, packet) > 1000 and not agent.controller_state.boost: double_jump(agent, packet)
    aim_to(agent, packet, goal)
    agent.controller_state.throttle = 1.0
    # if in front of the ball+200 reset car status
    if my_car.team == (my_car.physics.location.y-ball_location.y > -2000):
        agent.car_status = 'none'

class clear_ball:
    prediction_timer = 0
    ball_prediction = 0
    in_position = False
    def main(agent, packet):
        if clear_ball.ball_prediction != 0: ball_location = clear_ball.ball_prediction.physics.location #Vector2(packet.game_ball.physics.location.x, packet.game_ball.physics.location.y)
        else: ball_location = Vector2(packet.game_ball.physics.location.x, packet.game_ball.physics.location.y)
        my_car = packet.game_cars[agent.index]
        car_location = Vector2(my_car.physics.location.x, my_car.physics.location.y)
        car_to_ball_magnitude = Vector2(car_location.x - ball_location.x, car_location.y - ball_location.y).magnitude()
        car_direction = get_car_facing_vector(my_car)
        goal = get_own_goal(agent, packet)
        go_to = car_location
        plus = 0

        # when ball is on other side of the field. Stop clearing ball
        agent.car_status = 'none'

        clear_ball.prediction_timer -= 1/60
        if clear_ball.prediction_timer < 0: clear_ball.ball_prediction = 0 
        if clear_ball.prediction_timer % 1/car_to_ball_magnitude/100 < 0.001: # if round number update prediction
            time = clear_ball.predict_when_ball_hit(agent, packet)
            clear_ball.prediction_timer = time
            clear_ball.ball_prediction = get_ball_prediction(agent, int(time*60))
        if clear_ball.ball_prediction == 0:
            time = clear_ball.predict_when_ball_hit(agent, packet)
            clear_ball.prediction_timer = time
            clear_ball.ball_prediction = get_ball_prediction(agent, int(time*60))
            

        ball_location = clear_ball.ball_prediction.physics.location
        car_to_ball_magnitude = Vector2(car_location.x - ball_location.x, car_location.y - ball_location.y).magnitude()
        # If not in right line with ball and goal Go there.
        ideal_car_location = clear_ball.get_ideal_car_location(agent, packet)
        a = [ball_location.x, ball_location.y, 96]
        b = [ideal_car_location.x, ideal_car_location.y, 96]
        agent.renderer.draw_line_3d(a, b, own_color(agent, packet))
        ideal_ball_to_car_angle = Vector2(ball_location.x - ideal_car_location.x, ball_location.y - ideal_car_location.y).get_angle()
        ball_to_car_angle = Vector2(ball_location.x - car_location.x, ball_location.y - car_location.y).get_angle()
        difference_angle_car_ideal = difference_angles(ideal_ball_to_car_angle, ball_to_car_angle)
        car_inline_bool = abs(difference_angle_car_ideal) < 360 - clear_ball.get_angle_for_goal(agent, packet, ball_location)
        #if my_car.team == 0: print(ideal_ball_to_car_angle, ball_to_car_angle, difference_angle_car_ideal, clear_ball.get_angle_for_goal(self, packet, ball_location))
        # If car not close enough to ideal and car not close to idealLine. Go there
        # predict ball location and go there
        go_to = agent.ball.pos
        #print(': ', car_inline_bool, plus, difference_angle_car_ideal)
        if car_inline_bool: plus = -difference_angle_car_ideal/30
        if car_to_ball_magnitude < 1000: plus = -difference_angle_car_ideal/200
        if car_to_ball_magnitude > 2000: plus = -difference_angle_car_ideal/400
        if my_car.team == 0: agent.renderer.draw_string_2d(10, 100, 2, 2, str(plus), agent.renderer.create_color(255, 255, 255, 255))
        # draw line from car to ball to goal
        a = [my_car.physics.location.x, my_car.physics.location.y, my_car.physics.location.z]
        b = [ball_location.x, ball_location.y, 96]
        inline_with_ball = difference_angles(Vector2(ball_location.x, ball_location.y).get_angle(), car_location.get_angle()) < 20
        # Use boost. If inline. and ball close to goal
        if abs(packet.game_ball.physics.location.x) < 1000 and abs(packet.game_ball.physics.location.y) > 4000 and car_to_ball_magnitude > 1000 and agent.jumps == []: agent.controller_state.boost = True
        if agent.jumps == [] and my_car.physics.location.z < 17.1 and packet.game_ball.physics.location.z > 200 and inline_with_ball and car_to_ball_magnitude < 500: double_jump(agent, packet)
        agent.renderer.draw_line_3d(a, b, agent.renderer.create_color(255, 255, 255, 255))


        aim_to(agent, packet, go_to, plus)

        # If realy close to ball and good direction Jump
        if car_to_ball_magnitude < 200 and abs(car_direction.correction_to(Vector2(ball_location.x, ball_location.y) - car_location)) < 0.1:
            double_jump(agent, packet)
        agent.controller_state.throttle = 1.0

        # if me hit the ball stop kicking the ball
        if packet.game_ball.latest_touch.player_name == my_car.name and packet.game_info.seconds_elapsed - packet.game_ball.latest_touch.time_seconds < 1:
            agent.car_status = 'none'
            clear_ball.ball_prediction = 0
        return agent

    def get_angle_for_goal(self, packet, ball_location):
        opponents_goal = get_own_goal(self, packet)
        ball_to_pole1 = Vector2(opponents_goal.x+893-ball_location.x, opponents_goal.y-ball_location.y)
        ball_to_pole2 = Vector2(opponents_goal.x-893-ball_location.x, opponents_goal.y-ball_location.y)
        #draw lines
        a = [ball_location.x, ball_location.y, 96]
        b = [ball_to_pole1.x+ball_location.x, ball_to_pole1.y+ball_location.y, 96]
        c = [ball_to_pole2.x+ball_location.x, ball_to_pole2.y+ball_location.y, 96]
        self.renderer.draw_line_3d(a, b, self.renderer.create_color(255, 0, 0, 0))
        self.renderer.draw_line_3d(a, c, self.renderer.create_color(255, 0, 0, 0))
        # return angle
        return abs((ball_to_pole1.get_angle()-ball_to_pole2.get_angle())/2*1.5)

    def get_ideal_car_location(self, packet, ball_location=0):
        if ball_location == 0: ball_location = clear_ball.ball_prediction.physics.location
        my_car = packet.game_cars[self.index]
        car_location = Vector2(my_car.physics.location.x, my_car.physics.location.y)
        car_to_ball_magnitude = Vector2(car_location.x - ball_location.x, car_location.y - ball_location.y).magnitude()
        goal = get_own_goal(self, packet)
        go_to = car_location
        # If not in right line with ball and goal Go there.
        ball_to_goal_vector = Vector2(goal.x - ball_location.x, goal.y - ball_location.y)
        ball_to_goal_unit_vector = ball_to_goal_vector.unit_vector()
        distance_ball_and_car_needed = clear_ball.get_distance_ball_car_needed(self, packet, ball_to_goal_unit_vector)
        ideal_car_location_relative = ball_to_goal_unit_vector.multiply(distance_ball_and_car_needed)
        ideal_car_location = Vector2(ideal_car_location_relative.x+ball_location.x, ideal_car_location_relative.y+ball_location.y)

        return ideal_car_location

    def predict_when_ball_hit(self, packet):
        my_car = packet.game_cars[self.index]
        car_location = Vector2(my_car.physics.location.x, my_car.physics.location.y)
        sec = 0
        loop = True
        while loop:
            sec += 0.01+sec/12
            ball_location = get_ball_prediction(self, round(sec/60)).physics.location
            car_duration = time_needed_for_car(self, packet, car_location, ball_location)
            if car_duration < sec and ball_location.z < 400: loop = False
            if sec >= 5.5: loop = False

        return sec

    def get_distance_ball_car_needed(self, packet, ball_to_goal_unit_vector):
        
        distance_ball_and_car_needed = 3000
        ball_location = clear_ball.ball_prediction.physics.location
        ideal_car_location_relative = ball_to_goal_unit_vector.multiply(distance_ball_and_car_needed)
        ideal_car_location = Vector2(ideal_car_location_relative.x+ball_location.x, ideal_car_location_relative.y+ball_location.y)
        # https://i.imgur.com/UXvb76k.png

        if ideal_car_location.x > 4096: # sidewall x
            a = abs(4096-ideal_car_location.x) / abs(ideal_car_location.x - ball_location.x) * abs(ideal_car_location.y - ball_location.y)
            z = abs(4096-ideal_car_location.x)
            distance_ball_and_car_needed -= Vector2(a, z).magnitude()+400
            distance_ball_and_car_needed
        if ideal_car_location.x < -4096: # sidewall x
            a = abs(-4096-ideal_car_location.x) / abs(ideal_car_location.x - ball_location.x) * abs(ideal_car_location.y - ball_location.y)
            z = abs(-4096-ideal_car_location.x)
            distance_ball_and_car_needed -= Vector2(a, z).magnitude()+400
        if ideal_car_location.y > 5120: # backwall y
            a = abs(5120-ideal_car_location.y) / abs(ideal_car_location.y - ball_location.y) * abs(ideal_car_location.x - ball_location.x)
            z = abs(5120-ideal_car_location.y)
            distance_ball_and_car_needed -= Vector2(a, z).magnitude()+400
        if ideal_car_location.y < -5120: # backwall y
            a = abs(-5120-ideal_car_location.y) / abs(ideal_car_location.y - ball_location.y) * abs(ideal_car_location.x - ball_location.x)
            z = abs(-5120-ideal_car_location.y)
            distance_ball_and_car_needed -= Vector2(a, z).magnitude()+400
        
        return distance_ball_and_car_needed


def jumping(self, packet):
    # loop trough jumps
    for idx, val in enumerate(self.jumps):
        jump = val-1
        self.jumps[idx] = jump
        # If jump is 0 jump!
        if jump <= 0:
            self.controller_state.jump = True
            self.jumps.remove(jump)

def time_needed_for_car(self, packet, car_from, car_to):
    difference = Vector2(car_from.x-car_to.x, car_from.y-car_to.y)
    length = difference.magnitude()
    speed = (self.average_xy_speed+get_xy_speed(self, packet)+1400*8)/10
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

def kickoff(agent, packet):
    car = agent.car
    ball = agent.ball
    car_to_ball_magnitude = Vector2(car.pos.x - ball.pos.x, car.pos.y - ball.pos.y).magnitude()
    plus = 0

    
    agent.controller_state.boost = True
    agent.controller_state.throttle = 1.0

    # 255.97 and 3840.01
    if abs(car.pos.x) < 300:
        if car.team: plus = -car.pos.x/100
        else: plus = car.pos.x/100

    aim_to(agent, packet, agent.ball.pos, (random()*2-1)+plus, )
    #print(car_location.x, car_location.y)
    # if me hit the ball stop kicking the ball
    if packet.game_ball.latest_touch.player_name == car.name and packet.game_info.seconds_elapsed - packet.game_ball.latest_touch.time_seconds < 1:
        agent.car_status = 'none'

    # If realy close to ball Jump
    if car_to_ball_magnitude < 500: double_jump(agent, packet)
    # if on wrong side of the ball reset car status
    if car.team != (car.pos.y-agent.ball.pos.y > 0):
        agent.car_status = 'none'
    return agent

def decide_car_status(self, packet):
    my_car = packet.game_cars[self.index]
    ball_location = Vector2(packet.game_ball.physics.location.x, packet.game_ball.physics.location.y)

    # decide car status if none
    if self.car_status == 'none': 
        if my_car.team and (ball_location.y > 1000):
            self.car_status = 'clear_ball'
        elif not my_car.team and (ball_location.y < -1000):
            self.car_status = 'clear_ball'
        elif my_car.team == (my_car.physics.location.y-ball_location.y > 0):
            self.car_status = 'kick_ball'
            kick_ball.ball_prediction = 0
        elif my_car.boost < 50: self.car_status = 'get_boost'
        else: self.car_status = 'clear_ball'
    # if kickoff. Car status kick ball
    if packet.game_info.is_kickoff_pause:
        self.car_status = 'kickoff'
        self.jumps = []


def get_boost(agent, packet):
    my_car = packet.game_cars[agent.index]
    car_location = Vector2(my_car.physics.location.x, my_car.physics.location.y)
    if my_car.boost > 40: agent.car_status = 'none'

    closest_boost = get_closest_boost(agent, packet)
    #Turn to the boost
    aim_to(agent, packet, Vector3(closest_boost.location))
    # If close to the ball. Use Last boost
    if Vector2(car_location.x - closest_boost.location.x, car_location.y - closest_boost.location.y).magnitude() < my_car.boost*80:
       agent.controller_state.boost = True
    else:
        agent.controller_state.boost = False 



    agent.controller_state.throttle = 1.0
    # if 100 boost. reset game_status
    if my_car.boost == 100:
        agent.car_status = 'none'
    return agent

def get_closest_boost(self, packet):
    field_info = self.get_field_info()
    my_car = packet.game_cars[self.index]
    car_location = Vector2(my_car.physics.location.x, my_car.physics.location.y)

    # Get all big boost pads
    count = field_info.num_boosts
    big_pads = []
    for i, pad in enumerate(field_info.boost_pads):
        if i > count:
            break
        if pad.is_full_boost and packet.game_boosts[i].is_active:
            big_pads.append(pad)

    def big_pads_sort_function(e):
        return Vector2(car_location.x - e.location.x, car_location.y - e.location.y).magnitude()

    big_pads.sort(key=big_pads_sort_function)
    return big_pads[0]
   
