from Motion import *

class MotorDataLogger():
    def __init__(self, motion_class, filename):
        self.motion_class = motion_class
        self.filename = filename

        #Clears the file
        open(self.filename,"w").close()

        self.file = open(self.filename,"a")
        self.file.write("VL_Counts" + "," + "PWM" + "," + "Over_c" + "," +
                        "VR_Counts" + "," + "PWM" + "," + "Over_c" + "," + 
                        "HL_Counts" + "," + "PWM" + "," + "Over_c" + "," +
                        "HR_Counts" + "," + "PWM" + "," + "Over_c" + "," +
                        "Bat_Current" +"\n")
    
    def store(self, bat_current = None):
        """Store all motor-data (Counts, PWM, Overcurrent) in file"""
        vl_counts = self.motion_class.motor_VL.get_counts()
        vl__PWM =   self.motion_class.motor_VL.get_PWM()
        vl_over =   self.motion_class.motor_VL.get_overcurrent()
        vr_counts = self.motion_class.motor_VR.get_counts()
        vr__PWM =   self.motion_class.motor_VR.get_PWM()
        vr_over =   self.motion_class.motor_VR.get_overcurrent()
        hl_counts = self.motion_class.motor_HL.get_counts()
        hl__PWM =   self.motion_class.motor_HL.get_PWM()
        hl_over =   self.motion_class.motor_HL.get_overcurrent()
        hr_counts = self.motion_class.motor_HR.get_counts()
        hr__PWM =   self.motion_class.motor_HR.get_PWM()
        hr_over =   self.motion_class.motor_HR.get_overcurrent()

        self.file.write(    str(vl_counts) + "," + str(vl__PWM) + "," + str(vl_over) + "," +
                            str(vr_counts) + "," + str(vr__PWM) + "," + str(vr_over) + "," +
                            str(hl_counts) + "," + str(hl__PWM) + "," + str(hl_over) + "," +
                            str(hr_counts) + "," + str(hr__PWM) + "," + str(hr_over) + "," +
                            str(bat_current) + "\n")
        self.file.flush()

    def close_file(self):
        self.file.close()

if __name__ == "__main__":

    motion = Motion()
    motor_data = MotorDataLogger(motion, "motor_data_log.txt")
    motor_data.store()
