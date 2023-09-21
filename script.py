import sqlite3
import requests
import pandas as pd
import datetime as dt
import statistics
from matplotlib import pyplot as plt


dbase = sqlite3.connect('group42_project.db', isolation_level=None) #open db
dbase.execute("PRAGMA foreign_keys = 1") #Pour s'assurer que les FK qu'on crée soient les PK d'autres tables

#####################################
# READ A SPECIFIC TABLE WITH PANDAS #
#####################################
def read_data_pandas(table):
    dbase = sqlite3.connect('group42_project.db', isolation_level=None)
    dbase.execute("PRAGMA foreign_keys = 1")
    
    query = '''SELECT * FROM ''' + str(table)
    results = pd.read_sql_query(query, dbase)
    
    dbase.close()
    return print(results)
#read_data_pandas("invoice")


###############################
# READ ALL TABLES WITH PANDAS #
###############################
def read_all_tables_pandas():
    Tables = ("Customer", "Company", "Subscription", "Quote", "Invoice", "Payment")
    for i in Tables:
        print("Table name: " + str(i))
        print(read_data_pandas(i))
        print("\n")
#read_all_tables_pandas()


#########################################
# 7. REQUEST IF CUSTOMER HAS AN INVOICE #
#########################################
def request_invoice(email):
    dbase = sqlite3.connect('group42_project.db', isolation_level=None)
    
    #On récupère toutes les invoices de ce client
    Customer_invoices = dbase.execute('''SELECT * FROM Invoice WHERE Customer_Email = ? ''', (email,)).fetchall()
    
    dbase.close()

    #Servira à vérifier si invoice date < aujourd'hui
    current_date = str(dt.datetime.now()).split(" ")[0]
    today = int(current_date.replace("-", ""))
    
    invoice_pending = {} #On y ajoutera les invoices au format "invoice_id" : "invoice_price" due on "invoice_date"
    invoice_paid = [] #On y ajoutera les id des invoices déjà payées
    
    for invoice in Customer_invoices:
        
        invoice_date = int(invoice[3].replace("-", ""))
        
        if invoice_date <= int(today):
    
            #On récupère les infos de l'invoice : id, price, date
            invoice_pending_id = str(invoice[0])
            invoice_pending_price = str(invoice[6]) + "€"
            invoice_date = str(invoice[3])
            
            #On ajoute au dictionnaire invoice_pending les keys "invoice_pending_id" (= id) et les values "invoice_price" due on "invoice_date"
            invoice_pending[invoice_pending_id] = invoice_pending_price + " due on " + invoice_date
            
        else:
            invoice_paid_id = str(invoice[0])
            invoice_paid.append(invoice_paid_id) #On ajoute les id des invoices déjà payées à la liste invoice_paid
            
    print("You have already paid invoice(s) number " + str(invoice_paid) + " and you still need to pay these invoices (id:price & date): " + str(invoice_pending)) #S'affiche dans le terminal
    return "You have already paid invoice(s) number " + str(invoice_paid) + " and you still need to pay these invoices (id:price & date): " + str(invoice_pending) #Ne s'affiche pas dans le terminal
#request_invoice("mehdi.karkour@ulb.be")


