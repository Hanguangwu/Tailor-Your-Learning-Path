import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv
import random
import string

# 加载环境变量
load_dotenv()

def generate_verification_code(length=6):
    """生成随机验证码"""
    return ''.join(random.choices(string.digits, k=length))

def send_email_via_gmail(to_email, subject, html_content):
    """使用 Gmail SMTP 服务器发送邮件"""
    # Gmail SMTP 配置
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    # 从环境变量获取 Gmail 账号和应用专用密码
    gmail_user = os.getenv("GMAIL_USER")
    gmail_app_password = os.getenv("GMAIL_APP_PASSWORD")
    
    if not gmail_user or not gmail_app_password:
        print("Gmail 配置缺失，请在 .env 文件中设置 GMAIL_USER 和 GMAIL_APP_PASSWORD")
        return False
    
    # 创建邮件内容
    msg = MIMEMultipart()
    msg['From'] = f"CSDIY 学习平台 <{gmail_user}>"
    msg['To'] = to_email
    msg['Subject'] = subject
    
    # 添加 HTML 内容
    msg.attach(MIMEText(html_content, 'html'))
    
    try:
        # 连接到 SMTP 服务器
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.ehlo()  # 向邮件服务器标识自己
        server.starttls()  # 启用 TLS 加密
        server.ehlo()  # 重新标识
        
        # 登录
        server.login(gmail_user, gmail_app_password)
        
        # 发送邮件
        server.send_message(msg)
        
        # 关闭连接
        server.quit()
        
        print(f"邮件已成功发送到 {to_email}")
        return True
    except Exception as e:
        print(f"发送邮件失败: {e}")
        return False

def send_reset_password_email(to_email, code):
    """发送重置密码验证码邮件"""
    subject = "CSDIY 学习平台 - 密码重置验证码"
    html_content = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #e0e0e0; border-radius: 5px;">
      <h2 style="color: #4a4a4a; text-align: center; margin-bottom: 20px;">验证码</h2>
      <p style="color: #666; line-height: 1.6;">尊敬的用户：</p>
      <p style="color: #666; line-height: 1.6;">您好！您正在进行密码重置操作，请使用以下验证码完成操作：</p>
      <div style="background-color: #f5f5f5; padding: 15px; text-align: center; margin: 20px 0; border-radius: 4px;">
        <span style="font-size: 24px; font-weight: bold; color: #4285f4; letter-spacing: 5px;">{code}</span>
      </div>
      <p style="color: #666; line-height: 1.6;">此验证码有效期为 10 分钟，请勿将验证码泄露给他人。</p>
      <p style="color: #666; line-height: 1.6;">如果您没有进行相关操作，请忽略此邮件。</p>
      <p style="color: #666; line-height: 1.6; margin-top: 30px;">此致，</p>
      <p style="color: #666; line-height: 1.6;">CSDIY 团队</p>
    </div>
    """
    
    return send_email_via_gmail(to_email, subject, html_content)
