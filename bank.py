from flask import Flask,url_for,request,render_template,redirect,flash,render_template_string,Response
from datetime import datetime
import pyodbc

from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.backends.backend_svg import FigureCanvasSVG
import matplotlib.pyplot as plt

import io
import random

plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

# PC服务器参数设置
default_server = 'localhost'
default_database = 'bank'
default_username = 'sa'
default_password = 'qwaszx'

# 权限字典
permission = {}

class PYSQL:
	def __init__(self, server, database, username, password):
		self.server = server
		self.database = database
		self.username = username
		self.password = password

	def GetConnect(self):
		# 连接数据库返回游标
		if not self.database:
			raise NameError("database not found")
		self.conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=' + self.server + ';DATABASE=' + self.database + ';UID='+ self.username + ';PWD=' + self.password + ';CHARSET=GBK')
		# 获得游标
		cur = self.conn.cursor()
		if not cur:
			raise NameError("fail to connect database")
		else:
			return cur

	def ExecQuery(self,sql):
		# 执行sql查询语句并返回查询结果
		cur = self.GetConnect()
		cur.execute(sql)
		# 返回查询结果
		resList = cur.fetchall()
		self.conn.close()
		return resList

	def ExecNonQuery(self,sql):
		# 执行查询语句不返回查询结果
		cur = self.GetConnect()
		cur.execute(sql)
		self.conn.commit()
		self.conn.close()

# 初始化app对象
app = Flask(__name__)

# 根据ID查找用户信息
def search_info_from_ID(ID):
	A='''
	select * from Userinfo
	where ID='{ID}'
	'''.format(ID=ID)
	result=DB.ExecQuery(A)
	return result[0]


# 用户登录
@app.route('/',methods=['POST','GET'])
def login():
	if request.method == 'GET':
		return render_template('Login.html',message="")
	if request.method =='POST':
		if 'Login' in request.form.keys():
			ID=request.form['ID']
			password=request.form['password']
			if ID=='' or password=='':
				message=""
			else:
				A='''
				select * from Userinfo
				where ID='{ID}' and password='{password}'
				'''.format(ID=ID,password=password)
				result=DB.ExecQuery(A)
				if len(result)!=0:
					A='''
					select account from Userinfo
					where ID='{ID}' and password='{password}'
					'''.format(ID=ID,password=password)
					permission[str(ID)]=1
					return redirect(url_for('Index',ID=str(ID)))
				A='''
				select * from Userinfo
				where ID='{ID}'
				'''.format(ID=ID)
				result=DB.ExecQuery(A)
				if len(result)==0:
					message="错误:用户名不存在"
				else:
					message="错误:密码错误"		
			return render_template('Login.html',message=message)
		if 'Register' in request.form.keys():
			return redirect(url_for('Register'))				

# 用户注册
@app.route('/Register', methods=['POST', 'GET'])
def Register():
	if request.method =='GET':
		return render_template('Register.html')
	if request.method =='POST':
		if 'confirmed' in request.form.keys():
			message=""
			ID = request.form['ID']
			username = request.form['username']
			telephone = request.form['telephone']
			birth = request.form['birth']
			email = request.form['email']
			password1 = request.form['password1']
			password2 = request.form['password2']
			gender = request.form['gender']
			postcode = request.form['postcode']
			address = request.form['address']
			account = request.form['account']
			if ID=="" or username=="" or birth=="" or email=="" or password1=="" or password2=="" or gender=="" or postcode=="" or address=="" or account=="":
				message="错误: 用户信息不完整"
				return render_template('Register.html',message=message)
			A='''
			select * from Userinfo
			where ID='{ID}'
			'''.format(ID = ID)
			result=DB.ExecQuery(A)
			if len(result)!=0:
				message='错误: 用户已存在'
			if password1!=password2:
				message='错误: 两次输入密码不一致'
			if message=="":
				A='''
				insert
				into
				Userinfo
				values('{uid}','{ubirth}','{uname}','{utele}','{uemail}','{ugender}','{upostcode}','{uaddress}','{upwd}')
				'''.format(uid=ID,ubirth = birth,uname=username,utele=telephone,uemail=email,ugender=gender,upostcode=postcode,uaddress=address,upwd=password1)
				DB.ExecNonQuery(A)
				return redirect(url_for('login'))
			else:
				return render_template('Register.html',message=message)			

# 主菜单
@app.route('/<ID>/Index',methods=['POST', 'GET'])
def Index(ID):
	if ID not in permission.keys():
		permission[ID]=0
	if permission[ID]==0:
		return "请先登录再进行此操作"
	if request.method =='GET':
		return render_template('Index.html')
	if request.method =='POST':
		if 'Info' in request.form.keys():
			message=""
			A='''
			select ID,birth,username,telephone,email,gender,postcode,address,password
			from Userinfo
			where ID='{ID}' 
			'''.format(ID=ID)
			if message=="":
				cursor = DB.GetConnect()
				s = "<table style='border:1px solid red'>"
				s = s + "<tr><td>用户ID</td><td>生日</td><td>用户名</td><td>电话</td><td>邮箱</td><td>性别</td><td>邮编</td><td>居住地址</td><td>当前用户密码</td></tr>"				
				with cursor.execute(A):
					row = cursor.fetchone()
					while row:
						s = s + "<tr>"
						s = s + "<td>" + str(row[0]) + "</td>"
						print(str(row[0]))
						s = s + "<td>" + str(row[1]) + "</td>" 
						print(str(row[1]))
						s = s + "<td>" + row[2].encode('gbk').decode('gbk') + "</td>" 
						print(row[2].encode('gbk').decode('gbk'))
						s = s + "<td>" + str(row[3]) + "</td>" 
						print(str(row[3]))
						s = s + "<td>" + str(row[4]) + "</td>" 
						print(str(row[4]))
						s = s + "<td>" + str(row[5]) + "</td>" 
						print(str(row[5]))
						s = s + "<td>" + str(row[6]) + "</td>" 
						print(str(row[6]))
						s = s + "<td>" + str(row[7]) + "</td>" 
						print(str(row[7]))
						s = s + "<td>" + str(row[8]) + "</td>" 
						print(str(row[8]))																							
						row = cursor.fetchone()
						s = s +  "</tr>"
				s = s + "</table>"
				s = "<html><body>" + s +"</body></html>"
				return render_template_string(s)		
		if 'MA' in request.form.keys():
			return redirect(url_for('my_account',ID=ID))
		if 'exit' in request.form.keys():
			permission[ID]=0
			return redirect(url_for('login'))

