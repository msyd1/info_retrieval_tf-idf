import sys, os, re
import sqlite3
import math
import time

db = {}
docs = {}
stopwords = ['the', 'of', 'and', 'to', 'in', 'you', 'it', 'with', 'that', 'or', 'was', 'he', 'is', 'for', 'this', 'his', 'as', 'not', 'at', 'by', 'all', 'they', 'but', 'be', 'on', 'from', 'had', 'her', 'work', 'are', 'any', 'she', 'if', 'said', 'so', 'which', 'have', 'do', 'we', 'no', 'my', 'were', 'them', 'their', 'him', 'one', 'will', 'me', 'there', 'who', 'up', 'other', 'an', 'its', 'when', 'what', 'can', 'may', 'into', 'out', 'must', 'your', 'then', 'would', 'could', 'more', 'now', 'has', 'like', 'down', 'where', 'been', 'through', 'did', 'away', 'these', 'such', 'set', 'back', 'some', 'than', 'way', 'made', 'our', 'after', 'well', 'should', 'get', 'even', 'am', 'go', 'saw', 'just', 'put', 'while', 'ever', 'off', 'here', 'also']
documents = 0
tokens = 0
resultslist = {}
keylist = []
term = {}
chars = re.compile(r'\W+')
pattid= re.compile(r'(\d{3})/(\d{3})/(\d{3})')
tokens = 0
documents = 0
terms = 0
stopw = 0

class Docs():
        terms = {}


# split on any chars
def splitchars(line) :
        return chars.split(line)

def elenQ(elen, a):
        return(float(math.pow(a.idf,2))+float(elen))
def elenD(elen, a):
        return(float(math.pow(a.tfidf ,2))+ float(elen))

def process(filename):
        try:
                file = open(filename, 'r')
        except IOError:
                print ("Error in file %s" % filename)
                return False
        else:
                for l in file.readlines():
                        parsetoken(l)
        file.close()

class Term():
        termid = 0
        termfreq = 0
        docs = 0
        docids = {}

