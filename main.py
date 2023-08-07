###########################

# NAME: Kodari Saipranav Reddy
# Roll Number: CS20B040
# Course: CS3205 Jan. 2023 semester
# Lab number: 5
# Date of submission: Apr 28,2023
# I confirm that the source file is entirely written by me without
# resorting to any dishonest means.
# Website(s) that I used for basic socket programming code are:
# URL(s): NA

############################

import random
import socket
import time
import threading
import sys

const = False
# variable for termination condition


def send(src_id, neighbours, Socket, Hello_Interval, LSA_Interval, matrix, temp):
    if temp == 1:
        # Condition for Sending hello

        while not const:
            buffer = "HELLO" + " " + str(src_id)
            # buffer containing hello and src id
            length = len(neighbours)
            i = 0
            while (i < length):
                if neighbours[i] != (-1, -1):
                    Socket.sendto(buffer.encode(), ('127.0.0.1', 10000+i))
                # Sending the buffer message to all the node's neighbors
                i += 1
            time.sleep(Hello_Interval)
            # Sleep for {Hello_Interval} time
            # The loop gets terminated when the termination constant becomes true

    else:
        # Else - for Sending LSA
        seq_Number = 0

        while not const:
            msg = ""
            count = 0
            length = len(matrix[src_id])
            i = 0

            while (i < length):
                if matrix[src_id][i] != -1:
                    string = str(matrix[src_id][i]) + " "
                    msg = msg + str(i) + " " + string
                    count += 1
                i += 1
            buffer = "LSA" + " " + str(src_id) + " " + str(seq_Number) + " " + str(count) + " " + msg
            # buffer containing LSA, src_id, seq_num, count and respective neigh and cost for next {count} number of cells

            i = 0
            length = len(neighbours)
            while (i < length):
                if neighbours[i] != (-1, -1):
                    Socket.sendto(buffer.encode(), ('127.0.0.1', 10000+i))
                # Sending the buffer which we got above to all the node's neighbors
                i += 1
            seq_Number += 1
            time.sleep(LSA_Interval)
            # Increase the seq_num and sleep for {LSA_Interval} time and the loop terminates when the termination const is true


def Receive(src_id, neighbours, Socket, Matrix):

    seq_num = [-1] * len(neighbours)
    buffersize = 4096
    # initializing  buffersize and seq_num

    while not const:

        try:
            msg, port_num = Socket.recvfrom(buffersize)
            K = msg.decode().split()
            port = int(port_num[1])
            # Receive the msg and get the msg and the port number from the message

            if K[0] == "HELLO":
                recv_id = int(K[1])
                Min_Cij, Max_Cij = neighbours[recv_id]
                # If the message is hello then get the min and max costs and pick a random cost in between them
                Cost_buffer = random.randint(Min_Cij, Max_Cij)
                buffer = "HELLOREPLY" + " " + str(src_id) + " " + str(recv_id) + " " + str(Cost_buffer)
                # Update the buffer for sending helloreply containing src and recvr id's and the cost
                Socket.sendto(buffer.encode(), ('127.0.0.1', 10000 + recv_id))
                # Sending the buffer

            elif K[0] == "HELLOREPLY":
                x, y, dist = int(K[1]), int(K[2]), int(K[3])
                Matrix[y][x] = dist
                # If the msg is helloreply update the Matrix

            elif K[0] == "LSA":
                # If message is LSA update the below variables
                recv_id, recv_seqnum, No_Entries = int(K[1]), int(K[2]), int(K[3])

                if seq_num[recv_id] < recv_seqnum:
                    seq_num[recv_id] = recv_seqnum

                    i = 0
                    while (i < No_Entries):
                        # The (2*i + 4) term in the msg will be id and the (2*i + 5) term will be the cost
                        id, cost = int(K[(2*i)+4]), int(K[(2*i)+5])

                        if Matrix[recv_id][id] == -1:
                            Matrix[recv_id][id] = cost
                        elif Matrix[recv_id][id] > cost:
                            Matrix[recv_id][id] = cost
                        # Updating the Matrix
                        i += 1
                    j = 0
                    while (j < len(neighbours)):
                        if j != recv_id and neighbours[j] != (-1, -1):
                            # Sending the message it had received (LSA table) to all its neighbors
                            Socket.sendto(msg, ('127.0.0.1', 10000+j))
                        j += 1

        # If recv had an issue then exception might occur and loop breaks
        except Exception as e:
            print(f"Error Occurred : {e}")
            break


def dijkstra(adj_matrix, start, end):
    Num_of_rout = len(adj_matrix)
    distances = {}
    visited = {}
    # initializing  Distances to INT_MAX and visited to False
    for i in range(Num_of_rout):
        distances[i] = sys.maxsize
        visited[i] = False
    distances[start] = 0
    # distance at start = 0
    path_frame = {start: {"distances": 0, "path": [start]}}
    # path_frame contains the distance to that node i and the path to i

    for i in range(Num_of_rout):
        current_vertex = -1
        min_distance = sys.maxsize
        for j in range(Num_of_rout):
            if not visited[j]:
                if (distances[j] < min_distance):
                    current_vertex = j
                    min_distance = distances[j]
            # If the node is not visited and the distance is less than min distance updating the current node and the min distance
        visited[current_vertex] = True
        # Making the node visited

        for j in range(Num_of_rout):
            if not visited[j]:
                if adj_matrix[current_vertex][j] > 0:
                    dist = distances[current_vertex] + adj_matrix[current_vertex][j]
                    # We will check whether the distance of the unvisited vertex from current vertex is less than the prev distance to the unvisited node
                    if dist < distances[j]:
                        distances[j] = dist
                        path_frame[j] = {"distances": dist, "path": path_frame[current_vertex]["path"] + [j]}
                    # If yes update the distances and the pathframe of that node
    return path_frame
    # returning the path_frame


