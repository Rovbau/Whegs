from Scanner3d import *

scanner = Scanner()

n = 15 #zeilen
m = 20 #spalten
sorted_liste = [[0] * m for i in range(n)]
all_data = []
obstacles = [[]]

def fill_in():
    for element in all_data:
        sorted_liste[6+int(element[0]/1.8)][6+int(element[1]/1.8)] = element[2]

def pretty_print():
    for line in sorted_liste:
        for element in line:
            print("%4d" % element),
        print("\n")


scanner.do_3D_scan(step = 10)
scans = scanner.get_scan_data()

all_data = [[7.2, 7.2, 50] , [9.0, 7.2, 51]  , [-3.6, 7.2, 20], [-3.6, 9.0, 15],
            [0, 1.8, 13]   , [-5.4, 7.2, 22], [0, 5.4, 33]   , [0, 7.2, 16],
            [0, 9.0, 17]   , [-1.8, 9.0, 18], [-1.8, 7.2, 19],
            [-1.8, 5.4, 34], [-1.8, 3.6, 21]]


fill_in()
pretty_print()


for spalte in range(m):
    connect = False
    for zeile in range(n-1):
        next_to = (sorted_liste[zeile][spalte] - sorted_liste[zeile+1][spalte])
        
        if abs(next_to) < 5 and next_to != 0:
            if connect == False:
                obstacles.append([sorted_liste[zeile][spalte]])
                connect = True
            else:
                obstacles[-1].append(sorted_liste[zeile+1][spalte])
        else:
            connect = False
            
print(obstacles)
            
  
