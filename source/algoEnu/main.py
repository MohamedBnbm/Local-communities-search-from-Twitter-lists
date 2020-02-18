from utils import *

#Parameters
field = 'politique'
alpha = 0.8
lmbda = 0.8

#Read context
users, keywords, dic_users, dic_kws = read_context(field)

#Build context
contexte = build_context(users,keywords,dic_users,dic_kws)

#Enumeration
init_concept = concept(extent=[],intent=contexte.attributes,context=contexte,alpha=alpha)
patterns = algoEnu(contexte,alpha,lmbda,init_concept,0)

#Write patterns to file
write_patterns(field, patterns)