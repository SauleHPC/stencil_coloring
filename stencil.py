import networkx as nx
from mip import LinExpr, Model, xsum, minimize, BINARY, INTEGER, OptimizationStatus


def stencil_node_name(i, j):
    return "{}_{}".format(i,j)

def max_degree(G):
    return max(G.degree[i] for i in G.nodes)

def graph_build_stencil_2d_5pt(stencilX, stencilY):
    G = nx.Graph()
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


def build_starcoloring_problem(G, targetColor):
    m = Model("Coloring")
    x = {}
    #color variables
    for i in G.nodes:
        x[i] = {}
        for c in range(0,targetColor):
            x[i][c] = m.add_var(var_type=BINARY, name="x_{}_{}".format(i,c))
    # each vertex has a color
    for i in G.nodes:
        m += xsum([x[i][c] for c in x[i]]) == 1
    # maxcolor variable
    maxcolor = m.add_var(var_type=INTEGER, name="maxcolor")

    # set maxcolor value
    for i in G.nodes:
        for c in range (0, targetColor):
            m += maxcolor - c*x[i][c]  >= 0

    #each chain of 3 has three colors
    for i in G.nodes:
        for j in G.neighbors(i):
            for k in G.neighbors(j):
                if i != j and i != k:
                    #print (i, j, k)
                    for c in range (0,targetColor):
                        m += x[i][c] + x[j][c] + x[k][c] <= 1 #only 1 in 3
                    

    #set objective function
    m.objective = minimize(maxcolor)
    return (m,x,maxcolor)

sizex = 3
sizey = 3
targetcolor=5
G = graph_build_stencil_2d_5pt(sizex,sizey)
print(list(G.nodes))
print(list(G.edges))
    
m,x,maxcolor = build_starcoloring_problem(G, targetcolor)
m.write("starcoloring_{}_{}_{}.lp".format(sizex, sizey, targetcolor))
print (x)


solved = m.optimize()

if solved == OptimizationStatus.OPTIMAL:
    for i in G.nodes:
        for c in range (0, targetcolor):
            if x[i][c].x > 0.99:
                color = c
        print ("vertex {} has color {}".format(i, color))
    print ("number of color: {}".format(maxcolor.x+1))
else: # should really test all possible values of solved
    print ("UNFEASIBLE")    
