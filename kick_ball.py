from vectors import Vector2
from vectors import Vector3
import winsound
import math
from tools import *


class kick_ball:
    prediction_timer = 0
    correction_timer = 0
    ball_prediction = 0
    in_position = False
    ideal_location_away = 2000
    def main(agent, packet):
        if kick_ball.ball_prediction != 0: ball_location = kick_ball.ball_prediction.pos
        else: 
            ball_location = Vector3(packet.game_ball.physics.location)
            kick_ball.prediction_timer = -1
        ball = agent.ball
        car = agent.car
        car_location = car.pos.to_2d()
        car_to_ball_vector = Vector3(ball.pos) - Vector3(car.pos)
        car_to_ball_magnitude = car_to_ball_vector.magnitude()
        car_to_ball_magnitude_2d = car_to_ball_vector.to_2d().magnitude()
        car_direction = get_car_facing_vector(car)
        goal = get_opponents_goal(agent)
        go_to = car_location
        plus = 0

        # ball prediction
        kick_ball.prediction_timer -= 1/60
        if kick_ball.prediction_timer < -0.1:
            agent.car_status = 'none'
            kick_ball.in_position = False
            time = kick_ball.predict_when_ball_hit(agent, packet)
            kick_ball.prediction_timer = time
            kick_ball.ball_prediction = ball.prediction[int(time*60)]
        kick_ball.correction_timer = kick_ball.when_ball_hit_correction(agent)
        kick_ball.ball_prediction = ball.prediction[int(cap_num(kick_ball.prediction_timer*60, 0, 1e9))]

        # a few variables
        ball_location = kick_ball.ball_prediction.pos
        car_to_ball_vector = Vector3(ball.pos) - Vector3(car.pos)
        car_to_ball_magnitude = car_to_ball_vector.magnitude()
        car_to_ball_magnitude_2d = car_to_ball_vector.to_2d().magnitude()
        ideal_car_location = kick_ball.get_ideal_car_location(agent, packet, ball_location)

        # draw line from ball to ideal car location
        Vector3(ball_location).draw_to(agent, ideal_car_location, [0, 100, 0])

        # 3D correction timer vs actual prediction
        agent.renderer.draw_string_3d(car.pos.change('z', 100).get_array(), 2, 2, 'corr: '+str(round(kick_ball.correction_timer, 2)-round(kick_ball.prediction_timer, 2)), white(agent))

        # draw place where car will hit ball
        agent.renderer.draw_string_3d(ball_location.get_array(), 2, 2, ball_location.string(), white(agent))

        ideal_car_to_ball_angle = (ball_location - ideal_car_location).to_2d().get_angle()
        car_to_ball_to_angle = (ball_location - car.pos).to_2d().get_angle()
        difference_angle_car_ideal = difference_angles(ideal_car_to_ball_angle, car_to_ball_to_angle)
        if difference_angle_car_ideal > kick_ball.get_angle_for_goal(agent, packet, ball_location) * 2: kick_ball.in_position = False
        car_inline_bool = abs(difference_angle_car_ideal) < kick_ball.get_angle_for_goal(agent, packet, ball_location)*2
        # If car not close enough to ideal and car not close to idealLine. Go there
        if Vector2(ideal_car_location.x-car_location.x, ideal_car_location.y-car_location.y).magnitude() > 1000 and not car_inline_bool and not kick_ball.in_position:
            go_to = ideal_car_location
            plus = -difference_angle_car_ideal/40
            # double jump if on ground and straight and going good direction and far away
            far_away_enough = Vector2(car_location.x-ideal_car_location.x, car_location.y-ideal_car_location.y).magnitude() > 1000
            # draw ideal location
            a = [ideal_car_location.x, ideal_car_location.y, 17]
            agent.renderer.draw_rect_3d(a, 40, 40, True, own_color(agent, packet))
        # Else head towards the ball
        else:
            kick_ball.in_position = True
            # predict ball location and go there
            go_to = ball_location
            plus = -difference_angle_car_ideal/(car_to_ball_magnitude/100)
            #if car_to_ball_magnitude_2d > 2000: plus = -difference_angle_car_ideal/40
            # boost
            too_slow = kick_ball.correction_timer > kick_ball.prediction_timer+0.01
            if car.pos.z < 17.1 and car_inline_bool and too_slow: agent.controller_state.boost = True
            agent.renderer.draw_line_3d(car.pos.get_array(), ball_location.get_array(), agent.renderer.create_color(255, 255, 255, 255))
            agent.renderer.draw_line_3d(ideal_car_location.get_array(), ball_location.get_array(), own_color(agent, packet))

        draw_text(agent, 'LR. corr: '+str(plus), 110)
        aim_to(agent, go_to, plus)

        # If realy close to ball and good direction Jump
        if car_to_ball_magnitude < 200 and abs(car_direction.correction_to(Vector2(ball_location.x, ball_location.y) - car_location)) < 0.1:
            double_jump(agent)

        agent.controller_state.throttle = 1
        if kick_ball.correction_timer+0.05 < kick_ball.prediction_timer:
            agent.controller_state.throttle = 1 - (kick_ball.prediction_timer - kick_ball.correction_timer - kick_ball.prediction_timer)/5
        # if me hit the ball stop kicking the ball
        if packet.game_ball.latest_touch.player_name == car.name and packet.game_info.seconds_elapsed - packet.game_ball.latest_touch.time_seconds < 1:
            agent.car_status = 'none'
            kick_ball.ball_prediction = 0
        return agent

    def get_angle_for_goal(agent, packet, ball_location):
        opponents_goal = get_opponents_goal(agent)
        ball_to_pole1 = Vector2(opponents_goal.x+893-ball_location.x, opponents_goal.y-ball_location.y)
        ball_to_pole2 = Vector2(opponents_goal.x-893-ball_location.x, opponents_goal.y-ball_location.y)
        #draw lines
        a = [ball_location.x, ball_location.y, 96]
        b = [ball_to_pole1.x+ball_location.x, ball_to_pole1.y+ball_location.y, 96]
        c = [ball_to_pole2.x+ball_location.x, ball_to_pole2.y+ball_location.y, 96]
        agent.renderer.draw_line_3d(a, b, agent.renderer.create_color(255, 0, 0, 0))
        agent.renderer.draw_line_3d(a, c, agent.renderer.create_color(255, 0, 0, 0))
        # return angle
        return abs((ball_to_pole1.get_angle()-ball_to_pole2.get_angle())/2*1.5)

    def get_ideal_car_location(agent, packet, ball_location=0):
        if ball_location == 0: ball_location = kick_ball.ball_prediction.pos
        car = agent.car
        car_to_ball_vector = Vector3(ball_location) - Vector3(car.pos)
        car_to_ball_magnitude = car_to_ball_vector.magnitude()
        goal = Vector3(get_opponents_goal(agent))
        # If not in right line with ball and goal Go there.
        ball_to_goal_vector = goal - ball_location
        ball_to_goal_unit_vector = ball_to_goal_vector.unit_vector()
        distance_ball_and_car_needed = kick_ball.get_distance_ball_car_needed(agent, packet, ball_to_goal_unit_vector)
        ideal_car_location_relative = ball_to_goal_unit_vector.multiply(distance_ball_and_car_needed)
        ideal_car_location = ideal_car_location_relative + ball_location
        # if distance bigger than -500 inverse ideal and not in corners. And kick ball via wall
        if distance_ball_and_car_needed > -1000 and abs(ideal_car_location.y) < 4000:
            distance_ball_and_car_needed = kick_ball.ideal_location_away
            ideal_car_location_relative = ball_to_goal_unit_vector.multiply(distance_ball_and_car_needed)
            ideal_car_location_relative.y *= -1
            ideal_car_location = ideal_car_location_relative + ball_location
        else:
            ideal_car_location_relative = ball_to_goal_unit_vector.multiply(distance_ball_and_car_needed)
            ideal_car_location = ideal_car_location_relative + ball_location
        return ideal_car_location

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
        time = time_needed_for_car(agent, kick_ball.ball_prediction.pos) 
        return time

    def get_distance_ball_car_needed(agent, packet, ball_to_goal_unit_vector):
        
        distance_ball_and_car_needed = -kick_ball.ideal_location_away
        ball_location = kick_ball.ball_prediction.pos
        ideal_car_location_relative = ball_to_goal_unit_vector.multiply(distance_ball_and_car_needed)
        ideal_car_location = ideal_car_location_relative + ball_location
        # https://i.imgur.com/UXvb76k.png

        if ideal_car_location.x > 4096: # sidewall x
            x = abs(4096-ideal_car_location.x)
            y = abs(4096-ideal_car_location.x) / abs(ideal_car_location.x - ball_location.x) * abs(ideal_car_location.y - ball_location.y)
            z = abs(4096-ideal_car_location.x) / abs(ideal_car_location.x - ball_location.x) * abs(ideal_car_location.z - ball_location.z)
            distance_ball_and_car_needed += Vector3(x, y, z).magnitude()+400
        if ideal_car_location.x < -4096: # sidewall x
            x = abs(-4096-ideal_car_location.x)
            y = abs(-4096-ideal_car_location.x) / abs(ideal_car_location.x - ball_location.x) * abs(ideal_car_location.y - ball_location.y)
            z = abs(-4096-ideal_car_location.x) / abs(ideal_car_location.x - ball_location.x) * abs(ideal_car_location.z - ball_location.z)
            distance_ball_and_car_needed += Vector3(x, y, z).magnitude()+400
        if ideal_car_location.y > 5120: # backwall y
            x = abs(5120-ideal_car_location.y)
            y = abs(5120-ideal_car_location.y) / abs(ideal_car_location.y - ball_location.y) * abs(ideal_car_location.x - ball_location.x)
            z = abs(5120-ideal_car_location.y) / abs(ideal_car_location.y - ball_location.y) * abs(ideal_car_location.z - ball_location.z)
            distance_ball_and_car_needed +=Vector3(x, y, z).magnitude()+400
        if ideal_car_location.y < -5120: # backwall y
            x = abs(-5120-ideal_car_location.y)
            y = abs(-5120-ideal_car_location.y) / abs(ideal_car_location.y - ball_location.y) * abs(ideal_car_location.x - ball_location.x)
            z = abs(-5120-ideal_car_location.y) / abs(ideal_car_location.y - ball_location.y) * abs(ideal_car_location.z - ball_location.z)           
            distance_ball_and_car_needed += Vector3(x, y, z).magnitude()+400
        
        return distance_ball_and_car_needed
