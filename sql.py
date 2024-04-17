from pymysql import connect, cursors
import time


class SQL:
    def __init__(
        self, user: str, passwd: str, host: str, db: str, charset: str = "utf8"
    ) -> None:
        try:
            self.__conn = connect(
                user=user, passwd=passwd, host=host, db=db, charset=charset
            )
            self.__cursor = self.__conn.cursor(cursors.DictCursor)
        except Exception as e:
            print(f"SQL Error, {e}")
            raise e

    def set_sync_key(self, sync_key):
        """
        데이터를 갱신한후에 조회를 위해 필요한 sync_key값을 db에 업데이트 하기 위해 사용
        """
        query = f"UPDATE sync_key SET MONTH = '{sync_key}' WHERE pk = 0"
        try:
            self.__cursor.execute(query)
            result = self.__cursor.fetchall()
            time.sleep(0.1)
        except Exception as e:
            return
        finally:
            self.__conn.begin()

    def has_dup(self, data):
        """
         이미 DB에 같은 데이터가 존재하는지 확인하고 중복 여부 반환

         Args:
            data : DB에 넣으려고 시도하는 dict
        Return:
            중복값 존재시 True, 없을경우 False
        """
        query = "SELECT * FROM items WHERE *=*"

        for key, value in data.items():
            query += f" AND {key} = '{value}'"
        query += ";"
        try:
            self.__cursor.execute(self.__query)
            result = self.__cursor.fetchall()
        except Exception as e:
            print(f"{data} : {e}")
            return
        finally:
            self.__conn.begin()

        if len(result) > 0:
            return True
        else:
            return False

    def set_datas(self, datas, additional_datas={}, sync_key="2022:11"):
        """
        딕셔너리 리스트 형의 데이터를 일괄로 firebase에 set

        Args
        =======
            datas : db에 set 할 데이터들
            additional_datas : 기존 datas에 추가로 붙여 들어갈 데이터들 ex) 어느 편의점 데이터인지 gs,cu
            sync_key : 하위 collection의 부모가 될 document의 이름  sale - 2022:11 - items - gs25:대추
            set_coll : set할 collection 이름

        Return
        ======
            성공시...
        """
        query = (
            f"INSERT INTO items ( name, img, price, store, tag, sync_key ) VALUES ( "
        )

        for data in datas:
            data.update(additional_datas)

            if self.has_dup(data):
                continue

            one_query = (
                query
                + f"'{data['name']}', '{data['img']}', {data['price']}, '{data['store']}', '{data['tag']}', '{sync_key}' );"
            )
            try:
                self.__cursor.execute(one_query)
                result = self.__cursor.fetchall()
                time.sleep(0.1)
            except Exception as e:
                return
            finally:
                self.__conn.begin()

    def __del__(self):
        try:
            self.__conn.close()

        except Exception as e:
            print(f"sql Error!!! {e}")
            raise
