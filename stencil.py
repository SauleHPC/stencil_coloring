import networkx as nx
from mip import LinExpr, Model, xsum, minimize, BINARY, INTEGER, OptimizationStatus
import sys
import time
import stencillib as st


def max_degree(G):
    return max(G.degree[i] for i in G.nodes)



def pre_normalize(G, targetColor, m, x, maxcolor):
        #try to normalize solution by fixing a few vertices colors
    if G.name.startswith("2d_stencil_5pt"): #in a 5pt_box, (0,0), (1,0) is an edge so they have to be numbered differently.
        m += x[st.stencil_node_name(0,0)][0] == 1
        m += x[st.stencil_node_name(1,0)][1] == 1
    
    if G.name.startswith("2d_stencil_9pt_box"): #in a 9pt_box, (0,0), (1,0), (0,1), (1,1) is a K4 so they have to be numbered differently.
        m += x[st.stencil_node_name(0,0)][0] == 1
        m += x[st.stencil_node_name(1,0)][1] == 1
        m += x[st.stencil_node_name(0,1)][2] == 1
        m += x[st.stencil_node_name(1,1)][3] == 1
    
    if G.name.startswith("2d_stencil_9pt_star"): #in a 9pt_star, (0,0), (1,0), (2,0) is a triangle so they have to be numbered differently.
        m += x[st.stencil_node_name(0,0)][0] == 1
        m += x[st.stencil_node_name(1,0)][1] == 1
        m += x[st.stencil_node_name(2,0)][2] == 1
        # cutting basic symmetries; basically, pre-normalizing by preventing early vertices to have too high a color number
        for c in range(4, targetcolor):
            m += x[st.stencil_node_name(0,1)][c] == 0
        for c in range(5, targetcolor):
            m += x[st.stencil_node_name(1,1)][c] == 0
        for c in range(6, targetcolor):
            m += x[st.stencil_node_name(2,1)][c] == 0
        for c in range(7, targetcolor):
            m += x[st.stencil_node_name(0,2)][c] == 0
        for c in range(8, targetcolor):
            m += x[st.stencil_node_name(1,2)][c] == 0
        for c in range(9, targetcolor):
            m += x[st.stencil_node_name(2,2)][c] == 0



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




    #set objective function
    m.objective = minimize(maxcolor)
    
    pre_normalize(G, targetColor, m, x, maxcolor)
    return (m,x,maxcolor)



if len(sys.argv) < 4:
    print ("usage: python3 stencil.py <sizeX> <sizeY> <stenciltype> [xcyclic] [ycyclic]")
    print ("stenciltype can be 5pt 9pt_box 9pt_star")
    sys.exit(1)


sizex = int(sys.argv[1])
sizey = int(sys.argv[2])
if sys.argv[3] == "5pt":
    targetcolor=5
    G = st.graph_build_stencil_2d_5pt(sizex,sizey)
if sys.argv[3] == "9pt_box":
    targetcolor=9
    G = st.graph_build_stencil_2d_9pt_box(sizex,sizey)
if sys.argv[3] == "9pt_star":
    targetcolor=12
    G = st.graph_build_stencil_2d_9pt_star(sizex,sizey)

xcyclic = -1
if len(sys.argv)>4:
    xcyclic=int(sys.argv[4])

ycyclic = -1
if len(sys.argv)>5:
    ycyclic=int(sys.argv[5])
    
#print(list(G.nodes))
#print(list(G.edges))
problemname="starcoloring_{}_{}{}{}".format(G.name, targetcolor, ("_xc{}".format(xcyclic) if xcyclic>0 else ""), ("_yc{}".format(ycyclic) if ycyclic>0 else ""))
print(problemname)
    
m,x,maxcolor = build_starcoloring_problem(G, targetcolor)

# adding basic lower bounds based on solutions we already know
if sys.argv[3] == "9pt_star":
    if sizex > 7 and sizey > 7:
        m += maxcolor >= 7 #7x7 needs 8 colors
    

#adding cyclic constraints
if xcyclic > 0:
    for i in range(0,sizex):
        for j in range(0,sizey):
            for c in range(0, targetcolor):
                if i-xcyclic>=0:
                    m += x[st.stencil_node_name(i,j)][c] - x[st.stencil_node_name(i-xcyclic,j)][c] == 0

if ycyclic > 0:
    for i in range(0,sizex):
        for j in range(0,sizey):
            for c in range(0, targetcolor):
                if j-ycyclic>=0:
                    m += x[st.stencil_node_name(i,j)][c] - x[st.stencil_node_name(i,j-ycyclic)][c] == 0



m.write("{}.lp".format(problemname))
#print (x)

#use color attribute from graph to force color info
def seed (G, sizex, sizey, filename, model, x):
    st.load_color_info(G, sizex, sizey, filename)
    print("color loaded")
    for v in G.nodes:
        if "color" in G.nodes[v]:
            model += x[v][G.nodes[v]["color"]] == 1
            

#seed (G, 6, 6, "starcoloring_2d_stencil_9pt_box_6_6_9.sol", m, x)

#sys.exit( -1)
            
start_time = time.perf_counter()

solved = m.optimize()

# Record end time
end_time = time.perf_counter()

# Calculate elapsed time
solving_time = end_time - start_time


with open("{}.sol".format(problemname), 'w') as outfile:
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
        st.print_stencil_color (sizex, sizey, G, targetcolor, x)
        st.print_stencil_color (sizex, sizey, G, targetcolor, x, fileout=outfile)
    else: # should really test all possible values of solved
        print ("UNFEASIBLE")
        print ("UNFEASIBLE", file=outfile)    