# 账户菜单
@app.route('/<ID>/my_account',methods=['POST', 'GET'])
def my_account(ID):
	if ID not in permission.keys():
		permission[ID]=0
	if permission[ID]==0:
		return "请先登录再进行此操作"
	if request.method =='GET':
		return render_template('my_account.html')
	if request.method =='POST':
		if 'new_account' in request.form.keys():
			return redirect(url_for('new_account',ID=ID))	
		if 'login_account' in request.form.keys():
			return redirect(url_for('login_account',ID=ID))
		if 'delete_account' in request.form.keys():
			return redirect(url_for('delete_account',ID=ID))		
		if 'back' in request.form.keys():
			return redirect(url_for('Index',ID=ID))

# 开户
@app.route('/<ID>/new_account', methods=['POST', 'GET'])
def new_account(ID):
	if ID not in permission.keys():
		permission[ID]=0
	if permission[ID]==0:
		return "请先登录再进行此操作"
	if request.method =='GET':
		return render_template('new_account.html')
	if request.method =='POST':
		if 'submit' in request.form.keys():
			message=""
			account=request.form['account']
			if account=="":
				message="错误：请输入账号"
				return render_template('new_account.html',message=message)
			A='''
			select * from Account
			where account='{account}'
			'''.format(ID=ID,account=account)
			result=DB.ExecQuery(A)
			if len(result)!=0:
				message='错误：账号已经存在'
				return render_template('new_account.html',message=message)
			if message=="":
				A='''
				insert
				into
				Account
				values('{account}','0','False','{ID}')
				'''.format(account=account,ID=ID)
				DB.ExecNonQuery(A)
				B='''
				insert
				into
				Trade_History(ID,summary,my_account,sb_account,card_type,operation,money,pre_balance,post_balance,card_num)
				values('{ID}','用户开通账户','{account}',' ',' ','开户','0','0','0',' ')
				'''.format(ID=ID,account=account)
				DB.ExecNonQuery(B)
				return redirect(url_for('my_account',ID=ID))
		if 'back' in request.form.keys():
				return redirect(url_for('my_account',ID=ID))

# 销户
@app.route('/<ID>/delete_account', methods=['POST', 'GET'])
def delete_account(ID):
	if ID not in permission.keys():
		permission[ID]=0
	if permission[ID]==0:
		return "请先登录再进行此操作"
	if request.method =='GET':
		return render_template('delete_account.html')
	if request.method =='POST':
		if 'submit' in request.form.keys():
			message=""
			account=request.form['account']
			if account=="":
				message="错误：请输入账号"
				return render_template('delete_account.html',message=message)
			A='''
			select * from Account
			where account='{account}'
			'''.format(ID=ID,account=account)
			result=DB.ExecQuery(A)
			if len(result)==0:
				message='错误：账号不存在'
				return render_template('delete_account.html',message=message)
			if message=="":
				A='''
				update Account
				set logoff='True'
				where account='{account}' and ID='{ID}'
				'''.format(account=account,ID=ID)
				DB.ExecNonQuery(A)
				B='''
				delete
				from
				Account_Card
				where account='{account}'
				'''.format(account=account)
				DB.ExecNonQuery(B)
				C='''
				insert
				into
				Trade_History(ID,summary,my_account,sb_account,card_type,operation,money,pre_balance,post_balance,card_num)
				values('{ID}','用户注销账户','{account}',' ',' ','销户',' ',' ',' ',' ')				
				'''.format(ID=ID,account=account)
				DB.ExecNonQuery(C)
				return redirect(url_for('my_account',ID=ID))
		if 'back' in request.form.keys():
				return redirect(url_for('my_account',ID=ID))

# 登录账户
@app.route('/<ID>/login_account', methods=['POST', 'GET'])
def login_account(ID):
	if ID not in permission.keys():
		permission[ID]=0
	if permission[ID]==0:
		return "请先登录再进行此操作"
	if request.method =='GET':
		return render_template('login_account.html')
	if request.method =='POST':	
		if 'submit' in request.form.keys():
			message=""
			account=request.form['account']
			if account=="":
				message="错误：请输入登录账号"
				return render_template('login_account.html',message=message)
			A='''
			select * from Account
			where ID='{ID}' and account='{account}' and logoff='False'
			'''.format(ID=ID,account=account)
			result=DB.ExecQuery(A)
			if len(result)==0:
				message='错误：账户不存在'
				return redirect(url_for('my_account',ID=ID, message=message))
			if message=="":
				return redirect(url_for('account_center',ID=ID,account=account))
		if 'back' in request.form.keys():
			return redirect(url_for('my_account',ID=ID))
				

