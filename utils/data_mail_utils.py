import pandas as pd
from config import Config
import os
import shutil
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.header import Header
from config import MAIL_CONFIG
from datetime import datetime
from utils.get_week import get_week

def group_by_manager(df:pd.DataFrame,save_path:str,time:str): 
    '''根据推动人分组，并返回分组信息'''

    grouped=df.groupby("推动人")
    ans=""
    for name,group in grouped:
        ans=ans+f"{name}-{len(group)  }"
        # 如果指定了列顺序，则调整列的顺序
        column_order = [
            '漏洞名称', '威胁分值', 'CVEID', '分类-威胁', '分类-服务', '分类-系统', '分类-应用',
              '受影响主机', '受影响端口', '发现日期', '需要完成时间', '修复日期', '修复结果', '推动人',
                    '关联资产', '详细描述', '解决方案', '备注', '周次', '年份'
        ]
        # 创建一个新的DataFrame，包含指定的列，不存在的列用空值填充
        new_group = pd.DataFrame()
        for col in column_order:
            if col in group.columns:
                new_group[col] = group[col]
            else:
                new_group[col] = None  # 用None填充不存在的列
            # 按指定顺序重新排列列
        group = new_group

        group.to_excel(f"{save_path}{name}{time}.xlsx",index=False)
    return True

def getNameAndEmail(path):
    '''获得要发送邮件的安全员名单和邮箱'''
    
    nameEmailDf=pd.DataFrame(columns=["name","email"])
    files=os.listdir(path)
    for file in files:
        name=file.split(".")[0].split("2")[0]
        df=pd.read_excel(Config.PUSHER_PATH)
        dic=dict(zip(df["推动人"],df["邮箱"]))
        email=dic[name]
        nameEmailDf.loc[len(nameEmailDf)]=[name,email]
    return dict(zip(nameEmailDf["name"],nameEmailDf["email"]))

def __send_a_email(receiver,name,cc_email=None,attachment_paths=None):
    """
    发送电子邮件
    
    参数:
    sender (str): 发件人邮箱
    password (str): 邮箱密码
    receiver (str/list): 收件人邮箱（多个用列表）
    cc_email (str/list): 抄送邮箱（多个用列表）
    smtp_server (str): SMTP服务器地址
    smtp_port (int): SMTP服务器端口
    subject (str): 邮件主题
    content (str): 邮件正文内容
    attachment_path (str): 附件文件路径（可选）
    """
    # 邮箱配置
    sender = MAIL_CONFIG.SENDER       # 发件人邮箱
    password = MAIL_CONFIG.PASSWORD  # 邮箱密码，即内网密码
    smtp_server = MAIL_CONFIG.SMTP_SERVER
    smtp_port = MAIL_CONFIG.PORT

    # 邮件内容配置
    subject=MAIL_CONFIG.SUBJECT
    content=name+MAIL_CONFIG.CONTENT
    
    # 创建邮件对象
    msg = MIMEMultipart()
    msg['From'] = sender
    msg['To'] = ', '.join(receiver) if isinstance(receiver, list) else receiver
    
    # 添加抄送信息
    if cc_email:
        msg['Cc'] = ', '.join(cc_email) if isinstance(cc_email, list) else cc_email
        # 将抄送地址添加到实际接收者列表中
        if isinstance(receiver, list):
            all_receivers = receiver.copy()
        else:
            all_receivers = [receiver]
        
        if isinstance(cc_email, list):
            all_receivers.extend(cc_email)
        else:
            all_receivers.append(cc_email)
    else:
        all_receivers = receiver if isinstance(receiver, list) else [receiver]

    msg['Subject'] = Header(subject, 'utf-8')

    # 添加文本内容
    text_part = MIMEText(content, 'plain', 'utf-8')
    msg.attach(text_part)

    # 添加附件（如果存在）
    if attachment_paths:
        if isinstance(attachment_paths, str):  # 如果传入的是单个路径字符串，转为列表
            attachment_paths = [attachment_paths]
            
        for attachment_path in attachment_paths:
            try:
                with open(attachment_path, 'rb') as f:
                    attach_part = MIMEApplication(f.read())
                    attach_part.add_header(
                        'Content-Disposition',
                        'attachment',
                        filename=Header(os.path.basename(attachment_path), 'utf-8').encode()
                    )
                    msg.attach(attach_part)
            except Exception as e:
                print(f"添加附件 {attachment_path} 失败: {str(e)}")
                continue  # 跳过当前附件，继续处理其他附件

    try:
        # 连接SMTP服务器（SSL加密）
        server = smtplib.SMTP(smtp_server, smtp_port)
        # server.set_debuglevel(1)  # 开启调试模式
        
        # 登录邮箱
        server.login(sender, password)
        
        # 发送邮件
        server.sendmail(sender, all_receivers, msg.as_string())
        print(f"发送邮件至{name}成功！")
        
    except Exception as e:
        print(f"邮件发送失败: {str(e)}")
    finally:
        server.quit()

def zip_files(folder_path, output_zip_path):
    """
    将指定文件夹下的所有文件打包成zip文件。
    """
    import zipfile
    with zipfile.ZipFile(output_zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                zipf.write(file_path, os.path.relpath(file_path, folder_path))
    return output_zip_path

def send_mails(df:pd.DataFrame):
    '''批量发送邮件'''
    path=Config.TMP_MAIL_PATH+"/"
    time=get_week()
    try:
        shutil.rmtree(path)
    except:
        pass
    os.makedirs(path)
    ans=group_by_manager(df,path,time)
    nameEmail=getNameAndEmail(path)

    # 假设Config中添加了ADMIN_EMAIL属性
    admin_email = MAIL_CONFIG.ADMIN_EMAIL

    zipPath=Config.LOG_PATH+"/"+time
    # 修复：确保zipPath目录存在
    if not os.path.exists(zipPath):
        os.makedirs(zipPath)
        
    zipfile=zip_files(path,path+time+".zip")  # 修改：压缩path目录而不是zipPath
    
    for name,email in nameEmail.items():
        try:
            attachments=[path+name+time+".xlsx",zipfile]
            __send_a_email(email,name,admin_email,attachments)
        except Exception as e:
            print(f"发送给{name}的邮件失败: {str(e)}")
    return ans
