import sqlite3 as sl
from datetime import date
import pprint
import pandas as pd
import sys
class Bank:
    """
    This is Bank class to query Bank table. It is a Read-Only class.

    Attributes:
    bankmain - Read Only property 
    """
    def __init__(self):
        """
        Contructor for Bank class.
        """
        c=dbcon.cursor()
        self._bankmain = c.execute("select * from Bank").fetchall()
        pprint.pprint('\nWelcome to '+self._bankmain[0][1]+' portal')
        print("\nBank Code, address and phone number for your quick reference: ")
        pprint.pprint(self._bankmain[0])
    @property
    def bankmain(self):
        return self._bankmain
class BankBranch(Bank):
    """
    This is to query and operate on Branchs of the Bank. 

    Attributes:
    branchcode - branch code
    branchname - branch name 
    branchdetails - branch details from the BankBranch SQLite table
    branchdict - Dictionary form of the branch details
    """
    def __init__(self,brcode='',brname=''):
        self.branchcode = brcode
        self.branchname = brname
        self.branch()
    def branch(self):
        """
        This function is to query on the database and get the branch's details

        Args:
        No Args, self

        Returns:
        branchdict - dictionary form of the branch details
        """
        c=dbcon.cursor()
        self.branchdetails = c.execute("select * from BankBranch where BranchCode =? or BranchName =?",(self.branchcode,self.branchname)).fetchall()
        columns = c.description 
        self.branchdict = [{columns[index][0]:column for index, column in enumerate(value)} for value in self.branchdetails]
        return self.branchdict 
class AccountHolder:
    #CustID|FirstName|LastName|Address|PhoneNo|DOB|POC|StateID|BranchCode
    """
    This class is to hold and operate on Account Holder details i.e, customer details

    Attributes:
    custid - Customer ID to hold account holder id
    allaccounts - AllAccounts related to the customer id
    allaccountsdict - Dictorinary form of the allaccounts
    """
    def __init__(self, custid):
        #class Accountholder instead
        self.custid = custid
        self.allaccountsdict = {}
    def getdetails(self):
        """
        This function fetches the details of a particular customer ID

        Args:
        None, Self

        Returns:
        custdict - Dictionary form of customer details 
        """
        c=dbcon.cursor()
        custdetails = c.execute("select * from AccountHolder where CustID =%a;" %self.custid).fetchall()
        columns = c.description 
        custdict = [{columns[index][0]:column for index, column in enumerate(value)} for value in custdetails]
        return custdict
    def updatedetails(self, fname, lname, address, phno ):
        """
        Updates the AccountHolder details like fname, lname, address,phno into the DB

        Args:
        fname string 
        lname string 
        address string 
        phno number

        Returns:
        None
        """
        c=dbcon.cursor()
        c.execute("update AccountHolder set firstname = ?, lastname = ?, address = ?, PhoneNo = ? where custid=?",(fname, lname, address, phno,self.custid))
        dbcon.commit()
        print('Details updated succesfully to:')
        custdetails = c.execute("select * from AccountHolder where CustID =%a"%self.custid).fetchall()
        columns = c.description
        custdict = [{columns[index][0]:column for index, column in enumerate(value)} for value in custdetails]
        pprint.pprint(custdict)
    def getlinkedAccounts(self):
        """
        Fetches the accounts linked to the current customer ID and assigns to allaccountsdict

        Args:
        None, self

        Returns:
        None
        """
        c=dbcon.cursor()
        self.allaccounts = c.execute("select * from Account where custid =%a;" %self.custid).fetchall()
        columns = c.description 
        self.allaccountsdict = [{columns[index][0]:column for index, column in enumerate(value)} for value in self.allaccounts]
    def accessaccount(self):
        """
        To retrieve an account related to the customer. 
        Asks user to enter an account number and searches through the account numbers of the customer.
        Allows user to call deposit or withdraw actions.
        Args:
        None/self

        Returns:
        None
        """
        print('Which account do you want to access')
        custinput = int(input())
        found = 0
        for each in self.allaccountsdict:
            if (int(each['AccountNumber']) == custinput):
                acchandle= Account(int(each['AccountNumber']))
                found=1
                break
        if found == 0:
            print('Account not found')
            return
        print('Choose an option 1.Deposit 2.Withdraw')
        opt = int(input())
        print('Enter the amount in USD')
        amt=int(input())
        if opt == 1:
            acchandle.getAccountDetails()
            acchandle.deposit(amt)
        elif opt == 2:
            acchandle.getAccountDetails()
            acchandle.withdraw(amt)
        else:
            print('Wrong option selected')
