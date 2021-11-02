def save_usernames_insequence(usernames):
    with open('test.txt', 'w') as f:
        for username in usernames:
            f.write(username + '\n')

def read_usernames_insequence():
    with open('test.txt', 'r') as f:
        usernames = list(map(lambda x:x.strip('\n'),f.readlines()))
    return usernames

usernames = ['a', 'b', 'c', 'd', 'e', 'f']
# save_usernames_insequence(usernames)
print(read_usernames_insequence())