class PorterStemmer:

    def __init__(self):

        self.b = ""  # buffer for word to be stemmed
        self.k = 0
        self.k0 = 0
        self.j = 0   # j is a general offset into the string

    def cons(self, i):
        """cons(i) is TRUE <=> b[i] is a consonant."""
        if self.b[i] == 'a' or self.b[i] == 'e' or self.b[i] == 'i' or self.b[i] == 'o' or self.b[i] == 'u':
            return 0
        if self.b[i] == 'y':
            if i == self.k0:
                return 1
            else:
                return (not self.cons(i - 1))
        return 1

    def m(self):

        n = 0
        i = self.k0
        while 1:
            if i > self.j:
                return n
            if not self.cons(i):
                break
            i = i + 1
        i = i + 1
        while 1:
            while 1:
                if i > self.j:
                    return n
                if self.cons(i):
                    break
                i = i + 1
            i = i + 1
            n = n + 1
            while 1:
                if i > self.j:
                    return n
                if not self.cons(i):
                    break
                i = i + 1
            i = i + 1

    def vowelinstem(self):
        for i in range(self.k0, self.j + 1):
            if not self.cons(i):
                return 1
        return 0

    def doublec(self, j):
        if j < (self.k0 + 1):
            return 0
        if (self.b[j] != self.b[j-1]):
            return 0
        return self.cons(j)

    def cvc(self, i):
        if i < (self.k0 + 2) or not self.cons(i) or self.cons(i-1) or not self.cons(i-2):
            return 0
        ch = self.b[i]
        if ch == 'w' or ch == 'x' or ch == 'y':
            return 0
        return 1

    def ends(self, s):

        length = len(s)
        if s[length - 1] != self.b[self.k]: # tiny speed-up
            return 0
        if length > (self.k - self.k0 + 1):
            return 0
        if self.b[self.k-length+1:self.k+1] != s:
            return 0
        self.j = self.k - length
        return 1

    def setto(self, s):
        length = len(s)
        self.b = self.b[:self.j+1] + s + self.b[self.j+length+1:]
        self.k = self.j + length

    def r(self, s):
        """r(s) is used further down."""
        if self.m() > 0:
            self.setto(s)

    def step1ab(self):
        if self.b[self.k] == 's':
            if self.ends("sses"):
                self.k = self.k - 2
            elif self.ends("ies"):
                self.setto("i")
            elif self.b[self.k - 1] != 's':
                self.k = self.k - 1
        if self.ends("eed"):
            if self.m() > 0:
                self.k = self.k - 1
        elif (self.ends("ed") or self.ends("ing")) and self.vowelinstem():
            self.k = self.j
            if self.ends("at"):   self.setto("ate")
            elif self.ends("bl"): self.setto("ble")
            elif self.ends("iz"): self.setto("ize")
            elif self.doublec(self.k):
                self.k = self.k - 1
                ch = self.b[self.k]
                if ch == 'l' or ch == 's' or ch == 'z':
                    self.k = self.k + 1
            elif (self.m() == 1 and self.cvc(self.k)):
                self.setto("e")

    def step1c(self):
        """step1c() turns terminal y to i when there is another vowel in the stem."""
        if (self.ends("y") and self.vowelinstem()):
            self.b = self.b[:self.k] + 'i' + self.b[self.k+1:]

    def step2(self):
        """step2() maps double suffices to single ones.
        so -ization ( = -ize plus -ation) maps to -ize etc. note that the
        string before the suffix must give m() > 0.
        """
        if self.b[self.k - 1] == 'a':
            if self.ends("ational"):   self.r("ate")
            elif self.ends("tional"):  self.r("tion")
        elif self.b[self.k - 1] == 'c':
            if self.ends("enci"):      self.r("ence")
            elif self.ends("anci"):    self.r("ance")
        elif self.b[self.k - 1] == 'e':
            if self.ends("izer"):      self.r("ize")
        elif self.b[self.k - 1] == 'l':
            if self.ends("bli"):       self.r("ble") # --DEPARTURE--
            # To match the published algorithm, replace this phrase with
            #   if self.ends("abli"):      self.r("able")
            elif self.ends("alli"):    self.r("al")
            elif self.ends("entli"):   self.r("ent")
            elif self.ends("eli"):     self.r("e")
            elif self.ends("ousli"):   self.r("ous")
        elif self.b[self.k - 1] == 'o':
            if self.ends("ization"):   self.r("ize")
            elif self.ends("ation"):   self.r("ate")
            elif self.ends("ator"):    self.r("ate")
        elif self.b[self.k - 1] == 's':
            if self.ends("alism"):     self.r("al")
            elif self.ends("iveness"): self.r("ive")
            elif self.ends("fulness"): self.r("ful")
            elif self.ends("ousness"): self.r("ous")
        elif self.b[self.k - 1] == 't':
            if self.ends("aliti"):     self.r("al")
            elif self.ends("iviti"):   self.r("ive")
            elif self.ends("biliti"):  self.r("ble")
        elif self.b[self.k - 1] == 'g': # --DEPARTURE--
            if self.ends("logi"):      self.r("log")
        # To match the published algorithm, delete this phrase

    def step3(self):
        """step3() dels with -ic-, -full, -ness etc. similar strategy to step2."""
        if self.b[self.k] == 'e':
            if self.ends("icate"):     self.r("ic")
            elif self.ends("ative"):   self.r("")
            elif self.ends("alize"):   self.r("al")
        elif self.b[self.k] == 'i':
            if self.ends("iciti"):     self.r("ic")
        elif self.b[self.k] == 'l':
            if self.ends("ical"):      self.r("ic")
            elif self.ends("ful"):     self.r("")
        elif self.b[self.k] == 's':
            if self.ends("ness"):      self.r("")

    def step4(self):
        """step4() takes off -ant, -ence etc., in context <c>vcvc<v>."""
        if self.b[self.k - 1] == 'a':
            if self.ends("al"): pass
            else: return
        elif self.b[self.k - 1] == 'c':
            if self.ends("ance"): pass
            elif self.ends("ence"): pass
            else: return
        elif self.b[self.k - 1] == 'e':
            if self.ends("er"): pass
            else: return
        elif self.b[self.k - 1] == 'i':
            if self.ends("ic"): pass
            else: return
        elif self.b[self.k - 1] == 'l':
            if self.ends("able"): pass
            elif self.ends("ible"): pass
            else: return
        elif self.b[self.k - 1] == 'n':
            if self.ends("ant"): pass
            elif self.ends("ement"): pass
            elif self.ends("ment"): pass
            elif self.ends("ent"): pass
            else: return
        elif self.b[self.k - 1] == 'o':
            if self.ends("ion") and (self.b[self.j] == 's' or self.b[self.j] == 't'): pass
            elif self.ends("ou"): pass
            # takes care of -ous
            else: return
        elif self.b[self.k - 1] == 's':
            if self.ends("ism"): pass
            else: return
        elif self.b[self.k - 1] == 't':
            if self.ends("ate"): pass
            elif self.ends("iti"): pass
            else: return
        elif self.b[self.k - 1] == 'u':
            if self.ends("ous"): pass
            else: return
        elif self.b[self.k - 1] == 'v':
            if self.ends("ive"): pass
            else: return
        elif self.b[self.k - 1] == 'z':
            if self.ends("ize"): pass
            else: return
        else:
            return
        if self.m() > 1:
            self.k = self.j

    def step5(self):
        """step5() removes a final -e if m() > 1, and changes -ll to -l if
        m() > 1.
        """
        self.j = self.k
        if self.b[self.k] == 'e':
            a = self.m()
            if a > 1 or (a == 1 and not self.cvc(self.k-1)):
                self.k = self.k - 1
        if self.b[self.k] == 'l' and self.doublec(self.k) and self.m() > 1:
            self.k = self.k -1

    def stem(self, p, i, j):
        """In stem(p,i,j), p is a char pointer, and the string to be stemmed
        is from p[i] to p[j] inclusive. Typically i is zero and j is the
        offset to the last character of a string, (p[j+1] == '\0'). The
        stemmer adjusts the characters p[i] ... p[j] and returns the new
        end-point of the string, k. Stemming never increases word length, so
        i <= k <= j. To turn the stemmer into a module, declare 'stem' as
        extern, and delete the remainder of this file.
        """
        # copy the parameters into statics
        self.b = p
        self.k = j
        self.k0 = i
        if self.k <= self.k0 + 1:
            return self.b # --DEPARTURE--


        self.step1ab()
        self.step1c()
        self.step2()
        self.step3()
        self.step4()
        self.step5()
        return self.b[self.k0:self.k+1]