class Account:
    """
    To access Account details from the DB and operate on it. 
    Lets you deposit, update transaction log and retrive log.

    Attributes:
    accno - current account number to be accessed/operated upon
    accdetails - account details of a given account in list form
    accdetailsdict - dictionary form of account details
    """
    def __init__(self, accno):
        self.accno = accno
    #AccountType|AccountNumber|CustID|BalanceinUSD|InterestRate
    def getAccountDetails(self):
        """
        This method lets us access the Account table and get details into a list and dictionary format.

        Args:
        None/self

        Returns:
        self.accdetails
        self.accdetailsdict
        """
        c=dbcon.cursor()
        self.accdetails = c.execute("select * from Account where AccountNumber =%a" %self.accno).fetchall()
        columns = c.description 
        self.accdetailsdict = [{columns[index][0]:column for index, column in enumerate(value)} for value in self.accdetails]
        return self.accdetailsdict
    def updatetransactionlog(self, accno, balancebefore,debcre,balanceafter):
        """
        This updates the transaction log(txt file) everytime user deposits or withdraws an amount. 
        It logs acc no, balance before transaction, debit/credit, balance after the transaction, date.

        Args:
        self, accno, balancebefore,debcre,balanceafter

        Returns:
        None
        """
        f = open('/Users/SG/sqlite/transactionlog.txt','a')
        f.write('{}\t{}\t{}\t{}\t{}\n' .format(accno, balancebefore,debcre,balanceafter,date.today()))
        f.close()
    def gettransactions(self):
        """
        Lets us retrive the transactions of the current account number.

        Args:
        None/self

        Returns:
        None
        """
        df=pd.DataFrame
        df = pd.read_csv('/Users/SG/sqlite/transactionlog.txt', sep='\t',header =0)
        for i in df.index:
            if int(df['AccountNumber'][i]) == self.accno and df['DateofTransaction'][i] == str(date.today()):
                print(df.loc[[i]].values)
    def deposit(self, amt):
        """
        Lets the user deposit amount(USD) into the account.
        Gives a confirmation if the transaction is succesful. 

        Args:
        amt

        Returns:
        None
        """
        self.accdetailsdict[0]['BalanceinUSD'] = self.accdetailsdict[0]['BalanceinUSD'] + amt
        c=dbcon.cursor()
        c.execute("update Account set BalanceinUSD = ? where AccountNumber=?",(self.accdetailsdict[0]['BalanceinUSD'],self.accdetailsdict[0]['AccountNumber']))
        dbcon.commit()
        self.accdetails = c.execute("select * from Account where AccountNumber =%a" %self.accdetailsdict[0]['AccountNumber']).fetchall()
        columns = c.description 
        self.accdetailsdict = [{columns[index][0]:column for index, column in enumerate(value)} for value in self.accdetails]
        print("Transaction succesfull")
        print("Final balance: %s" %self.accdetailsdict[0]['BalanceinUSD'])
        self.updatetransactionlog(self.accdetailsdict[0]['AccountNumber'],self.accdetailsdict[0]['BalanceinUSD']-amt,'Credit',self.accdetailsdict[0]['BalanceinUSD'])        
    def withdraw(self,amt):
        """
        Lets user withdraw an amount specified. For savings account, balance should be a min of 1000.
        For current account, no min balance required. It should not go negative though. 
        Displays if transaction is succesful after commiting.

        Args:
        self, amt

        Returns:
        None
        """
        if self.accdetailsdict[0]['AccountType'] == 'Savings':
            if self.accdetailsdict[0]['BalanceinUSD'] - amt < 1000:
                print("not enough funds, min balance limit reached")
        elif self.accdetailsdict[0]['AccountType'] == 'Current':
            if self.accdetailsdict[0]['BalanceinUSD'] - amt < 0:
                print("not enough funds, min balance limit reached")
        else:
            self.accdetailsdict[0]['BalanceinUSD'] = self.accdetailsdict[0]['BalanceinUSD'] - amt
            c=dbcon.cursor()
            c.execute("update Account set BalanceinUSD = ? where AccountNumber=?",(self.accdetailsdict[0]['BalanceinUSD'],self.accdetailsdict[0]['AccountNumber']))
            dbcon.commit()
            print("Transaction succesfull")
            print("Remaining balance: %s" %self.accdetailsdict[0]['BalanceinUSD'])
            self.updatetransactionlog(self.accdetailsdict[0]['AccountNumber'],self.accdetailsdict[0]['BalanceinUSD']+amt,'Debit',self.accdetailsdict[0]['BalanceinUSD'])
