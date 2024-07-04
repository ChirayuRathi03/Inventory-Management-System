import pyodbc
import pandas as pd

conn = ('Driver={SQL Server Native Client 11.0};'
        'Server=localhost;'
        'Database=dbms_project;'
        'Trusted_Connection=yes;')

connection = pyodbc.connect(conn)
cursor = connection.cursor()

print("What do you want to do?")
print("   1. Purchase a Product")
print("   2. Add Components")
print("   3. Remove Components")
print("   4. Check availability of Components")
print("   5. Get Manufacturer Details")
print("   6. View Orders")

t = int(input())

if t == 1:
    # print the products:
    prodlist = 'SELECT prod_name as PRODUCT, prod_price as PRICE FROM dbo.prods'
    prodtable = pd.read_sql(prodlist, connection)
    print(prodtable)

    # ask user which product they want to buy:
    print("Product you want to purchase?")
    prodpurch = input()
    prodpurch = prodpurch.lower()
    print("Product you want to purchase is:", prodpurch)

    # use sql query and find out the price of the product:
    prodprice = cursor.execute("""select prod_price from prods where prod_name = ?""", prodpurch)
    for row in cursor:
        prodprice = row
        break
    prodprice = int(prodprice[0])
    print("₹", prodprice, "per product")

    # ask user how many of it do they want:
    qnty = int(input("how many?  "))
    # find out the final amount
    totalamt = prodprice * qnty
    print("Total Amount  =  ₹", totalamt)

    # insert the order into the 'orderss' table:
    insertorder = """insert into dbo.orderss(product_name,product_qnty, totalamt) values(?,?,?)"""
    cursor.execute(insertorder, prodpurch, qnty, totalamt)
    orderlist = 'SELECT * FROM dbo.orderss'
    ordertable = pd.read_sql(orderlist, connection)

    sql = """select comp_details from dbo.prods where prod_name=?"""
    qntycomplist = cursor.execute(sql, prodpurch).fetchval()
    cid, qt = list(), list()
    c = list(map(str, qntycomplist.split(',')))
    print(c)
    for x in c:
        # print(x)
        y, z = list(map(str, x.split()))
        cid.append(y)
        qt.append(int(z))
    print(cid, qt)
    length = len(cid)
    print(length)
    if length == 1:
        sql1 = """select qty_avail from dbo.Inventory where comp_id=?"""
        totalqt = int(cursor.execute(sql1, cid[0]).fetchval())
        print(totalqt)
        reqdqt = qnty * qt[0]

        if reqdqt < totalqt:
            newqt = totalqt - reqdqt
            sql3 = """update dbo.inventory
                      set qty_avail=?
                      where comp_id=?"""
            updateqt = cursor.execute(sql3, newqt, cid[0])
            sql4 = """select * from dbo.Inventory"""
            newinvent = pd.read_sql(sql4, connection)

        else:
            print("Dont have enough spare parts available.")
            sql2 = """select m.mfd_phno 
                      from dbo.Manufacturer m, dbo.Components c 
                      where c.mfd_id=m.mfd_id and c.comp_id=?"""
            mfdphno = cursor.execute(sql2, cid[0]).fetchval()
            print("Call", mfdphno, "to order more.")
            connection.rollback()




    else:
        for n in cid:
            x = 0
            a = n
            b = qt[int(x)]
            sql1 = """select qty_avail from dbo.Inventory where comp_id=?"""
            totalqt = int(cursor.execute(sql1, n).fetchval())
            reqdqt = qnty * qt[x]
            if reqdqt < totalqt:
                newqt = totalqt - reqdqt
                sql3 = """update dbo.Inventory
                          set qty_avail=?
                          where dbo.Inventory.comp_id= 
                                     (select comp_details from dbo.prods where prod_name=
                                                (select product_name from dbo.orderss where prod_name=?))"""
                updateqt = cursor.execute(sql3, newqt, n)
                sql4 = """select * from dbo.Inventory"""
                newinvent = pd.read_sql(sql4, connection)
                x += 1
            else:
                print("Dont have enough spare parts available.")
                sql2 = """select m.mfd_phno 
                          from dbo.Manufacturer m, dbo.Components c 
                          where c.mfd_id=m.mfd_id and c.comp_id=?"""
                mfdphno = cursor.execute(sql2, n).fetchval()
                sqln = """select comp_name from dbo.Components where comp_id=?"""
                componame = cursor.execute(sqln, n).fetchval()
                print("Call", mfdphno, "to order more", componame, ".")
                connection.rollback()

    print(ordertable)

