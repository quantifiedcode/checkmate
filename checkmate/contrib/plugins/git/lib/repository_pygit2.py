# -*- coding: utf-8 -*-

"""
NOTICE:

This version of the repository API migrates its code to pygit2, which is
a bit tricky to install but which provides a clean API to the git libraries.

In the future, it will replace the old repository module that relies on git's
command line interface.
"""

from __future__ import unicode_literals

import os
import subprocess
import datetime
import re
import time
import logging
import traceback
import select
import fcntl
import shutil
import StringIO
import tempfile
import pygit2
from collections import defaultdict

logger = logging.getLogger(__name__)

class GitException(BaseException):

    pass

def get_first_date_for_group(start_date,group_type,n):
    """
    :param start:   start date
    :n          :   how many groups we want to get
    :group_type :   daily, weekly, monthly
    """
    current_date = start_date
    if group_type == 'monthly':
        current_year = start_date.year
        current_month = start_date.month
        for i in range(n-1):
            current_month-=1
            if current_month == 0:
                current_month = 12
                current_year -= 1
        first_date = datetime.datetime(current_year,current_month,1)
    elif group_type == 'weekly':
        first_date=start_date-datetime.timedelta(days = start_date.weekday()+(n-1)*7)
    elif group_type == 'daily':
        first_date = start_date-datetime.timedelta(days = n-1)
    first_date = datetime.datetime(first_date.year,first_date.month,first_date.day,0,0,0)
    return first_date

def group_snapshots_by_date(snapshots, period):

    available_periods = {
        'daily' : lambda dt : dt.strftime("%Y-%m-%d"),
        'weekly' : lambda dt: dt.strftime("%Y-%W"),
        'monthly' : lambda dt: dt.strftime("%Y-%m")
    }
    formatter = available_periods[period]

    grouped_snapshots = defaultdict(list)

    for snapshot in snapshots:
        dt = datetime.datetime.fromtimestamp(snapshot.committer_date_ts).date()
        key = formatter(dt)
        grouped_snapshots[key].append(snapshot)

    return grouped_snapshots