class Employee:
    """
    Employee class lets you query on and handle the employee details. 
    It authenticates and lets the employee perform operations based on his/her role.

    Attributes:
    empid
    pwd
    """
    #EmployeeID|EmployeeName|EmployeeDesignation|EmployeeSecretCode
    def __init__(self,empid,pwd):
        self.empid = empid
        self.pwd = pwd
    def authenticateemployee(self, desig):
        """
        This method authenticates the user/employee by using the empid, pwd and designation.
        If authenticates succeeds, returns 1. If it fails returns 0.

        Args:
        desig

        Returns:
        1 or 0 based on employee authentication result.
        """
        c=dbcon.cursor()
        empdetails = c.execute("select EmployeeName from Employee where EmployeeID =? and EmployeeSecretCode = ? and EmployeeDesignation=?", (self.empid,self.pwd,desig)).fetchall()
        if len(empdetails) == 0:
            return 0
        else:
            return 1
    def accessTransactionLog(self):
        """
        This method lets the Employee access transaction log. 
        Lets user chose if he/she wants to see all transactions or just ones related to one Account ID.
        Asks user to enter an account ID and prints out all the transactions of that id.

        Args:
        None/self

        Returns:
        None
        """
        df=pd.DataFrame
        df = pd.read_csv('/Users/SG/sqlite/transactionlog.txt', sep='\t',header =0)
        print('Choose an option to get transaction history:\n1.Of an Account ID 2.All transactions')
        inp = int(input())
        if inp ==1:
            print('Enter Account number')
            accno = int(input())
            for i in df.index:
                if int(df['AccountNumber'][i]) == accno:
                    print(df.loc[[i]].values)
        elif inp == 2:
            print(df)
class AccountManager(Employee):
    """
    Inherits Employee class. But this is specific to handle Account Manager designated Employee.
    Lets user to do additional methods like createCustomer, createAccount and accessAccountDetails.

    Attributes:
    None/ Inherits empid and pwd from Employee
    """
    def createCustomer(self):
        """
        Lets user to create a customer entry in table Customer.
        Takes CustID|FirstName|LastName|Address|PhoneNo|DOB|POC|StateID|BranchCode and inserts into table.

        Args:
        None

        Returns:
        None
        """
        list1=[]
        print('Enter Customer Details in order in new lines:\nCustID|FirstName|LastName|Address|PhoneNo|DOB|POC|StateID|BranchCode')
        for line in sys.stdin:
            if line == '':
                break
            list1.append(line)
        c=dbcon.cursor()
        c.execute("insert into AccountHolder values (?,?,?,?,?,?,?,?,?)", tuple(list1)).fetchall()
        dbcon.commit()
        print('Customer Created')
        print('Create account 1.Now 2.Later')
        if int(input()) == 1:
            self.createAccount()
        return
    def createAccount(self):
        """
        Lets user create an account. 
        Takes user input AccountType|AccountNumber|CustID|BalanceinUSD|InterestRate and creates account in Account table.

        Args:
        None

        Returns:
        None
        """
        print('Enter Account Details in order in new lines:\nAccountType|AccountNumber|CustID|BalanceinUSD|InterestRate')
        list2 =[]
        for line in sys.stdin:
            list2.append(line)
        c=dbcon.cursor()
        c.execute("insert into Account values (?,?,?,?,?,?,?,?,?)", tuple(list2))
        dbcon.commit()
        print('Account Created')
        return
    def accessAccountDetails(self,custid):
        """
        Lets user access Account Details of all accounts of particular customer using custid.
        Calls methods Accountholder.accessaccount(), Accountholder.getlinkedAccounts() and Accountholder.accessaccount()

        Args:
        custid

        Returns:
        None
        """
        custhandle = AccountHolder(custid)
        print('What would you like to do:\n1. Get customer details\n2. Get Accounts of the customer')
        opt = int(input())
        if opt == 1:
            print(custhandle.getdetails())
            print('Access the account details further: 1.Yes 2.Quit')
            if int(input()) ==1:
                custhandle.accessaccount()
            else:
                return
        elif opt == 2:
            custhandle.getlinkedAccounts()
