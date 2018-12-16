from vectors import *
from tools import *

def get_boost(agent, packet):
    my_car = packet.game_cars[agent.index]
    car_location = Vector2(my_car.physics.location.x, my_car.physics.location.y)
    if my_car.boost > 40: agent.car_status = 'none'

    closest_boost = get_closest_boost(agent, packet)
    #Turn to the boost
    aim_to(agent, Vector3(closest_boost.location))
    # If close to the ball. Use Last boost
    if Vector2(car_location.x - closest_boost.location.x, car_location.y - closest_boost.location.y).magnitude() < my_car.boost*100:
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
   
