import sqlite3
import fill_tables
import script
import datetime as dt

# We need to import the Request object as well:
from fastapi import FastAPI, Request
import uvicorn

app = FastAPI()

@app.get("/")
def root():
      return {"message": "It works !"}

##########################
# 1. Register a customer #
##########################
@app.post("/register_customer")
async def register_customer(payload: Request):
      values_dict = await payload.json() #Dictionnaire de pairs
      
      fill_tables.insert_Customer(str(values_dict['Email']),
                                          str(values_dict['First_Name']),
                                          str(values_dict['Last_Name']),
                                          str(values_dict['Birth_Date']),
                                          str(values_dict['Password']),
                                          str(values_dict['Address']),
                                          str(values_dict['Billing_Address']),
                                          str(values_dict['Credit_Card'])
                                          )
      
      return "Customer {email} correctly registered to database".format(email = str(values_dict['Email']))


#########################
# 2. Register a company #
#########################
@app.post("/register_company")
async def register_company(payload: Request):
      values_dict = await payload.json() #Dictionnaire de pairs
      
      fill_tables.insert_Company(str(values_dict['VAT_Number']),
                                         str(values_dict['Company_Name']),
                                         str(values_dict['Address']),
                                         str(values_dict['Bank_Account'])
                                         )
      
      return "{name} correctly registered to database".format(name = str(values_dict['Company_Name']))


##############################
# 3. Register a subscription #
##############################
@app.post("/register_subscription")
async def register_subscription(payload: Request):
      values_dict = await payload.json() #Dictionnaire de pairs
      
      fill_tables.insert_Subscription(str(values_dict['Subscription_Name']),
                                              str(values_dict['Single_Price']),
                                              str(values_dict['Currency']),
                                              str(values_dict['Company_VAT_Number'])
                                              )
      
      return "{sub_name} from company {vat} correctly added to database".format(sub_name = str(values_dict['Subscription_Name']), vat = str(values_dict['Company_VAT_Number']))
  

#######################
# 4. Register a quote #
#######################
@app.post("/register_quote")
async def register_quote(payload: Request):
      values_dict = await payload.json() #Dictionnaire de pairs
      
      subscription_id = str(values_dict['Subscription_Reference'])
      
      dbase = sqlite3.connect('group42_project.db', isolation_level=None, check_same_thread=False) #open db
      Company_VAT_Number_In_Subscription = dbase.execute('''SELECT Company_VAT_Number FROM Subscription WHERE Subscription_ID = ?''', (subscription_id )).fetchall()[0][0]
      dbase.close() #close db
      
      
      if str(values_dict['Active']) == "False": #On ne peut pas créer une quote directement avec le statut "Active : TRUE" car elle ne serait liée à aucune invoice
            fill_tables.insert_Quote(str(Company_VAT_Number_In_Subscription),
                                             str(values_dict['Subscription_Reference']),
                                             str(values_dict['Quantity']),
                                             str(values_dict['Currency']),
                                             False
                                             )
            
            return "Subcription number {reference} from {vat} added to database".format(reference = str(values_dict['Subscription_Reference']), vat = str(Company_VAT_Number_In_Subscription))
      else:
            return "You cannot create a quote with an Active status on TRUE"


#############################
# 5. Display specific quote #
#############################
@app.post("/display_specific_quote")
async def display_specific_quote(payload: Request):
      values_dict = await payload.json()
      dbase = sqlite3.connect('group42_project.db', isolation_level=None, check_same_thread=False)
      
      specific = dbase.execute(''' SELECT Company_VAT_Number, Subscription_Reference, Quantity, Price_Without_VAT, Price_With_VAT, Currency, Active FROM Quote
                               WHERE Quote_ID = {}'''.format(str(values_dict['quote_id']))).fetchall()
      quote = {"Company_VAT_Number" : [], "Subscription_Reference" : [], "Quantity" : [], "Price_Without_VAT" : [], "Price_With_VAT" : [], "Currency" : [], "Active" : []}
      position = 0
      for key in quote:
            for value in specific:
                  quote[key].append(value[position])
                  position = position + 1
      dbase.close()
      return quote


