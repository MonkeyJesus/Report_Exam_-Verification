#encoding=utf8

from DBConnection.ConnectionPool import *

#根据schoolId 与 分表策略算出 具体分表
def getTableNumBySchoolId(schoolId):
    return schoolId % 10 + 1

#获取参加考试的所有学生的组织信息
def getStudentInfoByProduceTime(schoolId,gradeId,year,clzssIdList,produceTime):
    accountConnection = accountPool.connection()
    cur = accountConnection.cursor()

    examResultTableNum = getTableNumBySchoolId(schoolId)
    SQL = "select ba.id,ba.name,bao.year, bao.clzssId " \
          "from b_account ba " \
          "left join b_account_org_%s bao on ba.id=bao.accountId " \
          "where " \
                "bao.schoolId = %d " \
                "AND bao.year = %d " \
                "AND bao.gradeId = %d " \
                "AND bao.accountType = 1 " \
                "AND ba.status != -1 " \
          "group by ba.id" % (examResultTableNum,schoolId,year,gradeId)

    # "'%s' >= bao.createTime " \
    # "and ('%s' < bao.deleteTime or bao.deleteTime is null) " \

    print SQL

    result = cur.execute(SQL)
    accountOrgData = cur.fetchmany(result)

    # print SQL

    returnList = []
    for accountOrg in accountOrgData:
        returnList.append([accountOrg[0], accountOrg[1], accountOrg[2], accountOrg[3]])

    cur.close()
    accountConnection.close()
    return returnList
