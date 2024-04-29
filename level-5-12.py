import numpy as np
from time import strftime, perf_counter

WHITE = 'W'
ORANGE = 'O'
LOG_FILE_NAME = __file__ + f'-logs\{strftime("%Y-%m-%dT%H-%M-%S")}.txt'

class Node:
    def __init__(self, slots:int, empty:int, blocks:int, x:float, y:float) -> None:
        self.slots = slots
        self.empty = empty
        self.blocks = blocks
        self.x = x
        self.y = y
        self.in_color = None
        self.out_color = None

class Transceiver(Node):
    def __init__(self, slots: int, empty: int, blocks: int, x: float, y: float, color:str) -> None:
        super().__init__(slots, empty, blocks, x, y)
        self.in_color = color
        self.out_color = color

class Swapper(Node):
    def __init__(self, slots: int, empty: int, blocks: int, x: float, y: float) -> None:
        super().__init__(slots, empty, blocks, x, y)

class Connection:
    def __init__(self, start:str, end:str, nodes:dict[str,Node]) -> None:
        self.start = start
        self.end = end
        self.name = f'{start} -> {end}'
        self.pair = {start, end}

        start_node, end_node = nodes[start], nodes[end]

        self.slope = (end_node.y - start_node.y) / (end_node.x - start_node.x)
        self.intercept = start_node.y - self.slope * start_node.x

    def transfer(self, nodes:dict[str,Node]) -> None:
        start_node, end_node = nodes[self.start], nodes[self.end]

        if start_node.blocks > 0 and end_node.empty > 0:
            num_blocks = start_node.blocks if start_node.blocks <= end_node.empty else end_node.empty
            start_node.blocks -= num_blocks
            end_node.blocks += num_blocks
            end_node.empty -= num_blocks

            if end_node.in_color == None:
                end_node.in_color = start_node.out_color
                end_node.out_color = WHITE if start_node.out_color == ORANGE else ORANGE

            return 1
        
        return 0

    def intersects(self, other_conn:'Connection', nodes:dict[str,Node]) -> bool:
        if self.slope == other_conn.slope:
            return False
        
        a = np.array([[-self.slope, 1], [-other_conn.slope, 1]])
        b = np.array([self.intercept, other_conn.intercept])
        x, _ = np.linalg.solve(a, b)

        self_start_node, self_end_node, other_start_node, other_end_node = nodes[self.start], nodes[self.end], nodes[other_conn.start], nodes[other_conn.end]

        if ((self_start_node.x < x < self_end_node.x or self_start_node.x > x > self_end_node.x)
            and
            (other_start_node.x < x < other_end_node.x or other_start_node.x > x > other_end_node.x)
        ):
            return True
        else:
            return False

def transfer_loop(connections:list[Connection], nodes:dict[str,Node]):
    completed_connections = []

    for curr_connection in connections:
        curr_connection.transfer(nodes)
        completed_connections.append(curr_connection)
        connection_end = str(curr_connection.end)

        transfers_possible = True
        while connection_end in [connection.start for connection in completed_connections] and transfers_possible:
            for next_connection in [connection for connection in completed_connections if connection.start == connection_end]:
                if next_connection.transfer(nodes):
                    connection_end = str(next_connection.end)
                    transfers_possible = True
                    break
                else:
                    transfers_possible = False

def empty_left(nodes:dict[str,Node]):
    empty = 0

    for node in nodes:
        empty += nodes[node].empty

    return empty

def log(log_content:str):
    '''Logs content to the log file and adds a newline'''
    with open(LOG_FILE_NAME, 'a') as log_file:
        log_file.write(log_content + '\n')

if __name__ == '__main__':
    def create_nodes(connections:list[Connection]) -> dict[str,Node]:
        nodes = {
            'a': Swapper(3, 3, 0, 0, 2),
            'b': Transceiver(4, 3, 1, 2, 0, WHITE),
            'c': Swapper(2, 2, 0, 0.5, -2),
            'd': Transceiver(2, 1, 1, 8, 2, ORANGE),
            'e': Transceiver(2, 1, 1, 10, 0, ORANGE),
            'f': Transceiver(3, 3, 0, 8.5, -2, ORANGE)
        }

        if len(connections) > 0:
            transfer_loop(connections, nodes)

        return nodes
    
    blocked_connections = [
    ]

    # connections that are blocked if the starting node has an out_color of WHITE
    conditional_blocked_connections = [
    ]

    def connection_blocked(start:str, end:str, nodes:dict[str,Node]):
        all_blocked_connections = blocked_connections + conditional_blocked_connections if nodes[start].out_color == WHITE else blocked_connections

        return True if {start, end} in all_blocked_connections else False
    
    def game_loop():
        game_states = [[]]

        while True:
            next_game_states = []
            num_new_states = 0
            for state in game_states:
                for start_node_name in 'abcdef':
                    for end_node_name in 'abcdef':
                        if start_node_name == end_node_name:
                            continue

                        try:
                            nodes = create_nodes(state)

                            if connection_blocked(start_node_name, end_node_name, nodes):
                                raise Exception(f'Connection {start_node_name} -> {end_node_name} blocked by barrier.')

                            start_node, end_node = nodes[start_node_name], nodes[end_node_name]

                            if start_node.out_color != end_node.in_color and end_node.in_color != None:
                                raise Exception('Colors do not match.')
                            elif start_node.blocks == 0:
                                raise Exception('No blocks on start node.')
                            elif end_node.empty == 0:
                                raise Exception('No slots remaining on end node.')
                            
                            new_connection = Connection(start_node_name, end_node_name, nodes)

                            for connection in state:
                                if new_connection.pair == connection.pair:
                                    raise Exception(f'{start_node_name} and {end_node_name} already connected.')
                                elif new_connection.intersects(connection, nodes):
                                    raise Exception(f'{new_connection.name} intersects with {connection.name}.')
                                
                            next_state = state + [new_connection]
                            next_game_states.append(next_state)
                            num_new_states += 1

                            transfer_loop(next_state, nodes)

                            if empty_left(nodes) == 0:
                                log(', '.join([connection.name for connection in next_state]) + f' | Connections: {len(next_state)}')

                        except Exception as e:
                            continue

            if num_new_states == 0:
                return

            game_states = next_game_states


    tic = perf_counter()
    game_loop()
    toc = perf_counter()
    print(f'Time taken: {toc - tic}')