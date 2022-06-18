"""
Iterative Closest Point (ICP) SLAM example
author: Atsushi Sakai (@Atsushi_twi), Göktuğ Karakaşlı, Shamil Gemuev
"""

import math
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401 unused import
import matplotlib.pyplot as plt
import numpy as np

#  ICP parameters
EPS = 0.00001
MAX_ITER = 1000

show_animation = False


def icp_matching(previous_points, current_points):
    """
    Iterative Closest Point matching
    - input
    previous_points: 2D or 3D points in the previous frame
    current_points: 2D or 3D points in the current frame
    - output
    R: Rotation matrix
    T: Translation vector
    """
    H = None  # homogeneous transformation matrix

    dError = np.inf
    preError = np.inf
    count = 0

    if show_animation:
        fig = plt.figure()
        if previous_points.shape[0] == 3:
           fig.add_subplot(111, projection='3d')

    while dError >= EPS:
        count += 1

        if show_animation:  # pragma: no cover
            plot_points(previous_points, current_points, fig)
            plt.pause(1.1)

        indexes, error = nearest_neighbor_association(previous_points, current_points)
        Rt, Tt = svd_motion_estimation(previous_points[:, indexes], current_points)
        # update current points
        current_points = (Rt @ current_points) + Tt[:, np.newaxis]

        dError = preError - error
        #print("Residual:", error)

        if dError < 0:  # prevent matrix H changing, exit loop
            print("Not Converge...", preError, dError, count)
            break

        preError = error
        H = update_homogeneous_matrix(H, Rt, Tt)

        if dError <= EPS:
            print("Converge", error, dError, count)
            break
        elif MAX_ITER <= count:
            print("Not Converge...", error, dError, count)
            break

    R = np.array(H[0:-1, 0:-1])
    T = np.array(H[0:-1, -1])

    return R, T


def update_homogeneous_matrix(Hin, R, T):

    r_size = R.shape[0]
    H = np.zeros((r_size + 1, r_size + 1))

    H[0:r_size, 0:r_size] = R
    H[0:r_size, r_size] = T
    H[r_size, r_size] = 1.0

    if Hin is None:
        return H
    else:
        return Hin @ H


def nearest_neighbor_association(previous_points, current_points):

    # calc the sum of residual errors
    delta_points = previous_points - current_points
    d = np.linalg.norm(delta_points, axis=0)
    error = sum(d)

    # calc index with nearest neighbor assosiation
    d = np.linalg.norm(np.repeat(current_points, previous_points.shape[1], axis=1)
                       - np.tile(previous_points, (1, current_points.shape[1])), axis=0)
    indexes = np.argmin(d.reshape(current_points.shape[1], previous_points.shape[1]), axis=1)

    return indexes, error


def svd_motion_estimation(previous_points, current_points):
    pm = np.mean(previous_points, axis=1)
    cm = np.mean(current_points, axis=1)

    p_shift = previous_points - pm[:, np.newaxis]
    c_shift = current_points - cm[:, np.newaxis]

    W = c_shift @ p_shift.T
    u, s, vh = np.linalg.svd(W)

    R = (u @ vh).T
    t = pm - (R @ cm)

    return R, t


def plot_points(previous_points, current_points, figure):
    # for stopping simulation with the esc key.
    plt.gcf().canvas.mpl_connect(
        'key_release_event',
        lambda event: [exit(0) if event.key == 'escape' else None])
    if previous_points.shape[0] == 3:
        plt.clf()
        axes = figure.add_subplot(111, projection='3d')
        axes.scatter(previous_points[0, :], previous_points[1, :],
                    previous_points[2, :], c="r", marker=".")
        axes.scatter(current_points[0, :], current_points[1, :],
                    current_points[2, :], c="b", marker=".")
        axes.scatter(0.0, 0.0, 0.0, c="r", marker="x")
        figure.canvas.draw()
    else:
        plt.cla()
        plt.plot(previous_points[0, :], previous_points[1, :], ".r")
        plt.plot(current_points[0, :], current_points[1, :], ".b")
        plt.plot(0.0, 0.0, "xr")
        plt.axis("equal")


