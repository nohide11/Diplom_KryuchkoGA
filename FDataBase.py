class FDataBase:
    def __init__(self, db):
        self.__db = db
        self.__cur = db.cursor()

    def getGA(self, site_id=None):
        try:
            if site_id:
                self.__cur.execute("SELECT * FROM GA WHERE site_id = ?", (site_id,))
            else:
                self.__cur.execute("SELECT * FROM GA")
            return self.__cur.fetchall()
        except Exception as e:
            print("Ошибка getGA:", e)
            return []

    def getYM(self, site_id=None):
        try:
            if site_id:
                self.__cur.execute("SELECT * FROM YM WHERE site_id = ?", (site_id,))
            else:
                self.__cur.execute("SELECT * FROM YM")
            return self.__cur.fetchall()
        except Exception as e:
            print("Ошибка getYM:", e)
            return []

    def getERPBuyers(self):
        try:
            self.__cur.execute("SELECT * FROM ERP_buyer")
            return self.__cur.fetchall()
        except Exception as e:
            print("Ошибка getERPBuyers:", e)
            return []

    def getERPProducts(self):
        try:
            self.__cur.execute("SELECT * FROM ERP_products")
            return self.__cur.fetchall()
        except Exception as e:
            print("Ошибка getERPProducts:", e)
            return []
        
    def getFunctions(self):
        try:
            self.__cur.execute("SELECT * FROM function")
            return self.__cur.fetchall()
        except Exception as e:
            print("Ошибка чтения function:", e)
            return []

