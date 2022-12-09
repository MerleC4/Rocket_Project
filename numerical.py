import random
import math
import csv


def binsearch(arr, target):
        lower, upper = 0, len(arr) - 1
        
        while abs(upper - lower) > 1:
            mid = (upper + lower) // 2
            val = arr[mid]
            
            if target < val:
                upper = mid
            elif target > val:
                lower = mid
            else:
                return (mid, mid)
        
        return (lower, upper)


class Data:
    def __init__(self, start = 0, end = 0, values = []):
        self.bounds = (start, end)
        self.values = sorted(values, key = lambda x: x[0])
    
    def __iter__(self):
        for item in self.values:
            yield item
    
    def __len__(self):
        return self.bounds[1] - self.bounds[0]
    
    
    def __getitem__(self, time):
        if time < self.bounds[0] or self.bounds[1] < time:
            raise KeyError('Time Outside of Bounds')
        
        keys, vals = zip(*self.values)
        lower, upper = binsearch(keys, time)
        
        if lower == upper:
            return vals[lower]
        
        start, end = keys[lower], keys[upper]
        first, second = vals[lower], vals[upper]
        
        x = (time - start) / (end - start)
        return second * x + first * (1 - x)
    
    def __setitem__(self, time, val):
        indices = [i for i in range(len(self.values)) if self.values[i][0] == time]
        
        if len(indices) == 0:
            self.values.append((time, val))
            
            self.bounds = (min(time, self.bounds[0]), max(time, self.bounds[1]))
        else:
            self.values[indices[0]] = (time, val)
            for ind in indices[1:]:
                del self.values[ind]
    
    def __delitem__(self, time):
        if time < self.bounds[0] or self.bounds[1] < time:
            raise KeyError('Time Outside of Bounds')
        
        indices = [i for i in range(len(self.values)) if self.values[i][0] == time]
        for ind in indices:
            del self.values[ind]
    
    def __contains__(self, time):
        return self.bounds[0] <= time and time <= self.bounds[1]
    
    
    def maximum(self):
        time, high = 0, 0
        isset = False
        
        for t, v in self.values:
            if not isset or v > high:
                time, high = t, v
                isset = True
        
        return time, high
    
    def minimum(self):
        time, low = 0, 0
        isset = False
        
        for t, v in self.values:
            if not isset or v < low:
                time, low = t, v
                isset = True
        
        return time, low
    
    
    @staticmethod
    def fromCSV(csvfile, valueCol = 1):
        rdr = csv.reader(csvfile)
        
        start, end = 0, 0
        isset, isfirst = False, True
        values = []
        for row in rdr:
            if isfirst:
                isfirst = False
                continue
            
            time = float(row[0])
            if not isset:
                start, end = time, time
                isset = True
            else:
                start = min(start, time)
                end = max(end, time)
            
            values.append((time, float(row[valueCol])))
        
        return Data(start, end, values)


class StochasticData:
    def __init__(self, mean, stdev):
        lower = max(len(mean)[0], len(stdev)[0])
        upper = min(len(mean)[1], len(stdev)[1])
        self.bounds = (lower, upper)
        
        self.mean = mean
        self.stdev = stdev
    
    def __len__(self):
        return self.bounds
    
    def __getitem__(self, time):
        if time < self.bounds[0] or self.bounds[1] < time:
            raise KeyError('Time Outside of Bounds')
        
        return random.normalvariate(self.mean[time], self.stdev[time])
    
    def __setitem__(self, time, value):
        if time < self.bounds[0] or self.bounds[1] < time:
            raise KeyError('Time Outside of Bounds')
        
        self.mean[time], self.stdev[time] = value
    
    
    def fromSample(datas):
        sdt = StochasticData()
        for dt in datas:
            for t, _ in dt:
                if t in sdt:
                    continue
                
                mean, mean2 = 0, 0
                for other in datas:
                    v = other[t]
                    mean += v
                    mean2 += v * v
                
                mean /= len(datas)
                mean2 /= len(datas)
                
                correction = len(datas) / max(1, len(datas) - 1)
                stdev = math.sqrt((mean2 - mean * mean) * correction)
                sdt[t] = mean, stdev
        
        return sdt
