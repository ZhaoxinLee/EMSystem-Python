import numpy as np
from numpy import genfromtxt
import matplotlib.pyplot as plt


path = 'C:\\Users\\MicroRoboticsLab\\Documents\\EM System Files\\Code-GitHub\\Clinical-Electromagnetic-Actuation-System-Core\\src\\build-EM_System_App-Desktop_Qt_5_15_2_MSVC2019_64bit-Debug\\robot_data.csv'
robot_data = genfromtxt(path, delimiter=',')

print(robot_data)

time = robot_data[0, :]
q1d = robot_data[1, :]
q1m = robot_data[3, :]

#for i in range(len(q1d)):
#    q1d[i] = (180 / 3.14159265359)*q1d[i]
#    q1m[i] = (180 / 3.14159265359)*q1m[i]

plt.figure()
plt.plot(time[:], q1d[:])
plt.plot(time[:], q1m[:])
plt.xlabel('Time (s)')
plt.ylabel('Angle (deg)')
plt.show()
