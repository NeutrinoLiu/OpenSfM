import numpy as np

RAW_FILE = "merged.ply"
TARGET_FILE = "denoised_naive.ply"
THRESHOLD = 0.0000001 # percentage square of the farthest distance, 1/1000 of diag in this case

def getXYZ(str_row):
    dat = str_row.split(' ')
    return list(map(float, dat[0:3])) + [0] # last element for not_alone flag

f = open(RAW_FILE, "r")
rows = f.readlines()
f.close()
head = rows[0:15]
body = rows[15:]

points = np.array(list(map(getXYZ, body)))
xb = min(points[:,0])
xe = max(points[:,0])
yb = min(points[:,1])
ye = max(points[:,1])
zb = min(points[:,2])
ze = max(points[:,2])
print(f"x:{xb}~{xe}\ty:{yb}~{ye}\tz:{zb}~{ze}")

#
xe -= xb
ye -= yb
ze -= zb
dig = xe*xe + ye*ye + ze*ze
dist_thre = dig * THRESHOLD 
#

points = list(map(list,points))

f = open(TARGET_FILE, "w+")
for line in head:
    f.write(line)

k = 0
for i in range(len(points)):
    if i % 10000 == 0:
        print(f"screened {k} points from {i}/{len(points)} raw cloud points")
    for j in range(len(points)):
        if (points[i][3] == 1) or (0 < ((points[i][0]-points[j][0])**2 + (points[i][1]-points[j][1])**2 + (points[i][2]-points[j][2])**2) < dist_thre):
            points[j][3] = 1
            f.write(body[i])
            k += 1

f.close()

