#encoding=utf8

from DBConnection.ConnectionPool import *
from Verification.AccountVerificationFun import *

#获取试卷上传成绩列表
def getExamResultList(examId,schoolId):
    reportConnection = reportPool.connection()
    cur = reportConnection.cursor()

    examResultTableNum = getTableNumBySchoolId(schoolId)
    SQL = "select examId,subjectBaseId,gradeBaseId,studentId,clzssId,examQuestionId from exam_result_" + str(examResultTableNum) + \
                    " where schoolId = %d and examId = %d and status != 5" % (schoolId,examId)

    result = cur.execute(SQL)
    examResultData = cur.fetchmany(result)

    # print SQL

    returnList = []
    for examResult in examResultData:
        returnList.append([examResult[0],examResult[1],examResult[2],examResult[3],examResult[4],examResult[5]])

    cur.close()
    reportConnection.close()
    return returnList

#获取上传过成绩的学生ID列表
def getExamResultStudentIdList(examResultList):
    returnList = []
    if examResultList == None or isinstance(examResultList,list) is False:
        return returnList

    for examResult in examResultList:
        returnList.append(examResult[3])

    return {}.fromkeys(returnList).keys()


#获取上传过成绩的学生涉及到的班级ID列表
def getExamResultClzssIdList(examResultList):
    returnList = []
    if examResultList == None or isinstance(examResultList, list) is False:
        return returnList

    for examResult in examResultList:
        returnList.append(examResult[4])

    return {}.fromkeys(returnList).keys()