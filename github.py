#!/usr/local/bin/python
#===============================================================================
# github.py - backs up all the github repos in my org
#
# uses http basic auth to get list of repos - could use oauth?
#  ... see http://develop.github.com/p/general.html
# uses curl for repo list- could use Kenneth Reitz's Requests library
#  ... see http://pydanny.blogspot.com/2011/05/python-http-requests-for-humans.html
#
# uses ~/.gitconfig and ~/.ssh to clone repos 
#===============================================================================

import time
import string
import subprocess
import sys
import os
import json

def main():
    #===============================================================================
    # ### Settings ###
    #===============================================================================
    
    # gitHub login/password info
    # note user/pass is used for repo list only - git clone auth done via cert
    githubUser = "USERNAME"
    githubPass = "PASSWORD"
    org = "ORGNAME"
    orgUrl = "http://github.com/api/v2/json/organizations/" + org + "/repositories"
    backupDir = "/opt/backup/github"
    
    # logging, basics
    # this doesn't rotate itself, fyi...
    logSaveFile = backupDir + "github.log"
    logOut = open(logSaveFile, 'a')
    sys.stdout = logOut
    sys.stderr = logOut

    # start timer
    timeStart = time.time()
    print "Started at " + time.strftime('%Y-%m-%d %H:%M') + "\n"
    
    #===============================================================================
    #  get list of repos
    #===============================================================================

    curlcommand = 'curl -u "%s:%s" %s' % (githubUser,githubPass, orgUrl)
    results = subprocess.check_output(curlcommand, shell=True, stderr=logOut)
    repoList = json.loads(results)

    #===============================================================================
    #  for each repo, clone if new; otherwise git remote update 
    #  authenticating via ~/.gitconfig and ssh certificate
    #===============================================================================

    for repo in repoList['repositories']:
        repoDir = backupDir + repo['name']
        repoName = repo['name']
    # this next bit based on http://stackoverflow.com/q/273192
        try:
            os.makedirs( repoDir )
        except OSError:
            if os.path.isdir(repoDir):
                os.chdir(repoDir)
                subprocess.call('git remote update',shell=True, stderr=subprocess.STDOUT) 
                print "Updating %s" % (repoName)
                continue
            else:
                print "unknown error creating " + repoName
                break
        gitCommand = "git clone git@github.com:%s/%s %s/%s" % (org, repoName, backupDir, repoName)
        print gitCommand
        subprocess.call(gitCommand,shell=True, stderr=subprocess.STDOUT)

    #===============================================================================
    #  clean up....
    #===============================================================================
    totalSecondsElapsed = time.time() - timeStart
    hoursElapsed = int(totalSecondsElapsed / 3600)
    minutesElapsed = int((totalSecondsElapsed - hoursElapsed*3600) / 60)
    print 'Total time: %s hours, %s minutes (%s total seconds)' % (hoursElapsed, minutesElapsed, totalSecondsElapsed)

    logOut.close()
# end def of main()

if __name__ == '__main__':
    main()
