from collections import deque
from time import sleep
from copy import deepcopy

ids = 0
counter = 0

class TwoWayMap:
    def __init__(self):
        self.a_b = {}
        self.b_a = {}
    
    def update(self,a,b,type="n"):
        if type == "r":
            #then "a" is actually "b"
            self.b_a[a] = b
            self.a_b[b] = a
        else:
            self.a_b[a] = a
            self.a_b[b] = b

    def check(self,grab,type="n"):
        if type =="r":
            return True if grab in self.b_a else False
        else:
            return True if grab in self.a_b else False
        
    def grab(self, grab,type="n"):
        if type == "r":
            return self.b_a[grab]
        else:
            return self.a_b[grab]

class Node:
    def __init__(self):
        global counter
        self.transitions = {}
        self.id = counter
        self.accept = False
        self.NFAified = False #supposed to be DFAified and DFAify but i am extremely lazy
        counter += 1

    def transition_add(self, symbol, node):
        if not self.NFAified:
            if symbol not in self.transitions:
                self.transitions[symbol] = set()
            self.transitions[symbol].add(node)

    def NFAify(self):
        if self.NFAified:
            return
        else:
            self.NFAified = True
            newtransitions = {}
            for symbol in self.transitions:
                if self.transitions[symbol]:
                    newtransitions[symbol] = self.transitions[symbol].pop()
                else:
                    pass #ERROR
            self.transitions = newtransitions

class NFANode:
    def __init__(self):
        global counter
        self.transitions = {}
        self.id = counter
        self.accept = False
        counter += 1

    def transition_add(self, symbol, node):
        self.transitions[symbol] = node

