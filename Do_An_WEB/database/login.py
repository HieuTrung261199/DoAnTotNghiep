import sqlite3

class Login:
    def __init__(self,path):
        self.connection = None
        self.cursor = None
        self.path = path

    def connect(self):
        self.connection = sqlite3.connect(self.path)
        self.cursor = self.connection.cursor()

    def disconnect(self):
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
    def check_information(self,username,password,email):
        self.connect()
        self.cursor.execute("SELECT username,password,email FROM login")
        login = self.cursor.fetchall()
        for row in login:
            user_n , pass_w , e = row
            if user_n == username:
                self.disconnect()
                return True
            elif pass_w == password:
                self.disconnect()
                return True
        self.disconnect()
        return False

    def insert_information(self,username,password,email):
        check_login = self.check_information(username,password,email)
        if check_login == True:
            print(" tài khoản đã tồn tại ")
            return False
        else:
            many_data = (None,username,password,email)
            self.connect()
            try:
                self.cursor.execute("INSERT INTO login VALUES (?,?,?,?)",many_data)
                self.connection.commit()
                self.disconnect()
                print("tạo tk thành công")
                return True
            except:
                return False
        
    def select_information(self,username,password):
        self.connect()
        self.cursor.execute("""
                SELECT username,password FROM login
            """)
        inf = self.cursor.fetchall()
        print(inf)
        for row in inf:
            user_n ,pass_w = row
            if user_n == username and pass_w == password:
                print("đăng nhập thành công")
                return True
        return False
    
if __name__ == "__main__":
    path = 'database/QLSV.db'
    login = LoginMapper(path)
    usename = 'thuan'
    password = '123abcadasd'
    email = 'thuandinhltt9a7@gmail.com'
    a = login.select_information(usename,password)
