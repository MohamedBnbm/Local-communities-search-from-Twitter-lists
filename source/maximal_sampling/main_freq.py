from utils import *

#Parameters
repo = 'politique'
sds = dic_seeds[repo]
alpha = 0.8
lmbda = 0.8
n_samples = 100000

#read context
users, keywords, dic_users, dic_kws = read_context(repo,sds)

#Build set of lists and frequency dictionary
lists = []
u_freq = {}
k_freq = {}
for i in dic_users.keys():
    us = dic_users[i]
    kws = dic_kws[i]
    lists.append(liste(int(i),set(us),set(kws),1))
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
u_freq = [k:v/sum_us for k, v in u_freq.items()]
k_freq = [k:v/sum_kws for k, v in k_freq.items()]

#Sampling
patterns = maximal_sampling_mul(lists,alpha,lmbda,n_samples)
