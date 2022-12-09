import math


class Vector:
    def __init__(self, comps):
        self.components = comps
    
    def __len__(self):
        return len(self.components)
    
    def __abs__(self):
        total = 0
        for comp in self.components:
            total += comp * comp
        
        return math.sqrt(total)
    
    def __neg__(self):
        newcomps = []
        for comp in self.components:
            newcomps.append(-comp)
        
        return Vector(newcomps)
    
    
    def __getitem__(self, key):
        return self.components[key]
    
    
    def __add__(self, other):
        if len(self.components) != len(other.components):
            raise IndexError('Vector Dimensions do not Match')
        
        newcomps = []
        for i in range(len(self.components)):
            newcomps.append(self.components[i] + other.components[i])
        
        return Vector(newcomps)
    
    def __sub__(self, other):
        if len(self.components) != len(other.components):
            raise IndexError('Vector Dimensions do not Match')
        
        newcomps = []
        for i in range(len(self.components)):
            newcomps.append(self.components[i] - other.components[i])
        
        return Vector(newcomps)
    
    
    def __mul__(self, other):    
        if isinstance(other, Vector):
            if len(self.components) != len(other.components):
                raise IndexError('Vector Dimensions do not Match')
            
            total = 0
            for i in range(len(self.components)):
                total += self.components[i] * other.components[i]
            
            return total
        else:
            newcomps = []
            for comp in self.components:
                newcomps.append(comp * other)
            
            return Vector(newcomps)
    
    def __rmul__(self, other):
        return self.__mul__(other)
    
    def __xor__(self, other):
        selfLen, otherLen = len(self.components), len(other.components)
        if selfLen != otherLen:
            raise IndexError('Vector Dimensions do not Match')
        
        if selfLen == 2:
            x1, y1 = self.components
            x2, y2 = other.components
            return Vector([0, 0, x1 * y2 - y1 * x2])
        elif selfLen == 3:
            x1, y1, z1 = self.components
            x2, y2, z2 = other.components
            return Vector([y1 * z2 - z1 * y2, z1 * x2 - x1 * z2, x1 * y2 - y1 * x2])
        else:
            raise IndexError('Vector Cross Product not supported for beyond 3 Dimensions')
    
    def __truediv__(self, scalar):
        newcomps = []
        for comp in self.components:
            newcomps.append(comp / scalar)
        
        return Vector(newcomps)
    
    def __div__(self, scalar):
        return self.__truediv__(scalar)
    
    def __floordiv__(self, scalar):
        newcomps = []
        for comp in self.components:
            newcomps.append(comp // scalar)
        
        return Vector(newcomps)
    
    
    def __repr__(self):
        return 'Vector([' + ', '.join(map(str, self.components)) + '])'
    
    
    def rotate(self, rotand, angle):
        if abs(self) == 0:
            raise ValueError('Rotator Vector is Zero Vector')
        
        c, s = math.cos(angle), math.sin(angle)
        axis = self / abs(self)
        return rotand * c + (axis ^ rotand) * s + axis * (axis * rotand) * (1 - c)
    
    
    @staticmethod
    def zero(dims):
        return Vector([0] * dims)
