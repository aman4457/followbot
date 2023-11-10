import numpy as np

last_anchor_distance = np.array([25.0, 31, 50.0])  # Replace with actual values
anchor_matrix = np.array([[-19.75, 0.0], [19.75, 0.0], [0.0, 30.0]])  # Replace with actual values
current_tag_position = np.zeros(2)
current_distance_rmse = 0.0


N_ANCHORS = 3  # Replace with the actual number of anchors



def trilat2D_3A():

    # for method see technical paper at
    # https://www.th-luebeck.de/fileadmin/media_cosa/Dateien/Veroeffentlichungen/Sammlung/TR-2-2015-least-sqaures-with-ToA.pdf
    # S. James Remington 1/2022
    #
    # A nice feature of this method is that the normal matrix depends only on the anchor arrangement
    # and needs to be inverted only once. Hence, the position calculation should be robust.

    # Preliminary work
    static_first = True  # first time through, some preliminary work
    b = np.zeros(N_ANCHORS - 1)  # temp vector, distances from anchors
    d = np.copy(last_anchor_distance)

    # Copy distances to local storage
    if static_first:
        x = np.zeros(N_ANCHORS)  # intermediate vectors
        y = np.zeros(N_ANCHORS)
        k = np.zeros(N_ANCHORS)
        Ainv = np.zeros((2, 2))

        for i in range(N_ANCHORS):
            x[i] = anchor_matrix[i][0]
            y[i] = anchor_matrix[i][1]
            k[i] = x[i] * x[i] + y[i] * y[i]

        # Set up least squares equation
        A = np.zeros((N_ANCHORS - 1, 2))
        for i in range(1, N_ANCHORS):
            A[i - 1][0] = x[i] - x[0]
            A[i - 1][1] = y[i] - y[0]

        # Invert A
        det = A[0, 0] * A[1, 1] - A[1, 0] * A[0, 1]
        if np.abs(det) < 1.0E-4:
            print("***Singular matrix, check anchor coordinates***")
            while True:
                pass  # hang

        det = 1.0 / det
        # Scale adjoint
        Ainv[0, 0] = det * A[1, 1]
        Ainv[0, 1] = -det * A[0, 1]
        Ainv[1, 0] = -det * A[1, 0]
        Ainv[1, 1] = det * A[0, 0]

        static_first = False

    for i in range(1, N_ANCHORS):
        b[i - 1] = d[0] * d[0] - d[i] * d[i] + k[i] - k[0]

    # Least squares solution for position
    # solve: 2 * A * rc = b
    current_tag_position[0] = 0.5 * (Ainv[0, 0] * b[0] + Ainv[0, 1] * b[1])
    current_tag_position[1] = 0.5 * (Ainv[1, 0] * b[0] + Ainv[1, 1] * b[1])

    # Calculate RMS error for distances
    rmse = 0.0
    for i in range(N_ANCHORS):
        dc0 = current_tag_position[0] - anchor_matrix[i][0]
        dc1 = current_tag_position[1] - anchor_matrix[i][1]
        dc0 = d[i] - np.sqrt(dc0 * dc0 + dc1 * dc1)
        rmse += dc0 * dc0

    current_distance_rmse = np.sqrt(rmse / float(N_ANCHORS))

    return 1


trilat2D_3A()

# Example usage:
#last_anchor_distance = np.array([10.0, 12.0, 15.0])  # Replace with actual values
#anchor_matrix = np.array([[0.0, 0.0], [5.0, 0.0], [0.0, 5.0]])  # Replace with actual values
# current_tag_position = np.zeros(2)
# current_distance_rmse = 0.0
# trilat2D_3A()
print("Current Tag Position:", current_tag_position)
#print("Current Distance RMSE:", current_distance_rmse)