# 账户中心
@app.route('/<ID>/<account>/account_center',methods=['POST','GET'])
def account_center(ID,account):
	if ID not in permission.keys():
		permission[ID]=0
	if permission[ID]==0:
		return "You don't have permission,try to log in"
	if request.method =='GET':
		return render_template('account_center.html',ID=ID,account=account)
	if request.method =='POST':		
		if 'Info' in request.form.keys():
			message=""
			A='''
			select Account.account,Account_Card.card_num,Account_Card.card_type,Account_Card.balance 
			from Account
			inner join Account_Card
			ON Account.account = Account_Card.account 
			where Account.ID='{ID}' and Account.account='{account}' and logoff = 'False'
			'''.format(ID=ID,account=account)
			result=DB.ExecQuery(A)
			if len(result)==0:
				message='Account hasn\'t been bound'
				return render_template('account_center.html',ID=ID,account=account)
			if message=="":
				cursor = DB.GetConnect()
				s = "<table style='border:1px solid red'>"
				s = s + "<tr><td>账号</td><td>储蓄卡卡号</td><td>储蓄卡类型</td><td>储蓄卡余额</td></tr>"
				t = """<h3>账户当前余额</h3>
				<img src="/balance_bar/{{ID}}/{{account}}.png"
				alt="balance bar as png"
				height="700"
				>"""				
				with cursor.execute(A):
					row = cursor.fetchone()
					while row:
						s = s + "<tr>"
						s = s + "<td>" + str(row[0]) + "</td>"
						print(str(row[0]))
						s = s + "<td>" + str(row[1]) + "</td>" 
						print(str(row[1]))
						s = s + "<td>" + row[2].encode('gbk').decode('gbk') + "</td>" 
						print(row[2].encode('gbk').decode('gbk'))
						s = s + "<td>" + str(row[3]) + "</td>" 
						print(str(row[3]))						
						row = cursor.fetchone()
						s = s +  "</tr>"
				s = s + "</table>"
				s = "<html><body>" + s + t +"</body></html>"
				return render_template_string(s,ID=ID,account=account)
			
		if 'Bind' in request.form.keys():
			return redirect(url_for('Bind',ID=ID,account=account))
		# 一次性绑定/解绑两张卡
		if 'Bind2' in request.form.keys():
			return redirect(url_for('Bind2',ID=ID,account=account))
		if 'Deposit' in request.form.keys():
			return redirect(url_for('Deposit',ID=ID,account=account))
		if 'Withdraw' in request.form.keys():
			return redirect(url_for('Withdraw',ID=ID,account=account))
		if 'Transfer' in request.form.keys():
			return redirect(url_for('Transfer',ID=ID,account=account))
		if 'History' in request.form.keys():
			message=""
			A='''
			select * from Trade_History
			where ID ='{ID}' and my_account='{account}'
			order by OrderDate
			'''.format(ID=ID,account=account)
			result=DB.ExecQuery(A)
			if len(result)==0:
				message='Account hasn\'t been bound'
				return render_template('account_center.html',ID=ID,account=account)
			if message=="":
				cursor = DB.GetConnect()
				s = "<table style='border:1px solid red'>"
				s = s + "<tr><td>用户</td><td>摘要</td><td>我的账号</td><td>他人的账号</td><td>储蓄卡类型</td><td>操作</td><td>金额</td><td>交易前余额</td><td>交易后余额</td><td>卡号</td><td>操作时间</td></tr>"
				t = """<h3>账户余额变化</h3>
				<img src="/balance_variation/{{ID}}/{{account}}.png"
				alt="balance broken as png"
				height="700"
				>"""
				with cursor.execute(A):
					row = cursor.fetchone()
					while row:
						s = s + "<tr>"
						s = s + "<td>" + str(row[0]) + "</td>"
						print(str(row[0]))
						s = s + "<td>" + row[1].encode('gbk').decode('gbk') + "</td>" 
						print(row[1].encode('gbk').decode('gbk'))
						s = s + "<td>" + str(row[2]) + "</td>" 
						print(str(row[2]))
						s = s + "<td>" + str(row[3]) + "</td>" 
						print(str(row[3]))						
						s = s + "<td>" + row[4].encode('gbk').decode('gbk') + "</td>" 
						print(row[4].encode('gbk').decode('gbk'))
						s = s + "<td>" + row[5].encode('gbk').decode('gbk') + "</td>" 
						print(row[5].encode('gbk').decode('gbk'))	
						s = s + "<td>" + str(row[6]) + "</td>" 
						print(str(row[6]))
						s = s + "<td>" + str(row[7]) + "</td>" 
						print(str(row[7]))
						s = s + "<td>" + str(row[8]) + "</td>" 
						print(str(row[8]))
						s = s + "<td>" + str(row[9]) + "</td>" 
						print(str(row[9]))
						s = s + "<td>" + (str(row[10]))[:19] + "</td>" 
						print((str(row[10]))[:19])
						row = cursor.fetchone()																																		
						s = s +  "</tr>"
				s = s + "</table>"
				s = "<html><body>" + s + t +"</body></html>"
				return render_template_string(s,ID=ID,account=account)
		if 'Interest' in request.form.keys():
			return redirect(url_for('Interest',ID=ID,account=account))
		if 'exit' in request.form.keys():
			return redirect(url_for('login_account',ID=ID))


# 显示当前账户余额
@app.route("/balance_bar/<int:ID>/<int:account>.png")
def bar_plot_png(ID,account):
	fig = Figure()
	axis = fig.add_subplot(1, 1, 1)
	axis.set_ylabel('金额')
	A='''
	select Account_Card.balance
	from Account
	inner join Account_Card
	ON Account.account = Account_Card.account 
	where Account.ID='{ID}' and Account.account='{account}' and logoff = 'False'
	'''.format(ID=ID,account=account)
	result=DB.ExecQuery(A)

	B='''
	select *
	from Account
	inner join Account_Card
	ON Account.account = Account_Card.account 
	where Account.ID='{ID}' and Account.account='{account}' and logoff = 'False' and Account_Card.card_type = '主卡'
	'''.format(ID=ID,account=account)
	prime=DB.ExecQuery(B)

	C='''
	select *
	from Account
	inner join Account_Card
	ON Account.account = Account_Card.account 
	where Account.ID='{ID}' and Account.account='{account}' and logoff = 'False' and Account_Card.card_type = '副卡'
	'''.format(ID=ID,account=account)
	vice=DB.ExecQuery(C)	

	if len(result)==0:
		names=['主卡','副卡']
		values=[0, 0]
		axis.bar(names,values)
		output = io.BytesIO()
		FigureCanvasAgg(fig).print_png(output)
		return Response(output.getvalue(), mimetype="image/png")

	if len(result)==1 and len(prime)==1:
		names=['主卡']
		values=[float(result[0][0])]
		axis.bar(names,values)
		output = io.BytesIO()
		FigureCanvasAgg(fig).print_png(output)
		return Response(output.getvalue(), mimetype="image/png")

	if len(result)==1 and len(vice)==1: 		
		names=['副卡']
		values=[float(result[1][0])]
		axis.bar(names,values)
		output = io.BytesIO()
		FigureCanvasAgg(fig).print_png(output)
		return Response(output.getvalue(), mimetype="image/png")
	
	
	names=['主卡','副卡']
	values=[float(result[0][0]),float(result[1][0])]
	axis.bar(names,values)
	output = io.BytesIO()
	FigureCanvasAgg(fig).print_png(output)
	return Response(output.getvalue(), mimetype="image/png")
			