######################################################
# 6. Accept quote -> automatically create an invoice #
######################################################
@app.post("/accept_quote")
async def accepte_quote(payload: Request):
      values_dict = await payload.json() #Dictionnaire de pairs
      
      
      
      
      #Servira à vérifier que le statut de la quote n'est pas "Active : TRUE"
      quote_id = str(values_dict['Quote_Reference'])

      #On vérifie si le numéro de la quote est dans la database aka si elle existe
      dbase = sqlite3.connect('group42_project.db', isolation_level=None, check_same_thread=False)
      check_if_quote_exists = dbase.execute(''' SELECT * FROM Quote WHERE Quote_ID = ?''', (quote_id,)).fetchall()
      dbase.close()
      
      if len(check_if_quote_exists) == 1:
            
            #On récupère le statut de la quote sélectionnée
            dbase = sqlite3.connect('group42_project.db', isolation_level=None, check_same_thread=False)
            quote_statut = dbase.execute(''' SELECT * FROM Quote WHERE Quote_ID = ?''', (quote_id,)).fetchall()[0][7]
            dbase.close()
            
            if quote_statut == True:
                  return "This quote is already binded to an invoice, please create a new quote"
            
            elif quote_statut == False:
                  
                  fill_tables.insert_Invoice(str(values_dict['Quote_Reference']),
                                                str(values_dict['Customer_Email']),
                                                str(values_dict['End_Date']),
                                                str(values_dict['Currency'])
                                                )
                  
                  #We update the "Active" statut of the current quote to TRUE
                  dbase = sqlite3.connect('group42_project.db', isolation_level=None, check_same_thread=False)
                  
                  dbase.execute('''UPDATE Quote SET Active = ? WHERE Quote_ID = ?''', (True, quote_id,))
                  
                  dbase.close()
                  
                  return "New quote number {reference} correctly registered for {email}".format(reference = str(values_dict['Quote_Reference']), email = str(values_dict['Customer_Email']))
      else:
            return "This quote doesn't exist."


##############################################
# 7. Check if customer has a pending invoice #
##############################################
@app.post("/check_pending_invoice")
async def check_pending_invoice(payload: Request):
      values_dict = await payload.json() #Dictionnaire de pairs
      
      return script.request_invoice(str(values_dict['Email'])) #Permet de retourner le "return" de la fonction request_invoice


################################################
# 8. Pay invoice by using CC stored in account #
################################################
@app.post("/pay_invoice")
async def pay_invoice(payload: Request):
      values_dict = await payload.json() #Dictionnaire de pairs
      
      customer_email = str(values_dict['Customer_Email'])
      invoice_id = int(values_dict["Invoice_Reference"])
      
      #Servira à check si l'invoice existe
      dbase = sqlite3.connect('group42_project.db', isolation_level=None, check_same_thread=False) #open db
      check_if_invoice_exists = len(dbase.execute('''SELECT * FROM Invoice WHERE Customer_Email = ? AND Invoice_ID = ?''', (customer_email, invoice_id,)).fetchall())
      dbase.close()

      if check_if_invoice_exists == 1:
            
            #Servira à vérifier si la date d'invoice < aujourd'hui (et dans ce cas là on a une invoice à payer)
            dbase = sqlite3.connect('group42_project.db', isolation_level=None, check_same_thread=False) #open db
            Invoice_Date = dbase.execute('''SELECT Invoice_Date FROM Invoice WHERE Customer_Email = ? AND Invoice_ID = ?''', (customer_email, invoice_id,)).fetchall()[0][0]
            dbase.close()
            
            invoice_date_number = Invoice_Date.replace("-","")
            today = str(dt.datetime.now()).split(" ")[0]
            today_number = today.replace("-", "")

            if int(invoice_date_number) <= int(today_number): #On regarde si la date de facturation <= aujourd'hui (si c'est =, on doit aussi payer)
                  
                  #On récupère le prix de l'invoice pour s'assurer que le montant encodé est le bon
                  dbase = sqlite3.connect('group42_project.db', isolation_level=None, check_same_thread=False) #open db
                  correct_price = str(dbase.execute('''SELECT Total_Amount FROM Invoice WHERE Customer_Email = ? AND Invoice_ID = ?''', (customer_email, invoice_id)).fetchall()[0][0])
                  price_entered = str(values_dict['Amount_Paid_EUR'])
                  dbase.close()
                  
                  if price_entered == correct_price:
                        
                        #On récupère la CC enregistrée dans le compte du client et on prend la date sur l'invoice
                        dbase = sqlite3.connect('group42_project.db', isolation_level=None, check_same_thread=False) #open db
                        CC_registered = dbase.execute('''SELECT Credit_Card FROM Customer WHERE Email = ?''', (customer_email, )).fetchall()[0][0]
                        dbase.close()
                        
                        if script.CC_check(CC_registered) == True: #Si la carte est valide
                              
                              script.Pay_Invoice(str(values_dict['Invoice_Reference']),
                                                      str(values_dict['Customer_Email']),
                                                      str(CC_registered),
                                                      str(values_dict['Amount_Paid_EUR']),
                                                      str(values_dict['Currency'])
                                                      )
                              
                              #On augmente le mois de facturation d'un mois vu que le précédent a été payé
                              script.Invoice_paid(str(values_dict['Invoice_Reference']))    
                              
                              return script.Pay_Invoice(str(values_dict['Invoice_Reference']),
                                                            str(values_dict['Customer_Email']),
                                                            str(CC_registered),
                                                            str(values_dict['Amount_Paid_EUR']),
                                                            str(values_dict['Currency'])
                                                            ) #Permet de renvoyer le "return" de la fonction Pay_Invoice
                        else:
                              return "Sorry " + str(values_dict['Customer_Email']) + " but your CC is incorrect, please update it"
                  else:
                        return "Sorry " + str(values_dict['Customer_Email']) + ", you don't have entered the right amount. You have to pay " + str(correct_price) + "€"
            else:
                  return "Hello " + str(values_dict['Customer_Email']) + ", you don't have pending invoice"
      else:
            return "The invoice number is not yours or doesn't exist. If you think this is an error, please contact your administrator."