##############################################
# 8/9. PAY INVOICE (aka ADD DATA TO PAYMENT) #
##############################################
def Pay_Invoice(Invoice_Reference, Customer_Email, CC, Amount_Paid_EUR, Currency):
    dbase = sqlite3.connect('group42_project.db', isolation_level=None)
    dbase.execute("PRAGMA foreign_keys = 1")
    
    #On récupère la date de facturation
    Current_Invoice_Date = dbase.execute(''' SELECT Invoice_Date From Invoice WHERE Customer_Email = ?''', (str(Customer_Email),)).fetchall()[0][0]
    
    #On convertie le montant "Amount_Paid_EUR" par celui dans la Currency choisie
    Amount_Paid_FOREIGN = change_eur_to_foreign(float(Amount_Paid_EUR), Currency)
    
    
    dbase.execute(''' INSERT INTO Payment(Invoice_Reference, Current_Invoice_Date, Customer_Email, CC, Amount_Paid_EUR, Amount_Paid_FOREIGN, Currency)
            VALUES(?,?,?,?,?,?,?)
                ''', (Invoice_Reference, Current_Invoice_Date, Customer_Email, CC, Amount_Paid_EUR, Amount_Paid_FOREIGN, Currency)
                  )
    
    dbase.close()

    print(str(Customer_Email) + " has paid " + str(Amount_Paid_FOREIGN) + str(Currency) + " (" + str(Amount_Paid_EUR) + "€) for invoice #" + str(Invoice_Reference) + " due on " + str(Current_Invoice_Date))
    return str(Customer_Email) + " has paid " + str(Amount_Paid_FOREIGN) + str(Currency) + " (" + str(Amount_Paid_EUR) + "€) for invoice #" + str(Invoice_Reference) + " due on " + str(Current_Invoice_Date)
#Pay_Invoice("2", "noeline.deterwangne@ulb.be", "5301150401171978", "24.151600000000002", "EUR")


####################################################################################
# 8/9. ONCE THE MONTHLY INVOICE HAS BEEN PAID, WE INCREASE INVOICE_DATE BY 1 MONTH #
####################################################################################
def Invoice_paid(invoice_id):
    dbase = sqlite3.connect('group42_project.db', isolation_level=None)
    dbase.execute("PRAGMA foreign_keys = 1")
    
    Current_Invoice_Date = dbase.execute('''SELECT Invoice_Date FROM Invoice WHERE Invoice_ID = {id}'''.format(id = invoice_id)).fetchall()[0][0]
    Invoice_Date = Current_Invoice_Date.split("-")
    
    #On sépare les jours, mois et années pour les manipuler plus facilement
    current_year = int(Invoice_Date[0])
    current_month = int(Invoice_Date[1])
    current_day = int(Invoice_Date[2])
    
    if current_month == 12: #Si on est au 12e mois de l'année
        new_year = current_year + 1
        new_month = "01"
        
    else: #Si on est à un autre mois que le 12e
        new_year = current_year
        
        if current_month >= 9: #Si le mois est 9, 10 ou 11
            new_month = current_month + 1
        else: #Si le mois est entre 1 et 8, on remet un 0 devant pour garder le bon format
            new_month = "0" + str(current_month + 1)
            
    #On remet la date séparée au bon format (YYYY-MM-DD)
    next_billing_date = str(new_year) + "-" + str(new_month) + "-" + str(current_day)
    
    print("Next billing date: " + str(next_billing_date)) #S'affiche dans le terminal
    
    
    #On met à jour la date de facturation avec la nouvelle date (qui est celle augmentée d'un mois)
    dbase.execute('UPDATE Invoice SET Invoice_Date=? WHERE Invoice_ID = ?',(str(next_billing_date), invoice_id))
    
    dbase.close()
    
    print("Invoice number " + str(invoice_id) + " has been paid, the next billing is due on" + str(next_billing_date)) #S'affiche dans le terminal
#Invoice_paid("5")


