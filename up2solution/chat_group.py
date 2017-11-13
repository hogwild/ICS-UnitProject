S_ALONE = 0
S_TALKING = 1

#==============================================================================
# Group class:
# member fields: 
#   - An array of items, each a Member class
#   - A dictionary that keeps who is a chat group
# member functions:
#    - join: first time in
#    - leave: leave the system, and the group
#    - list_my_peers: who is in chatting with me?
#    - list_all: who is in the system, and the chat groups
#    - connect: connect to a peer in a chat group, and become part of the group
#    - disconnect: leave the chat group but stay in the system
#==============================================================================

class Group:
    
    def __init__(self):
        self.members = {}
        self.chat_grps = {}
        self.grp_ever = 0
        
    def join(self, name):
        self.members[name] = S_ALONE
        return
        
    #implement        
    def is_member(self, name):
        return name in self.members.keys()
    ## Alternatively:
#        if name in self.members:
#            return True
#        return False

            
    #implement
    def leave(self, name):
        self.disconnect(name)
        del self.members[name]
        return
    ## Another one for reference
#        if name in self.members:
#            for v in self.chat_grps.values():
#               if name in v:
#                   v.remove(name)
#            del self.members[name]
#            # remove the chat_group that only contains one member
#            key = []
#            peer = []
#            for k in self.chat_grps:
#                if len(self.chat_grps[k]) <= 1:
#                    key.append(k)
#                    peer += self.chat_grps[k]
#            while key:
#                del self.chat_grps[key.pop()]
#                self.members[peer.pop()] = S_ALONE
#        else:
#            print('{} is not in the group.'.format(name))
#        return
        
    #implement                
    def find_group(self, name):
        found = False
        group_key = 0
        for k in self.chat_grps:
            if name in self.chat_grps[k]:
                found = True
                group_key = k
                break # alternatively: return found, group_key
        return found, group_key
        
    #implement                
    def connect(self, me, peer):
        #if peer is in a group, join it
        peer_in_group, group_key = self.find_group(peer)
        if peer_in_group:
            print(peer, "is talking already, connect!")
            if me not in self.chat_grps[group_key]:
                self.chat_grps[group_key].append(me)
                self.members[me] = S_TALKING
        else:
            print(peer, "is idle as well")
            self.grp_ever += 1
            self.chat_grps[self.grp_ever] = [me, peer]
            self.members[me] = S_TALKING
            self.members[peer] = S_TALKING
            ## you can try sys.maxsize to see how many candidates
            ## for the key 
        # otherwise, create a new group with you and your peer
        return

    #implement                
    def disconnect(self, me):
        # find myself in the group, quit
        in_group, group_key = self.find_group(me)
        if in_group == True:
            self.chat_grps[group_key].remove(me)
            self.members[me] = S_ALONE
            # peer may be the only one left as well... handle this case
            if len(self.chat_grps[group_key]) == 1:
                peer = self.chat_grps[group_key].pop()
                self.members[peer] = S_ALONE
                del self.chat_grps[group_key]
        return
        
    def list_all(self):
        # a simple minded implementation
        full_list = "Users: ------------" + "\n"
        full_list += str(self.members) + "\n"
        full_list += "Groups: -----------" + "\n"
        full_list += str(self.chat_grps) + "\n"
        return full_list

    #implement
    def list_me(self, me):
        # return a list, "me" followed by other peers in my group
        my_list = [me]
        in_group, group_key = self.find_group(me)
        if in_group:
            [my_list.append(member) for member in \
             self.chat_grps[group_key] if member != me]
        return my_list
## Alternatively:
#        if me in self.members.keys():
#            my_list = []
#            my_list.append(me)
#            in_group, group_key = self.find_group(me)
#            if in_group == True:
#                for member in self.chat_grps[group_key]:
#                    if member != me:
#                        my_list.append(member)
#        return my_list


if __name__ == "__main__":
    g = Group()
    g.join('a')
    g.join('b')
    g.join('c')
    print(g.list_all())
    
    g.connect('a', 'b')
    g.connect('c', 'b')
    print(g.list_all())
    print(g.list_me('c'))
