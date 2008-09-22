#!/usr/bin/python

import poplib, email, re, sys;

__author__="imyousuf"
__date__ ="$Sep 20, 2008 9:18:28 AM$"

class ReferenceNode :
    def __init__(self, node, emailMessage, references=list(), children=dict(), slotted=bool("false")):
        self.node = node
        self.children = dict(children)
        self.references = references[:]
        self.slotted = slotted
        self.emailMessage = emailMessage
    def get_node(self):
        return self.node
    def get_children(self):
        return self.children
    def set_node(self, node):
        self.node = node
    def set_children(self, children):
        self.children = children
    def get_references(self):
        return self.references
    def is_slotted(self):
        return self.slotted
    def set_slotted(self, slotted):
        self.slotted = slotted
    def get_message(self):
        return self.emailMessage
    def __repr__(self):
        return self.node + "\nREF: " + str(self.references) + "\nChildren: " + str(self.children.keys()) + "\n"

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
        myPop3 = None
        if self.ssl_required :
            myPop3 = poplib.POP3_SSL(EmailConfig.get_hostname(self), EmailConfig.get_port(self))
        else :
            myPop3 = poplib.POP3(EmailConfig.get_pop_server(self), EmailConfig.get_port(self))
        myPop3.user(EmailConfig.get_username(self))
        myPop3.pass_(EmailConfig.get_password(self))
        return myPop3

def handleNode(currentNodeInAction, referenceNodeNow, referencesToCheck, patchMessageReferenceNode):
    for reference in referencesToCheck[:] :
        if reference in referenceNodeNow.get_children() :
            referencesToCheck.remove(reference)
            return patchMessageReferenceNode[reference]
    if len(referencesToCheck) == 0 :
        referenceNodeNow.get_children()[currentNodeInAction.get_node()] = currentNodeInAction
            

def makeChildren(patchMessageReferenceNode) :
    ref_keys = patchMessageReferenceNode.keys()
    ref_keys.sort()
    for messageId in ref_keys:
        referenceNode = patchMessageReferenceNode[messageId]
        print "Managing Message Id:", referenceNode.get_node()
        referenceIds = referenceNode.get_references()
        referenceIdsClone = referenceIds[:]
        print "Cloned References: ", referenceIdsClone
        if len(referenceIds) > 0 :
            nextNode = patchMessageReferenceNode[referenceIdsClone[0]]
            referenceIdsClone.remove(referenceIdsClone[0])
            while nextNode != None :
                print "Next Node: ", nextNode.get_node()
                print "Curent Node: ", referenceNode.get_node()
                print "REF: ", referenceIdsClone
                nextNode = handleNode(referenceNode, nextNode, referenceIdsClone, patchMessageReferenceNode)

def getText(nodelist):
    rc = ""
    for node in nodelist:
        if node.nodeType == node.TEXT_NODE:
            rc = rc + node.data
    return rc

def initializePopConfig() :
    from xml.dom.minidom import parse
    dom = parse("./email-configuration.xml")
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

if __name__ == "__main__":
    print "Checking POP3 for gmail"
    try:
        emailConfig = initializePopConfig()
        myPop = emailConfig.get_pop3_connection()
        numMessages = len(myPop.list()[1])
        patchMessages = dict()
        for i in range(numMessages):
            print "Index: ", i
            totalContent = ""
            for content in myPop.retr(i+1)[1]:
                totalContent += content + '\n'
            msg = email.message_from_string(totalContent)
            if 'subject' in msg :
                subject = msg['subject']
                subjectPattern = "^\[.*PATCH.*\].+"
                subjectMatch = re.match(subjectPattern, subject)
                print "Checking subject: ", subject
                if subjectMatch == None :
                    continue
            else :
                continue
            messageId = ""
            if 'message-id' in msg:
                messageId = re.search("<(.*)>", msg['message-id']).group(1)
                print 'Message-ID:', messageId
            referenceIds = []
            if 'references' in msg:
                references = msg['references']
                referenceIds = re.findall("<(.*)>", references)
            print "References: ", referenceIds
            currentNode = ReferenceNode(messageId, msg, referenceIds)
            patchMessages[messageId] = currentNode
            currentNode.set_slotted(bool("false"))
        print "**************Make Children**************"
        makeChildren(patchMessages)
        print "--------------RESULT--------------"
        print patchMessages
    except:
        print "Error: ", sys.exc_info()

