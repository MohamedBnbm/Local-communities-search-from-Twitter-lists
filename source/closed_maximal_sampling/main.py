from utils import *

#Parameters
repo = 'politique'
alpha = 0.8
lmbda = 0.8
n_samples = 2000

#Read context
users, keywords, dic_users, dic_kws = read_context(repo)

#Build set of lists
lists = []
for i in dic_users.keys():
    us = dic_users[i]
    kws = dic_kws[i]
    lists.append(liste(int(i),set(us),set(kws),1))

#Sampling
patterns = closed_maximal_sampling_mul(lists,alpha,lmbda,n_samples)

#Discarding redundant patterns
unique_patterns = filter(patterns)

#Write patterns to file
write_patterns(field, unique_patterns)
