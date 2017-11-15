# -*- coding: utf-8 -*-
import pickle
import string


class Index:
    def __init__(self, name):
        self.name = name
        self.msgs = [];
        self.index = {}
        self.total_msgs = 0
        self.total_words = 0
        
    def get_total_words(self):
        return self.total_words
        
    def get_msg_size(self):
        return self.total_msgs
        
    def get_msg(self, n):
        return self.msgs[n]
        
    def add_msg(self, m):
        self.msgs.append(m)
        self.total_msgs += 1
        
    def add_msg_and_index(self, m):
        self.add_msg(m)
        line_at = self.total_msgs - 1
        self.indexing(m, line_at)
 
    def indexing(self, m, l):
       # m = m.strip(string.punctuation + '\n')
        #print(m)
        words = m.split()
        self.total_words += len(words)
        for wd in words:
            wd = wd.strip(string.punctuation + '\n')
            #print(wd)
            if wd not in self.index:
                self.index[wd] = [l]
            else:
                self.index[wd].append(l)
                                    
    def search(self, term):
        msgs = []
        ##Here, term is a phrase containts a few words.
        words = term.split()
        indices = set(self.index[words.pop()])
        while words:
            ##Pick out those duplicated
            indices.intersection_update(set(self.index[words.pop()])) 
        for i in indices:
            if term in self.msgs[i]: ## refine the indices with the term
                msgs.append((i, self.msgs[i]))
        return msgs
        
#        terms = term.split()
#        if terms[0] in self.index.keys():
#            indices = self.index[terms[0]]
#            for i in indices:
#                if term in self.msgs[i]:
#                    msgs.append((i, self.msgs[i]))
#        return msgs
#        msgs = []
#        if (term in self.index.keys()):
#            indices = self.index[term]
#            msgs = [(i, self.msgs[i]) for i in indices]
#        return msgs

class PIndex(Index):
    def __init__(self, name):
        super().__init__(name)
        roman_int_f = open('roman.txt.pk', 'rb')
        self.int2roman = pickle.load(roman_int_f)
        #print(self.int2roman)
        roman_int_f.close()
        self.load_poems()
        
        # load poems
    def load_poems(self):
        lines = open(self.name, 'r').readlines()
        for l in lines:
            if l.rstrip(string.punctuation + '\n') in self.int2roman.values():
                #print(l.rstrip(string.punctuation + '\n'))
                self.add_msg_and_index('chapter' + l.strip())
                #print(('chapter' + l).strip(string.punctuation + '\n'))
            else:
                self.add_msg_and_index(l.strip())
    
    def get_poem(self, p):
        p_str = 'chapter' + self.int2roman[p]
        p_next_str = 'chapter' +  self.int2roman[p + 1] + '.'
        [(go_line, m)] = self.search(p_str)
        poem = []
        end = self.get_msg_size()
        theFirst = True
        while go_line < end:
            this_line = self.get_msg(go_line)
            if theFirst:
                this_line = this_line[7:] #remove the 'charpter'
                theFirst = False
            if this_line == p_next_str:
                break
            poem.append(this_line)
            go_line += 1
        return poem
    
if __name__ == "__main__":
    sonnets = PIndex("AllSonnets.txt")
    p3 = sonnets.get_poem(3)
    print(p3)
    s_love = sonnets.search("love in")
    print(s_love)
    s_look = sonnets.search("look in")
    print(s_look)
    s_look = sonnets.search("look into")
    print(s_look)

