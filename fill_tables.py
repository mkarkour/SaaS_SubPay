import sqlite3
import script
import datetime as dt

dbase = sqlite3.connect('project.db', isolation_level=None)
print('Database opened')

# Enable Referential Integrity Check. (Mandatory for the project)#
dbase.execute("PRAGMA foreign_keys = 1")
# By telling SQLite to check for foreign keys, you are enforcing referential integrity
# This means that ensuring that the relationships between tables are appropriate).
# So, if a value appears as a foreign key in one table,
# it must also appear as the primary key of a record in the referenced table.


#########################
#1 ADD DATA TO CUSTOMER #
#########################
def insert_Customer(Email, First_Name, Last_Name, Birth_Date, Password, Address, Billing_Address, Credit_Card):
    dbase = sqlite3.connect('project.db', isolation_level=None)
    dbase.execute("PRAGMA foreign_keys = 1")
    
    dbase.execute('''INSERT INTO Customer(Email, First_Name, Last_Name, Birth_Date, Password, Address, Billing_Address, Credit_Card)
            VALUES(?,?,?,?,?,?,?,?)
                ''', (Email, First_Name, Last_Name, Birth_Date, Password, Address, Billing_Address, Credit_Card)
                  )
    
    dbase.close()
    
    print(str(Email) + " added to the database") #Visible dans le terminal
    



########################
#2 ADD DATA TO COMPANY #
########################
def insert_Company(VAT_Number, Company_Name, Address, Bank_Account):
    dbase = sqlite3.connect('project.db', isolation_level=None)
    dbase.execute("PRAGMA foreign_keys = 1")
    
    dbase.execute('''INSERT INTO Company(VAT_Number, Company_Name, Address, Bank_Account)
            VALUES(?,?,?,?)
                ''', (VAT_Number, Company_Name, Address, Bank_Account)
                  )
    
    dbase.close()
    
    print(str(Company_Name) + " added to the database") #Visible dans le terminal
    



#############################    
#3 ADD DATA TO SUBSCRIPTION #
#############################
def insert_Subscription(Subscription_Name, Single_Price, Currency, Company_VAT_Number):
    dbase = sqlite3.connect('project.db', isolation_level=None)
    dbase.execute("PRAGMA foreign_keys = 1")
    
    dbase.execute('''INSERT INTO Subscription(Subscription_Name, Single_Price, Currency, Company_VAT_Number)
            VALUES(?,?,?,?)
                ''', (Subscription_Name, Single_Price, Currency, Company_VAT_Number)
                  )
    
    dbase.close()
    
    print(str(Subscription_Name) + " from " + str(Company_VAT_Number) + " added") #Visible dans le terminal
    
  


######################
#4 ADD DATA TO QUOTE #
######################
def insert_Quote(Company_VAT_Number, Subscription_Reference, Quantity, Currency, Active):
    dbase = sqlite3.connect('project.db', isolation_level=None)
    dbase.execute("PRAGMA foreign_keys = 1")
    
    #On récupère le prix individuel de la subscription
    Single_Price = dbase.execute(''' SELECT Single_Price FROM Subscription WHERE Subscription_ID = ? ''', (Subscription_Reference,)).fetchall()[0][0]
    
    #On calcule le prix total et on ajoute la TVA
    Price_Without_VAT = Single_Price * int(Quantity)
    Price_With_VAT = script.add_VAT(Price_Without_VAT, 0.21)
    
    
    dbase.execute('''INSERT INTO Quote(Company_VAT_Number, Subscription_Reference, Quantity, Price_Without_VAT, Price_With_VAT, Currency, Active)
            VALUES(?,?,?,?,?,?,?)
                ''', (Company_VAT_Number, Subscription_Reference, Quantity, Price_Without_VAT, Price_With_VAT, Currency, Active)
                  )
    
    dbase.close()
    
    print("Price without VAT: " + str(Price_Without_VAT) + "€") #Visible dans le terminal
    print("Price with VAT: " + str(Price_With_VAT) + "€") #Visible dans le terminal
    
    print("Quote by " + str(Company_VAT_Number) + "succesfully created") #Visible dans le terminal


