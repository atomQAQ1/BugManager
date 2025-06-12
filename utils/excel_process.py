import pandas as pd
import datetime
from utils.mongodb_connect import read_mongodb_to_dataframe
from config import Config

def match_rows(sum_sheet:pd.DataFrame,row:pd.DataFrame,columns_to_compare:list):
    mathing_rows=sum_sheet[(sum_sheet[columns_to_compare]==row[columns_to_compare]).all(axis=1)]

    return mathing_rows

def get_repair_msg(matching_rows:pd.DataFrame):
    '''获得过去修复情况'''
    repari_result=' '.join(matching_rows['修复结果'].astype(str).tolist())
    if "未启用" in repari_result:
        return "未启用该模块"
    elif "限源" in repari_result:
        return "限源"
    return ""
    
#对漏洞表中每一项进行处理
def get_recorded_msg(sum_sheet:pd.DataFrame,bugs:pd.DataFrame):
    for index,row in bugs.iterrows():
        #查找漏洞是否在总表中出现过
        matching_rows=match_rows(sum_sheet,row,["漏洞名称","受影响主机","受影响端口"])
        if matching_rows.empty:
            pass
        else:
            # 备注出现时间和修复信息
            occured_time=''.join(matching_rows["年份"].astype(str)+matching_rows["周次"].astype(str)+"\n")
            bugs.loc[index,"备注"]=get_repair_msg(matching_rows)+'\n'+occured_time
    return bugs

def get_monday_of_week():
    '''获得当前周的周一日期'''
    current_date = datetime.datetime.now().date()
    monday_date=current_date-datetime.timedelta(days=current_date.weekday())
    return monday_date


def get_week_of_month():
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
    return week_of_month

def get_finish_time(df:pd.DataFrame):
    '''根据资产等级完成时间'''
    df["需要完成时间"]=df["关联资产"].apply(lambda x:0 if "一级" in x else 2 if "二级" in x else 4 if "三级" in x else ValueError("资产等级错误"))
    df["需要完成时间"]=df["发现日期"]+pd.to_timedelta(df["需要完成时间"],"D")
    return df

def get_pusher(df:pd.DataFrame):
    #TODO
    pusher_df=pd.read_excel(Config.PUSHER_PATH)
    pusher_mapping=dict(zip(pusher_df["区域"],pusher_df["推动人"]))
    for index,row in df.iterrows():
        df.loc[index,"推动人"]=pusher_mapping["其他"]
        for each in pusher_mapping.keys():
            if each in row["关联资产"]:
                df.loc[index,"推动人"]=pusher_mapping[each]
                break
    return df
def add_columns(df:pd.DataFrame):
    try:
        df.insert(12,"发现日期",get_monday_of_week())
    except:
        print("填写发现日期失败！")
    df.insert(13,"需要完成时间",None)
    df.insert(14,"修复日期",None)
    df.insert(15,"修复结果",None)
    df.insert(16,"推动人",None)

    try:
        df=get_finish_time(df)
    except:
        print("填写需要完成时间失败！")
    try:
        df=get_pusher(df)
    except:
        print("填写推动人失败！")

    try:
        sum_table=read_mongodb_to_dataframe()
        df["备注"]=None
        df=get_recorded_msg(sum_table,df)
        df["周次"]=f'{datetime.datetime.now().month}W{get_week_of_month()}'
        df["年份"]=datetime.datetime.now().year
        df["数量"]=None
        df["超期天数(2025年开始统计)"]=None
    except:
        print("填写周次、年份失败！")

    return  df