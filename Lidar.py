import smbus
import time

class Lidar():
  def __init__(self):
    self.address = 0x62
    self.distWriteReg = 0x00
    self.distWriteVal = 0x04
    self.distReadReg1 = 0x8f
    self.distReadReg2 = 0x10
    self.velWriteReg = 0x04
    self.velWriteVal = 0x08
    self.velReadReg = 0x09
    self.status = 0x01
    self.connect(1)
    print("Init Lidar")

  def connect(self, bus):
    try:
      self.bus = smbus.SMBus(bus)
      time.sleep(0.5)
      return 0
    except:
      return -1

  def writeAndWait(self, register, value):
    try:
      self.bus.write_byte_data(self.address, register, value);
    except:
      print("Lidar not Write")
      return (-1)
    
  def readAndWait(self, register):
    try:
        res = self.bus.read_byte_data(self.address, register)
    except:
        res = 0
    return res

  def get_distance(self):
    """Read Lidar distance [cm], Waits for BusyFlag = low""" 
    self.writeAndWait(self.distWriteReg, self.distWriteVal)
    count = 0
    status_bit = self.readAndWait(self.status)
    status_bit = '{0:08b}'.format(status_bit)
    while status_bit[7] == "1":
        status_bit = self.readAndWait(self.status)
        status_bit = '{0:08b}'.format(status_bit)
        count += 1
        #time.sleep(0.01)
    dist1 = self.readAndWait(self.distReadReg1)
    dist2 = self.readAndWait(self.distReadReg2)
    #print(count)
    return (dist1 << 8) + dist2

  def get_velocity(self):
    self.writeAndWait(self.distWriteReg, self.distWriteVal)
    self.writeAndWait(self.velWriteReg, self.velWriteVal)
    vel = self.readAndWait(self.velReadReg)
    return self.signedInt(vel)

  def signedInt(self, value):
    if value > 127:
      return (256-value) * (-1)
    else:
      return value

if __name__ == "__main__":

  lidar = Lidar()

  liste = []
  start = time.time()
  for  i in range(30):
    x = lidar.get_distance()
    time.sleep(1)    
  
    print(x)
  stop = time.time()
  print(stop-start)

  
