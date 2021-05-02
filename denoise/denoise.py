import numpy as np

RAW_FILE = "merged.ply"
TARGET_FILE = "denoised.ply"
THRESHOLD = 0.00001 # percentage square of the farthest distance, 1/1000 of diag in this case
POINT_DENSITY = 20
# x_bins = 420
# y_bins = 280
# z_bins = 280
x_bins = 800
y_bins = 800
z_bins = 400

def getXYZ(str_row):
    dat = str_row.split(' ')
    return list(map(float, dat[0:3]))


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
print(f"field size:\t\tx[{xb}~{xe}] y[{yb}~{ye}] z[{zb}~{ze}]")

#
points[:,0] -= xb
xe -= xb
points[:,1] -= yb
ye -= yb
points[:,2] -= zb
ze -= zb
dig = xe*xe + ye*ye + ze*ze
dist_thre = dig * THRESHOLD 
print(f"largest dist will be:\t{dist_thre}")
#

x_unit = xe/x_bins
y_unit = ye/y_bins
z_unit = ze/z_bins
print("bin size are:\t\t" + format(x_unit,'.4f') + " x " + format(y_unit,'.4f') + " x " + format(z_unit, '.4f'))

bin_array = np.zeros([x_bins+1, y_bins+1, z_bins+1, 0]).tolist()
#print(f"x:{len(bin_array)} y:{len(bin_array[1])} z:{len(bin_array[1][1])}")

points = list(map(list,points))

for i in range(len(points)):
    # print(pt)
    # print(len(bin_array[ int(pt[0]/x_unit) ][ int(pt[1]/y_unit) ][ int(pt[2]/z_unit) ]))
    points[i] += [i, 0] # now each point: x,y,z,index,notAlone
    (bin_array[ int(points[i][0]/x_unit) ][ int(points[i][1]/y_unit) ][ int(points[i][2]/z_unit) ]).append(points[i])
    # print(len(bin_array[ int(pt[0]/x_unit) ][ int(pt[1]/y_unit) ][ int(pt[2]/z_unit) ]))


# for x in range(x_bins+1):
#     for y in range(y_bins+1):
#         for z in range(z_bins+1):
#             if len(bin_array[x][y][z]) > 0:
#                 print([x, y, z], end = ':')
#                 print((bin_array[x][y][z])[0:3])

def not_alone(pt, list_pt):
    if pt[4] == 1:
        return True
    for npt in list_pt:
        if 0 < ((npt[0]-pt[0])**2 + (npt[1]-pt[1])**2 + (npt[2]-pt[2])**2) < dist_thre:
            points[npt[3]][4] = 1 # the npt is also not alone then
            return True
    return False

def count_friend(pt, list_pt):
    cnt = 0
    for npt in list_pt:
        if 0 < ((npt[0]-pt[0])**2 + (npt[1]-pt[1])**2 + (npt[2]-pt[2])**2) < dist_thre:
            cnt += 1
    return cnt

def neighbor(pt):
    x_bin = int (pt[0] / x_unit)
    y_bin = int (pt[1] / y_unit)
    z_bin = int (pt[2] / z_unit)
    res = []
    for i in range(max(0,x_bin-1), min(x_bin+2, x_bins+1)):
        for j in range(max(0,y_bin-1), min(y_bin+2, y_bins+1)):
            for k in range(max(0,z_bin-1), min(z_bin+2, z_bins+1)):
                res += bin_array[i][j][k]
    return res

k = 0
for i in range(len(points)):
    if (i % 1000 == 0) or (i == (len(points) -1)):
        print(f"screened {k} points from {i}/{len(points)} raw cloud points")
    # if not_alone(points[i], neighbor(points[i])):
    if count_friend(points[i], neighbor(points[i])) >= POINT_DENSITY:
        points[i][4] = 1
        k += 1

f = open(TARGET_FILE, "w+")
for line in head[0:2]:
    f.write(line)
f.write(f"element vertex {k}\n")
for line in head[3:]:
    f.write(line)

for i in range(len(points)):
    if points[i][4] == 1:
        f.write(body[i])

f.close()
