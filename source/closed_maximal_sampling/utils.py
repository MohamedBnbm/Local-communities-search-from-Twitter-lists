from random import uniform
import io


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


#Function for initializing sets M and C before sampling start
def init_sampling(listes,alpha):
    M = {l:1 for l in listes}
    sorted_M = [k[0] for k in sorted(M.items(),key=lambda x:x[1])]
    C = sorted_M
    M = {l:M[l] for l in C}
    return M,C

#Function for computing closure of a set of lists
def closure(ls,u1,u2,k1,k2):
    ex = set()
    un = len(u1)
    kn = len(k1)
    for l in ls:
        if u1 & l.members == u1 and k1 & l.kws == k1:
            ex.add(l)
            u2 = max(u2,len(l.members))
            k2 = max(k2,len(l.kws))
    return ex,un,kn,u2,k2


#Function that computes closure of (R U liste) and returns its quality measure Q
def q_close(R,liste,listes,common_users, common_kws, max_users, max_kws, alpha):    
    u_n = common_users & liste.members
    u_d = max(max_users, len(liste.members),1)
    k_n = common_kws & liste.kws
    k_d = max(max_kws, len(liste.kws),1)
    res,u1,k1,u2,k2 = closure(listes,u_n,u_d,k_n,k_d)
    return [res,(alpha*(u1/u2)) + ((1-alpha)*(k1/k2)),u_n,k_n,u2,k2]


#Function for sampling from distribution M2
def sample_from_m2(dic):
    lists = list(dic.keys())
    if len(lists) == 1:
        return dic[lists[0]]
    cum_sum = [0]
    for l in lists:
        cum_sum.append(cum_sum[-1] + dic[l][1])
    r = uniform(0, cum_sum[-1])
    i = 0
    while cum_sum[i] < r:
        i += 1
    return dic[lists[i-1]]
    

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
            max_users = max(max_users,len(liste.members))
            max_kws = max(max_kws, len(liste.kws))
            common_users = common_users & liste.members
            common_kws = common_kws & liste.kws
        return (alpha*len(common_users)/max_users) + ((1-alpha)*len(common_kws)/max_kws)


#Function for sampling from distribution M
def sample_from_m(dic):
    lists = list(dic.keys())
    cum_sum = [0]
    for l in lists:
        cum_sum.append(cum_sum[-1] + dic[l])
    r = uniform(0, cum_sum[-1])
    i = 0
    while cum_sum[i] < r:
        i += 1
    return lists[i-1]
    

#Main function for single closed maximal sampling
def sample_closed_maximal(M0,C0,listes,alpha,lmbda):
    R = set()
    M = M0.copy()
    C = C0[:]
    x = sample_from_m(M)
    C.remove(x)
    R = R.union({x})
    comm_users = x.members
    comm_kws = x.kws
    max_users = len(x.members)
    max_kws = len(x.kws)
    scores = {l:q_close(R,l,listes,comm_users,comm_kws,max_users,max_kws,alpha) for l in C}
    C = [l for l in scores.keys() if scores[l][1]>=lmbda]
    while len(C) > 0:
        M = {l:scores[l] for l in C}
        s = sample_from_m2(M)
        R = s[0]
        for x in R:
            if x in C:
                C.remove(x)
        comm_users,comm_kws,max_users,max_kws = s[2:]
        scores = {l:q_close(R,l,listes,comm_users,comm_kws,max_users,max_kws,alpha) for l in C}
        C = [l for l in scores.keys() if scores[l][1]>=lmbda]
    return R,Q(R,alpha)


#Function for multiple closed maximal sampling
def closed_maximal_sampling_mul(lists,alpha,lmbda,n_samples):
    patterns = []
    M0, C0 = init_sampling(lists,alpha)
    for _ in range(n_samples):
        pattern, score = sample_closed_maximal(M0,C0,lists,alpha,lmbda)
        if score >= lmbda and len(pattern) > 1:
            patterns.append(pattern)
    return patterns


#Function for discarding redundant patterns
def filter(patterns):
    unique_patterns = []
    for pat in patterns:
        if set(pat) not in [set(l) for l in unique_patterns]:
            unique_patterns.append(pat)
    return unique_patterns


#Function for saving patterns to file
def write_patterns(field, patterns):
    with open('../../data/{}/patterns/closed_maximal_sampling/patterns.txt', 'w') as f:
        for pat in patterns:
            for l in pat:
                f.write(l.id+',')
            f.write('\n')