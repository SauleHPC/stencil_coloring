import networkx as nx
import sys

def stencil_node_name(i, j):
    return "{}_{}".format(i,j)

def graph_build_stencil_2d_5pt(stencilX, stencilY):
    G = nx.Graph(name="2d_stencil_5pt_{}_{}".format(stencilX, stencilY))
    for i in range (0,stencilX):
        for j in range (0,stencilY):
            G.add_node(stencil_node_name(i,j))
    for i in range (0,stencilX):
        for j in range (0,stencilY):
            for diff in [(-1,0), (1,0), (0, -1), (0,1)]:
                tox = i+diff[0]
                toy = j+diff[1]
                if tox>=0 and toy>=0 and tox <stencilX and toy<stencilY:
                    G.add_edge(stencil_node_name(i,j),stencil_node_name(tox,toy))
    return G


def graph_build_stencil_2d_9pt_box(stencilX, stencilY):
    G = nx.Graph(name="2d_stencil_9pt_box_{}_{}".format(stencilX, stencilY))
    for i in range (0,stencilX):
        for j in range (0,stencilY):
            G.add_node(stencil_node_name(i,j))
    for i in range (0,stencilX):
        for j in range (0,stencilY):
            for diff in [(-1,-1), (-1,0),(-1,1), (0, -1), (0,1), (1,-1), (1,0), (1,1)]:
                tox = i+diff[0]
                toy = j+diff[1]
                if tox>=0 and toy>=0 and tox <stencilX and toy<stencilY:
                    G.add_edge(stencil_node_name(i,j),stencil_node_name(tox,toy))
    return G


def graph_build_stencil_2d_9pt_star(stencilX, stencilY):
    G = nx.Graph(name="2d_stencil_9pt_star_{}_{}".format(stencilX, stencilY))
    for i in range (0,stencilX):
        for j in range (0,stencilY):
            G.add_node(stencil_node_name(i,j))
    for i in range (0,stencilX):
        for j in range (0,stencilY):
            for diff in [(-2,0), (-1,0), (1,0), (2,0), (0, -1), (0,-2), (0,1), (0,2)]:
                tox = i+diff[0]
                toy = j+diff[1]
                if tox>=0 and toy>=0 and tox <stencilX and toy<stencilY:
                    G.add_edge(stencil_node_name(i,j),stencil_node_name(tox,toy))
    return G



def print_stencil_color(sizex, sizey, G, targetcolor, color_variables, fileout=sys.stdout):
    for i in range(0,sizex):
        for j in range(0,sizey):
            vertexname = stencil_node_name(i,j)
            color=-1
            for c in range (0, targetcolor):
                if color_variables[vertexname][c].x > 0.99:
                    color = c
            print(hex(color)[2:], end='', file=fileout)
        print("", file=fileout)


def print_stencil_color_from_attribute(sizex, sizey, G, fileout=sys.stdout):
    for i in range(0,sizex):
        for j in range(0,sizey):
            color = G.nodes[stencil_node_name(i,j)]["color"]
            print(hex(color)[2:], end='', file=fileout)
        print("", file=fileout)
        

def load_color_info(G, sizex, sizey, filename):
    #load color information
    with open(filename, 'r') as f:
        for x in range(0,sizex):
            l = "continue:"
            while l.count("_")>0 or l.count(":")>0: #skip lines that aren't coloring
                l = f.readline()

            for y in range(0,sizey):
                color = int(l[y], 16)
                nx.set_node_attributes(G, {stencil_node_name(x,y): {"color":color}})