class Repository(object):

    def __init__(self,path):
        self._path = path
        self.devnull = open(os.devnull,"w")
        self.stderr = ''
        self.stdout = ''
        self.returncode = None

    @property
    def path(self):
        return self._path

    @path.setter
    def set_path(self,path):
        self._path = path

    @property
    def repo(self):
        if not hasattr(self,'_repo'):
            self._repo = pygit2.Repository(self._path)
        return self._repo

    def _call(self,args,kwargs,capture_stderr = True,timeout = None):

        if not 'cwd' in kwargs:
            kwargs['cwd'] = self.path

        if timeout:

            #We write command output to temporary files, so that we are able to read it
            #even if we terminate the command abruptly.
            with tempfile.TemporaryFile() as stdout,tempfile.TemporaryFile() as stderr:

                if capture_stderr:
                    stderr = stdout

                p = subprocess.Popen(*args,stdout = stdout,stderr = stderr,preexec_fn=os.setsid,**kwargs)

                def read_output():
                    stdout.flush()
                    stderr.flush()
                    stdout.seek(0)
                    self.stdout = stdout.read()
                    stderr.seek(0)
                    self.stderr = stderr.read()

                start_time = time.time()

                while time.time() - start_time < timeout:
                    if p.poll() != None:
                        break
                    time.sleep(0.001)

                timeout_occured = False

                if p.poll() == None:
                    timeout_occured = True
                    stdout.flush()
                    stderr.flush()
                    p.terminate()
                    time.sleep(0.1)
                    if p.poll() == None:
                        p.kill()

                read_output()

                if timeout_occured:
                    self.stderr+="\n[process timed out after %d seconds]" % int(timeout)

            self.returncode = p.returncode
            return p.returncode,self.stdout
        else:
            if capture_stderr:
                stderr = subprocess.STDOUT
            else:
                stderr = subprocess.PIPE
            p = subprocess.Popen(*args,stdout = subprocess.PIPE,stderr = stderr,**kwargs)
            stdout,stderr = p.communicate()
            return p.returncode,stdout


    def call(self,*args,**kwargs):
        if 'timeout' in kwargs:
            timeout = kwargs['timeout']
            del kwargs['timeout']
            return self._call(args,kwargs,timeout = timeout)
        else:
            return self._call(args,kwargs)

    def check_output(self,*args,**kwargs):
        returncode,stdout = self._call(args,kwargs,capture_stderr = False)
        if returncode != 0:
            raise subprocess.CalledProcessError(returncode,args[0],stdout)
        return stdout

    def add_remote(self,name,url):
        return_code,stdout = self.call(["git","remote","add",name,url])
        return return_code

    def remove_remote(self,name):
        return_code,stdout = self.call(["git","remote","remove",name])
        return return_code

    def get_remotes(self):
        remotes = []
        for remote in self.repo.remotes:
            remotes.append({
                'name' : remote.name,
                'url' : remote.url
                })
        return remotes

    def update_remote_url(self,remote,url):
        self.repo.remotes.set_url(remote,url)

    def update_remote_name(self,remote,name):
        self.repo.remotes.rename(remote,name)

    def init(self):
        return_code,stdout = self.call(["git","init"])
        return return_code

    def pull(self,remote = "origin",branch = "master"):
        return_code,stdout = self.call(["git","pull",remote,branch])
        return return_code

    def _get_ssh_wrapper(self):
        wrapper = os.path.abspath(__file__+"/..")+"/ssh"
        return wrapper

    def _get_ssh_config(self,identity_file):
        return """Host *
     StrictHostKeyChecking no
     IdentityFile "%s"
     IdentitiesOnly yes
""" % identity_file


    def fetch(self,remote = "origin",branch = None,ssh_identity_file = None,git_config = None,git_credentials = None):
        if not re.match(r"^[\w\d]+$",remote):
            raise ValueError("Invalid remote: %s" % remote)
        try:
            directory = tempfile.mkdtemp()
            env = {'HOME' : directory}
            if ssh_identity_file:
                #To Do: Security audit
                logger.debug("Fetching with SSH key")


                env.update({'CONFIG_FILE' : directory+"/ssh_config",
                            'GIT_SSH' : self._get_ssh_wrapper()})

                with open(directory+"/ssh_config","w") as ssh_config_file:
                    ssh_config_file.write(self._get_ssh_config(ssh_identity_file))

            if git_config:
                env.update({'GIT_CONFIG_NOSYSTEM' : '1'})

                with open(directory+"/.gitconfig","w") as git_config_file:
                    git_config_file.write(git_config)

            if git_credentials:

                with open(directory+"/.git-credentials","w") as git_credentials_file:
                    git_credentials_file.write(git_credentials)

            extra_args = []
            if branch is not None:
                extra_args.append(branch)

            return_code,stdout = self.call(["git","fetch",remote]+extra_args,env = env,timeout = 120)
        finally:
            shutil.rmtree(directory)

        return return_code

    def reset(self,branch):
        return_code,stdout = self.call(["git","reset",branch])

    def get_branches(self,include_remote = True):
        if include_remote:
            extra_args = ['-a']
        else:
            extra_args = []
        raw_output = self.check_output(["git","branch","--list"]+extra_args).decode("utf-8",'ignore')
        branches = [re.sub(r"^remotes\/","",ss) for ss in [re.sub(r"[^\~\w\d\-\:\/\.\\]*","",s.strip())
                                                           for s in raw_output.split("\n")] if ss]
        return branches

    def set_branch(self,branch):
        return self.call(["git","checkout",branch])[0]

    def filter_commits_by_branch(self,commits,branch = "master"):

        since = min([commit['committer_date_ts'] for commit in commits])
        until = max([commit['committer_date_ts'] for commit in commits])

        branch_commits = self.get_commits(branch = branch,since = since,until = until)
        branch_shas = [commit['sha'] for commit in branch_commits]

        filtered_commits = [commit for commit in commits if commit['sha'] in branch_shas]

        return filtered_commits

    def summarize_commits(self,commits,include_limit = 6):

        sorted_commits = sorted(commits,key = lambda commit : commit['committer_date'])
        summary = {'count' : len(commits)}

        if len(commits) <= include_limit:
            summary['commits'] = commits
            summary['slices'] = [(None,None)]
        else:
            summary['commits'] = commits[:include_limit/2:]+commits[-include_limit/2:]
            summary['slices'] = [(None,include_limit/2),(-include_limit/2,None)]

        summary['authors'] = {}

        for commit in commits:
            author_name = commit['author_name']
            if author_name in summary['authors']:
                author_summary = summary['authors'][author_name]
                author_summary['count']+=1
                if not commit['author_email'] in author_summary['emails']:
                    author_summary['emails'].append(commit['author_email'])
            else:
                summary['authors'][author_name] = {'emails' : [commit['author_email']],
                                                   'count' : 1,
                                                   'name' : author_name}

        summary['authors'] = summary['authors'].values()

        return summary


    def get_parents(self,commit_sha):
        base_args = ["git",
                     "rev-list",
                     "--parents",
                     "-n",
                     "1"]
        return self.check_output(base_args+[commit_sha]).decode('utf-8','ignore').split()[1:]

    def get_commits(self,branch = None,offset = 0,limit = 0,shas = None,params = None,
                    from_to = None,args = None, **kwargs):

        split_sequence = '---a4337bc45a8fc544c03f52dc550cd6e1e87021bc896588bd79e901e2---'
        try:
            base_args = ["git",
                         "--no-pager",
                         "log",
                         "--date=raw",
                         "--pretty=format:%H:-:%ct:-:%cn:-:%ce:-:%at:-:%an:-:%ae:-:%P:-:%T:-:%n%B%n"+split_sequence+"%n"]
            extra_args = []
            if params:
                extra_args.extend(params)
            if args:
                extra_args.extend(args)
            for key,value in kwargs.items():
                if key in ('before','until') and isinstance(value,datetime.datetime):
                    value = (value+datetime.timedelta(days = 1)).ctime()
                elif key in ('after','since') and isinstance(value,datetime.datetime):
                    value = (value-datetime.timedelta(days = 1)).ctime()
                base_args.append("--%s" % key.replace('_','-'))
                if value:
                    base_args.append("%s" % value)
            if shas:
                raw_log_output = ''
                for sha in shas:
                    sha_extra_args = extra_args+['-n','1',sha]
                    raw_log_output+=self.check_output(base_args+sha_extra_args).decode('utf-8','ignore')
            else:
                if branch:
                    extra_args.extend([branch])
                if from_to:
                    extra_args.extend([from_to[0]+".."+from_to[1]])
                if offset != 0:
                    extra_args.extend(["--skip","%d" % offset])
                if limit != 0:
                    extra_args.extend(["--max-count","%d" % limit])
                raw_log_output = self.check_output(base_args+extra_args).decode('utf-8','ignore')
        except subprocess.CalledProcessError as e:
            if not e.returncode in (141,128):
                raise
            raw_log_output = e.output.decode("utf-8","ignore")
        headers_and_logs_str = map(lambda x:x.lstrip().split("\n",1),raw_log_output.split(split_sequence))[:-1]
        headers_and_logs = map(lambda x:(x[0].split(":-:"),x[1]),headers_and_logs_str)

        def get_initials(name):
            parts = re.sub(r"[^\s\w\d]+","",name).split()
            if len(parts) <=3:
                return "".join([s[0].upper() for s in parts])
            else:
                return "".join([s[0].upper() for s in parts[:3]+parts[-1:]])

        def decode_entry(x):
            return  {
                    'sha': x[0][0],
                    'committer_date': datetime.datetime.fromtimestamp(int(x[0][1])) if x[0][1] else None,
                    'committer_date_ts' : int(x[0][1]) if x[0][1] else None,
                    'committer_name' : x[0][2],
                    'committer_email': x[0][3],
                    'committer_initials' : get_initials(x[0][2]),
                    'author_initials' : get_initials(x[0][5]),
                    'author_date': datetime.datetime.fromtimestamp(int(x[0][4])) if x[0][4] else None,
                    'author_date_ts' : int(x[0][4]) if x[0][4] else None,
                    'author_name': x[0][5],
                    'author_email': x[0][6],
                    'parents' : x[0][7].split(),
                    'tree_sha' : x[0][8],
                    'log' : x[1],
                }

        commits = sorted(map(decode_entry
                ,headers_and_logs),key = lambda x:x['committer_date_ts'])

        #Workaround to achieve precise datetime matching in the 'before' and 'since' fields.
        for key in ('before','until'):
            if key in kwargs and isinstance(kwargs[key],datetime.datetime):
                commits = [commit for commit in commits if commit['committer_date'] < kwargs[key]]
        for key in ('since','after'):
            if key in kwargs and isinstance(kwargs[key],datetime.datetime):
                commits = [commit for commit in commits if commit['committer_date'] > kwargs[key]]

        return commits

    def get_submodules(self):
        submodules = map(lambda x:x.split(" ")[1],
                         self.check_output(["git","submodule"]).split("\n")[:-1]).decode("utf-8",'ignore')
        return submodules

    def get_modifications_by_author(self,commits):
    	modifications_by_author = defaultdict(lambda : defaultdict(lambda : {'lines_added': 0,
                                                                             'lines_removed':0,
                                                                             'commits' : 0}))
    	for commit in commits:
            author_email = commit['author_email']
            sha = commit['sha']
            try:
                modified_files = [(int(v[0]),int(v[1]),v[2])
                                  for v in [s.split("\t")
                                            for s in self.check_output(["git",
                                                                        "diff",
                                                                        r"--numstat",
                                                                        "{sha}^..{sha}"\
                                                                        .format(sha = sha)\
                                                                        .decode("utf-8",'ignore')])\
                                                                        .strip()\
                                                                        .split("\n")]
                                            if len(v) == 3 \
                                               and v[2] != '' \
                                               and v[0] != '-' \
                                               and v[1] != '-']
            except subprocess.CalledProcessError:
            	continue
            for (lines_added,lines_removed,path) in modified_files:
            	d = modifications_by_author[author_email][path]
            	d['lines_added'] += lines_added
            	d['lines_removed'] += lines_removed
            	d['commits'] += 1
            return modifications_by_author

    def get_contributors(self,branch = None):
        args = ["-se"]
        if branch:
            args+=[branch]
        else:
            args+=["--all"]
        lines = self.check_output(["git","shortlog"]+args).decode("utf-8",'ignore').split("\n")
        contributors = []
        for line in lines:
            match = re.match("^.*?(\d+)\s+(.*?)\s*\<(.*)\>\s*$",line)
            if match:
                (n_commits,name,email) = match.groups()
                contributors.append({'name' : name,'email' : email,'n_commits' : int(n_commits)} )
        return contributors

    def get_number_of_commits(self,branch = None):
        if branch:
            command = ["git","rev-list",branch,"--count"]
        else:
            command = ["git","rev-list","HEAD","--count"]
        n_commits = int(self.check_output(command).strip().decode("utf-8",'ignore'))
        return n_commits

    def get_files_in_commit(self,commit_sha,path = None):
        if path == None:
            opts = ["--full-tree","-r",commit_sha]
        else:
            opts = ["%s:%s" % (commit_sha,path)]
        files = [dict(zip(['mode','type','sha','path'],f.strip().split()))
                           for f in self.check_output(["git","ls-tree"]+opts)\
                                        .decode("utf-8",'ignore')\
                                        .split("\n") if f]
        return files

    def get_file_details(self,commit_sha,path):
        (file_mode,file_type,file_sha,file_path) = self.check_output(["git",
                                                                      "ls-tree",
                                                                      commit_sha,
                                                                      path])\
                                                       .decode("utf-8",'ignore').split()
        return {'mode':file_mode,'type':file_type,'sha':file_sha,'path':file_path}

    def get_diffs(self,commit_sha_a,commit_sha_b = None):
        if not commit_sha_b:
            files = self.get_files_in_commit(commit_sha_a)
            return [['A',file['path']] for file in files]
        else:
            diffs = self.check_output(["git",
                                       "diff",
                                       "--name-status",
                                       commit_sha_a,
                                       commit_sha_b])\
                        .decode("utf-8",'ignore').split("\n")
            diffs = map(lambda x:x.split("\t"),diffs)
            return [x for x in diffs if len(x) == 2]

    def get_file_content(self,commit_sha,path):
        try:
            file_content = self.check_output(["git","show","%s:%s" % (commit_sha,path)])
        except subprocess.CalledProcessError:
            raise IOError
        return file_content

    def get_file_content_by_sha(self,sha):
        try:
            file_content = self.check_output(["git","cat-file","blob","%s" % (sha,)])
        except subprocess.CalledProcessError:
            raise IOError
        return file_content