def splitchars(line) :
        return chars.split(line)

def stripTags(s): 
    intag = False
    s2 = ""    
    for c in s:
        if c == '<':
            intag = True
        elif c == '>':
            intag = False
        if intag != True:
            s2 = s2+c      
    return(s2)

p = PorterStemmer()

def parsetoken(line):
        global documents
        global tokens
        global terms
        global stopw
        line = line.replace('\t',' ')
        line = line.strip()
        l = splitchars(line)
        for elmt in l:
                elmt = elmt.replace('\n','')

                lowerElmt = elmt.lower().strip()

                tokens += 1

                if len(lowerElmt) <2:
                        continue

                if (lowerElmt in stopwords):
                        stopw +=1
                        continue

                try:
                    dummy = int(lowerElmt)               
                except ValueError:
                        stemword = lowerElmt 
                else:
                        continue

                lowerElmt = p.stem(stemword, 0,len(stemword)-1)

                if not (lowerElmt in db.keys()):
                        terms+=1
                        db[lowerElmt] = Term()
                        db[lowerElmt].termid = terms
                        db[lowerElmt].docids = dict()
                        db[lowerElmt].docs = 0

                if not (documents in db[lowerElmt].docids.keys()):
                        db[lowerElmt].docs += 1
                        db[lowerElmt].docids[documents] = 0
                        
                db[lowerElmt].docids[documents] += 1
        return l

