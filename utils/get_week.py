import datetime
def get_week():
    ''' 获得当前周次'''
    # 获取当前日期
    now = datetime.datetime.now()
    # 获取当前日期是该月的第几天
    day_of_month = now.day
    # 获取本月第一天是星期几（0 表示星期一，6 表示星期日）
    first_day_of_month = now.replace(day=1)
    first_weekday = first_day_of_month.weekday()
    # 计算本月第一个周一的日期
    if first_weekday == 0:
        first_monday = 1
    else:
        first_monday = 8 - first_weekday
    # 计算当前是本月的第几周
    if day_of_month < first_monday:
        week_of_month = 0
    else:
        week_of_month = (day_of_month - first_monday) // 7 + 1
    return f'{datetime.datetime.now().year}_{datetime.datetime.now().month}W{week_of_month}'