########################
#5 ADD DATA TO INVOICE #
########################
def insert_Invoice(Quote_Reference, Customer_Email, End_Date, Currency):
    dbase = sqlite3.connect('project.db', isolation_level=None)
    dbase.execute("PRAGMA foreign_keys = 1")

    #On récupère le prix de la quote choisie
    Total_Amount = dbase.execute('''SELECT Price_With_VAT FROM Quote WHERE Quote_ID =?''', (Quote_Reference,)).fetchall()[0][0]
    
    #Date de début = aujourd'hui
    Start_Date = str(dt.datetime.now()).split(" ")[0]   #2021-12-18 10:31:21 GMT
    
    #Date de première facture = aujourd'hui
    Invoice_Date = str(dt.datetime.now()).split(" ")[0]
    
    dbase.execute('''INSERT INTO Invoice(Quote_Reference, Customer_Email, Start_Date, Invoice_Date, End_Date, Total_Amount, Currency)
            VALUES(?,?,?,?,?,?,?)
                ''', (Quote_Reference, Customer_Email, Start_Date, Invoice_Date, End_Date, Total_Amount, Currency)
                  )
    
    dbase.close()
    
    print("Invoice for " + str(Customer_Email) + " added to the database for a monthly billing of " + str(Total_Amount) + " " + str(Currency)) #Visible dans le terminal


########################
#6 ADD DATA TO PAYMENT #
########################
# def insert_Payment(Invoice_Reference, Customer_Email, Amount_Paid, Currency):
#     dbase = sqlite3.connect('project.db', isolation_level=None)
#     dbase.execute("PRAGMA foreign_keys = 1")
    
#     CC = dbase.execute('''SELECT Credit_Card From Customer WHERE Email = ?''', (Customer_Email,)).fetchall()[0][0]
    
    
#     Current_Invoice_Date = dbase.execute(''' SELECT Invoice_Date From Invoice WHERE Email = ?''', (Customer_Email,)).fetchall[0][0]
    
    
#     dbase.execute('''
    
#         INSERT INTO Payment(
#             Invoice_Reference, Current_Invoice_Date, Customer_Email, CC, Amount_Paid_EUR, Amount_Paid_FOREIGN, Currency)
#         VALUES(?,?,?,?,?,?,?,?)
#             ''', (Invoice_Reference, Current_Invoice_Date, Customer_Email, CC, Amount_Paid_EUR, Amount_Paid_FOREIGN, Currency)
                
#                )
        
#     print(str(Customer_Email) + " has paid " + str(Amount_Paid) + " for Invoice number " + str(Invoice_Reference)) + " due on" + str(Current_Invoice_Date)

#     dbase.close()

#     return True



# #insert_Customer(Email, First_Name, Last_Name, Birth_Date, Password, Address, Billing_Address, Credit_Card)
# insert_Customer("mehdi.karkour@ulb.be", "Mehdi", "Karkour", "1998-04-21", "Mehdi.123", "Alchemiststeeg 11, 1120 Neder-over-Heembeek, BE", "Rue De Wand 11, 1020 Laeken, BE", "5115800900636253")
# insert_Customer("noeline.deterwangne@ulb.be", "Noëline", "De Terwangne", "1998-02-11", "Noeline.123", "Rue De Wand 12, 1020 Laeken, BE", "Rue De Wand 12, 1020 Laeken, BE", "1234123412341234")
# insert_Customer("yannick.lu@ulb.be", "Yannick", "Lu", "1998-01-01", "Yannick.123", "Avenue Buyl 12, 1000 Ixelles, BE", "Avenue Buyl 12, 1000 Ixelles, BE", "5678567856785678")
# insert_Customer("ilias.mahri@ulb.be", "Ilias", "Mahri", "1998-10-19", "Ilias.123", "Avenue Wannecouter 10, 1020 Laeken, BE", "Avenue Wannecouter 10, 1020 Laeken, BE", "1234123412341234")
# insert_Customer("thien.huynh@ulb.be", "Thien", "Huynh", "1999-05-25", "Thien.123", "Berkendallaan 15, 1800 Vilvoorde, BE", "Berkendallaan 15, 1800 Vilvoorde, BE", "5301150401171978")
# insert_Customer("lady.gaga@ulb.be", "Lady", "Gaga", "1988-04-12", "Lady.123", "Alchemiststeeg 21, 1120 Neder-over-Heembeek, BE", "Rue De Wand 21, 1020 Laeken, BE", "5115800900636246")
# insert_Customer("charlotte.fraise@ulb.be", "Charlotte", "Fraise", "2001-02-01", "Charlotte.123", "Rue De Wand 1, 1020 Laeken, BE", "Rue De Wand 1, 1020 Laeken, BE", "1234123412341232")
# insert_Customer("harry.potter@ulb.be", "Harry", "Potter", "1990-10-11", "Harry.123", "Avenue Buyl 120, 1000 Ixelles, BE", "Avenue Buyl 120, 1000 Ixelles, BE", "5678567856785612")
# insert_Customer("police.nationale@ulb.be", "Police", "Nationale", "1991-05-14", "Police.123", "Avenue Wannecouter 101, 1020 Laeken, BE", "Avenue Wannecouter 101, 1020 Laeken, BE", "1234123412341211")
# insert_Customer("albert.einstein@ulb.be", "Albert", "Einstein", "1995-05-01", "Albert.123", "Berkendallaan 153, 1800 Vilvoorde, BE", "Berkendallaan 153, 1800 Vilvoorde, BE", "5301150401171978")