# 显示账户余额变化
@app.route("/balance_variation/<int:ID>/<int:account>.png")
def variation_plot_png(ID,account):
	fig = Figure()
	axis1 = fig.add_subplot(1, 2, 1)
	axis2 = fig.add_subplot(1, 2, 2)
	axis1.set_title('主卡')
	axis2.set_title('副卡')
	axis1.set_ylabel('金额')
	names1=[]
	values1=[]
	A='''
	select post_balance,OrderDate from Trade_History
	where ID ='{ID}' and my_account='{account}' and card_type = '主卡'
	'''.format(ID=ID,account=account)
	result1=DB.ExecQuery(A)
	for _ in range(len(result1)):
		names1.append((str(result1[_][1]))[:19])
		values1.append(float(result1[_][0]))

	for tick in axis1.get_xticklabels():  # 将横坐标倾斜30度，纵坐标可用相同方法
		tick.set_rotation(15)
	axis1.plot(names1,values1,'go--')

	names2=[]
	values2=[]
	B='''
	select post_balance,OrderDate from Trade_History
	where ID ='{ID}' and my_account='{account}' and card_type = '副卡'
	'''.format(ID=ID,account=account)
	result2=DB.ExecQuery(B)	
	for _ in range(len(result2)):
		names2.append((str(result2[_][1]))[:19])
		values2.append(float(result2[_][0]))

	for tick in axis2.get_xticklabels():  # 将横坐标倾斜30度，纵坐标可用相同方法
		tick.set_rotation(15)
	axis2.plot(names2,values2,'go--')

	output = io.BytesIO()
	FigureCanvasAgg(fig).print_png(output)
	return Response(output.getvalue(), mimetype="image/png")	



# 绑定/解绑银行卡 
@app.route('/<ID>/<account>/Bind',methods=['POST','GET'])
def Bind(ID,account):
	if ID not in permission.keys():
		permission[ID]=0
	if permission[ID]==0:
		return "You don't have permission,try to log in"
	if request.method == 'GET':
		return render_template('Bind.html',ID=ID,account=account)
	if request.method =='POST':
		if 'bind' in request.form.keys():
			message=""
			card_num=request.form['cardnum']
			card_type=request.form['cardtype']
			if card_num == "" or card_type == "":
				message="Error:Unfilled blanks"
				return render_template('Bind.html',ID=ID,account=account,message=message)
			A='''
			select * from Account_Card
			where card_num='{card_num}' and card_type='{card_type}' 
			'''.format(card_num=card_num,card_type=card_type)
			result=DB.ExecQuery(A)
			if len(result)!=0:
				message='Error: Card Has Been Bound'
				return render_template('Bind.html',ID=ID,account=account,message=message)
			B='''
			select count(*) from Account_Card
			where account='{account}' and card_num='{card_num}' and card_type='{card_type}'
			'''.format(account=account,card_num=card_num,card_type=card_type)
			result=DB.ExecQuery(B)
			if int(result[0][0])!=0:
				message='Error: Card of this type Has Been Bound'
				return render_template('Bind.html',ID=ID,account=account,message=message)
			if message=="":
				A='''
				insert
				into
				Account_Card
				values('{account}','{card_num}','{card_type}','0')
				'''.format(account=account,card_num=card_num,card_type=card_type)
				DB.ExecNonQuery(A)
				B='''
				insert
				into
				Trade_History(ID,summary,my_account,sb_account,card_type,operation,money,pre_balance,post_balance,card_num)
				values('{ID}','用户建立账户绑定银行卡','{account}',' ','{card_type}','绑定储蓄卡','0','0','0','{card_num}')
				'''.format(ID=ID,account=account,card_type=card_type,card_num=card_num)
				DB.ExecNonQuery(B)
				return redirect(url_for('Bind',ID=ID,account=account,message=message))
		if 'unbind' in request.form.keys():
			message=""
			card_num=request.form['cardnum']
			card_type=request.form['cardtype']
			if card_num == "" or card_type == "":
				message="Error:Unfilled blanks"
				return render_template('Bind.html',ID=ID,account=account,message=message)
			A='''
			select * from Account_Card
			where account='{account}' and card_num='{card_num}' and card_type='{card_type}'
			'''.format(account=account,card_num=card_num,card_type=card_type)
			result=DB.ExecQuery(A)
			if len(result)==0:
				message='Error: Card Has\'t Been Bound'
				return render_template('Bind.html',ID=ID,account=account,message=message)
			if message=="":
				A='''
				delete
				from
				Account_Card
				where account ='{account}'
				and card_num ='{card_num}'
				and card_type ='{card_type}'
				'''.format(account=account,card_num=card_num,card_type=card_type)
				DB.ExecNonQuery(A)
				B='''
				insert
				into
				Trade_History(ID,summary,my_account,sb_account,card_type,operation,money,pre_balance,post_balance,card_num)
				values('{ID}','用户账户取消绑定银行卡','{account}',' ','{card_type}','解绑储蓄卡','0','0','0','{card_num}')
				'''.format(ID=ID,account=account,card_type=card_type,card_num=card_num)
				DB.ExecNonQuery(B)
				return redirect(url_for('account_center',ID=ID,account=account,message=message))
		if 'back' in request.form.keys():
			return redirect(url_for('account_center',ID=ID,account=account))

