import vectors as vc
import numerical as nm

class RigidBody:
    def __init__(
            self, stats, consts, forces, mass, area, dragCoef,
            pos = vc.Vector.zero(3), vel = vc.Vector.zero(3),
            angPos = vc.Vector([0, 1, 0]), angVel = vc.Vector.zero(3)
    ):
        if len(pos) != len(vel):
            raise IndexError('Dimension of Velocity and Position Vectors do not Match')
        
        self.time = 0
        
        self.position = pos
        self.velocity = vel
        self.angularPosition = angPos
        self.angularVelocity = angVel
        
        self.mass = mass
        self.area = area
        self.dragCoef = dragCoef
        
        self.statistics = stats
        self.constraints = consts
        self.forces = forces
    
    def tick(self, dt):
        self.time += dt

        acc = vc.Vector.zero(len(self.velocity))
        for force in self.forces:
            force.tick(dt)
            acc += force(self) 
        acc /= self.mass
        
        self.velocity += acc * dt
        self.position += self.velocity * dt
        
        self.angularPosition /= abs(self.angularPosition)

        for const in self.constraints:
            const(self)
        
        for stat in self.statistics:
            stat(self)
    
    def run(self, duration, dt):
        time = 0
        while time <= duration:
            self.tick(dt)
            time += dt


# Statistics
class Statistics:
    def __init__(self):
        self.stats = nm.Data()
    
    def __call__(self, obj):
        self.stats[obj.time] = self.statistic(obj)

class RecordHeight(Statistics):
    def __init__(self, upward):
        Statistics.__init__(self)

        if abs(upward) == 0:
            raise ValueError('Upward Vector is Zero Vector')
        self.upward = upward / abs(upward)
    
    def statistic(self, obj):
        return obj.position * self.upward

class RecordSpeed(Statistics):
    def __init__(self):
        Statistics.__init__(self)
    
    def statistic(self, obj):
        return abs(obj.velocity)

# Constraints
class Ground:
    def __init__(self, point = vc.Vector.zero(3), normal = vc.Vector([0, 1, 0])):
        if abs(normal) == 0:
            raise ValueError('Normal Vector to Ground is Zero Vector')
        
        self.normal = normal / abs(normal)
        self.shift = self.normal * point
    
    def __call__(self, obj):
        if self.normal * obj.position < self.shift:
            obj.position -= (obj.position * self.normal) * self.normal
            obj.velocity *= 0

# Forces
class Gravity:
    def __init__(self, acc):
        self.acceleration = acc
    
    def tick(self, dt):
        pass
    
    def __call__(self, obj):
        return obj.mass * self.acceleration

class AirDrag:
    GAS_CONSTANT = 8.314459848
    
    def __init__(self, press, temp, lapseRate, molar, gacc, flowVel = vc.Vector.zero(3)):
        self.gravity = gacc
        
        self.pressure0 = press
        self.temperature0 = temp
        self.lapseRate = lapseRate
        self.molarity = molar
        self.flowVelocity = flowVel
    
    def tick(self, dt):
        pass
    
    def __call__(self, obj):
        alt = - self.gravity * obj.position / abs(self.gravity)
        
        flow = abs(self.flowVelocity - obj.velocity)
        if abs(obj.velocity) < 0.00001:
            return vc.Vector.zero(len(obj.velocity))
        
        direction = -obj.velocity / abs(obj.velocity)
        return flow * flow * self.density(alt) * obj.dragCoef * obj.area * direction / 2
    
    
    def pressure(self, alt):
        scale = 1 - self.lapseRate * alt / self.temperature0
        scale **= (abs(self.gravity) * self.molarity) / (AirDrag.GAS_CONSTANT * self.lapseRate)
        return self.pressure0 * scale
    
    def temperature(self, alt):
        return self.temperature0 - self.lapseRate * alt
    
    def density(self, alt):
        return (self.pressure(alt) * self.molarity) / (AirDrag.GAS_CONSTANT * self.temperature(alt))

class Engine:
    def __init__(self, thrust):
        self.thrust = thrust
        self.burntime = 0
    
    def tick(self, dt):
        self.burntime += dt
    
    def __call__(self, obj):
        if self.burntime not in self.thrust:
            return vc.Vector.zero(len(obj.velocity))
        
        return self.thrust[self.burntime] * obj.angularPosition



if __name__ == '__main__':
    g = 9.80665 * vc.Vector([0, -1, 0])
    grav = Gravity(g)
    drag = AirDrag(101325, 288.15, 0.0065, 0.0289644, g)
    
    csvfile = open('trial1.csv')
    thrustCurve = nm.Data.fromCSV(csvfile)
    eng = Engine(thrustCurve)
    
    ground = Ground()
    
    ht = RecordHeight(vc.Vector([0, 1, 0]))
    sp = RecordSpeed()
    
    rocket = RigidBody([ht, sp], [ground], [grav, eng, drag], mass = 0.1, area = 0.00008, dragCoef = 0.6)
    rocket.run(60, 0.01)
    
    print('Height: ' + str(ht.stats.maximum()))
    print('Speed: ' + str(sp.stats.maximum()))
