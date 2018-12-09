from vectors import Vector2
from vectors import Vector3
import winsound
import math
from tools import *

class clear_ball:
    prediction_timer = 0
    correction_timer = 0
    ball_prediction = 0
    in_position = False
    def main(agent, packet):
        if clear_ball.ball_prediction != 0: ball_pos = clear_ball.ball_prediction.pos
        else: 
            ball_pos = agent.ball.pos
            clear_ball.prediction_timer = -1
        car = agent.car
        ball = agent.ball
        own_goal = get_own_goal(agent)
        plus = 0
        agent.car_status = 'none'

        # ball prediction
        clear_ball.prediction_timer -= 1/60
        if clear_ball.prediction_timer < -0.1:
            agent.car_status = 'none'
            clear_ball.in_position = False
            time = clear_ball.predict_when_ball_hit(agent, packet)
            clear_ball.prediction_timer = time
            clear_ball.ball_prediction = ball.prediction[int(time*60)]
        clear_ball.correction_timer = clear_ball.when_ball_hit_correction(agent)-clear_ball.prediction_timer
        clear_ball.ball_prediction = ball.prediction[int(cap_num(clear_ball.prediction_timer*60, 0, 1e9))]

        # if correction is bigger than abs 1. recalculate hit prediction
        if abs(clear_ball.correction_timer) > 1: clear_ball.prediction_timer = -1

        ball_pos = clear_ball.ball_prediction.pos
        car_to_ball_magnitude_2d = (car.pos.to_2d() - ball_pos.to_2d()).magnitude()
        ideal_car_angle = clear_ball.get_ideal_car_angle(agent)
        ideal_car_pos = Vector3('angle', clear_ball.get_ideal_car_angle(agent))
        car_to_ball_angle = (ball_pos - car.pos).to_2d().get_angle()
        difference_angle_car_ideal = difference_angles(ideal_car_angle, car_to_ball_angle)
        car_inline_with_goal = ideal_car_angle < math.pi*2 - clear_ball.get_goal_angle(agent)
        car_on_ground = (car.pos.z < 17.5)
        no_jumps = (agent.jumps == [])
        go_to = ball_pos

        # draw line from ball to ideal car location
        agent.renderer.draw_line_3d(ball_pos.get_array(), ideal_car_pos.multiply(3000).get_array(), own_color(agent, packet))

        # 3D correction timer vs actual prediction
        agent.renderer.draw_string_3d(car.pos.change('z', 100).get_array(), 2, 2, 'corr: '+str(round(clear_ball.correction_timer, 2)), white(agent))

        # draw place where car will hit ball
        agent.renderer.draw_string_3d(ball_pos.get_array(), 2, 2, ball_pos.string(), white(agent))

        # aim towards ideal car angle. The closer to the ball
        plus = -ideal_car_angle/(car_to_ball_magnitude_2d/100)

        # Use boost. If inline. on the ground. and correction
        too_slow = clear_ball.correction_timer > 0.05
        if no_jumps and car_on_ground and too_slow:
            agent.controller_state.boost = True

        # double jump if close to the ball, inline, car on ground
        if car.pos.z < 17.1 and car_inline_with_goal and car_to_ball_magnitude_2d < 500: double_jump(agent)

        # full throttle. Exept if car is going to fast for predicted ball pos. Then slow down
        agent.controller_state.throttle = cap_num(clear_ball.correction_timer+1.05, 0, 1)

        aim_to(agent, go_to, plus)

        # if car hit the ball stop kicking the ball
        if packet.game_ball.latest_touch.player_name == car.name and packet.game_info.seconds_elapsed - packet.game_ball.latest_touch.time_seconds < 1:
            agent.car_status = 'none'
            clear_ball.prediction_timer = 0
        return agent

    def get_goal_angle(agent):
        ball = agent.ball
        ball_pos = clear_ball.ball_prediction.pos
        own_goal = agent.info.own_goal
        ball_to_pole1 = Vector2(893+ball_pos.x, own_goal.y-ball_pos.y)
        ball_to_pole2 = Vector2(893-ball_pos.x, own_goal.y-ball_pos.y)

        #draw lines
        agent.renderer.draw_line_3d(ball_pos.get_array(), own_goal.change('x', 893).get_array(), black(agent))
        agent.renderer.draw_line_3d(ball_pos.get_array(), own_goal.change('x', -893).get_array(), black(agent))

        # return angle
        return abs(difference_angles(ball_to_pole1.get_angle(), ball_to_pole2.get_angle())/2)

    def get_ideal_car_angle(agent):
        ball_pos = clear_ball.ball_prediction.pos
        own_goal = agent.info.own_goal
        ball_to_goal_vector = agent.info.own_goal - ball_pos
        return ball_to_goal_vector.to_2d().multiply(-1).get_angle()

    def predict_when_ball_hit(agent, packet):
        car = agent.car
        ball = agent.ball
        sec = 0
        loop = True
        while loop:
            sec += 0.01+sec/12
            ball_location = ball.prediction[round(sec/60)].pos
            car_duration = predict_time_needed_for_car(agent, packet, car.pos, ball_location)

            aerial = ball_location.z > 1000 and car.boost > 60
            ground_shot = ball_location.z < 150
            in_time = car_duration < sec
            if in_time and (ground_shot or aerial): loop = False
            if sec >= 5.5: loop = False
        return sec

    def when_ball_hit_correction(agent):
        car = agent.car
        ball = agent.ball
        time = time_needed_for_car(agent, clear_ball.ball_prediction.pos)
        return time