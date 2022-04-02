import time

class Regulators:
    __Kp = 0
    __Ki = 0
    __Kd = 0

    __prev = 0
    __sum = 0
    __freq = 0
    __time = 0

    def __init__(self, Kp, Ki, Kd, Ki_border=15):
        self.__Kp = Kp
        self.__Ki = Ki
        self.__Kd = Kd
        self.__KI_border=Ki_border
        self.__time = time.time()

    def set(self, Kp, Ki,Kd):
        self.__Kp = Kp
        self.__Ki = Ki
        self.__Kd = Kd
    def reset(self):
        self.__sum=0
        pass
    def apply(self, to_set, current):
        error = to_set - current
        self.__update_freq()
        # value = self.__Prop(error) + self.__Integ(error) + self.__Diff(error)
        #start
        value = 0
        value += self.__Prop(error)
        value += self.__Integ(error)
        value += self.__Diff(error)
        #print(self.__Diff(error), self.__freq)
        # end
        self.__prev = error
        return value

    def __Prop(self, error):
        return error * self.__Kp

    def __Integ(self, error):
        if self.__freq == 0: self.__freq = 1
        self.__sum += self.__Ki * (1 / self.__freq) * error
        if abs(self.__sum)> self.__KI_border:
            if self.__sum<0:
                self.__sum = -self.__KI_border
            else:
                self.__sum = self.__KI_border
        return self.__sum

    def __Diff(self, error):
        return self.__Kd / self.__freq * (error - self.__prev)

    def __update_freq(self):
        #self.__freq = -time. ticks_diff(self.__time, time.time())
        self.__freq = time.time() -self.__time
        #print(self.__freq)
        self.__time = time.time()


#reg_move = Regulators(30, 0.0001, 300)
#reg_move.set(p, i, d)
#p = reg_move.apply(to_set, current)