###################################
# 8/9. CREDIT CARD VALIDITY CHECK #
###################################
def CC_check(CC):
    string_CC = str(CC) #Pour pouvoir le parcourir dans une boucle for

    #On va enregistrer la valeur du dernier chiffre dans last_digit et ensuite le supprimer de la liste list
    list = []
    for number in string_CC:
        list.append(int(number))
    last_digit = list[15]
    del list[15]

    #On va retourner la suite de chiffres
    reverse_CC = []
    i = 14
    while i >= 0:
        last = list[i]
        reverse_CC.append(last)
        i = i - 1

    #On double les chiffres en position pair (position 0, position 2, position 4, ...)
    new_reverse = []
    j = 0
    while j <= 14:
        if j % 2 == 0: #Si chiffre pair (aka le reste de la division par deux est 0)
            double = 2 * reverse_CC[j]
            
            if double > 9: #Si quand on double le chiffre (en position pair) il est supérieur à 9, on doit retrancher 9 à ce nombre
                double = double - 9
                new_reverse.append(double)
                
            else:
                new_reverse.append(double)
                
        else:
            simple = reverse_CC[j]
            new_reverse.append(simple)
        j = j + 1

    #4 On additionne tous les chiffres (les 15) ainsi que le dernier chiffre qu'on avait supprimé temporairement (le 16e)
    new_CC = 0
    
    for k in new_reverse:
        new_CC = new_CC + int(k)
        
    new_CC = new_CC + last_digit
    
    if int(new_CC) % 10 == 0: #On vérifie si le résultat de cette somme est divisible par 10
        print("Yes it is, your card number is valid") #S'affiche dans le terminal
        return True
    else:
        print("No it's not, your card number is not valid. Please try again") #S'affiche dans le terminal
        return False
#CC_check(5301150401171978) #Ce numéro est valide
#CC_check(1234123412341234) #Ce numéro n'est pas valide
    
    
#############################################################
# DEF PayInvoice. CHANGE PRICE IN EUROS TO ANOTHER CURRENCY #
#############################################################
def change_eur_to_foreign(price, currency):
    online_currency = requests.get("https://v6.exchangerate-api.com/v6/06099ddd07168bc8d7db68eb/latest/{}".format(currency)).json() #Dictionnaire dans un dictionnaire
    
    exchange_rate = online_currency["conversion_rates"]["EUR"] #conversion_rates est un dictionnaire (qui est lui-même dans un dictionnaire)
    
    price_in_foreign = price / exchange_rate # EUR * FOREIGN/EUR
    
    print("Daily rate: " + str(exchange_rate) + " " + str(currency) + "/EUR")
    print(str(price) + "€ = " + str(price_in_foreign) + " " + str(currency))
    return price_in_foreign
#change_currency(1000, "EUR")


#######################
# FillTables. ADD VAT #
#######################
def add_VAT(price_without_VAT, VAT):

    price_with_VAT = price_without_VAT * (1 + VAT)
    
    print("Total price excluding VAT: " + str(price_without_VAT) + " EUR") #S'affiche dans le terminal
    print("Total price including VAT: " + str(price_with_VAT) + " EUR") #S'affiche dans le terminal
    
    return price_with_VAT
#add_VAT(1000, 0.21)


##################################
# READ ANALYTICS (FOR COMPANIES) #
##################################

######################################
#10. Monthly Recurring Revenue (MRR) #
######################################
def MRR(company_VAT_Number, date_choose):
    
    date_choose_list=date_choose.split("-") # 2022-12-21
    #print(date_choose_list)
    year_choose = int(date_choose_list[0])
    month_choose = int(date_choose_list[1])
    
    dbase = sqlite3.connect('group42_project.db', isolation_level=None)
    company_name = dbase.execute('''SELECT Company_Name FROM Company WHERE VAT_Number= ? ''',(company_VAT_Number,)).fetchall()[0][0]
    #On part du principe que chaque invoice a une quote (relaiton 1-1) --> ils ont le même ID
    quotes_invoices = dbase.execute('''SELECT Start_Date, Invoice_ID, Quote_ID, Company_VAT_Number, Price_With_VAT, Quantity
    FROM Quote 
    INNER JOIN Invoice ON Quote_ID = Invoice_ID
    WHERE Company_VAT_Number="{}"  AND Active = True'''.format(company_VAT_Number)).fetchall()
    dbase.close()
    print(quotes_invoices)

    #On va prendre les invoices dont le mois est dans la période
    invoices_with_valid_month = []
    for quote_invoice in quotes_invoices:
        for start in quote_invoice:
            date = str(start)
            break #Autre manière de prendre seulement le premier élément (idem que quote_invoice[0])
        
        Start_date = date.split("-")
        year_start = int(Start_date[0])
        month_start = int(Start_date[1])
        
        if year_choose == year_start: #Si l'invoice est de la même année, on doit encore s'assurer que le mois choisi est après le mois de départ
            if month_choose >= month_start:
                    invoices_with_valid_month.append(quote_invoice)

        elif year_choose > year_start: #Si l'année choisie est supérieure à l'année de départ, on prend d'office en compte l'invoice
            invoices_with_valid_month.append(quote_invoice)
    
    #On calcule le MRR
    revenue = 0
    
    for single_invoice in invoices_with_valid_month:
        price_with_VAT = single_invoice[4]
        revenue += price_with_VAT
        
        
    print("The monthly recurring revenue of {} ".format(company_name) +   "is "  +  str(revenue)  +  " EUR")
    return "The monthly recurring revenue of {} ".format(company_name) +  "is "  +  str(revenue)  +  " EUR "
