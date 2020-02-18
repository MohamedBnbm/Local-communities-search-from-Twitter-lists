from random import uniform
import io
from math import log


#Class for list object
class liste:
    def __init__(self, id, members, kws, weight):
        self.id = id
        self.members = members
        self.kws = kws
        self.u_weight = weight


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


#Function for creating set of lists and calculating frequencies of users and keywords
def calculate_frequencies(dic_users,dic_keywords):
    lists = []
    b = []
    cumsum = [0]
    u_freq = {}
    k_freq = {}
    for i in dic_users.keys():
        us = dic_users[i]
        l = len(us)
        kws = dic_kws[i]
        if l > 1:
            lists.append(liste(int(i),set(us),set(kws),1))
            b.append(b_pi_u(lists[-1],alpha))
            cumsum.append(cumsum[-1] + b[-1])
        new_us = set(us) - set(u_freq.keys())
        old_us = set(us) & set(u_freq.keys())
        new_kws = set(kws) - set(k_freq.keys())
        old_kws = set(kws) & set(k_freq.keys())
        for u in new_us:
            u_freq[u] = 1
        for u in old_us:
            u_freq[u] += 1
        for kw in new_kws:
            k_freq[kw] = len([el for el in kws if el == kw])
        for kw in old_kws:
            k_freq[kw] += len([el for el in kws if el == kw])
    sum_us = sum(u_freq.values())
    sum_kws = sum(k_freq.values())
    u_freq = {k:v/sum_us for k, v in u_freq.items()}
    k_freq = {k:v/sum_kws for k, v in k_freq.items()}
    return lists, cumsum, u_freq, k_freq


#Function for computing list's weight for sampling
def b_pi_u(liste,alpha):
    return log(2 ** (alpha*len(liste.members) + (1-alpha)*len(liste.kws)))


#Function for computing user's or keyword's weight for sampling
def proba_pi(e,ings,ing_count,sum_ings,kw_count,sum_kws):
    if ings:
        dic = ing_count
        sm = sum_ings
    else:
        dic = kw_count
        sm = sum_kws
    b_e = dic[e]*sm
    return b_e/(1+b_e)


#Function for sampling a subset of set E
def sequential_step(E,ings,ing_count,sum_ings,kw_count,sum_kws):
    x = set()
    y = set()
    for e in E:
        p = proba_pi(e,ings,ing_count,sum_ings,kw_count,sum_kws)
        if p < uniform(0,1):
            y.add(e)
        else:
            x.add(e)
    return x


#Function for computing quality measure of a set of lists
def Q(set_lists,alpha):
    if len(set_lists) == 1:
        return 0
    else:
        set_lists = list(set_lists)
        max_users = len(set_lists[0].members)
        max_kws = len(set_lists[0].kws)
        common_users = set_lists[0].members
        common_kws = set_lists[0].kws
        for liste in set_lists[1:]:
            max_users = max(max_users,len(liste.members),1)
            max_kws = max(max_kws, len(liste.kws),1)
            common_users = common_users & liste.members
            common_kws = common_kws & liste.kws
        return (alpha*len(common_users)/max_users) + ((1-alpha)*len(common_kws)/max_kws)


#Main function for multiple two-step sampling
def two_step_mul(lists,alpha,lmbda,n_samples,u_freq,sum_us,k_freq,sum_kws,cumsum):
    patterns = []
    for _ in range(n_samples):
        r = uniform(0,1) * cumsum[-1]
        i = 0
        while cumsum[i] < r:
            i += 1
        us = list(lists[i-1].members)
        kws = list(lists[i-1].kws)
        sub_us = sequential_step(us,True,u_freq,sum_us,k_freq,sum_kws)
        sub_kws = sequential_step(kws,False,u_freq,sum_us,k_freq,sum_kws)
        pattern = find_extent(sub_us,sub_kws,lists)
        if Q(pattern,alpha) >= lmbda and len(pattern) > 1:
            patterns.append(pattern)
    return patterns


#Function for finding lists that have s_u in their users and s_k in their keywords
def find_extent(s_u,s_k,lists):
    extent = []
    for l in lists:
        if (l.members & s_u == s_u) and (l.kws & s_k == s_k):
            extent.append(l)
    return extent


#Function for discarding redundant patterns
def filter(patterns):
    unique_patterns = []
    for pat in patterns:
        if set(pat) not in [set(l) for l in unique_patterns]:
            unique_patterns.append(pat)
    return unique_patterns


#Function for saving patterns to file
def write_patterns(field, patterns):
    with open('../../data/{}/patterns/two_step/patterns.txt', 'w') as f:
        for pat in patterns:
            for l in pat:
                f.write(l.id+',')
            f.write('\n')