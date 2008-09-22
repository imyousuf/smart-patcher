# This programs is intended to manage patches and apply them automatically
# through email in an automated fashion.
#
# Copyright (C) 2008  Imran M Yousuf (imran@smartitengineering.com)
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

class EmailConfig :
    def __init__(self, email, hostname, username, password, sslRequired=bool("false"), port=-1):
        self.email = email
        self.hostname = hostname
        self.username = username
        self.password = password
        self.ssl_required = sslRequired
        self.port = port
    def get_email(self):
        return self.email
    def get_hostname(self):
        return self.hostname
    def get_username(self):
        return self.username
    def get_password(self):
        return self.password
    def is_ssl_required(self):
        return self.ssl_required
    def get_port(self):
        return self.port
        
class PopEmailConfig (EmailConfig) :
    def __init__(self, email, popServer, username, password, popSslRequired=bool("false"), port=-1):
        if port < 0 and popSslRequired == "true" :
            port = 995
        elif port < 0 and popSslRequired == "false" :
            port = 110
        EmailConfig.__init__(self, email, popServer, username, password, popSslRequired, port)

    def get_pop3_connection(self):
        import poplib
        myPop3 = None
        if self.ssl_required :
            myPop3 = poplib.POP3_SSL(EmailConfig.get_hostname(self), EmailConfig.get_port(self))
        else :
            myPop3 = poplib.POP3(EmailConfig.get_pop_server(self), EmailConfig.get_port(self))
        myPop3.user(EmailConfig.get_username(self))
        myPop3.pass_(EmailConfig.get_password(self))
        return myPop3

def getText(nodelist):
    rc = ""
    for node in nodelist:
        if node.nodeType == node.TEXT_NODE:
            rc = rc + node.data
    return rc

def initializePopConfig(xmlConfigFilePath) :
    from xml.dom.minidom import parse
    dom = parse(xmlConfigFilePath)
    popMailDom = dom.getElementsByTagName("pop-mail-config")[0]
    emailAddress = getText(popMailDom.getElementsByTagName("email")[0].childNodes)
    hostname = getText(popMailDom.getElementsByTagName("pop-server")[0].childNodes)
    username = getText(popMailDom.getElementsByTagName("username")[0].childNodes)
    passwordAsClearText = getText(popMailDom.getElementsByTagName("password")[0].childNodes)

    popPort = -1
    try:
        popPort = getText(popMailDom.getElementsByTagName("pop-port")[0].childNodes)
    except:
        pass
    
    sslRequiredFlag = "false"
    try :
      sslRequiredFlag = getText(popMailDom.getElementsByTagName("ssl")[0].childNodes)
    except:
        pass

    return PopEmailConfig(emailAddress, hostname, username, passwordAsClearText, sslRequiredFlag, popPort)