################################
# 9. Update CC and pay invoice #
################################
@app.post("/update_cc_and_pay_invoice")
async def update_cc_and_pay_invoice(payload: Request):
      values_dict = await payload.json() #Dictionnaire de pairs
      
      customer_email = str(values_dict['Customer_Email'])
      invoice_id = int(values_dict["Invoice_Reference"])
      
      
      #Servira à check si l'invoice existe      
      dbase = sqlite3.connect('group42_project.db', isolation_level=None, check_same_thread=False) #open db
      check_if_invoice_exists = len(dbase.execute('''SELECT * FROM Invoice WHERE Customer_Email = ? AND Invoice_ID = ?''', (customer_email, invoice_id,)).fetchall())
      dbase.close() #close db

      
      if check_if_invoice_exists == 1:
            
            #Servira à vérifier si la date d'invoice < aujourd'hui (et dans ce cas là on a une invoice à payer)
            dbase = sqlite3.connect('group42_project.db', isolation_level=None, check_same_thread=False) #open db
            Invoice_Date = dbase.execute('''SELECT Invoice_Date FROM Invoice WHERE Customer_Email = ? AND Invoice_ID = ?''', (customer_email, invoice_id,)).fetchall()[0][0]
            dbase.close()
            
            invoice_date_number = Invoice_Date.replace("-","")
            today = str(dt.datetime.now()).split(" ")[0]
            today_number = today.replace("-", "")
            
            if int(invoice_date_number) <= int(today_number): #On regarde si la date de facturation <= aujourd'hui (si c'est =, on doit aussi payer)
                  
                  #On récupère le prix de l'invoice pour s'assurer que le montant encodé est le bon
                  dbase = sqlite3.connect('group42_project.db', isolation_level=None, check_same_thread=False) #open db
                  correct_price = str(dbase.execute('''SELECT Total_Amount FROM Invoice WHERE Customer_Email = ? AND Invoice_ID = ?''', (customer_email, invoice_id,)).fetchall()[0][0])
                  price_entered = str(values_dict['Amount_Paid_EUR'])
                  dbase.close()

                  if price_entered == correct_price:
                        
                        New_CC = str(values_dict['CC'])
                        
                        if script.CC_check(New_CC) == True: #Si la nouvelle carte est valide

                              script.Pay_Invoice(str(values_dict['Invoice_Reference']),
                                                      str(values_dict['Customer_Email']),
                                                      str(values_dict['CC']),
                                                      str(values_dict['Amount_Paid_EUR']),
                                                      str(values_dict['Currency'])
                                                      )
                              
                              #On met à jour la CC présente dans le compte du client avec la nouvelle carte valide
                              dbase = sqlite3.connect('group42_project.db', isolation_level=None, check_same_thread=False)
                              dbase.execute('''UPDATE Customer SET Credit_Card = ? WHERE Email = ?''', (New_CC, str(values_dict['Customer_Email'])))
                              dbase.close()
                              
                              #On augmente le mois de facturation d'un mois vu que le précédent a été payé
                              script.Invoice_paid(str(values_dict['Invoice_Reference']))
                              
                              
                              return script.Pay_Invoice(str(values_dict['Invoice_Reference']),
                                                            str(values_dict['Customer_Email']),
                                                            str(values_dict['CC']),
                                                            str(values_dict['Amount_Paid_EUR']),
                                                            str(values_dict['Currency'])
                                                            ) #Permet de renvoyer le "return" de la fonction Pay_Invoice
                                    
                        elif script.CC_check(New_CC) == False: #Si la nouvelle carte n'est pas valide
                              return "Sorry " + str(values_dict['Customer_Email']) + " but your CC is still incorrect, please update it"
                  else:
                        return "Sorry " + str(values_dict['Customer_Email']) + ", you don't have entered the right amount. You have to pay " + str(correct_price) + "€ for invoice #" + str(values_dict['Invoice_Reference'])
            else:
                  return "Hello " + str(values_dict['Customer_Email']) + ", you don't have pending invoice"
      else:
            return "The invoice number is not yours or doesn't exist. If you think this is an error, please contact your administrator."


