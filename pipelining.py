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
        SkillDomains.append(oneHotSkillDomainList)

    return skills, domains, SkillDomains

def create_matrices(user_skill_dict, Allskills):
    user_skill_dict.sort()
    UserNames = []
    UserSkills = []
    for username,skill_list in user_skill_dict:
        UserNames.append(username)
        oneHotSkillList = []
        for skill in Allskills:
            if(skill in skill_list):
                oneHotSkillList.append(1)
            else:
                oneHotSkillList.append(0)
        UserSkills.append(oneHotSkillList)
    return UserNames, UserSkills

def weights(UserSkills, SkillDomains):
    UserSkills = np.array(UserSkills)
    SkillDomains = np.array(SkillDomains)
    UserDomains = np.dot(UserSkills, SkillDomains)
    return UserDomains

def get_target_user_data(target_user_skills, skills, SkillDomains):
    target_skills = []
    for skill in skills:
        if(skill in target_user_skills):
            target_skills.append(1)
        else:
            target_skills.append(0)
    target_skills = np.array(target_skills)
    SkillDomains = np.array(SkillDomains)
    target_domains = np.dot(target_skills, SkillDomains)
    return target_skills, target_domains


def create_models(UserSkills, UserDomains, UserNames):
    user_skill_features = csr_matrix(UserSkills)
    user_domain_features = csr_matrix(UserDomains)

    skill_based_model = NearestNeighbors(metric='cosine',n_neighbors=10, n_jobs=-1)
    domain_based_model = NearestNeighbors(metric='cosine',n_neighbors=10, n_jobs=-1)

    skill_based_model.fit(user_skill_features)
    domain_based_model.fit(user_domain_features)

    joblib.dump(skill_based_model,'KNN_user_skills.pkl')
    joblib.dump(domain_based_model,'KNN_user_domains.pkl')

def recommendUsers(target_skills, target_domains, UserNames):

    skill_based_model = joblib.load('KNN_user_skills.pkl', mmap_mode='r')
    domain_based_model = joblib.load('KNN_user_domains.pkl', mmap_mode='r')

    target_skills = [target_skills]
    target_domains = [target_domains]

    #TODO: See this return distances parameter and how to access these distances
    skills_based_similar_users, skills_based_similar_user_distances = skill_based_model.kneighbors(target_skills,10)
    domains_based_similar_users, domains_based_similar_user_distances = domain_based_model.kneighbors(target_domains,10)

    skill_based_user_names = []
    domain_based_user_names = []

    for usr_indx in skills_based_similar_users[0]:
        skill_based_user_names.append(UserNames[usr_indx])
    for usr_indx in domains_based_similar_users[0]:
        domain_based_user_names.append(UserNames[usr_indx])
    

    pass

#TODO : write the main driver code which will connect all these functions.
#TODO : see error handling and exception handling in python (erros generated from database)