elif t == 2:
    # print the components:
    complist = 'SELECT c.comp_name as Component, i.qty_avail as Qnty_Avail, c.comp_price as Price ' \
               'FROM dbo.Components c, dbo.Inventory i ' \
               'WHERE c.comp_id=i.comp_id'
    comptable = pd.read_sql(complist, connection)
    print(comptable)

    # ask user which item is to be added:
    z = int(input("Component to be added: "))
    z = z + 1
    if z < 10:
        z = "C0" + str(z)
    elif 10 <= z < 20:
        z = str(z)
        z = "C1" + z[-1]
        print(z)
    elif 20 <= z < 30:
        z = str(z)
        z = "C2" + z[-1]
        print(z)
    elif 30 <= z < 36:
        z = str(z)
        z = "C3" + z[-1]
        print(z)
    else:
        print("Error! Input valid number.")

    # use sql query to print jut the row that is to be updated:
    sql = """select c.comp_name as Component, i.Qty_avail as Qnty_Avail, c.comp_price as Price
            from dbo.Components c, dbo.Inventory i
            where i.comp_id=c.comp_id and c.comp_id=?"""
    component = cursor.execute(sql, z)
    for row in cursor:
        component = row
        print(component)
        break
    compname = component[0]
    compqty = int(component[1])
    compprice = component[2]

    # ask user how many are to be added
    qnty = int(input("How many? "))
    totalamt = qnty * compprice
    compqty = compqty + qnty
    print("Total amount to pay=  ₹", totalamt)
    print("new quantity=", compqty)

    # update 'inventory' and 'components' table
    updateinvent = """update inventory set qty_avail=? where comp_id=?"""
    update_invent_table = cursor.execute(updateinvent, compqty, z)
    inventtable = pd.read_sql(complist, connection)
    print(inventtable)

    # update the database:
    connection.commit()

elif t == 3:
    # print the components:
    complist = 'SELECT c.comp_name as Component, i.qty_avail as Qnty_Avail, c.comp_price as Price ' \
               'FROM dbo.Components c, dbo.Inventory i ' \
               'WHERE c.comp_id=i.comp_id'
    comptable = pd.read_sql(complist, connection)
    print(comptable)

    # ask user which item is to be added:
    z = int(input("Component to be removed: "))
    z = z + 1
    if z < 10:
        z = "C0" + str(z)
    elif 10 <= z < 20:
        z = str(z)
        z = "C1" + z[-1]
        print(z)
    elif 20 <= z < 30:
        z = str(z)
        z = "C2" + z[-1]
        print(z)
    elif 30 <= z < 36:
        z = str(z)
        z = "C3" + z[-1]
        print(z)
    else:
        print("Error! Input valid number.")

    # use sql query to print jut the row that is to be updated:
    sql = """select c.comp_name as Component, i.Qty_avail as Qnty_Avail, c.comp_price as Price
            from dbo.Components c, dbo.Inventory i
            where i.comp_id=c.comp_id and c.comp_id=?"""
    component = cursor.execute(sql, z)
    for row in cursor:
        component = row
        print(component)
        break
    compname = component[0]
    compqty = int(component[1])
    compprice = component[2]

    # ask user how many are to be removed:
    qnty = int(input("How many? "))

    if qnty > compqty:
        print("Cant remove", qnty, compname, "as only", compqty, "are available")
        mfdcontact = """select m.mfd_phno, c.comp_name as Component
                      from dbo.Manufacturer m, dbo.Components c
                      where m.mfd_id=c.mfd_id and c.comp_id=?"""
        mfdphone = cursor.execute(mfdcontact, z)
        for row in cursor:
            component = row
            break
        print("call", component[0], "to order more", compname)

    elif qnty == compqty:
        print("Left with 0", compname)
        mfdcontact = """select m.mfd_phno, c.comp_name as Component
                              from dbo.Manufacturer m, dbo.Components c
                              where m.mfd_id=c.mfd_id and c.comp_id=?"""
        mfdphone = cursor.execute(mfdcontact, z)
        for row in cursor:
            component = row
            break

        compqty = compqty - qnty

        # update 'inventory' and 'components' table
        updateinvent = """update inventory set qty_avail=? where comp_id=?"""
        update_invent_table = cursor.execute(updateinvent, compqty, z)
        inventtable = pd.read_sql(complist, connection)
        print(inventtable)

        print("left with 0 more", compname, ".Call", component[0], "to order more.")

    else:
        print("Left with 0", compname)
        mfdcontact = """select m.mfd_phno, c.comp_name as Component
                        from dbo.Manufacturer m, dbo.Components c
                        where m.mfd_id=c.mfd_id and c.comp_id=?"""
        mfdphone = cursor.execute(mfdcontact, z)
        for row in cursor:
            component = row
            break

        compqty = compqty - qnty
        # update 'inventory' and 'components' table
        updateinvent = """update inventory set qty_avail=? where comp_id=?"""
        update_invent_table = cursor.execute(updateinvent, compqty, z)
        inventtable = pd.read_sql(complist, connection)
        print(inventtable)

        # update the database:
        connection.commit()


elif t == 4:
    # print the components:
    complist = 'SELECT c.comp_name as Component, i.qty_avail as Qnty_Avail, c.comp_price as Price ' \
               'FROM dbo.Components c, dbo.Inventory i ' \
               'WHERE c.comp_id=i.comp_id'
    comptable = pd.read_sql(complist, connection)
    print(comptable)

elif t == 5:
    mfddet = """select c.comp_name as Component, m.mfd_phno as Manufacturer
           from dbo.Manufacturer m, dbo.Components c
           where m.mfd_id=c.mfd_id"""
    manufacturerdetails = pd.read_sql(mfddet, connection)
    print(manufacturerdetails)

elif t == 6:
    sql = """select * from dbo.orderss"""
    ordertable = pd.read_sql(sql, connection)
    print(ordertable)


else:
    print("Select Valid Operation")

connection.commit()
