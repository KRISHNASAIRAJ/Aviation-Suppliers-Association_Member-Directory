import csv
import os
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from prettytable import PrettyTable

class Data(webdriver.Chrome):
    def __init__(self, driver_path=r'E:/Projects/Web Scraping/', teardown=False):
        self.driver_path = driver_path
        self.teardown = teardown
        os.environ['PATH'] += self.driver_path
        options = webdriver.ChromeOptions()  # Class for dev tools options
        options.add_experimental_option('excludeSwitches', ['enable-logging'])  # Removing warnings
        super(Data, self).__init__(options=options)
        self.implicitly_wait(10)
        self.maximize_window()

    # def __exit__(self, exc_type: Type[BaseException], exc: BaseException, traceback: TracebackType):
    #     if self.teardown:
    #         self.quit()

    def landing_page(self):
        self.get('https://www.aviationsuppliers.org/member-directory')
        self.implicitly_wait(30)
        time.sleep(3)

    def extract_data(self):
        df = pd.read_csv('data.csv')
        company_names = df['name']  # Skipping the first row
        res=[]
        count=981
        for company_name in company_names:
            print("Remaining:",count)
            print()
            count-=1
            try:
                search_box_ele = self.find_element(By.XPATH, '//*[@id="page24"]/div/div/div/table/tbody/tr/td/div/div[2]/div/div/div/figure/form/table/tbody/tr[4]/td[1]/table/tbody/tr/td[1]/input')
                search_box_ele.click()
                search_box_ele.clear()
                search_box_ele.send_keys(company_name)
                search_box_ele.send_keys(Keys.ENTER)
                self.implicitly_wait(10)
                
                company_ele = self.find_element(By.XPATH, '//*[@id="resContainer"]/table/tbody/tr/td[1]/a')
                company_ele.click()
                self.implicitly_wait(20)
                
                # Company name
                try:
                    company_name_ele = self.find_element(By.CLASS_NAME, 'subHead')
                    company_name_text = company_name_ele.get_attribute('innerHTML')
                except:
                    company_name_text = ""
                
                # Address
                try:
                    full_text = self.find_element(By.XPATH, '//*[@id="resContainer"]/table/tbody/tr[1]/td[1]').text
                    address = full_text.split('Contact:')[0].strip()  # Everything before 'Contact:' is the address
                    address_lines = address.split('\n')
                except:
                    address_lines = [""]

                # Contact person
                try:
                    contact_ele = self.find_element(By.XPATH, '//*[@id="resContainer"]/table/tbody/tr[1]/td[1]/a[1]')
                    contact_person = contact_ele.text
                except:
                    contact_person = ""

                # Contact position
                try:
                    contact_position = self.find_element(By.XPATH, '//*[@id="resContainer"]/table/tbody/tr[1]/td[1]').text.split('Contact: ')[1].split(' - ')[1].split('\n')[0]
                except:
                    contact_position = ""

                # Contact email
                try:
                    contact_email = contact_ele.get_attribute('href').replace('mailto:', '')
                except:
                    contact_email = ""

                # Phone, Join Date, Expiration Date, Fax
                phone = fax = join_date = Expiration_date = ""
                try:
                    phone_ele = self.find_elements(By.XPATH, '//*[@id="resContainer"]/table/tbody/tr[1]')
                    for e in phone_ele:
                        try:
                            temp1 = e.text.index('Phone:')
                            try:
                                temp11 = e.text.index('Fax:')
                                phone = str(e.text[temp1+7:temp11+1]).strip()
                                fax = str(e.text[temp11+6:e.text.index('Website URL:')]).strip()
                            except:
                                fax = ""
                                phone = str(e.text[temp1+7:e.text.index('Website URL:')]).strip()
                        except:
                            phone = ""
                        
                        try:
                            temp3 = e.text.index('Join Date : ')
                            join_date = str(e.text[temp3+12:e.text.index('Expiration Date :')]).strip()
                        except:
                            join_date = ""
                        
                        try:
                            temp4 = e.text.index('Expiration Date : ')
                            Expiration_date = str(e.text[temp4+18:temp4+29]).strip()
                        except:
                            Expiration_date = ""
                except:
                    phone = join_date = Expiration_date = fax = ""

                # Website URL
                try:
                    website_url = self.find_element(By.XPATH, '//*[@id="resContainer"]/table/tbody/tr[1]/td[1]/a[2]').get_attribute('href')
                except:
                    website_url = ""

                res.append([company_name_text,' '.join(address_lines[1:]),contact_person,contact_position,contact_email,phone,join_date, Expiration_date,website_url])
                time.sleep(3)
                self.landing_page()
            except Exception as e:
                print(f"Error occurred while processing {company_name}: {e}")
                continue

        with open("data_aviation.csv",mode='w',newline='') as file:
            writer=csv.writer(file)
            writer.writerow(["Company name", "Company address", "Contact Name",
                                        "Contact Position", "Contact email", "Phone", "Joined date", "Expiration date", "Website"])
            writer.writerows(res)
        print("Data written to data_aviation.csv")