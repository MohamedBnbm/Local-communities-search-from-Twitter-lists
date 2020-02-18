from utils import *

#Parameters
field = 'politique'
alpha = 0.8
lmbda = 0.8
n_samples = 10000

#read context
users, keywords, dic_users, dic_kws = read_context(field)

#Build set of lists and frequency dictionary
lists = []
for i in dic_users.keys():
    us = dic_users[i]
    kws = dic_kws[i]
    lists.append(liste(int(i),set(us),set(kws),1))

#Sampling
patterns = maximal_sampling_mul(lists,alpha,lmbda,n_samples)

#Discarding redundant patterns
unique_patterns = filter(patterns)

#Write patterns to file
write_patterns(field, unique_patterns)