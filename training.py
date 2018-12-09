from tools import *
from kick_ball import kick_ball
from clear_ball import clear_ball
import math
import rlbot.utils.game_state_util
import winsound

class game_state:
    timer = 7
    def main(agent):
        ball = agent.ball 
        car = agent.car 
        # if ball going in goal. reset ball
        if abs(agent.ball.pos.y) > 5050 or abs(ball.prediction[10].pos.y) > 5050:
            game_state.timer = 0
            winsound.Beep(100, 100)
            a = rlbot.utils.game_state_util
            state = a.GameState()
            ball_state = a.BallState(a.Physics(location=a.Vector3(0, 0, 0)))
            state = a.GameState(ball=ball_state)
            agent.set_game_state(state)
        if agent.training == 'aerial_shot':
            game_state.timer -= 1/60
            if game_state.timer > 0: return
            game_state.timer = 7
            a = rlbot.utils.game_state_util
            state = a.GameState()
            kick_ball.prediction_timer = -1
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
        if agent.training == 'ground_shot':
            game_state.timer -= 1/60
            if game_state.timer > 0: return
            game_state.timer = 6
            a = rlbot.utils.game_state_util
            state = a.GameState()
            kick_ball.prediction_timer = -1
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

        if agent.training == 'defend_ground':
            game_state.timer -= 1/60
            if game_state.timer > 0: return
            game_state.timer = 6
            a = rlbot.utils.game_state_util
            state = a.GameState()
            clear_ball.prediction_timer = -1
            agent.car_status = 'clear_ball'
            ball_state = a.BallState(a.Physics(
                                                location=a.Vector3(1000, 2000, 0),  
                                                velocity=a.Vector3(-300, -2000, 0),
                                                rotation=a.Rotator(math.pi / 2, 0, 0), angular_velocity=a.Vector3(0, 0, 0)
                                                ))
            car_state = a.CarState(boost_amount=100,
                                        physics=a.Physics(
                                                location=a.Vector3(-2000, -3000, 20),  
                                                velocity=a.Vector3(0, 0, 0),
                                                rotation=a.Rotator(0, -math.pi / 2, 0), angular_velocity=a.Vector3(0, 0, 0)
                                                ))
            agent.jumps = []
            state = a.GameState(ball=ball_state, cars={agent.index: car_state})
            agent.set_game_state(state)


        if agent.training == 'dribble':
            game_state.timer -= 1/60
            #if game_state.timer > 0: return
            if agent.ball.pos.z > 100: return
            game_state.timer = 2
            a = rlbot.utils.game_state_util
            state = a.GameState()
            agent.car_status = 'dribble'
            ball_state = a.BallState(a.Physics(
                                                location=a.Vector3(0, 0, 600),  
                                                velocity=a.Vector3(0, 10, 0),
                                                rotation=a.Rotator(math.pi / 2, 0, 0), angular_velocity=a.Vector3(0, 0, 0)
                                                ))
            car_state = a.CarState(boost_amount=100,
                                        physics=a.Physics(
                                                location=a.Vector3(0, 300, 0),  
                                                velocity=a.Vector3(0, 0, 0),
                                                rotation=a.Rotator(0, -math.pi / 2, 0), angular_velocity=a.Vector3(0, 0, 0)
                                                ))
            agent.jumps = []
            state = a.GameState(ball=ball_state, cars={agent.index: car_state})
            agent.set_game_state(state)


        if agent.training == 'constant':
            a = rlbot.utils.game_state_util
            state = a.GameState()
            agent.car_status = 'dribble'
            ball_state = a.BallState(a.Physics(
                                                location=a.Vector3(0, 0, 500),  
                                                velocity=a.Vector3(0, 0, 0),
                                                rotation=a.Rotator(math.pi / 2, 0, 0), angular_velocity=a.Vector3(0, 0, 0)
                                                ))
            car_state = a.CarState(boost_amount=100,
                                        physics=a.Physics(
                                                location=a.Vector3(0, -50, 0),  
                                                velocity=a.Vector3(0, 0, 0),
                                                rotation=a.Rotator(0, math.pi/2, 0), angular_velocity=a.Vector3(0, 0, 0)
                                                ))
            agent.jumps = []
            state = a.GameState(ball=ball_state, cars={agent.index: car_state})
            agent.set_game_state(state)