class Tree:
    def __init__(self):
        self.branches = set()
        self.root = None
        self.priority = {"ROOT": -1, "LEFTP": 0, "RIGHTP": 1, "KLEENE": 2, "PLUS": 3, "OR": 4, "CONCAT": 5, "SYMBOL": 6}
        self.nodes = set()
        self.garbagehogger = set()
        self.alphabet = set()

    def constructTree(self, tokenized):
        rootNode = Branch("", "ROOT")
        self.root = rootNode
        self.root.parent = self.root
        self.nodes.add(rootNode)
        self.AST(tokenized, 0, rootNode)
        return (self.root, self.nodes)
        
    def AST(self, tokenized, index, currentBranch):
        firstBranch = Branch(currentBranch, "CONCAT")
        currentBranch.addChild(firstBranch)
        currentBranch = firstBranch
        self.nodes.add(firstBranch)
        while index < len(tokenized):
            #print(tokenized[index])
            token = tokenized[index][0]
            if token == "SYMBOL":
                if currentBranch.ttype != "CONCAT":
                    #make a new node, it is currentBranch's child
                    conBranch = Branch(currentBranch, "CONCAT")
                    currentBranch.addChild(conBranch)
                    self.nodes.add(conBranch)
                    currentBranch = conBranch
                symbranch = Branch(currentBranch, "SYMBOL")
                self.nodes.add(symbranch)
                symbranch.data = tokenized[index][1]
                currentBranch.addChild(symbranch)
                index += 1
            else:
                priority = self.priority[token]
                currentBranchPriority = self.priority[currentBranch.ttype]
                if token == "LEFTP":
                    leftbranch = Branch(currentBranch, token)
                    currentBranch.addChild(leftbranch)
                    concatbranch = Branch(leftbranch, "CONCAT")
                    leftbranch.addChild(concatbranch)
                    currentBranch = concatbranch
                    self.nodes.add(leftbranch)
                    self.nodes.add(concatbranch)
                elif token == "RIGHTP":
                    #go up the tree until you find "LEFTP" branch
                    while currentBranch.ttype != "LEFTP":
                        #go up the tree
                        currentBranch = currentBranch.parent
                    currentBranch = currentBranch.parent
                elif token == "PLUS" or token == "KLEENE":
                    #special fucking handling!!!
                    #from whatever the current branch is, look at the last child
                    lastchild = currentBranch.children[-1]
                    #whatever lastchild is, make the new branch its parent
                    kparent = Branch(currentBranch, token)
                    currentBranch.addChild(kparent)
                    currentBranch.removeChild(lastchild, kparent)
                    self.nodes.add(kparent)
                elif priority >= currentBranchPriority:
                    #make the worse pirority branch the child of the current branch
                    lpBranch = Branch(currentBranch, token)
                    currentBranch.addChild(lpBranch)
                    currentBranch = lpBranch
                    self.nodes.add(lpBranch)
                else: #priority is higher than current branch
                    #make new branch the parent of the current 
                    global counter
                    b = currentBranch
                    oldparent = currentBranch.parent
                    hpBranch = Branch(oldparent, token)
                    oldparent.removeChild(b, hpBranch)
                    self.nodes.add(hpBranch)
                    currentBranch = hpBranch
                    oldparent.addChild(hpBranch)
                    counter += 1                    
                index += 1
        return
        
    def makeNFA(self, root):
        #print(f"resolving {root.id} which is of type {root.ttype} with parent {root.parent} and children {[child.id for child in root.children]}")
        #reach the main root, return the child's NFA
        #check if each child is either resolved or a SYMBOL
        unresolved_children = []
        for child in root.children:
            if child.NFA is None:
                unresolved_children.append(child)
        #recursive call to resolve unresolved nodes
        for child in unresolved_children:
            self.makeNFA(child)
            #if root.ttype=="ROOT":
                #print(f"my child's nfa start node is {child.get_startnode().id} and their endnode is {child.get_endnode().id}")

        #create the NFA based on the root node
        if root.ttype == "SYMBOL":
            startnode = Node()
            endnode = Node()
            set_of_nodes = set([startnode, endnode])
            startnode.transition_add(root.data, endnode)
        elif root.ttype == "CONCAT":
            #if we only have one elem, we're done
            if len(root.children) == 1:
                startnode = root.children[0].get_startnode()
                endnode = root.children[0].get_endnode()
                set_of_nodes = root.children[0].get_nfa_nodes()
            else:
            #connect the first child's startnode to startnode and the last child's endnode to endnode with epsilon transitions
                startnode = Node()
                endnode = Node()
                set_of_nodes = set([startnode, endnode])
                first_child = root.children[0]
                last_child = root.children[len(root.children) - 1]
                startnode.transition_add("epsilon", first_child.get_startnode())
                last_child.get_endnode().transition_add("epsilon", endnode)
                set_of_nodes = set_of_nodes | last_child.get_nfa_nodes()
                #go through the children (except the last child) and connect the endnode with the next child's startnode
                for i, child in enumerate(root.children):
                    if i == len(root.children) - 1:
                        continue
                    else:
                        nextchild = root.children[i+1]
                        child.get_endnode().transition_add("epsilon", nextchild.get_startnode())
                        set_of_nodes = set_of_nodes | child.get_nfa_nodes()
        elif root.ttype == "OR":
            startnode = Node()
            endnode = Node()
            set_of_nodes = set([startnode, endnode])
            #connect all children's startnode to the startnode with an epsilon transition
            #connect all chldren's endnodes to the endnode with an epsilon transition
            #don't forget to add all children's NFAs to set_of_nodes!
            for child in root.children:
                startnode.transition_add("epsilon", child.get_startnode())
                child.get_endnode().transition_add("epsilon", endnode)
                set_of_nodes = set_of_nodes | child.get_nfa_nodes()
        elif root.ttype == "PLUS":
            startnode = Node()
            endnode = Node()
            set_of_nodes = set([startnode, endnode])
            child = root.children[0]
            #connect startnode to child's startnode with an epsilon transition
            startnode.transition_add("epsilon", child.get_startnode())
            #connect child's endnode to endnode with an epsilon transition
            child.get_endnode().transition_add("epsilon", endnode)
            #connect child's endnode to the startnode with an epsilon transition
            child.get_endnode().transition_add("epsilon", startnode)
            #don't forget the set, etc etc
            set_of_nodes = set_of_nodes | child.get_nfa_nodes()
        elif root.ttype == "KLEENE":
            startnode = Node()
            endnode = Node()
            set_of_nodes = set([startnode, endnode])
            child = root.children[0]
            #connect startnode to child's startnode with an epsilon transition
            startnode.transition_add("epsilon", child.get_startnode())
            #connect child's endnode to endnode with an epsilon transition
            child.get_endnode().transition_add("epsilon", endnode)
            #connect child's endnode to the startnode with an epsilon transition
            child.get_endnode().transition_add("epsilon", startnode)
            #don't forget the set, etc etc
            set_of_nodes = set_of_nodes | child.get_nfa_nodes()
            #what makes kleene different than a plus is that you can just go directly from the startnode to the endnode
            startnode.transition_add("epsilon",endnode)
        elif root.ttype == "LEFTP" or root.ttype == "ROOT":
            #the startnode and endnode is the exact same as the child's startnodes and endnodes
            child = root.children[0]
            startnode = child.get_startnode()
            endnode = child.get_endnode()
            set_of_nodes = child.get_nfa_nodes()
        else:
            #do nothing
            print("the rizzler")
        
        root.NFA = [startnode, endnode, set_of_nodes]
        return root.NFA
    
    def epsilon_reachable_nodes(self, node):
        toret = set()
        explored = set()
        queue = deque()
        queue.append(node)
        while queue:
            exploring = queue.popleft()
            if "epsilon" in exploring.transitions:
                set_of_reachable_nodes = exploring.transitions['epsilon']
                for a_node in set_of_reachable_nodes:
                    toret.add(a_node)
                    if a_node not in explored:
                        explored.add(a_node)
                        queue.append(a_node)

        torm = []
        for a_node in toret:
            if a_node.transitions == 1 and "epsilon" in a_node.transitions:
                torm.append(a_node)
        for a_node in torm:
            toret.remove(a_node)
        return toret
    
    def reachable_nodes(self, node):
        toret = set()
        explored = set()
        queue = deque()
        queue.append(node)
        while queue:
            exploring = queue.popleft()
            set_of_reachable_nodes = set()
            for symbol in exploring.transitions:
                set_of_reachable_nodes = set_of_reachable_nodes | exploring.transitions[symbol]
                for a_node in set_of_reachable_nodes:
                    toret.add(a_node)
                    if a_node not in explored:
                        explored.add(a_node)
                        queue.append(a_node)

        return toret

    def epsilon_elimination(self, startnode, endnode):

        e_to_r = {} #mapping of e-NFA nodes to NFA nodes
        reachable = deque() #stack/queue of reachable nodes
        processed = set()
        #get all stuff reachable from startnode 
        startnode
        reachable.append(startnode)
        while reachable:
            nodey = reachable.popleft()
            if nodey not in e_to_r:
                e_to_r[nodey] = Node()
            equivalent = e_to_r[nodey]
            processed.add(nodey)
            reachable_nodes = self.epsilon_reachable_nodes(nodey)
            '''print(f"I am node {equivalent.id}, the equivalent of {nodey.id}, and I can reach via epsilon transitions: ", end="")
            for n in reachable_nodes:
                print(f"{n.id},", end="")
            print()'''
            for a_node in reachable_nodes:
                if a_node not in processed:
                    reachable.append(a_node)
                for a_transition in a_node.transitions:
                    if a_transition == "epsilon":
                        continue
                    for tonode in a_node.transitions[a_transition]:
                        if tonode not in e_to_r:
                            e_to_r[tonode] = Node()
                        if tonode not in processed:
                            reachable.append(tonode)
                        eqtonode = e_to_r[tonode]
                        equivalent.transition_add(a_transition, eqtonode)
            if endnode in reachable_nodes:
                equivalent.accept = True

        '''for key in e_to_r:
            print(f"{key.id} : {e_to_r[key].id}")'''
        processed = set(e_to_r.values())

        self.garbagehogger = self.garbagehogger | processed
        return (e_to_r[startnode], processed)
        

    def combine_transitions(self, a, b):
        #add the transitions of node b into node a (changes node a)
        for symbol in b.transitions:
            if symbol in a.transitions:
                a.transitions[symbol] = a.transitions[symbol] | b.transitions[symbol]
            else:
                a.transitions[symbol] = b.transitions[symbol]

    def make_omegastate(self, tuple_of_states):
        newnode = Node()
        for a_state in tuple_of_states:
            self.combine_transitions(newnode, a_state)
            if a_state.accept:
                newnode.accept = True
        return newnode

    def eliminate_multiple_transitions(self, allnodes, startnode):
        #TODO: stare at this really carefully and see if there's anything fuckywucky here.
        nfanodes_omeganodes = {} #tuples to nodes
        q = deque()
        q.append(startnode)
        resolved = set()
        while q:
            '''print("queue: ", end="")
            for item in q:
                print(str(item.id) + " ", end="")
            print()'''
            node = q.popleft()
            resolved.add(node)
            #now look through the symbols
            for symbol in node.transitions:
                #print([a.id for a in node.transitions[symbol]])
                #print(symbol)
                #if there's only one transition to the symbol, add it to q if it's not resolved and leave it
                if not len(node.transitions[symbol]) > 1:
                    for neighbor in node.transitions[symbol]:
                        if neighbor not in resolved:
                            q.append(neighbor)
                            resolved.add(neighbor)
                else:
                    #check if it's an "omega state" we have already created.
                    t = list(node.transitions[symbol])
                    t.sort(key=lambda x: x.id)
                    t = tuple(t)
                    #if we didn't, create it add it to the TwoWayMap
                    if t not in nfanodes_omeganodes:
                        nfanodes_omeganodes[t] = self.make_omegastate(t)
                    omegastate = nfanodes_omeganodes[t]
                    #add this omegastate into the q if it's not resolved and make node of it on the two-way map
                    if omegastate not in resolved:
                        q.append(omegastate)
                        resolved.add(omegastate)
                    #change the transition function to only include this megastate
                    node.transitions[symbol] = set([omegastate])
        self.garbagehogger = self.garbagehogger | resolved
        return (startnode, resolved)
    
    def DFAify(self, startnode, set_of_nodes):
        dfa_start = startnode
        for a_node in set_of_nodes:
            a_node.NFAify()
        return dfa_start, set_of_nodes


