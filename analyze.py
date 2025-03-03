import networkx as nx
import sys
import stencillib as st


def permutate_colors(G, mapping):
    for v in G.nodes:
        if G.nodes[v]["color"] in mapping :
           G.nodes[v]["color"] = mapping[G.nodes[v]["color"]]

           

if len(sys.argv) < 4:
    print ("usage: python3 stencil.py <sizeX> <sizeY> <stenciltype> <coloringoutput>")
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



st.load_color_info(G, sizex, sizey, sys.argv[4])
                

for x in range(0,sizex):
    for y in range(0,sizey):
        print (G.nodes[st.stencil_node_name(x,y)]["color"], end='')
    print()

print()

if len(sys.argv)>5:
    for i in range (5, len(sys.argv)):
        permutate_colors(G, eval(sys.argv[i]))
        st.print_stencil_color_from_attribute(sizex, sizey, G)
        print()
else:
    #normalize automatically
    currcolor=0
    for k in range(1, max(sizex, sizey)):
        for x in range (0, min(k,sizex)):
            for y in range (0, min(k,sizey)):
                if G.nodes[st.stencil_node_name(x,y)]["color"] >= currcolor:
                    permutate_colors(G, {currcolor: G.nodes[st.stencil_node_name(x,y)]["color"], G.nodes[st.stencil_node_name(x,y)]["color"]: currcolor})
                    currcolor = currcolor+1
                    st.print_stencil_color_from_attribute(sizex, sizey, G)
                    print()
                
        