class CustCare(Employee):
    """
    This class is to handle employee of desgination Customer Care.
    Inherits Employee class.
    Has no additional methods or attributes.

    Attributes:
    None
    """
    pass
class NetBanking:
    #UserID|UserPwd|CustID
    """
    This class is to handle internet banking account of a customer. 
    Authenticates the account holder using userid and password.
    Lets user access AccountHolder class if authentication succeeds.

    Attributes:
    uid
    pwd
    """
    def __init__(self,uid, pwd):
        self.userid = uid
        self.loginandproceed(pwd)
    def loginandproceed(self,pwd):
        """
        Lets customer login and access other classes as applicable.

        Args:
        self, pwd

        Returns:
        None
        """
        c=dbcon.cursor()
        customerid = c.execute("select custid from NetBanking where userid =? and userpwd = ?", (self.userid,pwd)).fetchall()
        for i in range(3):
            if customerid:
                print(customerid)
                custhandle = AccountHolder(customerid[0])
                custfulldetails = custhandle.getdetails()
                custhandle.getlinkedAccounts()
                print('Welcome, here are your details'+ custfulldetails[0]['FirstName'] +' '+ custfulldetails[0]['LastName'])
                print('\nHere are your available accounts\n')
                print(custhandle.allaccountsdict)
                print('Choose an option: 1.Access Account 2.Exit')
                if int(input()) == 1:
                    custhandle.accessaccount()
                elif int(input()) ==2:
                    break
                break
            else:
                if i != 2:
                    print('Authentication failed. Enter again')
                else:
                    print('Maximum attempts reached. Try again on a different day')
class Interaction:
    """
    This is basically an interaction related class. Does not handle any Object/Item related to banking.
    It starts the conversation with user, takes inputs and calls the appropriate classes/methods.

    Attributes:
    None
    """
    def talk(self,level):
        """
        Talks to customer and takes input. Leads the way as per user input.

        Args:
        level

        Returns:
        none
        """
        if level == 1:
            print('Please select the type of login: 1. Account Manager 2. Customer Care 3. NetBanking')
            userinput= int(input())
            if userinput == 1:
                print('Hi there. Please enter your ID and secretcode')
                userid,pwd = int(input()),input()
                be=AccountManager(userid,pwd)
                if be.authenticateemployee('AccountManager') == 1:
                    print('What would you like to do:\n1.Access a customer account 2.Access transaction log 3.Create customer 4.Create account')
                    inp = int(input())
                    if inp == 1:
                        print('Enter Customer ID')
                        cusid = int(input())
                        print(cusid)
                        be.accessAccountDetails(cusid)
                    elif inp ==2:
                        be.accessTransactionLog()
                    elif inp ==3:
                        be.createCustomer()
                    elif inp ==4:
                        be.createAccount()
                    else:
                        print('Wrong input')
                else: 
                    print('Authentication failed try later')
            elif userinput == 2:
                print('Hi there, Please enter your ID and secretcode')
                userid,pwd = int(input()),input()
                bc=CustCare(userid,pwd)
                if bc.authenticateemployee('CustomerCare') == 1:
                    bc.accessTransactionLog()
                else: 
                    print('Authentication failed try later')
            elif userinput == 3:
                print('Hi AccountHolder, please enter your CustID and Pwd')
                userid, pwd = input(),input()
                cust = NetBanking(userid,pwd)
        elif level == 2:
            print('Thank you for banking with us. Bye')

#main
try:
    dbcon = sl.connect('/Users/SG/sqlite/Banking_System.db')
    bank = Bank()
    talktocust = Interaction()
    print('Enter option 1. Login 2. Logout')
    i = input()
    if int(i) == 1:
        talktocust.talk(1)
    else:
        talktocust.talk(2)
    print('BuBye')
except:
    print("Something went wrong in main logic")
finally:
    dbcon.close()