class Branch:
    def __init__(self, parent, token_type):
        global ids
        self.parent = parent
        self.children = []
        self.ttype = token_type
        self.data = None
        self.NFA = None
        self.id = ids
        ids += 1

    def get_startnode(self):
        if self.NFA:
            return self.NFA[0]
        else:
            raise Exception("self.NFA is not defined")
        
    def set_startnode(self, startnode):
        if not self.NFA:
            self.NFA = [None, None, set()]
        self.NFA[0] = startnode

    def get_endnode(self):
        if self.NFA:
            return self.NFA[1]
        else:
            raise Exception("self.NFA is not defined")
        
    def set_endnode(self, endnode):
        if not self.NFA:
            self.NFA = [None, None, set()]
        self.NFA[1] = endnode
        
    def get_nfa_nodes(self):
        if self.NFA:
            return self.NFA[2]
        else:
            raise Exception("self.NFA is not defined")

    def isRoot(self):
        if self.parent == None and self.ttype == "ROOT":
            return True
        return False
    
    def addChild(self, child):
        self.children.append(child)
        child.parent = self

    def removeChild(self, child, newparent):
        self.children.remove(child)
        child.parent = newparent
        newparent.addChild(child)

    def childrenToString(self):
        if not self.children:
            string = "None"
            return string
        string = "["
        for child in self.children:
            string += str(child.id) + ", "
        string = string[:-2] + "]"
        return string

    def printBranch(self):
        print(f"Branch Type: {self.ttype}, Branch ID: {self.id}, Branch Parent: {self.parent.id}, Branch Children: {self.childrenToString()}")