# dbase.execute(''' UPDATE Customer SET Credit_Card = "1111111111111111" WHERE Email = "noeline.deterwangne@ulb.be" ''')


# ######## insert_Company(VAT_Number, Company_Name, Address, Bank_Account) #######
# insert_Company("BE111111111", "Spotify", "Alchemiststeeg 159, 1120 Neder-over-Heembeek, BE", "BE00123412341111")
# insert_Company("BE222222222", "Microsoft", "Avenue Buyl 101, 1000 Ixelles, BE", "BE00678967892222")
# insert_Company("BE333333333", "Youtube", "Avenue Wannecouter 13, 1020 Laeken, BE", "BE89123412343333")
# insert_Company("BE444444444", "Netflix", "Rue De Wand 102, 1020 Laeken, BE", "BE00678967894444")
# insert_Company("BE555555555", "Amazon Prime", "Berkendallaan 100, 1800 Vilvoorde, BE", "BE00678967895555")



# ####### insert_Subscription(Subscription_Name, Single_Price, Currency, Company_VAT_Number) #######
# insert_Subscription("Spotify Family", 14.99, "EUR", "BE111111111")                   #1
# insert_Subscription("Spotify Premium", 9.99, "EUR", "BE111111111")                   #2
# insert_Subscription("Spotify Premium Student", 4.99, "EUR", "BE111111111")           #3
# insert_Subscription("Microsoft OneDrive 100 GB", 2.00, "EUR", "BE222222222")         #4
# insert_Subscription("Youtube Premium", 11.99, "EUR", "BE333333333")                  #5
# insert_Subscription("Youtube Premium Student", 6.99, "EUR", "BE333333333")           #6
# insert_Subscription("Amazon Prime", 5.99, "EUR", "BE555555555")                      #7
# insert_Subscription("Amazon Prime Student", 2.99, "EUR", "BE555555555")              #8
# insert_Subscription("Netflix Essential (1 screen)", 8.99, "EUR", "BE444444444")      #9
# insert_Subscription("Netflix Standard (2 screen)", 13.49, "EUR", "BE444444444")      #10
# insert_Subscription("Netflix Premium (4 screens)", 17.99, "EUR", "BE444444444")      #11



# ####### insert_Quote(Company_VAT_Number, Subscription_Reference, Quantity, Currency, Active) #######
# insert_Quote("BE333333333", "5", "5", "EUR", True)  #1
# insert_Quote("BE333333333", "5", "1", "EUR", True)  #2
# insert_Quote("BE555555555", "7", "1", "EUR", True)  #3
# insert_Quote("BE222222222", "4", "1", "EUR", True)  #4
# insert_Quote("BE444444444", "10", "5", "EUR", True) #5
# insert_Quote("BE111111111", "2", "4", "EUR", True)  #6
# insert_Quote("BE111111111", "3", "1", "EUR", True)  #7
# insert_Quote("BE555555555", "6", "3", "EUR", True)  #8
# insert_Quote("BE444444444", "11", "2", "EUR", True) #9
# insert_Quote("BE333333333", "6", "2", "EUR", True)  #10
# insert_Quote("BE111111111", "1", "5", "EUR", True)  #11
# insert_Quote("BE222222222", "4", "3", "EUR", True)  #12
# insert_Quote("BE555555555", "7", "1", "EUR", True)  #13
# insert_Quote("BE333333333", "6", "2", "EUR", True)  #14
# insert_Quote("BE555555555", "6", "4", "EUR", True)  #15
# insert_Quote("BE444444444", "10", "2", "EUR", True) #16
# insert_Quote("BE444444444", "9", "4", "EUR", True)  #17
# insert_Quote("BE111111111", "2", "3", "EUR", True)  #18
# insert_Quote("BE444444444", "11", "3", "EUR", True) #18
# insert_Quote("BE111111111", "3", "1", "EUR", True)  #19
# insert_Quote("BE444444444", "9", "3", "EUR", True)  #6
# insert_Quote("BE111111111", "1", "2", "EUR", True)  #9