#MRR("BE444444444","2022-01-20")

######################################
# 10. Annual Recurring Revenue (ARR) #
######################################
def ARR(company_VAT_Number, date_choose):
    date_choose_list = date_choose.split("-")
    year_choose = int(date_choose_list[0])

    dbase = sqlite3.connect('group42_project.db', isolation_level=None)
    company_name = dbase.execute('''SELECT Company_Name FROM Company WHERE VAT_Number= ? ''',(company_VAT_Number,)).fetchall()[0][0]
    quotes_invoices = dbase.execute('''
    SELECT Start_Date, Price_With_VAT AS Amount, subscription_name AS Subscription
    FROM Quote
    INNER JOIN Invoice ON Quote_ID = Invoice_ID 
    LEFT JOIN Subscription on subscription_id=subscription_reference
    WHERE Quote.Company_VAT_Number="{}"  AND Active = True
    '''.format(company_VAT_Number)).fetchall()
    dbase.close()
    
    #print(quote_invoice)
    #print(len)
    
    revenue = 0
    
    for quote_invoice in quotes_invoices:
        for start in quote_invoice:
            date=str(start)
            break
        
        start_date = date.split("-")
        year_start = int(start_date[0])
        month_start = int(start_date[1])
        
        
        december = 13
        amount = quote_invoice[1]
                       
        if year_choose > year_start:
            new_revenue = amount * 12
            revenue += new_revenue

        elif year_choose == year_start: #On paye aussi le mois où on souscrit l'abonnement -> on va compter le nombre de mois à partir du mois de départ de l'abonnement si on est dans la même année (elif)
                month_paid = december - month_start # month_paid est le nombre de mois où l'abo est actif
                new_revenue = amount * month_paid
                revenue += new_revenue
        else:
            print("There is no quote for {date} for {company} company".format(date = str(year_choose),company = str(company_name)))
            return "There is no quote for {date} for {company} company".format(date = str(year_choose),company = str(company_name))
           

    print("The annual recurring revenue of {} ".format(company_name) + "is " + str(revenue) + " EUR (per year)")
    return "The annual recurring revenue of {} ".format(company_name) + "is "  +  str(revenue) + " EUR (per year)"
#ARR("BE444444444", "2021-12-03")


################################
# Average revenue per customer #
################################
def average_revenue(company_VAT_number):
    dbase = sqlite3.connect('group42_project.db', isolation_level=None)
    quotes_invoices = dbase.execute('''
    SELECT customer_email As customer, total_amount, company_name
    FROM Quote
    INNER JOIN Invoice ON Quote_ID = Invoice_ID
    LEFT JOIN Company ON company_vat_number=vat_number
    WHERE Quote.Company_VAT_Number="{}"  AND Active = True
    '''.format(company_VAT_number)).fetchall()
    dbase.close()
    
    for quote in quotes_invoices:
        company_name = quote[2]
        break

    revenue_all = 0
    for amount in quotes_invoices:
        revenue_all += amount[1]

    number_customer = []
    for email in quotes_invoices:
        number_customer.append(email[0])
    
    #On compte le nombre de fois qu'il y a un même customer et on retire les doublons
    for customer in number_customer:
        apparitions = number_customer.count(customer)
        while apparitions > 1:
            number_customer.remove(customer)
            apparitions -= 1

    total_customer = len(number_customer)
    #total_quote = len(quote_invoice)
    #average_revenue_quote = revenue_all/total_quote
    average_revenue_customer = revenue_all/total_customer

    print("The average revenue per customer for all {} quotes is ".format(company_name) + str(average_revenue_customer) + " EUR")
    return "The average revenue per customer for all {} quotes is ".format(company_name) + str(average_revenue_customer) + " EUR"
