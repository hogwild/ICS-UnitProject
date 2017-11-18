import time
import socket
import select
import sys
import string
import indexer
import pickle as pkl
from chat_utils import *
import chat_group as grp

class Server:
    def __init__(self):
        self.new_clients = [] #list of new sockets of which the user id is not known
        self.logged_name2sock = {} #dictionary mapping username to socket
        self.logged_sock2name = {} # dict mapping socket to user name
        self.all_sockets = []
        self.group = grp.Group()
        #start server
        self.server=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind(SERVER)
        self.server.listen(5)
        self.all_sockets.append(self.server)
        #initialize past chat indices
        self.indices={}
        #sonnet indexing
        self.sonnet = indexer.PIndex('AllSonnets.txt')
        
    def new_client(self, sock):
        #add to all sockets and to new clients
        print('new client...')
        sock.setblocking(0)
        self.new_clients.append(sock)
        self.all_sockets.append(sock)

    def login(self, sock):
        #read the msg that should have login code plus username
        msg = myrecv(sock)
        if len(msg) > 0:
            code = msg[0]

            if code == M_LOGIN:
                name = msg[1:]
                if self.group.is_member(name) != True:
                    #move socket from new clients list to logged clients
                    self.new_clients.remove(sock)
                    #add into the name to sock mapping
                    self.logged_name2sock[name] = sock
                    self.logged_sock2name[sock] = name
                    #load chat history of that user
                    if name not in self.indices.keys():
                        try:
                            self.indices[name]=pkl.load(open(name+'.idx','rb'))
                        except IOError: #chat index does not exist, then create one
                            self.indices[name] = indexer.Index(name)
                    print(name + ' logged in')
                    self.group.join(name)
                    mysend(sock, M_LOGIN + 'ok')
                else: #a client under this name has already logged in
                    mysend(sock, M_LOGIN + 'duplicate')
                    print(name + ' duplicate login attempt')
            else:
                print ('wrong code received')
        else: #client died unexpectedly
            self.logout(sock)

    def logout(self, sock):
        #remove sock from all lists
        name = self.logged_sock2name[sock]
        pkl.dump(self.indices[name], open(name + '.idx','wb'))
        del self.indices[name]
        del self.logged_name2sock[name]
        del self.logged_sock2name[sock]
        self.all_sockets.remove(sock)
        self.group.leave(name)
        sock.close()

#==============================================================================
# main command switchboard
#==============================================================================
    def handle_msg(self, from_sock):
        #msg is the string sent by the client state machine: IMPORTANT
        msg = myrecv(from_sock)
        if len(msg) > 0:
            code = msg[0]           
#==============================================================================
#             handle connect request: this is implemented for you
#==============================================================================
            if code == M_CONNECT:
                to_name = msg[1:]
                from_name = self.logged_sock2name[from_sock]
                if to_name == from_name:
                    msg = M_CONNECT + 'hey you'
                # connect to the peer
                elif self.group.is_member(to_name):
                    to_sock = self.logged_name2sock[to_name]
                    self.group.connect(from_name, to_name)
                    the_guys = self.group.list_me(from_name)
                    msg = M_CONNECT + 'ok'
                    for g in the_guys[1:]:
                        to_sock = self.logged_name2sock[g]
                        mysend(to_sock, M_CONNECT + from_name)
                else:
                    msg = M_CONNECT + 'no_user'
                mysend(from_sock, msg)
#==============================================================================
#             handle multicast message exchange; IMPLEMENT THIS    
#==============================================================================
            elif code == M_EXCHANGE:
                from_name = self.logged_sock2name[from_sock]
                # Finding the list of people to send to
                the_guys = self.group.list_me(from_name)#[1:]
                for g in the_guys[1:]:
                    to_sock = self.logged_name2sock[g]                
                    mysend(to_sock, "...Remember to index the messages before sending, or search won't work")
#==============================================================================
#             listing available peers; IMPLEMENT THIS
#==============================================================================
            elif code == M_LIST:
                from_name = self.logged_sock2name[from_sock]
                msg = "M_LIST handler needs to use self.group functions to work"
                mysend(from_sock, msg)
#==============================================================================
#             retrieve a sonnet; IMPLEMENT THIS
#==============================================================================
            elif code == M_POEM:
                poem_indx = 0
                from_name = self.logged_sock2name[from_sock]\
                #note: the poem retrive from the sonnet is a list of strings
                poem = ["M_POEM handler needs to use self.sonnet functions to work"]
                mysend(from_sock, M_POEM + '\n'.join(poem))
#==============================================================================
#             retrieve the time; IMPLEMENT THIS
#==============================================================================
            elif code == M_TIME:
                ctime = "M_TIME handler has to calc current date/time to send (use time module)"
                mysend(from_sock, ctime)
#==============================================================================
#             search handler; IMPLEMENT THIS
#==============================================================================
            elif code == M_SEARCH:
                search_rslt = "M_SEARCH handler needs to use self.indices search to work"
                #note: search_rslt is a list of tupple
                mysend(from_sock, M_SEARCH + search_rslt) 
#==============================================================================
#             the "from" guy has had enough (talking to "to")!
#==============================================================================
            elif code == M_DISCONNECT:
                from_name = self.logged_sock2name[from_sock]
                the_guys = self.group.list_me(from_name)
                self.group.disconnect(from_name)
                the_guys.remove(from_name)
                if len(the_guys) == 1:  # only one left
                    g = the_guys.pop()
                    to_sock = self.logged_name2sock[g]
                    mysend(to_sock, M_DISCONNECT)
#==============================================================================
#                 the "from" guy really, really has had enough
#==============================================================================
            elif code == M_LOGOUT:
                self.logout(from_sock)
        else:
            #client died unexpectedly
            self.logout(from_sock)   

#==============================================================================
# main loop, loops *forever*
#==============================================================================
    def run(self):
        print ('starting server...')
        while(1):
           read,write,error=select.select(self.all_sockets,[],[])
           print('checking logged clients..')
           for logc in list(self.logged_name2sock.values()):
               if logc in read:
                   self.handle_msg(logc)
           print('checking new clients..')
           for newc in self.new_clients[:]:
               if newc in read:
                   self.login(newc)
           print('checking for new connections..')
           if self.server in read :
               #new client request
               sock, address=self.server.accept()
               self.new_client(sock)
           
def main():
    server=Server()
    server.run()

main()
