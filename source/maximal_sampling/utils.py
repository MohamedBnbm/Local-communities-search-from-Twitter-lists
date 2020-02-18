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


#Function for adding a list to a set of lists and computing quality measure of the resulting set of lists
def q(liste,common_users, common_kws, max_users, max_kws, alpha):
    u_n = len(common_users & liste.members)
    u_d = max(max_users, len(liste.members),1)
    k_n = len(common_kws & liste.kws)
    k_d = max(max_kws, len(liste.kws),1)
    if k_d == 0:
        k_d = 1
    return (alpha*(u_n/u_d)) + ((1-alpha)*(k_n/k_d))
    

#Main function for single maximal sampling
def sample_maximal(M0,C0,listes,alpha,lmbda):
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
    scores = {l:q(l,comm_users,comm_kws,max_users,max_kws,alpha) for l in C}
    C = [l for l in scores.keys() if scores[l]>=lmbda]
    while len(C) > 0:
        M = {l:scores[l] for l in C}
        x = sample_from_m(M)
        C.remove(x)
        R = R.union({x})
        comm_users = comm_users & x.members
        comm_kws = comm_kws & x.kws
        max_users = max(max_users, len(x.members))
        max_kws = max(max_kws, len(x.kws))
        scores = {l:q(l,comm_users,comm_kws,max_users,max_kws,alpha) for l in C}
        C = [l for l in scores.keys() if scores[l]>=lmbda]
    return R,Q(R,alpha)


#Function for multiple maximal sampling
def maximal_sampling_mul(lists,alpha,lmbda,n_samples):
    patterns = []
    M0, C0 = init_sampling(lists,alpha)
    for _ in range(n_samples):
        pattern, score = sample_maximal(M0,C0,lists,alpha,lmbda)
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
    with open('../../data/{}/patterns/maximal_sampling/patterns.txt', 'w') as f:
        for pat in patterns:
            for l in pat:
                f.write(l.id+',')
            f.write('\n')