#average_revenue("BE444444444")


#######################################
# 11. Number of clients for a company #
#######################################
def number_client(Company_VAT_Number):

    dbase = sqlite3.connect('group42_project.db', isolation_level=None)
    company_name = dbase.execute('''SELECT Company_Name FROM Company WHERE VAT_Number= ? ''',(Company_VAT_Number,)).fetchall()[0][0]
    #print("Company name: " + str(company_name))
    quote = dbase.execute('''SELECT * FROM Quote WHERE Company_VAT_Number = ? AND Active=TRUE''', (Company_VAT_Number,)).fetchall()
    number_quote = len(quote) #On récupère le nombre de quote pour ne pas le dépasser dans la boucle for
    
    customer_in_compagny = []
    
    #Le range permet de prendre la portée (ex: range(10) va prendre comme valeurs 0, 1, ..., 9)
    for number in range(number_quote):         # for num in range (6)
        id_quote = quote[number][0]
        customer_in_compagny.append(id_quote)
        
    #print("All quotes" + str(quote) , "and more precisely, the quote id :"+ str(customer_in_compagny))
    
    customer_email = []
    
    for id in customer_in_compagny:
        quote_to_invoice = dbase.execute('''SELECT Customer_Email FROM Invoice WHERE Quote_Reference= ?''',(id,)).fetchall()[0][0] #On part du principe que relation 1-1 entre quote et invoice
        customer_email.append(quote_to_invoice)
    
    #On compte le nombre de fois qu'il y a un même customer et on retire les doublons
    for email in customer_email:
        apparition = customer_email.count(email)
        while apparition > 1:
            customer_email.remove(email)
            apparition -= 1

    number_client = len(customer_email)
    #print(customer_email)

    subscription_id = []
    subscription_product = []
    for q in quote:
        subscription_id.append(q[2])
    for s in subscription_id:
        subscription_name=dbase.execute('''SELECT Subscription_Name FROM Subscription WHERE Subscription_ID=?''',(s,)).fetchall()[0][0]
        subscription_product.append(subscription_name)
    
    for subscription in subscription_product:
        apparition = subscription_product.count(subscription)
        while apparition > 1:
            subscription_product.remove(subscription)
            apparition -= 1
    # print(subscription_id)
    # print(subscription_name)
    # print(subscription_product)
    dbase.close()

    print("The company {} have ".format(company_name) + str(number_client) + " customers in total, for the following subscription(s) : "+ str(subscription_product))
    return "The company {} have ".format(company_name) + str(number_client) + " customers in total, for the following subscription(s) : "+ str(subscription_product)
#number_client("BE444444444")


################################################
# Table with customers and their subscriptions #
################################################
def customer_subscription(VAT):
    dbase = sqlite3.connect('group42_project.db', isolation_level=None)
    dbase.execute("PRAGMA foreign_keys = 1")

    query = '''SELECT Company_Name AS Company, Subscription_Name AS Subscription,Customer_Email AS Customer, Total_Amount AS Amount
    FROM Quote 
    INNER JOIN Invoice ON Invoice_ID = Quote_ID 
    INNER JOIN Subscription ON Subscription_Reference = Subscription_ID
    LEFT JOIN Company ON Quote.Company_VAT_Number = VAT_Number
    WHERE Quote.Company_VAT_Number="{}"  
    ORDER BY Customer_Email  '''.format(VAT)

    results = pd.read_sql_query(query,dbase)

    dbase.close()
    
    print(results)
    return results
