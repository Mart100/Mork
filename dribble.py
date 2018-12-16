from tools import *
from vectors import Vector2
from vectors import Vector3
import winsound
import math


class dribble:
    def main(agent, packet):
        car = agent.car
        ball = agent.ball
        car_to_ball_vector = Vector3(ball.pos - car.pos)
        ball_car_magnitude_2d = car_to_ball_vector.to_2d().magnitude()
        rotated_car_to_ball_vector2 = car_to_ball_vector.to_2d().rotate(car.rotation.yaw)
        throttle = -cap_num(rotated_car_to_ball_vector2.x/800, -1, 1)
        # if ball is far away from ball. or on ground. stop dribbling
        if ball_car_magnitude_2d > 2000 or ball.pos.z < 100:
            aim_to(agent, ball.pos)
            agent.car_status = 'none'

        # if ball in air. Try to get under it
        if ball.pos.z > 155:
            aim_to(agent, ball.pos)
            agent.controller_state.throttle = ball_car_magnitude_2d/200
            agent.renderer.draw_string_3d(car.pos.change('z', 100).get_array(), 2, 2, str(round(throttle*100)/100), white(agent))
            #if ball_car_magnitude_2d > 400: agent.controller_state.boost = True

        # if ball on top of car
        elif ball_car_magnitude_2d < 150:
            aim_to(agent, ball.pos)
            # difference velocity car and ball
            diff = (ball.velocity.to_2d().magnitude()-car.velocity.to_2d().magnitude())/20
            agent.controller_state.throttle = cap_num(throttle+diff, -1, 1)
            if throttle+diff > 4: agent.controller_state.boost = True
            agent.renderer.draw_string_3d(car.pos.change('z', 100).get_array(), 2, 2, str(round(throttle*100)/100)+' :: '+str(round(diff*100)/200), white(agent))
    
            # flip the ball when its about to fall off
            if throttle > 0.15:
                double_jump(agent)
                agent.car_status = 'none'