#coding=utf-8

import pandas
from DBConnection.ConnectionPool import *


#获取试卷 exam_org 信息列表
def getExamOrgList(examId):

    returnList = []

    examConnection = examPool.connection()
    cur = examConnection.cursor()

    SQL = "select examId,schoolId,gradeId,gradeBaseId,subjectId,subjectBaseId,clzssId from exam_org where examId = %d" % (examId)

    result = cur.execute(SQL)
    dataInfo = cur.fetchmany(result)

    for eo in dataInfo:
        returnList.append([eo[0],eo[1],eo[2],eo[3],eo[4],eo[5],eo[6]])

    cur.close()
    examConnection.close()

    return returnList

#获取试卷的第一次成绩上传时间
def getExamPeoduceTimeAndSchoolId(examId):
    examConnection = examPool.connection()
    cur = examConnection.cursor()

    SQL = "select produceTime,year from exam where id = %d" % (examId)

    result = cur.execute(SQL)
    dataInfo = cur.fetchone()

    returnList = []
    returnList.append(dataInfo[0])
    returnList.append(dataInfo[1])
    return returnList

#获取试卷组织结构信息
def getExamInfo(examId):
    examConnection = examPool.connection()
    cur = examConnection.cursor()

    SQL = "select schoolId,id,rootId,parentId,ifRelated,questionTitle,paperId,hasContent from exam_question where examId = %d" % (examId)
    # print SQL
    result = cur.execute(SQL)
    dataInfo = cur.fetchmany(result)

    returnList = []
    if isinstance(dataInfo,tuple) is False or len(dataInfo) < 1:
        print "试卷 examId:" + str(examId) + " 没有题目信息"
    else:
        for question in dataInfo:
            returnList.append(list(question))
    cur.close()
    examConnection.close()
    # print returnList
    return returnList

#获取题目知识点关联关系
def getExamQuestionKnowledgeList(examId):
    examConnection = examPool.connection()
    cur = examConnection.cursor()

    SQL = "select jkKnowId,examQuestionId from exam_question_knowledge where examId = %d" % (examId)

    result = cur.execute(SQL)
    dataInfo = cur.fetchmany(result)

    returnList = []
    if len(dataInfo) > 0:
        for ekInfo in dataInfo:
            returnList.append(list(ekInfo))

    cur.close()
    examConnection.close()
    return returnList

#获取作答题目列表
def getLittleQuestionList(examQuestionList):
    returnDict = {}
    for question in examQuestionList:
        if question[6] is not None:
            returnDict[question[1]] = question
    return returnDict


#根据小题递归获取关联题题的大题
#schoolId,id,rootId,parentId,ifRelated,questionTitle,paperId,hasContent
def getLeadQuestionListRecursive(question,allExamQuestionLst,returnList,removeRepeat):
    if question[4] == 0 and question[1] not in removeRepeat:
        qdict = {}
        qdict["question"] = question
        returnList.append(qdict)
        removeRepeat.append(question[1])
    else:
        parentId = question[3]
        for eq in allExamQuestionLst:
            if eq[1] == parentId:
                getLeadQuestionListRecursive(eq,allExamQuestionLst,returnList,removeRepeat)
                break

#根据小题获取关联题题的大题
def getLeadQuestionList(allExamQuestionLst):
    returnList = []
    for question in allExamQuestionLst:
        if question[7] == 1:
            qdict = {}
            qdict["question"] = question
            returnList.append(qdict)
    return returnList

#组装题目数
def getQuestionTree(parentList,allQuestions,flag,littleQuestionDict):
    for parent in parentList:
        # if (int)(parent["question"][4]) + (int)(parent["question"][7]) < 1:
        #     print "错误examQuestionId：" + str(parent["question"][1])
        #     flag[0] = False
        if parent.has_key("children"):
            getQuestionTree(parent["children"],allQuestions)
        else:
            children = []
            for nodeQuestion in allQuestions:
                nodeNum = 0
                if parent["question"][1] == nodeQuestion[3]:
                    nodeNum += 1
                    qdict = {}
                    qdict["question"] = nodeQuestion
                    children.append(qdict)

            if len(children) > 0:
                getQuestionTree(children,allQuestions,flag,littleQuestionDict)
                parent["children"] = children
            else:
                littleQuestionDict[parent["question"][1]] = 1