def spf(src_id, matrix, outfile, SPF_Interval):
    time_const = 0
    while (time_const < 100):
        time.sleep(SPF_Interval)
        time_const += SPF_Interval
        # Sleep for {SPF_Interval} and update the time constant
        outfile.write(f"Routing Table for node number {src_id} at time {time_const}\n\n")
        headers = ("Destination","Path","Cost")
        row_format = "{:<14} {:<14} {:<8}"
        outfile.write(row_format.format(*headers))
        outfile.write("\n")
        # Updating the outfile - src_id and the time constant

        length = len(matrix)

        i = 0
        while (i < length):
            if i != src_id:

                path_frame = dijkstra(matrix, src_id, i)
                path_framei = path_frame[i]
                path = path_framei['path']
                shortest_distance = path_framei['distances']
                # Calling the dijkstra function and getting the path and distances of the particular node from the start node

                outfile.write(row_format.format(i,str(path),shortest_distance))
                outfile.write("\n")
                # Updating these values in the outfile
            i += 1
        outfile.write("\n")
    # Terminating the loop to close the outfile

    outfile.close()
    # Closing the outfile


if __name__ == "__main__":

    Node_identifier = 0
    Input_file = ''
    Output_file = ''
    Hello_Interval = 1
    LSA_Interval = 5
    SPF_Interval = 20
    # initializing  the variables to the default values

    inputs = sys.argv[1:]
    length = len(inputs)
    i = 0
    # Taking the inputs

    while i < length:
        if inputs[i] == '-i':
            Node_identifier = int(inputs[i+1])
            i += 2
        elif inputs[i] == '-f':
            Input_file = inputs[i+1]
            i += 2
        elif inputs[i] == '-o':
            Output_file = inputs[i+1]
            i += 2
        elif inputs[i] == '-h':
            Hello_Interval = int(inputs[i+1])
            i += 2
        elif inputs[i] == '-a':
            LSA_Interval = int(inputs[i+1])
            i += 2
        elif inputs[i] == '-s':
            SPF_Interval = int(inputs[i+1])
            i += 2
    # Updating the variables with respect to the inputs taken

    Ipointer = open(Input_file, 'r')
    P = Ipointer.readline().split()
    Num_of_rout = int(P[0])
    Num_of_links = int(P[1])
    # Opening the file and updating the respective variables

    adj_matrix = {}
    # initializing  the adjacency dictionary

    for i in range(Num_of_rout):
        if i not in adj_matrix:
            adj_matrix[i] = {}
            for j in range(Num_of_rout):
                adj_matrix[i][j] = (-1, -1)
        # If that node is not present in the dictionary then we allot it as an dictionary and initialize all its values as (-1,-1)

    for line in Ipointer:
        P = line.strip().split()
        i = int(P[0])
        j = int(P[1])
        Min_Cij = int(P[2])
        Max_Cij = int(P[3])
        # Reading every line and updating the Min and Max cost values

        if i not in adj_matrix:
            adj_matrix[i] = {}

        adj_matrix[i][j] = (Min_Cij, Max_Cij)

        if j not in adj_matrix:
            adj_matrix[j] = {}

        adj_matrix[j][i] = (Min_Cij, Max_Cij)
        # Similarly updating the min and max cost values in the adjacencny Matrix

    print(f"The adjacency Matrix will be as : \n")
    for i in range(len(adj_matrix)):
        print(adj_matrix[i])
    print("\n")
    # Printing the adjacency Matrix

    Hello_threads = []
    recv_threads = []
    LSA_threads = []
    temp = 1
    # Initialising the thread arrays

    for i in range(Num_of_rout):

        Udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        Udp_socket.bind(('127.0.0.1', 10000+i))
        # Binding the sockets

        Matrix = [[-1] * Num_of_rout for _ in range(Num_of_rout)]
        # Initialising a n x n matrix

        T1 = threading.Thread(target=send, args=(i, adj_matrix[i], Udp_socket, Hello_Interval, LSA_Interval, Matrix, 1))
        Hello_threads.append(T1)

        T2 = threading.Thread(target=Receive, args=(i, adj_matrix[i], Udp_socket, Matrix))
        recv_threads.append(T2)

        T3 = threading.Thread(target=send, args=(i, adj_matrix[i], Udp_socket, Hello_Interval, LSA_Interval, Matrix, 2))
        LSA_threads.append(T3)
        # Calling the respective threads for each function and append them to the respective arrays

        if i == Node_identifier: 
            Outfilename = Output_file + '-' + str(i) + '.txt'
            Opointer = open(Outfilename, 'w')
            # if i is Node identifier update the output file and get the output pointer and call the thread for the spf function
            temp = threading.Thread(target=spf, args=(i, Matrix, Opointer, SPF_Interval))

    # Start receiving threads
    for i, t in enumerate(recv_threads):
        print(f"Starting Thread -- Receive --- Node {i}")
        t.start()

    # Start sending Hello Threads
    for i, t in enumerate(Hello_threads):
        time.sleep(1)
        print(f"Starting Thread -- Send HELLO --- Node {i}")
        t.start()

    # Waiting for HELLO Packets to be exchanged
    time.sleep(4)

    # Start sending LSA Packets
    for i, t in enumerate(LSA_threads):
        print(f"Starting Thread -- Send LSA --- Node {i}")
        t.start()
        time.sleep(1)

    # Starting the spf function
    temp.start()
    temp.join()

    print("Outputs are written into the outfile")
    print("Closing the output file")
    # Closing the output file once outputs are written into it and making the termination constant as True
    const = True