# 绑定/解绑两张银行卡
@app.route('/<ID>/<account>/Bind2',methods=['POST','GET'])
def Bind2(ID,account):
	if ID not in permission.keys():
		permission[ID]=0
	if permission[ID]==0:
		return "You don't have permission,try to log in"
	if request.method == 'GET':
		return render_template('Bind2.html',ID=ID,account=account)
	if request.method =='POST':
		if 'bind' in request.form.keys():
			message=""
			card_num1=request.form['cardnum1']
			card_num2=request.form['cardnum2']
			if card_num1 == "" and card_num2 == "":
				message="Error:Unfilled blanks"
				return render_template('Bind2.html',ID=ID,account=account,message=message)
			if card_num2 == "":
				# 仅填写了主卡信息
				A='''
				select * from Account_Card
				where card_num='{card_num1}' and card_type='主卡' 
				'''.format(card_num1=card_num1)
				result=DB.ExecQuery(A)
				if len(result)!=0:
					message='Error: Card as Prime card Has Been Bound'
					return render_template('Bind2.html',ID=ID,account=account,message=message)
				B='''
				select count(*) from Account_Card
				where account='{account}' and card_num='{card_num1}' and card_type='主卡'
				'''.format(account=account,card_num1=card_num1)	
				result=DB.ExecQuery(B)
				if int(result[0][0])!=0:
					message='Error: Card as Prime card Has Been Bound'
					return render_template('Bind2.html',ID=ID,account=account,message=message)
				if message=="":
					C='''
					insert
					into
					Account_Card
					values('{account}','{card_num1}','主卡','0')
					'''.format(account=account,card_num1=card_num1)
					DB.ExecNonQuery(C)
					D='''
					insert
					into
					Trade_History(ID,summary,my_account,sb_account,card_type,operation,money,pre_balance,post_balance,card_num)
					values('{ID}','用户建立账户绑定银行卡','{account}',' ','主卡','绑定储蓄卡','0','0','0','{card_num1}')
					'''.format(ID=ID,account=account,card_num1=card_num1)
					DB.ExecNonQuery(D)
					return redirect(url_for('Bind2',ID=ID,account=account,message=message))				
			elif card_num1 == "":
				# 仅填写了副卡信息
				A='''
				select * from Account_Card
				where card_num='{card_num2}' and card_type='副卡' 
				'''.format(card_num2=card_num2)
				result=DB.ExecQuery(A)
				if len(result)!=0:
					message='Error: Card as Vice card Has Been Bound'
					return render_template('Bind2.html',ID=ID,account=account,message=message)
				B='''
				select count(*) from Account_Card
				where account='{account}' and card_num='{card_num2}' and card_type='副卡'
				'''.format(account=account,card_num2=card_num2)	
				result=DB.ExecQuery(B)
				if int(result[0][0])!=0:
					message='Error: Card as Vice card Has Been Bound'
					return render_template('Bind2.html',ID=ID,account=account,message=message)
				if message=="":
					C='''
					insert
					into
					Account_Card
					values('{account}','{card_num2}','副卡','0')
					'''.format(account=account,card_num2=card_num2)
					DB.ExecNonQuery(C)
					D='''
					insert
					into
					Trade_History(ID,summary,my_account,sb_account,card_type,operation,money,pre_balance,post_balance,card_num)
					values('{ID}','用户建立账户绑定银行卡','{account}',' ','副卡','绑定储蓄卡','0','0','0','{card_num2}')
					'''.format(ID=ID,account=account,card_num2=card_num2)
					DB.ExecNonQuery(D)
					return redirect(url_for('Bind2',ID=ID,account=account,message=message))	
			else:
				# 填写了主卡副卡信息
				# 检查主卡
				A1='''
				select * from Account_Card
				where card_num='{card_num1}' and card_type='主卡' 
				'''.format(card_num1=card_num1)
				result=DB.ExecQuery(A1)
				if len(result)!=0:
					message='Error: Card as Prime card Has Been Bound'
					return render_template('Bind2.html',ID=ID,account=account,message=message)
				B1='''
				select count(*) from Account_Card
				where account='{account}' and card_num='{card_num1}' and card_type='主卡'
				'''.format(account=account,card_num1=card_num1)	
				result=DB.ExecQuery(B1)
				if int(result[0][0])!=0:
					message='Error: Card as Prime card Has Been Bound'
					return render_template('Bind2.html',ID=ID,account=account,message=message)
				if message=="":
					C1='''
					insert
					into
					Account_Card
					values('{account}','{card_num1}','主卡','0')
					'''.format(account=account,card_num1=card_num1)
					DB.ExecNonQuery(C1)
					D1='''
					insert
					into
					Trade_History(ID,summary,my_account,sb_account,card_type,operation,money,pre_balance,post_balance,card_num)
					values('{ID}','用户建立账户绑定银行卡','{account}',' ','主卡','绑定储蓄卡','0','0','0','{card_num1}')
					'''.format(ID=ID,account=account,card_num1=card_num1)
					DB.ExecNonQuery(D1)
				# 检查副卡
				A2='''
				select * from Account_Card
				where card_num='{card_num2}' and card_type='副卡' 
				'''.format(card_num2=card_num2)
				result=DB.ExecQuery(A2)
				if len(result)!=0:
					message='Error: Card as Vice card Has Been Bound'
					return render_template('Bind2.html',ID=ID,account=account,message=message)
				B2='''
				select count(*) from Account_Card
				where account='{account}' and card_num='{card_num2}' and card_type='副卡'
				'''.format(account=account,card_num2=card_num2)	
				result=DB.ExecQuery(B2)
				if int(result[0][0])!=0:
					message='Error: Card as Vice card Has Been Bound'
					return render_template('Bind2.html',ID=ID,account=account,message=message)
				if message=="":
					C2='''
					insert
					into
					Account_Card
					values('{account}','{card_num2}','副卡','0')
					'''.format(account=account,card_num2=card_num2)
					DB.ExecNonQuery(C2)
					D2='''
					insert
					into
					Trade_History(ID,summary,my_account,sb_account,card_type,operation,money,pre_balance,post_balance,card_num)
					values('{ID}','用户建立账户绑定银行卡','{account}',' ','副卡','绑定储蓄卡','0','0','0','{card_num2}')
					'''.format(ID=ID,account=account,card_num2=card_num2)
					DB.ExecNonQuery(D2)
					return redirect(url_for('Bind2',ID=ID,account=account,message=message))	
		
		if 'unbind' in request.form.keys():
			message=""
			card_num1=request.form['cardnum1']
			card_num2=request.form['cardnum2']
			if card_num1 == "" and card_num2 == "":
				message="Error:Unfilled blanks"
				return render_template('Bind2.html',ID=ID,account=account,message=message)
			if card_num2 == "":
				# 解绑主卡
				A='''
				select * from Account_Card
				where account='{account}' and card_num='{card_num1}' and card_type='主卡'
				'''.format(account=account,card_num1=card_num1)
				result=DB.ExecQuery(A)
				if len(result)==0:
					message='Error: Prime Card Has\'t Been Bound'
					return render_template('Bind2.html',ID=ID,account=account,message=message)
				if message=="":
					A='''
					delete
					from
					Account_Card
					where account ='{account}'
					and card_num ='{card_num1}'
					and card_type ='主卡'
					'''.format(account=account,card_num1=card_num1)
					DB.ExecNonQuery(A)
					B='''
					insert
					into
					Trade_History(ID,summary,my_account,sb_account,card_type,operation,money,pre_balance,post_balance,card_num)
					values('{ID}','用户账户取消绑定银行卡','{account}',' ','主卡','解绑储蓄卡','0','0','0','{card_num1}')
					'''.format(ID=ID,account=account,card_num1=card_num1)
					DB.ExecNonQuery(B)
				return redirect(url_for('account_center',ID=ID,account=account,message=message))
			elif card_num1 == "":
				# 解绑副卡
				A='''
				select * from Account_Card
				where account='{account}' and card_num='{card_num2}' and card_type='副卡'
				'''.format(account=account,card_num2=card_num2)
				result=DB.ExecQuery(A)
				if len(result)==0:
					message='Error: Vice Card Has\'t Been Bound'
					return render_template('Bind2.html',ID=ID,account=account,message=message)
				if message=="":
					A='''
					delete
					from
					Account_Card
					where account ='{account}'
					and card_num ='{card_num2}'
					and card_type ='副卡'
					'''.format(account=account,card_num2=card_num2)
					DB.ExecNonQuery(A)
					B='''
					insert
					into
					Trade_History(ID,summary,my_account,sb_account,card_type,operation,money,pre_balance,post_balance,card_num)
					values('{ID}','用户账户取消绑定银行卡','{account}',' ','副卡','解绑储蓄卡','0','0','0','{card_num2}')
					'''.format(ID=ID,account=account,card_num2=card_num2)
					DB.ExecNonQuery(B)
				return redirect(url_for('account_center',ID=ID,account=account,message=message))
			else:
				# 解绑主卡与副卡
				A1='''
				select * from Account_Card
				where account='{account}' and card_num='{card_num1}' and card_type='主卡'
				'''.format(account=account,card_num1=card_num1)
				result=DB.ExecQuery(A1)
				if len(result)==0:
					message='Error: Prime Card Has\'t Been Bound'
					return render_template('Bind2.html',ID=ID,account=account,message=message)
				if message=="":
					A1='''
					delete
					from
					Account_Card
					where account ='{account}'
					and card_num ='{card_num1}'
					and card_type ='主卡'
					'''.format(account=account,card_num1=card_num1)
					DB.ExecNonQuery(A1)
					B1='''
					insert
					into
					Trade_History(ID,summary,my_account,sb_account,card_type,operation,money,pre_balance,post_balance,card_num)
					values('{ID}','用户账户取消绑定银行卡','{account}',' ','主卡','解绑储蓄卡','0','0','0','{card_num1}')
					'''.format(ID=ID,account=account,card_num1=card_num1)
					DB.ExecNonQuery(B1)

				A2='''
				select * from Account_Card
				where account='{account}' and card_num='{card_num2}' and card_type='副卡'
				'''.format(account=account,card_num2=card_num2)
				result=DB.ExecQuery(A2)
				if len(result)==0:
					message='Error: Vice Card Has\'t Been Bound'
					return render_template('Bind2.html',ID=ID,account=account,message=message)
				if message=="":
					A2='''
					delete
					from
					Account_Card
					where account ='{account}'
					and card_num ='{card_num2}'
					and card_type ='副卡'
					'''.format(account=account,card_num2=card_num2)
					DB.ExecNonQuery(A2)
					B3='''
					insert
					into
					Trade_History(ID,summary,my_account,sb_account,card_type,operation,money,pre_balance,post_balance,card_num)
					values('{ID}','用户账户取消绑定银行卡','{account}',' ','副卡','解绑储蓄卡','0','0','0','{card_num2}')
					'''.format(ID=ID,account=account,card_num2=card_num2)
					DB.ExecNonQuery(B3)
			return redirect(url_for('account_center',ID=ID,account=account))					
		if 'back' in request.form.keys():
			return redirect(url_for('account_center',ID=ID,account=account))	