#customer_subscription("BE444444444")

############################################################################################
# Bonus : Display some statistics for one company with "statistics" & "matplotlib" modules #
############################################################################################
def statistic_customer(VAT):
    dbase = sqlite3.connect('group42_project.db', isolation_level=None)
    customer_data=dbase.execute('''
    SELECT first_name AS firstname, last_name as lastname, birth_date AS birthday,customer_email As customer, company_vat_number as VAT, subscription_reference
    FROM Quote
    INNER JOIN Invoice ON Quote_ID = Invoice_ID
    LEFT JOIN Customer on customer_email=email
    WHERE Quote.Company_VAT_Number="{}"  
    '''.format(VAT)).fetchall()

    name_subscription_type = dbase.execute('''SELECT Subscription_Name FROM Subscription WHERE Company_VAT_Number="{}" '''.format(VAT)).fetchall()
    print(name_subscription_type)
    #print(name_subscription_type)
    #print(customer_data)

    subscription = {}
    for subscription_type in name_subscription_type:
        subscription[subscription_type[0]] = 0
    #print(subscription)
    
    for one_type in name_subscription_type:
        quantity_subscription =dbase.execute('''
        SELECT Subscription_Name, Quantity
        FROM Quote
        INNER JOIN Invoice ON Invoice_ID=Quote_ID
        LEFT JOIN Subscription on Subscription_Reference=Subscription_ID
        WHERE Quote.Company_VAT_Number="{vat}" AND Subscription_Name = "{name}"
        ORDER BY Quantity ASC
        '''.format(vat=VAT, name = one_type[0])).fetchall()
        quantity_for_one_type = 0
        for q in quantity_subscription:
            quantity_for_one_type+=q[1]
            subscription[q[0]] = quantity_for_one_type
        #print(quantity_for_one_type)
        #print(quantity_subscription)

    today = str(dt.datetime.now()) #2022-12-1
    d = today.split()
    date_ref = d[0]
    y_ref = date_ref.split("-")
    year_ref= int(y_ref[0])
    # print(today)
    # print(year_ref)

    customer_data_filter = []
    for data in customer_data:
        customer_data_filter.append(data[3])
    #print(customer_data_filter)

    for one in customer_data_filter:
        apparition = customer_data_filter.count(one)
        while apparition > 1:
            customer_data_filter.remove(one)
            apparition -= 1

    customer_age = []
    for client in customer_data_filter:
        c_age=dbase.execute('''SELECT Birth_Date FROM Customer WHERE Email = "{}" '''.format(client)).fetchall()[0][0]  #  [(1998-05-06)]
        date_age=c_age.split("-")
        year_age=int(date_age[0])
        customer_age.append(year_age)

    #print(customer_age)
    
    data_age = []
    for person in customer_age:
        age = year_ref-int(person)
        data_age.append(age)

    average_age = statistics.mean(data_age)
    median_age = statistics.median(data_age)
    mode_age = statistics.mode(data_age)
    standard_deviation_age = statistics.stdev(data_age)
    variance_age = statistics.variance(data_age)

    plt.hist(data_age)
    plt.title('Histogram of user ages', loc="center", fontstyle='italic', color='red')
    plt.xlabel('Age', color='red')
    plt.ylabel('Number of customers', color='red')
    plt.show()

    dbase.close()
    
    print1 = "The average age of the company's subscription users is " + str(average_age) +" Years " + " ,the median age is " +str(median_age) + ", the mode is "+ str(mode_age) +", the standard deviation is " + str(standard_deviation_age) + " , and finally, the variance is " +str(variance_age)
    print2 = "The following table shows the most popular products :" + str(subscription)
    print(print1 + print2)
    return str(print1) + str(print2)

#statistic_customer("BE444444444")

# def delete_record(id):
#     dbase.execute(''' DELETE from employee_records WHERE ID =''' + str(id))
#     print('Deleted')
#     return 'Deleted'






dbase.close()