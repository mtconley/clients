class JiraClient(object):
    import json
    import requests
    import unicodedata
    import datetime
    import re
    import base64
    import getpass

    RESPONSE_OK = 200
    

    """
    TODO
    ----
    customefield_10301 maps to owner data
    """

    def __init__(self):
     
        self._get_configuration('.settings.json')
        
        self.HEADERS = { 
            'Authorization': 'Basic ' + self.user_key,
            'Content-Type': 'application/json',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_3) ' +
            'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.101 Safari/537.36'
        }
        
        self.run = 0

    def set_issue(self, issue):
        if not self.re.findall('.*-\d{1,5}$', issue):
            raise ValueError('{0} is an invalid JIRA issue number'.format(issue))
        self.issue = issue

    def get_data(self):
        self._parse_data()

    def _get_configuration(self, filename):
        try:
            settings = self.json.load(open(filename))
        except IOError:
            self._make_settings_conf()
            settings = self.json.load(open(filename))
        
        self.preparer = settings['displayName']
        self.preparer_email = settings['emailAddress']
        
        self.host = settings['host']
        self.user_key = settings['user_key']
        self.jira_email = settings.get('jira_mail', None)

        self.template_target = settings['template_target']
        
    def _request(self, api_url):
        response = self.requests.get(api_url, headers=self.HEADERS)
        if response.status_code != self.RESPONSE_OK:
            response.raise_for_status()
        return response
    
    def _query_issue(self):
        api_url = self.host + "/rest/api/2/issue/" + self.issue
        response = self._request(api_url)
        self.issue_json = response.json()
        
    def _query_issue_watchers(self):
        api_url = self.host + "/rest/api/2/issue/" + self.issue + '/watchers'
        response = self._request(api_url)
        self.watcher_json = response.json()
    
    def _query_user(self, username):
        api_url = self.host + "/rest/api/2/user?username=" + username
        response = self._request(api_url)
        user_json = response.json()
        return user_json
    
    def _parse_user(self, user_json):
            displayName = user_json['displayName']
            emailaddress = user_json['emailAddress']
            return {'name': displayName, 'email': emailaddress}
        
    def _parse_watchers(self):
        self._query_issue_watchers()
        watcher_dict = {}
        for watcher in self.watcher_json['watchers']:
            username = watcher['name']
            user_json = self._query_user(username)
            user_info = self._parse_user(user_json)
            watcher_dict[username] = user_info
        return watcher_dict
        
    def _parse_data(self):
        
        self._query_issue()
        data = self.issue_json
        
        key = data['key']
        url = self.host + '/browse/' + key
        fields = data['fields']

        self.description = {
            'name': key,
            'url': url,
            'date_created': self._cdate(fields['created'][:10]),
            'date_now': self._date_now(),
            'summary': fields['summary'],
            'description_text': self._format_text(fields['description'])
        }

        
        self.people = {
            'requestor': {'name': fields['creator']['displayName'],
                         'email': fields['creator']['emailAddress']},
            'creator':   {'name': fields['creator']['displayName'], 
                         'email': fields['creator']['emailAddress']},
            'reporter':  {'name': fields['reporter']['displayName'], 
                         'email': fields['reporter']['emailAddress']},
            'assignee':  {'name': fields['assignee']['displayName'], 
                         'email': fields['assignee']['emailAddress']},
            'preparer':  {'name': self.preparer,
                         'email': self.preparer_email}
        }
        
        self.attachments = dict([(fields['attachment'][i]['filename'], 
                        fields['attachment'][i]['content']) 
                        for i in range(len(fields['attachment']))])
        
        
        self.watchers = self._parse_watchers()

        for name, value in self.description.iteritems():
            setattr(self, name, value)
        
        self.run = 1
        
    def _download_file(self, file_name, file_source):
        response = self.requests.get(file_source, headers=self.HEADERS)
        path_name = '{0}/{1}/{2}'.format(self.template_target, self.issue, file_name)
        output = open(path_name, 'w')
        output.write(response.content)
        output.close

    def _format_text(self, text):
        text = self._replace_embedded_users_text(text)
        text = self._cstr(text)
        text = text.strip('\n').strip().replace('\r\n', '<br>')
        return text

    def _replace_embedded_users_text(self, text):
        pattern_user = '\[~(.*)\]'
        embedded_users = self.re.findall(pattern_user, text)
        if embedded_users:
            for username in embedded_users:
                pattern_user = '\[~{0}\]'.format(username)
                user_json = self._query_user(username)
                user_dict = self._parse_user(user_json)
                user_link = self._user_to_link(user_dict)
                text = self.re.sub(pattern_user, user_link, text)
        return text

    def _cstr(self, string): 
        string = self.unicodedata.normalize('NFKD', string)
        string = string.encode('ascii', 'ignore')
        return string

    def _user_to_link(self, user_dict):
        user_dict['subject'] = self.issue
        user_link = \
        """<a href='mailto:{email}?subject=[JIRA] {subject}' 
        target='_top' style='color:#cc0000; font-weight:bold;'>
        {name} </a>""".format(**user_dict)
        return user_link
    
    def _cdate(self, date_string):
        date_obj = self.datetime.datetime.strptime(date_string, '%Y-%m-%d')
        date_string = date_obj.strftime('%Y-%m-%d')
        return date_string
    
    def _date_now(self):
        date_now = self.datetime.datetime.now().strftime('%Y-%m-%d')
        return date_now
    
    def _make_settings_conf(self):
        repeat = True
        while repeat:
            yes_no = raw_input("""You are missing a file, .settings.json, 
                         \rin your projects directory.\n
                         \rWould you like to make one now? (y or n): """)
            yes_no = yes_no.lower()[0]
            if yes_no in 'yn':
                repeat = False
        if yes_no=='n':
            raise IOError("No settings.json cofiguration file")
        displayName = raw_input("Please enter your full name: ")
        email = raw_input("What is your email address? : ")
        username = raw_input("What is your jira username?: ")
        user_key = self.base64.b64encode(
            "{0}:{1}".format(username,
                self.getpass.getpass(
                    """What is your JIRA password?
                    \rThis will immediately be encrypted: """)))
        host = raw_input("""What is your jira instances address?
                        \r (https://jira.mycompany.com): """)
        template_target = '.'
        jira_email = raw_input("Please enter the default email for your jira bot")

        settings = {
            "emailAddress": email, 
            "host": host, 
            "template_target": template_target,
            "displayName": displayName, 
            "user_key": user_key,
            "jira_email": jira_email
        }

        self.json.dump(settings, open('.settings.json', 'w'), 
                       sort_keys=True, indent=4, separators=(',', ': '))
        print '.settings.json created'


