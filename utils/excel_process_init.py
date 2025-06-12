import pandas as pd
from utils.excel_process import add_columns
from config import Config
'''本周漏洞初步处理'''
def is_in_white_list():
    '''
    判断漏洞警告对象是否在白名单内，
    分离成两个文件，非白名单和待人工判断
    其中待人工判断中的负责人信息在白名单中出现，但需要进一步确认是否是已报备的问题
    非白名单还需要删除DES报警等其他形式的白名单
    需要注意文件的编码方式必须为utf-8
    '''
    file_path=Config.DOWNLOADS_FOLDER+"/"+Config.WEEKLY_SCAN_RESULT_PATH
    white_list_path=Config.WHITELIST_PATH
    df=pd.read_excel(file_path)


    # 添加指定列，使数据可以直接添加到总表
    df=add_columns(df)
    df["负责人"]=df["关联资产"].str.extract(r'&([^&-]*)-')

    #分割白名单中信息和非白名单中信息
    white_list=open(white_list_path,mode="r",encoding='utf-8').read()
    is_substring = df['负责人'].apply(lambda x: x in white_list)
    df.drop(columns="负责人",inplace=True)# 删除负责人列
    wrong_msg=df[is_substring]
    right_msg=df[~is_substring]
    


    #分别存储
    wrong_msg.to_excel(Config.DOWNLOADS_FOLDER+"/疑似白名单.xlsx",index=False)
    right_msg.to_excel(Config.DOWNLOADS_FOLDER+"/非白名单.xlsx",index=False)
    print("处理完成！")

def __match_rows(sum_sheet:pd.DataFrame,row:pd.DataFrame,columns_to_compare:list):
    '''对某行数据在总表中进行匹配'''
    matching_rows=sum_sheet[(sum_sheet[columns_to_compare]==row[columns_to_compare].astype(str)).all(axis=1)]
    matching_rows=matching_rows.reset_index(drop=True)
    return matching_rows

def whether_not_use(comparing_df:pd.DataFrame,compared_df:pd.DataFrame,columns:list):
    '''根据修复结果判断某个模块是否存在未启用情况，并删除未启用的报漏'''
    new_df=pd.DataFrame()
    for index,row in comparing_df.iterrows():
        matching_rows=__match_rows(compared_df,row,columns)
        if matching_rows.empty:
            new_df=pd.concat([new_df,row.to_frame().T],ignore_index=True)
        else:
            for i,match_row in matching_rows.iterrows():
                repari_result=' '.join(matching_rows['修复结果'].astype(str).tolist())
                if '未启用' not in repari_result:
                    new_df=pd.concat([new_df,row.to_frame().T],ignore_index=True)
    return new_df

