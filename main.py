import math

from rlbot.agents.base_agent import BaseAgent, SimpleControllerState
from rlbot.utils.structures.game_data_struct import GameTickPacket
from rlbot.utils.structures.quick_chats import QuickChats
from random import *
import winsound
from vectors import Vector2
from vectors import Vector3
from kick_ball import kick_ball
from clear_ball import clear_ball
from boost import *
from dribble import dribble
from training import game_state
from tools import *


class main(BaseAgent):

    def initialize_agent(self):
        #This runs once before the bot starts up
        self.controller_state = SimpleControllerState()
        self.car_status = 'none'
        self.jumps = []
        self.average_xy_speed = 0
        self.training = 'none'


    def get_output(self, packet: GameTickPacket) -> SimpleControllerState:

        #print(difference_angles(Vector2(1, 1).get_angle(), Vector2(-1, 1).get_angle()))
        #return self.controller_state
        
        self.training = 'none'
        self.ball = Ball(self, packet.game_ball)
        self.car = Car(packet.game_cars[self.index])
        self.info = Info(self)

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
        if self.training != 'none': game_state.main(self)
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
        if self.car_status == 'dribble':
            dribble.main(self, packet)

        # If jumps planned stop boosting
        if self.jumps != []:
            self.controller_state.boost = False
        
        draw_text(self, 'throttle:  '+str(self.controller_state.throttle), 120)
        self.renderer.end_rendering()
        return self.controller_state


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
    def __init__(self, agent, ball, is_prediction=False):
        self.pos = Vector3(ball.physics.location)
        self.rotation = ball.physics.rotation
        self.velocity = Vector3(ball.physics.velocity)
        self.ang_velocity = Vector3(ball.physics.angular_velocity)
        if not is_prediction: self.latest_touch = ball.latest_touch
        self.prediction = []
        if not is_prediction:
            prediction = agent.get_ball_prediction_struct()
            for num in range(360):
                prediction_slice = prediction.slices[num]
                self.prediction.append(Ball(agent, prediction_slice, True))

def draw_ball_prediction(agent, packet):
    ball = agent.ball
    ball_predicts = []
    for idx, ball in enumerate(ball.prediction):
        if idx % 20: continue
        loc = ball.pos
        if loc.x == 0 and loc.y == 0: continue
        ball_predicts.append(loc.get_array())
    if len(ball_predicts) <= 2: return
    agent.renderer.draw_polyline_3d(ball_predicts, agent.renderer.create_color(255, 0, 255, 0))

def calculate_average_xy_speed(self, packet):
    self.average_xy_speed -= self.average_xy_speed/100
    self.average_xy_speed += get_xy_speed(self)/100

class Info:
    def __init__(self, agent):
        field_info = agent.get_field_info()
        self.field_info = field_info
        self.own_goal = get_own_goal(agent)
        self.opponents_goal = get_opponents_goal(agent)

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
    if my_car.physics.location.z > 1000: double_jump(self)

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
    difference = abs(difference_angles(Vector3(goal).to_2d().get_angle(), car_location.get_angle()))
    # double jump if on ground and straight and going good direction
    if agent.jumps == [] and my_car.physics.location.z < 17.1 and difference < 10 and get_xy_speed(agent, packet) > 1000 and my_car.boost > 50: agent.controller_state.boost = True
    if agent.jumps == [] and my_car.physics.location.z < 17.1 and difference < 10 and get_xy_speed(agent, packet) > 1000 and not agent.controller_state.boost: double_jump(agent)
    aim_to(agent, goal)
    agent.controller_state.throttle = 1.0
    # if in front of the ball+200 reset car status
    if my_car.team == (my_car.physics.location.y-ball_location.y > -2000):
        agent.car_status = 'none'

def jumping(self, packet):
    # loop trough jumps
    for idx, val in enumerate(self.jumps):
        jump = val-1
        self.jumps[idx] = jump
        # If jump is 0 jump!
        if jump <= 0:
            self.controller_state.jump = True
            self.jumps.remove(jump)

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

    aim_to(agent, agent.ball.pos, (random()*2-1)+plus, )
    #print(car_location.x, car_location.y)
    # if me hit the ball stop kicking the ball
    if packet.game_ball.latest_touch.player_name == car.name and packet.game_info.seconds_elapsed - packet.game_ball.latest_touch.time_seconds < 1:
        agent.car_status = 'none'

    # If realy close to ball Jump
    if car_to_ball_magnitude < 500: double_jump(agent)
    # if on wrong side of the ball reset car status
    if car.team != (car.pos.y-agent.ball.pos.y > 0):
        agent.car_status = 'none'
    return agent

def decide_car_status(agent, packet):
    car = agent.car
    ball = agent.ball
    car_to_ball_vector = Vector3(ball.pos - car.pos)
    ball_car_magnitude_2d = car_to_ball_vector.to_2d().magnitude()
    ball_location = Vector3(packet.game_ball.physics.location)

    # decide car status if none
    if agent.car_status == 'none': 
        if car.team and ((ball_location.y > 1000) or predict_ball_own_goal(agent)):
            agent.car_status = 'clear_ball'
        elif not car.team and ((ball_location.y < -1000) or predict_ball_own_goal(agent)):
            agent.car_status = 'clear_ball'
        elif car.team == (car.pos.y-ball_location.y > 0):
            agent.car_status = 'kick_ball'
            # if ball in air and close. dribble
            if agent.ball.pos.z > 1000 and ball_car_magnitude_2d < 2000:
                agent.car_status = 'dribble'
            kick_ball.ball_prediction = 0
        elif car.boost < 50: agent.car_status = 'get_boost'
        else: agent.car_status = 'clear_ball'
    # if kickoff. Car status kick ball
    if packet.game_info.is_kickoff_pause:
        agent.car_status = 'kickoff'
        agent.jumps = []

def predict_ball_own_goal(agent):
    car = agent.car
    ball = agent.ball
    for i in range(5):
        if car.team and ball.prediction[i*60].pos.y > 4500: return True
        if not car.team and ball.prediction[i*60].pos.y < -4500: return True
    return False