def match_scans(scan1, scan2):
    # simulation parameters
    nPoint = len(scan1)
    fieldLength = 1000.0
    motion = [100.0, 0.0, np.deg2rad(-10.0)]  # movement [x[m],y[m]

    nsim = 1  # number of simulation

    for _ in range(nsim):
        # previous points
        px = [item[0] for item in scan1]
        py = [item[1] for item in scan1]
        previous_points = np.vstack((px, py))

        # current points
        cx = [item[0] for item in scan2]
        cy = [item[1] for item in scan2]
        current_points = np.vstack((cx, cy))

        R, T = icp_matching(previous_points, current_points)
        #print("R:", R)
        #print("T:", T)
        turn = np.math.degrees(np.math.asin(R[1][0]))
        x, y = T
        return(x ,y ,turn)



  
if __name__ == '__main__':

    # Set show_animation to True if you have a Screen to show the animation

    scan1 = [[91, -199], [86, -198], [82, -195], [77, -192], [73, -188], [69, -186], [65, -183], [60, -182], [55, -181], [51, -178], [48, -175], [44, -173], [39, -170], [39, -158], [41, -140], [46, -117], [44, -110], [38, -114], [36, -111], [33, -108], [29, -106], [27, -102], [23, -103], [21, -99], [16, -99], [15, -95], [-3, -119], [-7, -117], [-3, -103], [2, -86], [8, -71], [2, -74], [-5, -80], [-20, -94], [-34, -105], [-40, -106], [-42, -102], [-20, -70], [-19, -61], [-18, -56], [-20, -53], [-22, -50], [-1, -25], [2, -17], [1, -14], [0, -13], [-2, -11], [-3, -8], [0, -3], [-2, 0], [0, 5], [-2, 5], [-3, 8], [-6, 9], [-5, 12], [0, 20], [21, 36], [22, 39], [22, 41], [30, 48], [39, 55], [39, 57], [39, 60], [41, 62], [41, 64], [39, 65], [38, 65], [35, 66], [33, 68], [31, 68], [29, 69], [28, 71], [26, 71], [22, 72], [20, 74], [16, 75], [17, 77], [18, 79], [18, 80], [19, 83], [21, 85], [22, 86], [22, 89], [25, 91], [25, 93], [28, 95], [48, 98], [50, 99], [55, 101], [54, 103]]

    scan2 = [[103, -193], [99, -190], [94, -188], [89, -187], [85, -184], [81, -182], [76, -178], [71, -177], [68, -175], [63, -173], [60, -168], [62, -145], [63, -124], [62, -118], [59, -115], [56, -110], [52, -111], [47, -114], [48, -103], [44, -102], [40, -102], [37, -99], [34, -99], [32, -94], [12, -122], [10, -119], [22, -88], [22, -81], [24, -70], [19, -74], [5, -87], [0, -88], [-12, -100], [-24, -109], [-2, -74], [-4, -71], [-7, -68], [-6, -62], [-7, -57], [10, -32], [9, -28], [12, -20], [11, -17], [10, -15], [9, -11], [10, -8], [9, -5], [8, -3], [10, 2], [6, 2], [5, 4], [4, 7], [8, 14], [25, 29], [28, 34], [34, 40], [43, 49], [44, 52], [44, 54], [46, 57], [46, 59], [44, 60], [43, 61], [40, 62], [39, 63], [36, 63], [34, 64], [30, 65], [27, 65], [24, 65], [31, 71], [31, 72], [28, 74], [28, 75], [37, 81], [36, 81], [37, 84], [34, 84], [34, 86], [51, 91], [55, 94], [56, 96], [57, 96], [57, 98], [57, 99], [58, 101], [56, 101], [56, 103], [59, 104], [60, 106]]
 
    match_scans(scan1, scan2)
 
  