#验证试卷结构信息是否正确（参数 exam_question 表信息）
def verExamQuestion(examQuestionInfoList,examId,littleQuestionList):

    #小题字典
    littleQuestionDict = {}
    for littleId in littleQuestionList:
        littleQuestionDict[littleId] = 0

    returnDict = {}
    flag = [True]
    #非空判断
    if isinstance(examQuestionInfoList,list) is False or len(examQuestionInfoList) < 1:
        print "试卷 examId:" + str(examId) + " 没有题目信息"
        return False

    questionDict = {}

    removeRepeat = []
    #获取关联题题的大题
    # rootQuestionList = getLeadQuestionList(examQuestionInfoList)
    rootQuestionList = []
    for eqId in littleQuestionList:
        for eq in examQuestionInfoList:
            if eq[1] == eqId:
                getLeadQuestionListRecursive(eq,examQuestionInfoList,rootQuestionList,removeRepeat)
                break

    #获取题目树
    getQuestionTree(rootQuestionList,examQuestionInfoList,flag,littleQuestionDict)

    if flag[0]:
        for k in littleQuestionDict.keys():
            if littleQuestionDict[k] == 0:
                print str(k) + "题目有问题"
                flag[0] = False
                break

    #验证是否少题目
    if flag[0]:
        idList = []
        for eq in examQuestionInfoList:
            idList.append(eq[1])
        relatedIds = []
        for eq in examQuestionInfoList:
            if eq[3]:
                relatedIds.append(eq[3])
        relatedIds = {}.fromkeys(relatedIds).keys()

        for id in relatedIds:
            if id not in idList:
                print str(id) + " 缺失"
                flag[0] = False
                break

    returnDict["tree"] = rootQuestionList
    returnDict["status"] = flag[0]
    return returnDict

#递归判断关联题的所有题是否都关联了知识点
def verRelatedQuestionIfAllHasKnowledge(knowId,parent,allExamQuestionIds,flag):
    if flag[0] is False:
        return flag
    examQuestion = parent["question"]
    eqId = examQuestion[1]
    if eqId in allExamQuestionIds:
        if parent.has_key("children"):
            parentList = parent["children"]
            for node in parentList:
                verRelatedQuestionIfAllHasKnowledge(knowId,node,allExamQuestionIds,flag)
    else:
        flag[0] = False
        flag.append(knowId)
        flag.append(eqId)
        return flag
    return flag

#验证试卷所赋知识点是否正确
def verExamKnowledge(examQuestionKnowledgeList,examQuestionTree):
    if isinstance(examQuestionKnowledgeList,list) is False or len(examQuestionKnowledgeList) < 1:
        print "该试卷没有被赋予知识点"
        return True

    knowIdDict = {}
    for eqk in examQuestionKnowledgeList:
        if knowIdDict.has_key(eqk[0]) is False:
            knowIdDict[eqk[0]] = []
        knowIdDict[eqk[0]].append(eqk[1])

    flag = [True]
    for knowId in knowIdDict.keys():
        allEqIdList = knowIdDict[knowId]
        for parent in examQuestionTree:
            if parent["question"][1] in allEqIdList:
                flag = verRelatedQuestionIfAllHasKnowledge(knowId,parent,allEqIdList,flag)
                if flag[0] is False:
                    print "知识点：" + str(flag[1]) + " 与题目：" + str(flag[2]) + " 没有关联上"
                    return False
    return True

#验证exam_org 信息是否正确
def verExamOrg(examOrgList,examResultClzssIdList):
    if isinstance(examOrgList,list) is False or len(examOrgList) < 1:
        print "exam_org 信息有问题"
        return False
    if isinstance(examResultClzssIdList,list) is False or len(examResultClzssIdList) < 1:
        print "exam_result 班级信息有问题"
        return False

    #验证上传的成绩信息中的班级都已经发布
    examOrgClzssIdLis = []
    for examOrg in examOrgList:
        examOrgClzssIdLis.append(examOrg[6])
    examOrgClzssIdLis = {}.fromkeys(examOrgClzssIdLis).keys()

    for examResultClzssId in examResultClzssIdList:
        if examResultClzssId not in examOrgClzssIdLis:
            print "上传的成绩中包含未发布的班级：" + str(examResultClzssId)
            return False

    return True



#打印出题目树的结构图
#schoolId,id,rootId,parentId,ifRelated,questionTitle,paperId,hasContent
def printQuestionTree(rootQuestionList):
    for question in rootQuestionList:
        print str(question["question"][5])
        if question.has_key("children"):
            printQuestionTree(question["children"])

