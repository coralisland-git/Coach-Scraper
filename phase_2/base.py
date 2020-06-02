EV_KEY = 'pONjp5zOEC3NCxPp3cBoM'

def validate(item):    
    if item == None:
        item = ''
    if type(item) == int or type(item) == float:
        item = str(item)
    if type(item) == list:
        item = ' '.join(item)
    return item.replace(u'\u2013', '-').encode('ascii', 'ignore').encode("utf8").replace('\t', '').replace('\n', ' ').strip()

def eliminate_space(items):
    rets = []
    for item in items:
        item = validate(item)
        if item != '':
            rets.append(item)
    return rets

def get_index(val, arr):
    for idx, item in enumerate(arr):
        if val == item:
            return idx
    return 0

def get_name(e_name):
    sps = [',', '/', '(', '|', '-']
    e_name = validate(e_name)
    for sp in sps:
        e_name = e_name.split(sp)[0] if sp in e_name else e_name
    return e_name

def check_email_combination(session, e_emails):
    for idx, e_email in enumerate(e_emails[:-1]):
        e_verify_url = 'https://apps.emaillistverify.com/api/verifEmail?secret={}&email={}'.format(EV_KEY, e_email)
        e_verify_status = session.get(e_verify_url).text
        if 'ok' in e_verify_status:            
            return { 'status' : True, 'idx' : idx, 'checked' : True }
    return { 'status' : False, 'idx' : -1, 'checked' : True }

def generate_email(fullname, s_email):
    if fullname == '' or s_email == '' or '@' not in s_email:
        return ['', '', '', '', '']
    s_domain = validate(s_email.split('@')[-1])
    names = eliminate_space(fullname.lower().replace('.', '').replace("'", '').strip().split(' '))
    if len(names) < 2:
        names += ['']
    e_emails = [
        names[0][0] + ''.join(names[1:]) + '@' + s_domain,
        ''.join(names[1:]) + names[0][0] + '@' + s_domain,
        names[0] + '.' + ''.join(names[1:]) + '@' + s_domain,
        names[0] + '_' + ''.join(names[1:]) + '@' + s_domain,
        ''
    ]
    return e_emails

def verify_email(session, e_emails):
    for idx, e_email in enumerate(e_emails[:-1]):
        if e_email != '' and '@' in e_email:
            e_verify_url = 'https://apps.emaillistverify.com/api/verifEmail?secret={}&email={}'.format(EV_KEY, e_email)
            e_verify_status = session.get(e_verify_url).text            
            if 'ok' in e_verify_status:            
                return e_email
    return ''

def is_in_needed_sports(item):
    titles = ['basket', 'volley', 'foot']
    for title in titles:
        if title in item.lower():
            return True
    return False

def is_not_contact(item):
    titles = ['Administrator', 'Secretary', 'Provider', 'Council', 'Director']
    for title in titles:
        if title in item:
            return False
    return True