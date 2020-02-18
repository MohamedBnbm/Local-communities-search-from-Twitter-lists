import io
import sys

sys.setrecursionlimit(15000)


# Class for list object
class liste:
    def __init__(self,id,ord,ings,kws):
        self.id = id
        self.ord = ord
        self.ings = set(ings)
        self.kws = set(kws)


# Class for intent object
class intent:
    def __init__(self,ings,kws):
        self.ings = ings
        self.kws = kws


#Class for extent object
class context:
    def __init__(self,attributes,objects,dataset):
        self.attributes = attributes
        self.objects = objects
        self.dataset = dataset


#CLass for concept object
class concept:
    def __init__(self,**kwargs):
        self.context = kwargs['context']
        self.lists = kwargs['extent']
        if 'intent' not in kwargs:
            self.intent = find_intent(kwargs['extent'],self.context)
            self.extent = find_extent(self.intent,self.context)
        elif 'extent' not in kwargs:
            self.extent = find_extent(kwargs['intent'],kwargs['context'])
            if len(self.extent) != 0:
                self.intent = find_intent(self.extent,self.context)
            else:
                self.intent = kwargs['intent']
        else:
            self.intent = kwargs['intent']
            self.extent = kwargs['extent']
        if len(self.extent) <= 1:
            self.weight = 0
        else:
            max_ings = 1
            max_kws = 1
            for e in self.extent:
                max_ings = max(max_ings,len(e.ings))
                max_kws = max(max_kws,len(e.kws))
            self.weight = (kwargs['alpha']*len(self.intent.ings)/max_ings) + ((1-kwargs['alpha'])*len(self.intent.kws)/max_kws)


#Function for reading context
def read_context(repo):
    dic_users = {}
    dic_kws = {}
    users = []
    kws = []
    with io.open('../../data/{}/context.txt'.format(repo),encoding='utf-8') as f:
        for i,line in enumerate(f):
            line = line[:-1].split('|')
            li = line[0]
            us = line[1][:-1].split(',')
            ks = line[2][:-1].split(',')
            if len(us)<200 and len(us)>20:
                dic_users[li] = us
                dic_kws[li] = ks
                users = users + us
                kws = kws + ks
    return set(users),set(kws),dic_users,dic_kws


#Function for building context
def build_context(users,keywords,dic_users,dic_kws):
    attributes = intent(users, keywords)
    objects = list(dic_users.keys())
    dataset = []
    for i,o in enumerate(objects):
        dataset.append(liste(int(o),i,dic_users[o],dic_kws[o]))
    return context(attributes,objects,dataset)


#Function for computing the intent of an extent
def find_intent(extent,context):
    if len(extent) == 0:
        return context.attributes
    elif len(extent) == len(context.objects):
        return intent(set(),set())
    ings = extent[0].ings
    kws = extent[0].kws
    for e in extent[1:]:
        ings = ings & e.ings
        kws = kws & e.kws
        if ings == set() and kws == set():
            return intent(set(),set())
    return intent(ings,kws)


#Function for computing the extent of an intent
def find_extent(intent,context):
    if len(intent.ings) == 0 and len(intent.kws) == 0:
        return context.dataset
    elif len(intent.ings)+len(intent.kws) == 7870:
        return []
    extent = set()
    if len(intent.ings) == 0:
        for r in context.dataset:
            if intent.kws.issubset(r.kws):
                extent.add(r)
    elif len(intent.kws) == 0:
        for r in context.dataset:
            if intent.ings.issubset(r.ings):
                extent.add(r)
    else:
        for r in context.dataset:
            if intent.ings.issubset(r.ings) and intent.kws.issubset(r.kws):
                extent.add(r)
    return list(extent)


#Function for measuring the quality of a set of lists (extent)
def q(lists,alpha):
    if len(lists)<=1:
        return 1
    ings = lists[0].ings
    kws = lists[0].kws
    m_ings = len(ings)
    m_kws = len(kws)
    for l in lists[1:]:
        ings = ings & l.ings
        kws = kws & l.kws
        m_ings = max(m_ings,len(l.ings),1)
        m_kws = max(m_kws,len(l.kws),1)
    return (alpha * len(ings)/m_ings) + ((1-alpha)*len(kws)/m_kws)


#Main function for enumeration
def algoEnu(context,lmbda,alpha,curr_concept,i,res=[]):
    if i == len(context.dataset):
        a = 0
    else:
        cont = False
        new_intent = intent(curr_concept.intent.ings & context.dataset[i].ings, curr_concept.intent.kws & context.dataset[i].kws)
        new_extent = []
        for r in context.dataset:
            if new_intent.ings.issubset(r.ings) and new_intent.kws.issubset(r.kws):
                if r not in curr_concept.extent+[context.dataset[i]]:
                    if r.ord < i:
                        cont = True
                        break
                    else:
                        new_extent.append(r)
                else:
                    new_extent.append(r)
        if not cont:
            new_concept = concept(intent=new_intent,extent=new_extent,context=context,alpha=alpha)
            qu = q(new_concept.extent,alpha)
            if qu>=lmbda:
                if len(new_concept.extent)>1 and set(new_concept.extent) not in [set(l[0].extent) for l in res]:
                    # print(str([l.ord for l in new_concept.extent]+[qu]))
                    res.append((new_concept,qu))
                algoEnu(context,lmbda,alpha,new_concept,i+1,res)
        algoEnu(context,lmbda,alpha,curr_concept,i+1,res)
    return res


#Function for saving patterns to file
def write_patterns(field, patterns):
    with open('../../data/{}/patterns/algoEnu/patterns.txt', 'w') as f:
        for pat in patterns:
            for l in pat:
                f.write(l.id+',')
            f.write('\n')