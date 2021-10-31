import pandas as pd
import numpy as np
import json
from scipy.sparse import csr_matrix
from sklearn.neighbors import NearestNeighbors
import joblib

#This code is supposed to be run once/twice in a week

# User - Skill mapping
# { "Username" : [skill1, skill2, skill3, ......., skilln] }

def get_skills_n_domains(skill_domain_dict):
    skills = set()
    domains = set()
    skill_domain_map = {}
    for element in skill_domain_dict:
        domains.add(element['domain_name'])
        for skill in element['skills']:
            skills.add(skill['skill_name'])
        skill_domain_map[element['domain_name']] = skills
    skills = list(skills)
    domains = list(domains)
    skills.sort()
    domains.sort()

    SkillDomains = []
    for domain in domains:
        oneHotSkillDomainList = []
        for skill in skills:
            if(skill in skill_domain_map[domain]):
                oneHotSkillDomainList.append(1)
            else:
                oneHotSkillDomainList.append(0)
        oneHotSkillDomainList.insert(0,skill)
        SkillDomains.append(oneHotSkillDomainList)
    columns = []
    columns.extend(domains)
    columns.insert(0,'SkillName')
    df_skill_n_domains = pd.DataFrame(SkillDomains,columns=columns)
    df_skill_n_domains.to_csv('skill_n_domain.csv',index=False)
    return skills, SkillDomains

def get_user_names(user_skill_dict):
    UserNames = []
    for username,skill_list in user_skill_dict.items():
        UserNames.append(username)
    return UserNames

def create_models(UserSkills, UserDomains):
    user_skill_features = csr_matrix(UserSkills)
    user_domain_features = csr_matrix(UserDomains)

    skill_based_model = NearestNeighbors(metric='cosine',n_neighbors=10, n_jobs=-1)
    domain_based_model = NearestNeighbors(metric='cosine',n_neighbors=10, n_jobs=-1)

    skill_based_model.fit(user_skill_features)
    domain_based_model.fit(user_domain_features)

    joblib.dump(skill_based_model,'KNN_user_skills.pkl')
    joblib.dump(domain_based_model,'KNN_user_domains.pkl')


def user_data_matrix(user_skill_dict, Allskills):
    user_skill_dict.sort()
    UserSkills = []
    UserNames = {}
    for username,skill_list in user_skill_dict.items():
        UserNames.append(username)
        oneHotSkillList = []
        for skill in Allskills:
            if(skill in skill_list):
                oneHotSkillList.append(1)
            else:
                oneHotSkillList.append(0)
        UserSkills.append(oneHotSkillList)
    json.dump(UserNames,open('allUserNames.json','w'))
    return UserSkills

def weights(UserSkills, SkillDomains):
    UserSkills = np.array(UserSkills)
    SkillDomains = np.array(SkillDomains)
    UserDomains = np.dot(UserSkills, SkillDomains)
    return UserDomains

def get_target_user_data(target_user_skills):
    target_skills = []
    df_skill_n_domain = pd.read_csv('skill_n_domain.csv')
    skills = df_skill_n_domain['SkillName'].values
    for skill in skills:
        if(skill in target_user_skills):
            target_skills.append(1)
        else:
            target_skills.append(0)
    target_skills = np.array(target_skills)
    
    SkillDomains = np.array(df_skill_n_domain.iloc[:,1:].values)

    target_domains = np.dot(target_skills, SkillDomains)
    return target_skills, target_domains

def recommendUsers(target_user_skills, target_user_domains, UserNames):
    skill_based_model = joblib.load('KNN_user_skills.pkl', mmap_mode='r')
    domain_based_model = joblib.load('KNN_user_domains.pkl', mmap_mode='r')

    #TODO: See this return distances parameter and how to access these distances
    skills_based_similar_users, skills_based_similar_user_distances = skill_based_model.kneighbors([target_user_skills],10)
    domains_based_similar_users, domains_based_similar_user_distances = domain_based_model.kneighbors([target_user_domains],10)

    skill_based_user_names = []
    domain_based_user_names = []

    for usr_indx in skills_based_similar_users[0]:
        skill_based_user_names.append(UserNames[usr_indx])
    for usr_indx in domains_based_similar_users[0]:
        domain_based_user_names.append(UserNames[usr_indx])
    
    return skill_based_user_names, domain_based_user_names

#TODO : write the main driver code which will connect all these functions.
#TODO : see error handling and exception handling in python (erros generated from database)

def update_models(skill_domain_dict, user_skill_dict):
    skills, SkillDomains = get_skills_n_domains(skill_domain_dict)
    UserSkills = user_data_matrix(user_skill_dict, skills) #user-skill-data-matrix
    UserDomains = weights(UserSkills, SkillDomains)
    create_models(UserSkills, UserDomains)

#TODO: think of a waay to not require the user-skill-dict as its costly operation
def predict(target_user_skills):
    UserNames = json.load(open('allUserNames.json')) #[1]
    encoded_target_user_skills, encoded_target_user_domains = get_target_user_data(target_user_skills)
    similar_skill_users, similar_domain_users = recommendUsers(encoded_target_user_skills, encoded_target_user_domains, UserNames)


"""
[1] Suppose a model is trained today, now in next 3 days some users have updated/deleted their
profile. This means their data is not present in database but is considered in model.pkl file.
This pkl file will be updated after some days so till then we are saving the previous sequence of
usernames so the returned indexes for a target user match the correct users.
These recommended users may not be present in database and we will have to do error handling there.
"""