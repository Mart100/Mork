import math
import inspect

class Vector2:
    def __init__(self, x=0, y=0):
        self.x = float(x)
        self.y = float(y)

    def __add__(self, val):
        return Vector2(self.x + val.x, self.y + val.y)
    def __truediv__(self, val):
        return Vector2(self.x / val.x, self.y / val.y)
    def multiply(self, val):
        return Vector2(self.x*val, self.y*val)
    def get_3d(self, val):
        return Vector3(self.x, self.y, val)
    def __sub__(self, val):
        return Vector2(self.x - val.x, self.y - val.y)
    def unit_vector(self):
        magnitude = self.magnitude()
        return Vector2(self.x/magnitude, self.y/magnitude)
    def correction_to(self, ideal):
        # The in-game axes are left handed, so use -x
        current_in_radians = math.atan2(self.y, -self.x)
        ideal_in_radians = math.atan2(ideal.y, -ideal.x)

        correction = ideal_in_radians - current_in_radians

        # Make sure we go the 'short way'
        if abs(correction) > math.pi:
            if correction < 0:
                correction += 2 * math.pi
            else:
                correction -= 2 * math.pi

        return correction
    def get_angle(self):
        if self.x == 0: self.x = 0.0000000000000001
        return math.degrees(math.atan2(self.y, self.x))
    def magnitude(self): 
        return (self.x ** 2 + self.y ** 2) ** 0.5

class Vector3:
    def __init__(self, x=0, y=0, z=0):
        if type(x) == dict or hasattr(x, 'x'):
            self.x = float(x.x)
            self.y = float(x.y)
            self.z = float(x.z)
        elif type(x) == int or type(x) == float:
            self.x = float(x)
            self.y = float(y)
            self.z = float(z)
    
    def unit_vector(self):
        magnitude = self.magnitude()
        return Vector3(self.x/magnitude, self.y/magnitude, self.z/magnitude)
    def get_angle(self, wich):
        if wich == 'x': return math.atan2(math.sqrt(self.y**2+self.z**2),self.x)
        if wich == 'y': return math.atan2(math.sqrt(self.z**2+self.x**2),self.y)
        if wich == 'z': return math.atan2(math.sqrt(self.x**2+self.y**2),self.z)-math.pi/2
    def get_array(self):
        return [self.x, self.y, self.z]
    def get_2d(self):
        return Vector2(self.x, self.y)
    def magnitude(self):
        return (self.x ** 2 + self.y ** 2 + self.z ** 2) ** 0.5
    def __add__(self, val):
        return Vector3(self.x + val.x, self.y + val.y, self.z + val.z)
    def __truediv__(self, val):
        return Vector3(self.x / val.x, self.y / val.y, self.z / val.z)
    def __mul__(self, val):
        return Vector3(self.x * val.x, self.y * val.y, self.z * val.z)
    def __sub__(self, val):
        return Vector3(self.x - val.x, self.y - val.y, self.z - val.z)
    def difference(val1, val2):
        return Vector3(val1.x - val2.x, val1.y - val2.y, val1.z - val2.z)
    def draw(self, agent, pos, color=[0,0,0]):
        color = more_colors(agent, color)
        agent.renderer.draw_line_3d(pos.get_array(), (pos+self).get_array(), agent.renderer.create_color(255, color[0], color[1], color[2]))
    def multiply(self, val):
        return Vector3(self.x*val, self.y*val, self.z*val)
    def draw_to(self, agent, to, color=[0,0,0]):
        color = more_colors(agent, color)
        agent.renderer.draw_line_3d(self.get_array(), to.get_array(), agent.renderer.create_color(255, color[0], color[1], color[2]))
    

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