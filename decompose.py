import sys

with open(sys.argv[1]) as myfile:
    colors = myfile.readlines()[3:]
    print (colors)
    for c1 in range(0,8):
        for c2 in range(c1+1, 8):
            inset = {c1, c2}
            for line in colors:
                for char in line:
                    if char != '\n':
                        if int(char) in inset:
                            print (char, end='')
                        else:
                            print ('.', end='')
                print()
            print()
    