def walkdir(cur, dirname):
        global documents
        all = {}
        all = [f for f in os.listdir(dirname) if os.path.isdir(os.path.join(dirname, f)) or os.path.isfile(os.path.join(dirname, f))]
        for f in all:
                if os.path.isdir(dirname + '/' + f):
                        walkdir(cur, dirname + '/' + f)
                else:
                        documents += 1
                        cur.execute("insert into DocumentDictionary values (?, ?)", (dirname+'/'+f, documents))
                        process(dirname + '/' + f)
        return True


def writeindex(db):        
        for k in db.keys():
                cur.execute('insert into TermDictionary values (?,?)', (k, db[k].termid))
                docfreq = db[k].docs
                ratio = float(documents) / float(docfreq)
                idf = math.log10(ratio)

                for i in db[k].docids.keys():
                        termfreq = db[k].docids[i]
                        tfidf = float(termfreq) * float(idf)
                        if tfidf > 0:
                                cur.execute('insert into Posting values (?, ?, ?, ?, ?)', (db[k].termid, i, tfidf, docfreq, termfreq))




if __name__ == '__main__':
        t2 = time.localtime()
        folder = '../data/%'   # Your path to folder with data
        print ('Start Time: %.2d:%.2d' % (t2.tm_hour, t2.tm_min))
        con = sqlite3.connect("../database.db") # Your path to database
        con.isolation_level = None
        cur = con.cursor()
        cur.execute("drop table if exists DocumentDictionary")
        cur.execute("drop index if exists idxDocumentDictionary")
        cur.execute("create table if not exists DocumentDictionary (DocumentName text, DocId int)")
        cur.execute("create index if not exists idxDocumentDictionary on DocumentDictionary (DocId)")
        cur.execute("drop table if exists TermDictionary")
        cur.execute("drop index if exists idxTermDictionary")
        cur.execute("create table if not exists TermDictionary (Term text, TermId int)")
        cur.execute("create index if not exists idxTermDictionary on TermDictionary (TermId)")
        cur.execute("drop table if exists Posting")
        cur.execute("drop index if exists idxPosting1")
        cur.execute("drop index if exists idxPosting2")
        cur.execute("create table if not exists Posting (TermId int, DocId int, tfidf real, docfreq int, termfreq int)")
        cur.execute("create index if not exists idxPosting1 on Posting (TermId)")
        cur.execute("create index if not exists idxPosting2 on Posting (Docid)")
        walkdir(cur, folder)
        writeindex(db)
        print ('Indexing and writing complete: %.2d:%.2d' % (t2.tm_hour, t2.tm_min))
        line = input('Enter the search terms, each separated by a space: ')
        l = splitchars(line)
        cur.execute("SELECT COUNT(*) from DocumentDictionary")
        row = cur.fetchone()
        if row[0] > 0:
                q = "select docid, tfidf, docfreq, termfreq, posting.termid from termdictionary,posting where posting.termid = termdictionary.termid and term = '%s' order by docid, posting.termid" % (l)
                cur.execute(q)
        for row in cur:
                i_termid = row[4]
                i_docid = row[0]
                if not ( i_docid in docs.keys()):
                        docs[i_docid] = Docs()
                        docs[i_docid].terms = {}
                        if not ( i_termid in docs[i_docid].terms.keys()):
                                docs[i_docid].terms[i_termid] = Term()
                                docs[i_docid].terms[i_termid].docfreq = row[2]
                                docs[i_docid].terms[i_termid].termfreq = row[3]
                                docs[i_docid].terms[i_termid].idf = 0.0
                                docs[i_docid].terms[i_termid].tfidf = 0.0
        keylist = resultslist.keys()
        for f in resultslist.keys():
                print(f)
                keylist.append(f)
        keylist.sort(reverse=True)
        i = 0
        for key in keylist:
                i+= 1
                if i > 20:
                        continue
                cur.execute("select DocumentName from documentdictionary where docid = '%d' % (resultslist[key])")
                row = cur. fetchone()
                print ("Document: %s Has Relevance o %f" % (row[0], float(key)/10000))
        con.close()
        t2 = time.localtime()
        print ('End Time: %.2d:%.2d' % (t2.tm_hour, t2.tm_min))