################################################################################
# 10. Display MRR & ARR and the average revenue per customer for one compagnie #
################################################################################
@app.post("/display_analytics")
async def display_analytics(payload: Request):
      values_dict = await payload.json() #Dictionnaire de pairs
      
      Company_VAT = str(values_dict['Company_VAT_Number'])
      Date = str(values_dict['Choosen_Date'])

      #Servira à check si la compagnie existe    
      dbase = sqlite3.connect('group42_project.db', isolation_level=None, check_same_thread=False) #open db
      check_if_company_exists = len(dbase.execute('''SELECT * FROM Company WHERE VAT_Number = ? ''', (Company_VAT,)).fetchall())
      dbase.close() #close db
      
      if check_if_company_exists == 1 and len(Date) == 10:
            MRR = script.MRR(Company_VAT, Date)
            ARR = script.ARR(Company_VAT, Date)
            Average_revenue = script.average_revenue(Company_VAT)
      
            return (MRR, ARR, Average_revenue)
      else:
            return "The VAT you have entered doesn't exist in our database or the date format is not correct. The right format is YYYY-MM-DD."


#################################################
# 11. Display number of clients for a compagnie #
#################################################
@app.post("/display_customer")
async def display_customer(payload: Request):
      values_dict = await payload.json() #Dictionnaire de pairs
      
      Company_VAT = str(values_dict['Company_VAT_Number'])
      
      #Servira à check si la compagnie existe      
      dbase = sqlite3.connect('group42_project.db', isolation_level=None, check_same_thread=False) #open db
      check_if_company_exists = len(dbase.execute('''SELECT * FROM Company WHERE VAT_Number = ? ''', (Company_VAT,)).fetchall())
      dbase.close() #close db      
      
      if check_if_company_exists == 1:
            clients = script.number_client(Company_VAT)
            
            return clients
      else:
            return "The VAT you have entered doesn't exist in our database."


######################################################
# 12. Show customer and subscription for one company #
######################################################
@app.post("/display_cust_sub")
async def display_cust_sub(payload: Request):
      values_dict = await payload.json()
      
      Company_VAT = str(values_dict['Company_VAT_Number'])
      
      #Servira à check si la compagnie existe      
      dbase = sqlite3.connect('group42_project.db', isolation_level=None, check_same_thread=False) #open db
      check_if_company_exists = len(dbase.execute('''SELECT * FROM Company WHERE VAT_Number = ? ''', (Company_VAT,)).fetchall())
      dbase.close() #close db
      
      if check_if_company_exists == 1:
      
            table = script.customer_subscription(Company_VAT)
            
            return table
      else:
            return "The VAT you have entered doesn't exist in our database."

##############################################################
# 13. Display statistic about the customer for one compagnie #
##############################################################
@app.post("/display_stat")
async def display_stat(payload: Request):
      values_dict = await payload.json() #Dictionnaire de pairs
      
      Company_VAT = str(values_dict['Company_VAT_Number'])
      
      #Servira à check si la compagnie existe      
      dbase = sqlite3.connect('group42_project.db', isolation_level=None, check_same_thread=False) #open db
      check_if_company_exists = len(dbase.execute('''SELECT * FROM Company WHERE VAT_Number = ? ''', (Company_VAT,)).fetchall())
      dbase.close() #close db
      
      if check_if_company_exists == 1:
            stat = script.statistic_customer(Company_VAT) 
            
            return (stat)
      else:
            "The VAT you have entered doesn't exist in our database."


if __name__ == '__main__':
      uvicorn.run(app, host='127.0.0.1', port=8000)
  
