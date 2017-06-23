#coding=utf-8

import sys
import time
from Verification.ExamVerificationFun import *
from Verification.ReportVerificationFun import *

#试卷id
examId = 145361
examId = 200031

#获取试卷 exam_org 信息列表
examOrgList = getExamOrgList(examId)
if isinstance(examOrgList,list) is False or len(examOrgList) < 1:
    print "试卷exam_org信息错误"
    sys.exit()

#学校id
schoolId = examOrgList[0][1]

#年级id
gradeId = examOrgList[0][2]

#获取试卷的第一次成绩上传时间
produceTime = getExamPeoduceTimeAndSchoolId(examId)[0]
year = getExamPeoduceTimeAndSchoolId(examId)[1]

print "examId = " + str(examId) + " and schoolId = " + str(schoolId) + " and gradeId = " + str(gradeId) + " and year = " + str(year)

#获取试卷上传成绩列表
examResultList = getExamResultList(examId,schoolId)

#获取上传过成绩的学生ID列表
examResultStudentIdList = getExamResultStudentIdList(examResultList)

#获取上传过成绩的学生涉及到的班级ID列表
examResultClzssIdList = getExamResultClzssIdList(examResultList)

#非空判断
if isinstance(examResultClzssIdList,list) is False or len(examResultClzssIdList) < 1:
    print "试卷没有成绩 ：" + str(examId)
    sys.exit()


#验证exam_org 信息是否正确
flag = verExamOrg(examOrgList,examResultClzssIdList)
if flag is False:
    sys.exit()

#获取参加考试的所有学生的组织信息
studentInfoList = getStudentInfoByProduceTime(schoolId,gradeId,year,examResultClzssIdList,produceTime)

#获取试卷题目信息（exam_question）
examQuestionList = getExamInfo(examId)

#非空判断
if isinstance(examQuestionList,list) is False or len(examQuestionList) < 1:
    print "试卷没有题目信息，examId ：" + str(examId)
    sys.exit()

#获取作答题目列表
littleQuestionList = getLittleQuestionList(examQuestionList)

#判断试卷结构信息是否正确
questionDuct = verExamQuestion(examQuestionList,examId,littleQuestionList.keys())

status = questionDuct["status"]

questionTree = questionDuct["tree"]
# printQuestionTree(questionTree)

if status is False:
    print "试卷结构信息错误"
    sys.exit()



#获取题目知识点关联关系
examQuestionKnowledgeList = getExamQuestionKnowledgeList(examId)

#验证试卷所赋知识点是否正确
flag = verExamKnowledge(examQuestionKnowledgeList,questionTree)
if flag is False:
    print "知识点与题目关联关系有误"
    sys.exit()


print "试卷未发现已知问题"