special_characters = {"(":"LEFTP", ")" : "RIGHTP", "*":"KLEENE", "+": "PLUS", "|": "OR"}
rules = {"S" : "R", "RR": "R", "(R)":"R", "R*":"R", "R+":"R", "R|R" : "R", "RS":"R"}

def tokenize(string):
    global special_characters
    toret = []
    for char in string:
        if char in special_characters:
            toret.append((special_characters[char], char))
        else:
            toret.append(("SYMBOL",char))
    return toret

def parse(tokenized):
    global rules
    global special_characters
    transformed = ""
    toret = False
    for item in tokenized:
        token = item[0]
        if token == "SYMBOL":
            transformed += "S"
        elif token == "LEFTP":
            transformed += "("
        elif token == "RIGHTP":
            transformed += ")"
        elif token == "OR":
            transformed += "|"
        elif token == "KLEENE":
            transformed += "*"
        elif token == "PLUS":
            transformed += "+"
        else:
            return False
    
    j = len(transformed) - 1
    if j == -1:
        return False #empty string
        
    queue = deque()
    raw_text = [token[1] for token in tokenized]
    for char in transformed:
        queue.append(char)

    #print(transformed)
    transformed = ""
    looking = True
    once = True

    while queue or once:
        while(looking):
            looking = False
            #new code
            if len(transformed) > 2:
                #try to match the last character
                if transformed[-1] in rules:
                    transformed =  transformed[:-1] + rules[transformed[-1]]
                    looking = True
                #try to match the last two characters:
                elif transformed[-2:] in rules:
                    transformed = transformed[:-2] + rules[transformed[-2:]]
                    looking = True
                elif transformed[-3:] in rules:
                    transformed = transformed[:-3] + rules[transformed[-3:]]
                    looking = True
                else:
                    looking = False
            elif len(transformed) == 2:
                #still try to match the last token
                if transformed[-1] in rules:
                    transformed = transformed[:-1] + rules[transformed[-1]]
                    looking = True
                #try to match the entire token
                elif transformed in rules:
                    transformed = rules[transformed]
                    looking = True
                else:
                    looking = False
            else:
                if transformed in rules:
                    transformed = rules[transformed[-1:]]
                    looking = True
                else: 
                    looking = False

        if not once:
            break
        if not queue:
            once = False
            continue
        
        thischar = queue.popleft()
        transformed += thischar
        
        #print(transformed)
        looking = True
        
    #print(transformed)

    if transformed == "R" or transformed in rules:
        toret = True

    return toret


