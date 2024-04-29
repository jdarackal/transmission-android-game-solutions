from time import strftime

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
    def __init__(self, start:str, end:str) -> None:
        self.start = start
        self.end = end
        self.name = f'{start} -> {end}'
        self.pair = {start, end}

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
    
def log(log_content:str):
    '''Logs content to the log file and adds a newline'''
    with open(LOG_FILE_NAME, 'a') as log_file:
        log_file.write(log_content + '\n')

nodes = {
    'a': Swapper(3, 3, 0, 0, 2),
    'b': Transceiver(4, 3, 1, 2, 0, WHITE),
    'c': Swapper(2, 2, 0, 0.5, -2),
    'd': Transceiver(2, 1, 1, 8, 2, ORANGE),
    'e': Transceiver(2, 1, 1, 10, 0, ORANGE),
    'f': Transceiver(3, 3, 0, 8.5, -2, ORANGE)
}

log(f'''Nodes:
\tSlots\tEmpty\tBlocks\tIn color  Out color
a\t{nodes['a'].slots}\t{nodes['a'].empty}\t{nodes['a'].blocks}\t{nodes['a'].in_color}\t  {nodes['a'].out_color}
b\t{nodes['b'].slots}\t{nodes['b'].empty}\t{nodes['b'].blocks}\t{nodes['b'].in_color}\t  {nodes['b'].out_color}
c\t{nodes['c'].slots}\t{nodes['c'].empty}\t{nodes['c'].blocks}\t{nodes['c'].in_color}\t  {nodes['c'].out_color}
d\t{nodes['d'].slots}\t{nodes['d'].empty}\t{nodes['d'].blocks}\t{nodes['d'].in_color}\t  {nodes['d'].out_color}
e\t{nodes['e'].slots}\t{nodes['e'].empty}\t{nodes['e'].blocks}\t{nodes['e'].in_color}\t  {nodes['e'].out_color}
f\t{nodes['f'].slots}\t{nodes['f'].empty}\t{nodes['f'].blocks}\t{nodes['f'].in_color}\t  {nodes['f'].out_color}
''')

path_string = 'b -> c, c -> f, e -> d, d -> f, f -> e, f -> a, a -> b, c -> a'
connection_nodes_list = [connection_string.split(' -> ') for connection_string in path_string.split(', ')]
connections = [Connection(connection_nodes[0], connection_nodes[1]) for connection_nodes in connection_nodes_list]

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

    log(f'''------------------------------------------------------------------------------------------------
        
Connections: {', '.join([connection.name for connection in completed_connections])}

Nodes:
\tSlots\tEmpty\tBlocks\tIn color  Out color
a\t{nodes['a'].slots}\t{nodes['a'].empty}\t{nodes['a'].blocks}\t{nodes['a'].in_color}\t  {nodes['a'].out_color}
b\t{nodes['b'].slots}\t{nodes['b'].empty}\t{nodes['b'].blocks}\t{nodes['b'].in_color}\t  {nodes['b'].out_color}
c\t{nodes['c'].slots}\t{nodes['c'].empty}\t{nodes['c'].blocks}\t{nodes['c'].in_color}\t  {nodes['c'].out_color}
d\t{nodes['d'].slots}\t{nodes['d'].empty}\t{nodes['d'].blocks}\t{nodes['d'].in_color}\t  {nodes['d'].out_color}
e\t{nodes['e'].slots}\t{nodes['e'].empty}\t{nodes['e'].blocks}\t{nodes['e'].in_color}\t  {nodes['e'].out_color}
f\t{nodes['f'].slots}\t{nodes['f'].empty}\t{nodes['f'].blocks}\t{nodes['f'].in_color}\t  {nodes['f'].out_color}
''')