# 存钱
@app.route('/<ID>/<account>/Deposit',methods=['POST','GET'])
def Deposit(ID,account):
	if ID not in permission.keys():
		permission[ID]=0
	if permission[ID]==0:
		return "You don't have permission,try to log in"
	if request.method == 'GET':
		return render_template('Deposit.html',ID=ID,account=account)
	if request.method =='POST':	
		if 'submit' in request.form.keys():
			message=""
			card_num=request.form['cardnum']
			money=request.form['money']
			if card_num == "" or money == "":
				message="Error:Unfilled blanks"
				return render_template('Deposit.html',ID=ID,account=account,message=message)
			else:
				A='''
				select * from Account_Card
				where account='{account}' and card_num='{card_num}'
				'''.format(account=account,card_num=card_num)
				result=DB.ExecQuery(A)
				if len(result)==0:
					message="Error:This card hasn't been bound with an account"
					return render_template('Deposit.html',ID=ID,account=account,message=message)
				else:
					card_type=result[0][2]
					pre_balance=result[0][3]
					B='''
					update Account_Card
					set balance = balance + '{money}'
					where account = '{account}' and card_num = '{card_num}'
					'''.format(money=money,account=account,card_num=card_num)
					DB.ExecNonQuery(B)
					C='''
					select balance from Account_Card
					where account='{account}' and card_num='{card_num}'
					'''.format(account=account,card_num=card_num)
					result=DB.ExecQuery(C)
					post_balance=result[0][0]
					D='''
					insert 
					into
					Trade_History(ID,summary,my_account,sb_account,card_type,operation,money,pre_balance,post_balance,card_num)
					values('{ID}','用户账户存款','{account}',' ','{card_type}','存款','{money}','{pre_balance}','{post_balance}','{card_num}')
					'''.format(ID=ID,account=account,card_type=card_type,money=money,pre_balance=pre_balance,post_balance=post_balance,card_num=card_num)
					DB.ExecNonQuery(D)
					E='''
					update Account
					set Account.balance = (select sum(balance)
								   		  from Account_Card
								          where Account_Card.account = '{account}'
								          )
					where account = '{account}'
					'''.format(account=account)
					DB.ExecNonQuery(E)
					# 从第一笔存款开始计息
					F='''
					select * from Cal_Interest
					where account = '{account}'
					'''.format(account=account)
					result=DB.ExecQuery(F)
					if len(result)==0:
						G='''
						insert
						into
						Cal_Interest
						values('{account}','','','0')
						'''.format(account=account)
						DB.ExecNonQuery(G)
						H='''
						update Cal_Interest
						set cur_calc = GETDATE(),pre_calc = GETDATE()
						where account = '{account}'
						'''.format(account=account)
						DB.ExecNonQuery(H)
					else:
						# 计息函数
						calc_interest(account,pre_balance)
					return redirect(url_for('account_center',ID=ID,account=account,message=message))
		if 'back' in request.form.keys():
			return redirect(url_for('account_center',ID=ID,account=account))				