def regex(string):
    t = tokenize(string)
    p = parse(t)
    if p:
        tree = Tree()
        root, branches = tree.constructTree(t)
        an_nfa = tree.makeNFA(root)
        startnode = an_nfa[0]
        endnode = an_nfa[1]
        startnode, no_eps = tree.epsilon_elimination(startnode, endnode)
        almost_dfa = tree.eliminate_multiple_transitions(no_eps, startnode)
        #start, allstates = tree.DFAify(almost_dfa[0], almost_dfa[1])
        start = almost_dfa[0] #disable this if you uncomment the dfa thing
        '''print(f"I'm an NFA with only one state! My startnode is {almost_dfa[0].id}")
        for thingy in almost_dfa[1]:
            print(f"I am node {thingy.id}, and ")
            for thing in thingy.transitions:
                print(f"\twhen I see {thing}, I go to node(s) ", end="")
                for a_node in thingy.transitions[thing]:
                    print(str(a_node.id) + ", ", end="")
                print()
            print(f"Am I a success state? {thingy.accept}")'''

        return start
    else:
        print("error: invalid regex")
        return None
    
def check_if_valid(start, string):
    match = False
    currentnode = start
    for char in string:
        print(char, end="")
        if char in currentnode.transitions:
            currentnode = currentnode.transitions[char]
            match = currentnode.accept
        else:
            print()
            return False
    print()
    return match


def check_if_valid_nonregularized(start, string):
    match = False
    currentnode = start
    for char in string:
        print(char, end="")
        if char in currentnode.transitions:
            itr = iter(currentnode.transitions[char])
            currentnode = next(itr)
            match = currentnode.accept
        else:
            print()
            return False
    print()
    return match
