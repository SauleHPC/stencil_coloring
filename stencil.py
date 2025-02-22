import networkx as nx
from mip import LinExpr, Model, xsum, minimize, BINARY, INTEGER, OptimizationStatus
import sys
import time

def stencil_node_name(i, j):
    return "{}_{}".format(i,j)

def max_degree(G):
    return max(G.degree[i] for i in G.nodes)

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



def build_starcoloring_problem(G, targetColor):
    m = Model("Coloring")
    x = {}
    #color variables
    for i in G.nodes:
        x[i] = {}
        for c in range(0,targetColor):
            x[i][c] = m.add_var(var_type=BINARY, name="color_{}_{}".format(i,c))
    # each vertex has a color
    for i in G.nodes:
        m += xsum([x[i][c] for c in x[i]]) == 1
    # maxcolor variable
    maxcolor = m.add_var(var_type=INTEGER, name="maxcolor")

    # set maxcolor value
    for i in G.nodes:
        for c in range (0, targetColor):
            m += maxcolor - c*x[i][c]  >= 0

    #each chain of 3 edges has at least three colors
    for i in G.nodes:
        for j in G.neighbors(i):
            if j != i:
                for c in range (0,targetColor):
                    m += x[i][c] + x[j][c] <= 1 #distance 1 coloring must hold
                for k in G.neighbors(j):
                    if k != i and k != j:
                        for l in G.neighbors(k):
                            if l != i and l != j and l != k:
                                #print (i, j, k)
                                for c in range (0,targetColor):
                                    for c2 in range (c+1,targetColor):
                                        m += x[i][c] + x[j][c] + x[k][c] + x[l][c] +  x[i][c2] + x[j][c2] + x[k][c2] + x[l][c2] <= 3 #at most 3 out of 2 colors in 4



    #try to normalize solution by having the first two vertices have particular colors
    m += x[stencil_node_name(0,0)][0] == 1
    m += x[stencil_node_name(1,0)][1] == 1

    #set objective function
    m.objective = minimize(maxcolor)
    return (m,x,maxcolor)


def print_stencil_color(sizex, sizey, G, color_variables, fileout=sys.stdout):
    for i in range(0,sizex):
        for j in range(0,sizey):
            vertexname = stencil_node_name(i,j)
            color=-1
            for c in range (0, targetcolor):
                if color_variables[vertexname][c].x > 0.99:
                    color = c
            print(color, end='', file=fileout)
        print("", file=fileout)


if len(sys.argv) < 4:
    print ("usage: python3 stencil.py <sizeX> <sizeY> <stenciltype>")
    print ("stenciltype can be 5pt 9pt_box 9pt_star")
    sys.exit(1)


sizex = int(sys.argv[1])
sizey = int(sys.argv[2])
if sys.argv[3] == "5pt":
    targetcolor=5
    G = graph_build_stencil_2d_5pt(sizex,sizey)
if sys.argv[3] == "9pt_box":
    targetcolor=9
    G = graph_build_stencil_2d_9pt_box(sizex,sizey)
if sys.argv[3] == "9pt_star":
    targetcolor=12
    G = graph_build_stencil_2d_9pt_star(sizex,sizey)


print(list(G.nodes))
print(list(G.edges))
    
m,x,maxcolor = build_starcoloring_problem(G, targetcolor)
m.write("starcoloring_{}_{}.lp".format(G.name, targetcolor))
#print (x)


start_time = time.perf_counter()

solved = m.optimize()

# Record end time
end_time = time.perf_counter()

# Calculate elapsed time
solving_time = end_time - start_time


with open("starcoloring_{}_{}.sol".format(G.name, targetcolor), 'w') as outfile:
    # Print the solving time
    print(f"Solving time: {solving_time:.4f} seconds")
    print(f"Solving time: {solving_time:.4f} seconds", file=outfile)

    if solved == OptimizationStatus.OPTIMAL:
        print (G.name)
        print (G.name, file=outfile)
        for i in G.nodes:
            for c in range (0, targetcolor):
                if x[i][c].x > 0.99:
                    color = c
            print ("vertex {} has color {}".format(i, color))
        print ("number of color: {}".format(maxcolor.x+1))
        print ("number of color: {}".format(maxcolor.x+1), file=outfile)
        print_stencil_color (sizex, sizey, G, x)
        print_stencil_color (sizex, sizey, G, x, fileout=outfile)
    else: # should really test all possible values of solved
        print ("UNFEASIBLE")
        print ("UNFEASIBLE", file=outfile)    






