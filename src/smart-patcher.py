#!/usr/bin/python

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

import poplib, email, re, sys, xmlConfigs, utils;

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
        utils.verboseOutput(verbose, "Managing Message Id:", referenceNode.get_node())
        referenceIds = referenceNode.get_references()
        referenceIdsClone = referenceIds[:]
        utils.verboseOutput(verbose, "Cloned References: ", referenceIdsClone)
        if len(referenceIds) > 0 :
            nextNode = patchMessageReferenceNode[referenceIdsClone[0]]
            referenceIdsClone.remove(referenceIdsClone[0])
            while nextNode != None :
                utils.verboseOutput(verbose, "Next Node: ", nextNode.get_node())
                utils.verboseOutput(verbose, "Curent Node: ", referenceNode.get_node())
                utils.verboseOutput(verbose, "REF: ", referenceIdsClone)
                nextNode = handleNode(referenceNode, nextNode, referenceIdsClone, patchMessageReferenceNode)

if __name__ == "__main__":
    arguments = sys.argv
    verbose = "false"
    pseudoArgs = arguments[:]
    while len(pseudoArgs) > 1 :
        argument = pseudoArgs[1]
        if argument == "-v" or argument == "--verbose" :
            verbose = "true"
        pseudoArgs.remove(argument)
    utils.verboseOutput(verbose, "Checking POP3 for gmail")
    try:
        emailConfig = xmlConfigs.initializePopConfig("./email-configuration.xml")
        myPop = emailConfig.get_pop3_connection()
        numMessages = len(myPop.list()[1])
        patchMessages = dict()
        for i in range(numMessages):
            utils.verboseOutput(verbose, "Index: ", i)
            totalContent = ""
            for content in myPop.retr(i+1)[1]:
                totalContent += content + '\n'
            msg = email.message_from_string(totalContent)
            if 'subject' in msg :
                subject = msg['subject']
                subjectPattern = "^\[.*PATCH.*\].+"
                subjectMatch = re.match(subjectPattern, subject)
                utils.verboseOutput(verbose, "Checking subject: ", subject)
                if subjectMatch == None :
                    continue
            else :
                continue
            messageId = ""
            if 'message-id' in msg:
                messageId = re.search("<(.*)>", msg['message-id']).group(1)
                utils.verboseOutput(verbose, 'Message-ID:', messageId)
            referenceIds = []
            if 'references' in msg:
                references = msg['references']
                referenceIds = re.findall("<(.*)>", references)
            utils.verboseOutput(verbose, "References: ", referenceIds)
            currentNode = ReferenceNode(messageId, msg, referenceIds)
            patchMessages[messageId] = currentNode
            currentNode.set_slotted(bool("false"))
        utils.verboseOutput(verbose, "**************Make Children**************")
        makeChildren(patchMessages)
        utils.verboseOutput(verbose, "--------------RESULT--------------")
        utils.verboseOutput(verbose, patchMessages)
    except:
        utils.verboseOutput(verbose, "Error: ", sys.exc_info())