# 取钱
@app.route('/<ID>/<account>/Withdraw',methods=['POST','GET'])
def Withdraw(ID,account):
	if ID not in permission.keys():
		permission[ID]=0
	if permission[ID]==0:
		return "You don't have permission,try to log in"
	if request.method == 'GET':
		return render_template('Withdraw.html',ID=ID,account=account)
	if request.method =='POST':	
		if 'submit' in request.form.keys():
			message=""
			card_num=request.form['cardnum']
			money=request.form['money']
			if card_num == "" or money == "":
				message="Error:Unfilled blanks"
				return render_template('Withdraw.html',ID=ID,account=account,message=message)
			else:
				A='''
				select * from Account_Card
				where account='{account}' and card_num='{card_num}'
				'''.format(account=account,card_num=card_num)
				result=DB.ExecQuery(A)
				if len(result)==0:
					message="Error:This card hasn't been bound with an account"
					return render_template('Withdraw.html',ID=ID,account=account,message=message)
				else:
					B='''
					select * from Account_Card 
					where account='{account}' and card_num='{card_num}' and balance>'{money}'
					'''.format(account=account,card_num=card_num,money=money)
					result=DB.ExecQuery(B)
					if len(result)==0:
						message="Error:This card doesn't have enough money"
						return render_template('Withdraw.html',ID=ID,account=account,message=message)
					else:
						C='''
						select * from Account_Card
						where account='{account}' and card_num='{card_num}'
						'''.format(account=account,card_num=card_num)
						result=DB.ExecQuery(C)
						card_type=result[0][2]
						pre_balance=result[0][3]
						D='''
						update Account_Card
						set balance = balance - '{money}'
						where account = '{account}' and card_num = '{card_num}'
						'''.format(money=money,account=account,card_num=card_num)
						DB.ExecNonQuery(D)
						E='''
						select balance from Account_Card
						where account='{account}' and card_num='{card_num}'
						'''.format(account=account,card_num=card_num)
						result=DB.ExecQuery(E)
						post_balance=result[0][0]
						F='''
						insert 
						into
						Trade_History(ID,summary,my_account,sb_account,card_type,operation,money,pre_balance,post_balance,card_num)
						values('{ID}','用户账户取款','{account}',' ','{card_type}','取款','{money}','{pre_balance}','{post_balance}','{card_num}')
						'''.format(ID=ID,account=account,card_type=card_type,money=money,pre_balance=pre_balance,post_balance=post_balance,card_num=card_num)
						DB.ExecNonQuery(F)
						G='''
						update Account
						set Account.balance = (select sum(balance)
											from Account_Card
											where Account_Card.account = '{account}'
											)
						where account = '{account}'
						'''.format(account=account)
						DB.ExecNonQuery(G)
						# 计息函数
						calc_interest(account,pre_balance)
						return redirect(url_for('account_center',ID=ID,account=account,message=message))
		if 'back' in request.form.keys():
			return redirect(url_for('account_center',ID=ID,account=account))												

# 转账
@app.route('/<ID>/<account>/Transfer',methods=['POST','GET'])
def Transfer(ID,account):
	if ID not in permission.keys():
		permission[ID]=0
	if permission[ID]==0:
		return "You don't have permission,try to log in"
	if request.method == 'GET':
		return render_template('Transfer.html',ID=ID,account=account)
	if request.method =='POST':	
		if 'submit' in request.form.keys():
			message=""
			mycard_num=request.form['mycardnum']
			sbcard_num=request.form['sbcardnum']
			money=request.form['money']
			if mycard_num == "" or sbcard_num =="" or money == "":
				message="Error:Unfilled blanks"
				return render_template('Transfer.html',ID=ID,account=account,message=message)
			else:
				A='''
				select * from Account_Card
				where account='{account}' and card_num='{card_num}'
				'''.format(account=account,card_num=mycard_num)
				result=DB.ExecQuery(A)
				if len(result)==0:
					message="Error:Your card hasn't been bound with an account"
					return render_template('Transfer.html',ID=ID,account=account,message=message)
				B='''
				select Account_Card.account,Account.ID
				from Account_Card
				inner join Account
				on Account_Card.account = Account.account
				where card_num='{card_num}'
				'''.format(card_num=sbcard_num)
				result=DB.ExecQuery(B)
				if len(result)==0:
					message="Error:Another card hasn't been bound with an account"
					return render_template('Transfer.html',ID=ID,account=account,message=message)
				sb_account=result[0][0]
				sb_ID=result[0][1]
				C='''
				select * from Account_Card 
				where account='{account}' and card_num='{card_num}' and balance>'{money}'
				'''.format(account=account,card_num=mycard_num,money=money)
				result=DB.ExecQuery(C)
				if len(result)==0:
					message="Error:Your card doesn't have enough money"
					return render_template('Transfer.html',ID=ID,account=account,message=message)
				# 从本人卡上扣钱
				D='''
				select * from Account_Card
				where account='{account}' and card_num='{card_num}'
				'''.format(account=account,card_num=mycard_num)
				result=DB.ExecQuery(D)
				mycard_type=result[0][2]
				mypre_balance=result[0][3]
				E='''
				update Account_Card
				set balance = balance - '{money}'
				where account = '{account}' and card_num = '{card_num}'
				'''.format(money=money,account=account,card_num=mycard_num)
				DB.ExecNonQuery(E)
				F='''
				select balance from Account_Card
				where account='{account}' and card_num='{card_num}'
				'''.format(account=account,card_num=mycard_num)
				result=	DB.ExecQuery(F)
				mypost_balance=result[0][0]
				G='''
				insert 
				into
				Trade_History(ID,summary,my_account,sb_account,card_type,operation,money,pre_balance,post_balance,card_num)
				values('{ID}','用户向其他账户转账','{myaccount}','{sbaccount}','{card_type}','发起转账','{money}','{pre_balance}','{post_balance}','{card_num}')
				'''.format(ID=ID,myaccount=account,sbaccount=sb_account,card_type=mycard_type,money=money,pre_balance=mypre_balance,post_balance=mypost_balance,card_num=mycard_num)
				DB.ExecNonQuery(G)
				G1='''
				update Account
				set Account.balance = (select sum(balance)
							   		  from Account_Card
							          where Account_Card.account = '{account}'
							          )
				where account = '{account}'
				'''.format(account=account)
				DB.ExecNonQuery(G1)
				# 调用计息函数
				calc_interest(account,mypre_balance)

				# 收到转账
				H='''
				select * from Account_Card
				where account='{account}' and card_num='{card_num}'
				'''.format(account=sb_account,card_num=sbcard_num)
				result=DB.ExecQuery(H)
				sbcard_type=result[0][2]
				sbpre_balance=result[0][3]
				I='''
				update Account_Card
				set balance = balance + '{money}'
				where account = '{account}' and card_num = '{card_num}'
				'''.format(money=money,account=sb_account,card_num=sbcard_num)
				DB.ExecNonQuery(I)
				J='''
				select balance from Account_Card
				where account='{account}' and card_num='{card_num}'
				'''.format(account=sb_account,card_num=sbcard_num)
				result=DB.ExecQuery(J)
				sbpost_balance=result[0][0]
				K='''
				insert 
				into
				Trade_History(ID,summary,my_account,sb_account,card_type,operation,money,pre_balance,post_balance,card_num)
				values('{ID}','用户收到其他账户转账','{account}','{sbaccount}','{card_type}','收到转账','{money}','{pre_balance}','{post_balance}','{card_num}')
				'''.format(ID=sb_ID,account=sb_account,sbaccount=account,card_type=sbcard_type,money=money,pre_balance=sbpre_balance,post_balance=sbpost_balance,card_num=sbcard_num)				
				DB.ExecNonQuery(K)
				K1='''
				update Account
				set Account.balance = (select sum(balance)
							   		  from Account_Card
							          where Account_Card.account = '{account}'
							          )
				where account = '{account}'
				'''.format(account=sb_account)
				DB.ExecNonQuery(K1)
				# 调用计息函数
				calc_interest(sb_account,sbpre_balance)
				return redirect(url_for('account_center',ID=ID,account=account,message=message))
		if 'back' in request.form.keys():
			return redirect(url_for('account_center',ID=ID,account=account))