class JiraHTMLMediator(JiraClient):

    def __init__(self, issue, Formatter):
        self.Formatter = Formatter

        super(self.__class__, self).__init__()
        self.set_issue(issue)
        self.get_data()

    def build_html(self):
        adressee = self.jira_email
        summary = self.summary
        date = self.date_now
        description = self.description_text
        address = self.url
        issue = self.issue
        people = self.people
        attachments = self.attachments

        HTMLWriter = self.Formatter()
        
        HTMLWriter = self.Formatter()
        HTMLWriter.add_header(('JIRA '+issue, address, summary))
        HTMLWriter.add_break()
        HTMLWriter.add_date(date)
        HTMLWriter.add_break()
        for title in ['requestor', 'creator', 'reporter', 'assignee','preparer']:
            contact, attrib = self._contact_attributes(title, adressee, people, 'RE: '+issue)
            HTMLWriter.add_tab()
            HTMLWriter.add_contact((title, contact), attrib)
            HTMLWriter.add_break()
        HTMLWriter.add_title('Description')
        HTMLWriter.add_text(description)
        HTMLWriter.add_title('Attachments')
        for attachment, url in attachments.iteritems():
            HTMLWriter.add_link(attachment, {'href': url})
            HTMLWriter.add_break()

        return HTMLWriter.build_html()


    def _contact_attributes(self, displayName, addressee, recipients, subject):
        contact = recipients[displayName]['name']
        contact_email = recipients[displayName]['email']
        email = {'email': addressee,
                'cc': [x['email'] for x in sorted(recipients.values(),
                             key=lambda x: x['email']==contact_email,
                             reverse=True)],
                 'subject': 'RE: '+ subject}
        attrib = {'href': email, 'target': '_top'}
        return contact, attrib

class IpynbClient(object):
    import json
    
    cell_markdown = """{
           "cell_type": "markdown",
           "metadata": {},
           "source": []
        }"""
    
    cell_code =   """{
           "cell_type": "code",
           "execution_count": null,
           "metadata": {
            "collapsed": true
           },
           "outputs": [],
           "source": []
        }"""
    
    def __init__(self):
        
        self.ipynb = self.json.loads("""{
             "cells": [],
             "metadata": {
              "kernelspec": {
               "display_name": "Python 2",
               "language": "python",
               "name": "python2"
              },
              "language_info": {
               "codemirror_mode": {
                "name": "ipython",
                "version": 2
               },
               "file_extension": ".py",
               "mimetype": "text/x-python",
               "name": "python",
               "nbconvert_exporter": "python",
               "pygments_lexer": "ipython2",
               "version": "2.7.10"
              }
             },
             "nbformat": 4,
             "nbformat_minor": 0
            }""")
        
    def _new_cell(self, cell_type):
        return {'code': self.json.loads(self.cell_code),
                'markdown': self.json.loads(self.cell_markdown)}[cell_type]
        
    def write(self, lines, cell_type='markdown'):
        cell_types = {'code', 'markdown'}
        if isinstance(lines, str):
            lines = [lines]
        if cell_type in cell_types:

            lines[-1] = lines[-1].strip('\n')

            cell = self._new_cell(cell_type)
            cell['source'] = lines

            self.ipynb['cells'].append(cell)
        else:
            raise ValueError('cell_type must be "{0}" or "{1}"'.format(*cell_types))
            
    def save(self, location):
        if not location.endswith('.ipynb'):
            location += '.ipynb'
        self.json.dump(self.ipynb, open(location, 'w'), 
                       sort_keys=True, indent=4, separators=(',', ': '))
