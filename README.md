# SubShell Web Shell Framework

Author: Joe Vest

Copyright 2015 - SubShell

Written by: Joe Veat

Company: MINIS

DISCLAIMER: This is only for testing purposes and can only be used where strict consent has been given. Do not use this for illegal purposes.

Please read the LICENSE in LICENSE.md for the licensing information


```
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
    --mysqlu=<username>      Set MYSQL Username
    --mysqlp=<password>      Set MySQL Password
    --mysqls=<server>        Set MySQL Server IP or Hostname
    --logdir=<logdir>        Directory path to logs [default: ./logs]
    --debug                  Enable Debugging

```
SubShell is a python command shell used to control and execute commands through HTTP requests to a webshell.  SubShell acts as the interface to the remote webshells.  

SubShell has a companion project named TinyShell.  TinyShell is similar and may offer benefits over SubShell in certain situations.

TinyShell - https://github.com/minisllc/tinyshell

This project was born out of the need for a consolidated webshell framework.  There are numerous available, but I wanted to created backend framework that supports numerous web languages with a common backend.

This project uses the principle of hiding in plain sight (even over non-encrypted communications).  The goal is minimize attention.  Like numerous malicious tools, they are easy to find by defenders once they have a reason to look.  This project is designed to be stealthy, not through high-tech means, but by minimizing the triggering of a defenses such as IDS, Firewall, AV etc.

How does it do this?

  - POST requests minmize data written web logs
  - Encoded traffic helps avoid clear text detection 
  - Console interface forces a slow down when issuing commands.  Use of a webshell should be deliberate and focused.  Numerous connections may attract attention.
  - Customization of user-agent to help blend in.
  - Valid 404 errors displayed when attemped to connect to shell without 'authetnication' information

## Current Features

  - Designed for used agains Windows Based servers
  - Supports shells in asp, aspx, php, jsp
  - Logging of all actions
  - Base64 encoded command sent and receivied in POST requests
  - Invalid request generates a legitimate 404 message.
  - Tracks current directory by implementing common commands (cd, pwd, ls, dir)
  - Built in helper commands
  - Simple replay attack prevention.  Uses a token that is only valid +/- 12 hours of current time.
  - 'Authentication' using replay attack prevention

## Python Dependencies
 
 - refer to requirements.txt

## SubShell Console Reference 

Interaction with a remote 'shell' using subshell is similar to a non-interactive shell.  Non interactive commands can be submited and the results displayed.  

If an interactive command is submitted, the command will not return.  Command will display a timeout error.  This is an HTTP timeout and not an error of whether the command executed or not.


| Command       | Description                                                                                                         | Example
|---------------|---------------------------------------------------------------------------------------------------------------------|--------------------------------------
|cd             | change directory                                                                                                    | cd c:\temp
|command        | Optional command used to issue remote command.  If no other built in command matches, then this command is assumed. | command tasklist
|config         | Show current settings                                                                                               | config
|dir            | directory command                                                                                                   | dir c:\temp
|download       | download remote file.  Files stored in ./downloads.  The original file structure is created.                        | download c:\temp\myfile.txt
|exit           | exit command shell                                                                                                  | exit
|help           | Display help for commands                                                                                           | help
|history        | show command  history                                                                                               | history
|ls             | alias for dir                                                                                                       | ls c:\temp
|mysql          | Issue SQL command to MySQL Server base on MySQL configuration                                                       | mysql show databases
|mysql_db       | Select MySQL databse                                                                                                | mysql_db mysql
|mysql_password | Select MySQL password                                                                                               | mysql_password password
|mysql_server   | Select MySQL server                                                                                                 | mysql_server localhost
|mysql_username | Select MySQL username                                                                                               | mysql_username root
|ps             | List processes                                                                                                      | ps
|pwd            | show current directory                                                                                              | pwd
|python         | drop to interactive python shell                                                                                    | python
|shell          | submit command to local shell                                                                                       | shell ifconfig 
|status         | Show status for Uploads and Downloads                                                                               | status
|timeout        | display or set the command timeout setting in seconds                                                               | timeout 120
|upload         | upload file to remote server.                                                                                       | upload myfile.txt c:\windows\temp\myfile.txt


## API Used to Communicate to web shells

All command submitted to the shell are POST request with a minimum of 2 parameters (sessionid,command)

POST Parameters

|Parameter  | Description |
|-----------|-------------|
|sessionid  |Used to 'authenticate' requests and minimized replay attacks.  Based on current time.  Any request +/- 12hrs will not be allowed.  If the time is off an HTTP 408 will be sent with the HTTP header expires:'timevalue'.  SubShell can use this value to adjust its authentication it sends.|            
|apikey     |used to submit OS commands|
|apikeyd    |Download file from remote host|
|apikeyu    |Upload file to remote host |
|feed       |stores Base64 encoded file.  Used for upload |

## Features Support by Shell Type

|Feature           | jsp  | aspx | asp  | php  |
|------------------|------|------|------|------|
|Replay Protection |  x   |   x  |   x  |  x   |
|Issue command     |  x   |   x  |   x  |  x   |
|Upload            |  x   |      |      |  x   |
|Download          |  x   |   x  |   x  |  x   |
|MySQL connector   |      |      |      |  x   |
|404 on GET        |  x   |   x  |   x  |  x   |

 
----------------------------------------------------------------------------------- 

## Initial Thought and Requirements to build project
  - Single command and control server
  - Web shell payloads (3 versions)
    - .jsp, .asp, .aspx
  - Requests/Responses must be obfuscated or encrypted
    - SubShell is currently using base64
  - Web shell features
    - File browsing – (track current directory)
    - File Upload/Download
    - Command execution
    - HTTP POST Requests used for C2 traffic
    - Non-POST Requests render a valid 404 response