# 账户利息中心 
@app.route('/<ID>/<account>/Interest',methods=['POST','GET'])
def Interest(ID,account):
	if ID not in permission.keys():
		permission[ID]=0
	if permission[ID]==0:
		return "You don't have permission,try to log in"
	if request.method == 'GET':
		return render_template('Interest.html',ID=ID,account=account)
	if request.method =='POST':
		if 'history' in request.form.keys():
			message=""
			A='''
			select * from Cal_Interest
			where account = '{account}'
			'''.format(account=account)
			result=DB.ExecQuery(A)
			if len(result)==0:
				message='Account has no money'
				return render_template('Interest.html',ID=ID,account=account)
			if message=="":
				cursor = DB.GetConnect()
				s = "<table style='border:1px solid red'>"
				s = s + "<tr><td>账户</td><td>上次计息日期</td><td>本次计息日期</td><td>累积利息</td></tr>"
				with cursor.execute(A):
					row = cursor.fetchone()
					while row:
						s = s + "<tr>"
						s = s + "<td>" + str(row[0]) + "</td>"
						print(str(row[0]))
						s = s + "<td>" + str(row[1]) + "</td>" 
						print(str(row[1]))
						s = s + "<td>" + str(row[2]) + "</td>" 
						print(str(row[2]))
						s = s + "<td>" + str(row[3]) + "</td>" 
						print(str(row[3]))
						row = cursor.fetchone()
						s = s +  "</tr>"
				s = s + "</table>"
				s = "<html><body>" + s +"</body></html>"
				return render_template_string(s,ID=ID,account=account)
		if 'extract' in request.form.keys():
			message=""
			A='''
			select * from Cal_Interest
			where account = '{account}'
			'''.format(account=account)
			result=DB.ExecQuery(A)
			if len(result)==0:
				message='Account has no money'
				return render_template('account_center.html',ID=ID,account=account)
			if message=="":
				# 添加计息记录
				A='''
				select top 1 interest
				from Cal_Interest
				where account = '{account}'	
				order by cur_calc desc
				'''.format(account=account)
				result=DB.ExecQuery(A)
				interest=float(result[0][0])
				B='''
				insert
				into
				Cal_Interest
				values('{account}','','',NULL)
				'''.format(account=account)
				DB.ExecNonQuery(B)
				C='''
				update Cal_Interest
				set cur_calc = GETDATE(),pre_calc = (select max(cur_calc) 
													from Cal_Interest
													where account = '{account}' and interest is not null
													)
				where account = '{account}'
				'''.format(account=account)
				DB.ExecNonQuery(C)
				D='''
				update Cal_Interest
				set interest = '0'
				where account = '{account}' and interest is null
				'''.format(interest=interest,account=account)
				DB.ExecNonQuery(D)
				# 利息转入某卡中
				E='''
				select top 1 post_balance,card_num,card_type 
				from Trade_History
				where ID = '{ID}' and my_account = '{account}' and operation != '解绑储蓄卡'
				order by OrderDate desc
				'''.format(ID=ID,account=account)
				result=DB.ExecQuery(E)
				pre_balance = float(result[0][0])
				post_balance = pre_balance + interest
				card_num = int(result[0][1])
				card_type = str(result[0][2])
				F='''
				insert
				into 
				Trade_History(ID,summary,my_account,sb_account,card_type,operation,money,pre_balance,post_balance,card_num)
				values('{ID}','用户获得利息','{account}',' ','{card_type}','获得利息','{money}','{pre_balance}','{post_balance}','{card_num}')
				'''.format(ID=ID,account=account,card_type=card_type,money=interest,pre_balance=pre_balance,post_balance=post_balance,card_num=card_num)
				DB.ExecNonQuery(F)
				G='''
				update Account
				set Account.balance = (select sum(balance)
							   		  from Account_Card
							          where Account_Card.account = '{account}'
							          )
				where account = '{account}'
				'''.format(account=account)
				DB.ExecNonQuery(G)
				return redirect(url_for('account_center',ID=ID,account=account,message=message))


# 计息函数
def calc_interest(account,pre_balance):
	I='''
	insert
	into
	Cal_Interest
	values('{account}','','',NULL)
	'''.format(account=account)
	DB.ExecNonQuery(I)
	# 获取利率
	OP='''
	select top 1 interest 
	from Cal_Interest 
	where account = '{account}'
	order by cur_calc desc
	'''.format(account=account)
	result=DB.ExecQuery(OP)
	interest=float(result[0][0])
	J='''
	update Cal_Interest
	set cur_calc = GETDATE(),pre_calc = (select max(cur_calc) 
										from Cal_Interest
										where account = '{account}' and interest is not null
										)
	where account = '{account}'
	'''.format(account=account)
	DB.ExecNonQuery(J)
	K='''
	select datediff(day,pre_calc,cur_calc) as daydiff
    from Cal_Interest 
    where interest is null
	'''
	result=DB.ExecQuery(K)
	daydiff=int(result[0][0])
	interest += 0.015* daydiff /365 * float(pre_balance) 
	L='''
	update Cal_Interest
	set interest = '{interest}'
	where account = '{account}' and interest is null
	'''.format(interest=interest,account=account)
	DB.ExecNonQuery(L)



def init():
    global DB
    DB = PYSQL(default_server, default_database, default_username, default_password)

if __name__ == "__main__":
	init()
	app.run(debug=True, port=5000)