# ####### insert_Invoice(Quote_Reference, Customer_Email, End_Date, Currency) #######
# insert_Invoice("1","albert.einstein@ulb.be","2030-11-23","EUR")         #1
# insert_Invoice("2","harry.potter@ulb.be","2030-11-23","EUR")            #2
# insert_Invoice("3","charlotte.fraise@ulb.be","2030-11-23","EUR")        #3
# insert_Invoice("4", "yannick.lu@ulb.be", "2030-10-24", "EUR")           #4
# insert_Invoice("5","lady.gaga@ulb.be", "2030-11-24", "EUR")             #5
# insert_Invoice("6","mehdi.karkour@ulb.be","2030-11-23","EUR")           #6
# insert_Invoice("7", "mehdi.karkour@ulb.be", "2030-11-24", "EUR")        #7
# insert_Invoice("8", "noeline.deterwangne@ulb.be", "2030-11-25", "EUR")  #8
# insert_Invoice("9","police.nationale@ulb.be","2030-11-23","EUR")        #9
# insert_Invoice("10", "mehdi.karkour@ulb.be", "2030-11-28", "EUR")       #10
# insert_Invoice("11", "noeline.deterwangne@ulb.be", "2030-11-25", "EUR") #11
# insert_Invoice("12","lady.gaga@ulb.be", "2030-11-24", "EUR")            #12
# insert_Invoice("13", "ilias.mahri@ulb.be", "2030-11-28", "EUR")         #13
# insert_Invoice("14", "albert.einstein@ulb.be", "2030-12-27", "EUR")     #14
# insert_Invoice("15", "thien.huynh@ulb.be", "2030-12-27", "EUR")         #15
# insert_Invoice("16","mehdi.karkour@ulb.be","2030-11-23","EUR")          #16
# insert_Invoice("17", "mehdi.karkour@ulb.be", "2030-11-24", "EUR")       #17
# insert_Invoice("18","charlotte.fraise@ulb.be","2030-11-23","EUR")       #18
# insert_Invoice("19","albert.einstein@ulb.be","2030-11-23","EUR")        #19
# insert_Invoice("20", "lady.gaga@ulb.be", "2030-10-24", "EUR")           #20
# insert_Invoice("21", "police.nationale@ulb.be", "2030-11-28", "EUR")    #21
# insert_Invoice("22", "police.nationale@ulb.be", "2030-11-28", "EUR")    #22


# dbase.execute('UPDATE Invoice SET Invoice_Date="2021-10-24" WHERE Invoice_ID = 1')    #1
# dbase.execute('UPDATE Invoice SET Invoice_Date="2021-10-25" WHERE Invoice_ID = 2')    #2
# dbase.execute('UPDATE Invoice SET Invoice_Date="2021-09-24" WHERE Invoice_ID = 3')    #3

# dbase.execute('UPDATE Invoice SET Start_Date="2019-10-24" WHERE Invoice_ID = 1')    #1
# dbase.execute('UPDATE Invoice SET Start_Date="2020-10-25" WHERE Invoice_ID = 2')    #2
# dbase.execute('UPDATE Invoice SET Start_Date="2018-09-24" WHERE Invoice_ID = 3')    #3
# dbase.execute('UPDATE Invoice SET Start_Date="2016-10-24" WHERE Invoice_ID = 4')    #4
# dbase.execute('UPDATE Invoice SET Start_Date="2014-10-25" WHERE Invoice_ID = 5')    #5
# dbase.execute('UPDATE Invoice SET Start_Date="2012-09-24" WHERE Invoice_ID = 6')    #6
# dbase.execute('UPDATE Invoice SET Start_Date="2018-10-24" WHERE Invoice_ID = 7')    #7
# dbase.execute('UPDATE Invoice SET Start_Date="2017-10-25" WHERE Invoice_ID = 8')    #8
# dbase.execute('UPDATE Invoice SET Start_Date="2014-09-24" WHERE Invoice_ID = 9')    #9
# dbase.execute('UPDATE Invoice SET Start_Date="2016-10-24" WHERE Invoice_ID = 10')   #10
# dbase.execute('UPDATE Invoice SET Start_Date="2020-10-25" WHERE Invoice_ID = 11')   #11
# dbase.execute('UPDATE Invoice SET Start_Date="2019-09-24" WHERE Invoice_ID = 12')   #12
# dbase.execute('UPDATE Invoice SET Start_Date="2015-10-24" WHERE Invoice_ID = 13')   #13
# dbase.execute('UPDATE Invoice SET Start_Date="2021-05-25" WHERE Invoice_ID = 14')   #14
# dbase.execute('UPDATE Invoice SET Start_Date="2020-09-24" WHERE Invoice_ID = 15')   #15


dbase.close()
print("Database closed")