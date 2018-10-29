import psycopg2
from connection import connection
from pandas_datareader import data, wb
import pandas_datareader.data as web
import datetime

def makeRow(symbol, f, date_list):
    ret = []
    for date in date_list:
        row = [symbol, date]
        row.append(float(f.loc[date,"Open"]))
        row.append(float(f.loc[date,"High"]))
        row.append(float(f.loc[date,"Low"]))
        row.append(float(f.loc[date,"Close"]))
        row.append(int(f.loc[date,"Volume"]))
        ret.append(row)
    return ret

def init_table(db, c, tableName, sequenceName):
    """
    @params
    db              database connection object
    c               database cursor
    tableName       string        name of table to initialize
    sequenceName    string        name of sequence to initialize

    This function creates a new table on the provided db with
    the eod format as shown
    """
    print("[LOG] creating table {}".format(tableName))

    # First try and make the sequence that will be used for primary key
    try:
        print("[LOG] Creating sequence {}".format(sequenceName))
        c.execute("create sequence {} start 1 increment 1;".format(sequenceName))
        db.commit()
    except Exception as e:
        print(e)
        db.rollback()

    # Next we try and create our table
    try:
        c.execute("Create table {} (    \
            primary_key     serial PRIMARY KEY,\
            symbol          varchar(7), \
            date            date,       \
            open            float(4),   \
            high            float(4),   \
            low             float(4),   \
            close           float(4),   \
            volume          int \
            );".format(tableName))
        db.commit()
    except Exception as e:
        print(e)
        db.rollback()



if __name__ == "__main__":

    start = datetime.datetime(2017,1,1)
    #watchlist1 = set(["AAPL", 'AMD', 'AMZN', 'ATVI', 'BABA', 'BAC', 'BLK', 'CELG', 'CRM', 'F', 'FB','GOOG','IBM','INTC','JPM','KORS','LMT','LULU','MOMO','MSFT','MU','NFLX','NKE','NVDA','PCLN','PFE','RTN','SBUX','SHOP','SNAP','SPY','SQ','TAP','TSLA','ULTA','V','VOO','VOOG','VXX'])
    watchlist = set(['AAPL', 'NFLX', 'BABA'])
    #watchlist = watchlist1 | watchlist2
    curr = 1
    tot = len(watchlist)
    biglist = []

    for symbol in watchlist:
        connected = False
        i = 1
        while not connected and i < 4:
            try:
                f = web.DataReader(symbol.lower(), 'yahoo', start)
                print("connected ",symbol,'\t\t(',curr,' of ',tot,')')
                curr += 1
                connected = True
            except Exception as e:

                print("couldn't connect to data for: ",symbol, ' (Attempt number ', i,')',sep='')
                i += 1
                continue

        l = []
        for index in f.index:
            l.append(index.strftime('%Y-%m-%d'))

        attempts_sql = 1
        insql = False
        while not insql and attempts_sql < 4:
            try:
                results = makeRow(symbol, f, l)
                biglist.extend(results)
                #print(results)
                insql = True
            except Exception as e:
                #print("couldn't add ", symbol, ' to mysql (Attempt number ',attempts_sql,')',sep='')
                attempts_sql += 1
                continue


    # Postgres

    tableName = "eod_tmp1"
    sequenceName = "quote_id"

    # db is connection c is cursor
    db, c = connection()

    try:
        print("[LOG] Dropping table {}").format(tableName)
        c.execute("drop table {};".format(tableName))
        db.commit()
    except Exception as e:
        print(e)
        db.rollback()

    try:
        print("[LOG] Dropping sequence {}".format(sequenceName))
        c.execute("drop sequence {};".format(sequenceName))
        db.commit()
    except Exception as e:
        print(e)
        db.rollback()


    try:
        init_table(db, c, tableName, sequenceName)
    except Exception as e:
        print(e)
        db.rollback()

    for row in biglist:
        #print(row)
        try:
            c.execute("INSERT into {} (primary_key, symbol, date, open, high, low, close, volume) values (nextVal('{}'), '{}', to_date('{}','YYYY-MM-DD'), {}, {}, {}, {}, {});"\
            .format(tableName, sequenceName,row[0],row[1],row[2],row[3],row[4],row[5], row[6]))
            db.commit()
        except Exception as e:
            print(e)
            db.rollback()
    db.close()







    #
