from utils import *

#Parameters
field = 'politique'
alpha = 0.8
lmbda = 0.8
n_samples = 100000

#Read context
users, keywords, dic_users, dic_kws = read_context(field)

#Build set of lists and frequency dictionaries of users and keywords
lists, cumsum, u_freq, k_freq = calculate_frequencies(dic_users,dic_keywords)

#Sampling
patterns = two_step_mul(lists,alpha,lmbda,n_samples,u_freq,sum_us,k_freq,sum_kws,cumsum)

#Discarding redundant patterns
unique_patterns = filter(patterns)

#Write patterns to file
write_patterns(field, unique_patterns)