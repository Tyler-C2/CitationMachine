from bs4 import BeautifulSoup
import datetime
import maya
import re 
import requests

class Citation:
    def __init__(self):
        self.url = None
        self.title = None
        self.author = None
        self.date = None
        self.date_cite_made = None
        self.soup = None
        self.response_error = False

    tag_lst= ("div","a","p","span","h4")

    # takes a url and returns the text for scraping.
    def get_web_soup(self, url_to_cite):
        try:
            response = requests.get(url_to_cite).text #!!! remove html replace with comment!!!
            self.soup = BeautifulSoup(response, "html.parser")
            self.url = url_to_cite

        except:
            print("No response from website.")
            self.url = f"NO RESPONSE FROM {url_to_cite}."
            self.response_error = True
            
    # collects title from html. stores title in title instance variable.
    def get_title(self):
        self.title = self.soup.find("h1").get_text()

    # collect author from html. passes list of authors to format method stores returned value in the author instance variable.
    def get_author(self):
        key_words = ("name", "author", "byline")
        exclude = (",","@", "staff", "busi", "tech", "&", "and", "sign", "bio", "name", "edit")
        author_lst = []

        for tag in self.tag_lst:
            for word in key_words:
                if self.soup.find_all(tag, re.compile(word)):
                    soup_of_author = self.soup.find_all(tag, re.compile(word))
                    for j in soup_of_author:
                        possible_name = self.name_check(j.get_text())
                        if possible_name not in author_lst:
                            author_lst.append(possible_name)

        for name in author_lst:
            name_lower = name.lower()
            for items in exclude:
                if items in name_lower:
                    name_lower, author_lst[author_lst.index(name)] = '', ''
        author_lst = [name for name in author_lst if name != '']
        self.author = author_lst

    def name_check(self, name):
        if len(name) < 8 or len(name) >= 18:
            name = ''
        if name != '':
            temp_split = name.split()
            if len(temp_split) > 1:
                for i in temp_split:
                    if i.lower() == 'by':
                        temp_split.remove(i) 
                name = ' '.join(temp_split)
            else:
                name = ''
        return name

    # formats names in names list so that it reads last name comma first initial. returns list. 
    def author_format(self, author_lst):
        if author_lst == None or len(author_lst) == 0:
            return author_lst
        for author in author_lst:
            split_author = author.split(" ")
            first_initial = split_author[0][0] + "."
            lastname = split_author[-1]
            author_lst[author_lst.index(author)] = lastname +", "+ first_initial
        self.author = author_lst 

    # collects date from html. passes date to convert string date to a list 
    # converts month to number if needed and makes all values integers. stores value in the date instance variable. 
    def get_date(self):
        exclude = ("pub")
        class_date_lst = ("date", "mod date", "published", "content-date", "time", "jeg_meta_date")
        date_as_lst = []

        if self.soup.find_all("time"):
            try:
                date = self.soup.find("time").contents[0]
                temp_split = date.split()
                for i in temp_split:
                    lower = i.lower()
                    if exclude in lower:
                        temp_split.remove(i)
                date = " ".join(elem for elem in temp_split)
                date_as_lst = self.date_to_sterile_lst(str(self.maya_convert(date)))
            except:
                try:
                    get_text_date = self.soup.find("time").get_text()
                    date_as_lst = self.date_to_sterile_lst(self.maya_convert(get_text_date))
                except:
                    date_as_lst = []
        else:
            for tag in self.tag_lst:
                for i in class_date_lst:
                    if self.soup.find_all(tag, {"class": re.compile(i)}):
                        try:
                            date = self.soup.find(class_ = i).contents[0]
                            temp_split = date.split()
                            for i in temp_split:
                                lower = i.lower()
                                if exclude in lower:
                                    temp_split.remove(i)
                            date = " ".join(elem for elem in temp_split)
                            date_as_lst = self.date_to_sterile_lst(str(self.maya_convert(date)))
                            break
                        except:
                            date_as_lst = []  

        for string in date_as_lst:
            if string.isalpha() == True:
                date_as_lst[date_as_lst.index(string)] = self.month_str_to_number(string)
        self.date = self.str_to_num(date_as_lst)

    def maya_convert(self,str):
        dt = maya.parse(str).datetime()
        return dt.date()

    # formats date stored in current instance variable. moves year to the fist element in list 
    # returns a string in the order of year, month, day. If only the year is present then that is the only value returned. 
    def date_format(self):
        date_lst = self.date
        if date_lst == None or len(date_lst) == 0:
            self.date = "n.a."
        else:    
            # for num in date_lst:
            #     if len(str(num)) == 4:
            #         year = date_lst.pop(date_lst.index(num))
            #         date_lst.insert(0, year)
            if len(date_lst) == 3:
                self.date = f"{date_lst[0]}, {date_lst[1]} {date_lst[2]}"
            else:
                self.date = f"{date_lst[0]}"

    # seperates date into a list of three strings.
    def date_to_sterile_lst(self, str):
        return str.split('-')

    # converts spelled out month into the corosponding number.
    def month_str_to_number(self, str):
        months = {
            'jan': 1,
            'feb': 2,
            'mar': 3,
            'apr': 4,
            'may': 5,
            'jun': 6,
            'jul': 7,
            'aug': 8,
            'sep': 9,
            'oct': 10,
            'nov': 11,
            'dec': 12
            }
        s = str.strip()[:3].lower()

        try:
            out =  months[s]
            return out
        except:
            raise ValueError('Not a month')

    # converts number month into the corosponding string 
    def number_to_month_str(self, lst):
        months = {
            1: 'January',
            2: 'February',
            3: 'March',
            4: 'April',
            5: 'May',
            6: 'June',
            7: 'July',
            8: 'August',
            9: 'September',
            10: 'October',
            11: 'November',
            12: 'December'
            }

        try:
            lst[1] =  months[lst[1]]
            return lst
        except:
            return []
        
    # convert date string to an integer.
    def str_to_num(self, lst):
        try:
            if len(lst) == 0:
                return lst
            for str in lst:
                lst[lst.index(str)] = int(str)
            return lst
        except:
            return []
            
    # method that generates an APA citation based on instance variables. 
    def APA_cite_generator(self):
        title = self.title
        url = self.url
        date = f"({self.date})"

        if self.author == None or self.author == []:
            author_string = "n.a."
        else:
            author_string = ", ".join(self.author)
            
        return f"{author_string} {date}. {title}. Retrieved from {url}"

    def populate_cite_obj(self, url):
        self.get_web_soup(url)
        if self.response_error == False:
            self.get_title()
            self.get_author()
            self.get_date()

    def clear_cite_obj(self):
        self.url = None
        self.title = None
        self.author = None
        self.date = None
        self.date_cite_made = None
        self.soup = None

if __name__ == "__main__":  
    loop = True
    while loop == True:
        input_url = input("Enter the URL of the website you want to cite: ")
        new_cite = Citation()
        new_cite.populate_cite_obj(input_url)
        str_month_date = new_cite.number_to_month_str(new_cite.date)

        print(f"The URL is: {new_cite.url}")
        print(f"The title of the artical is: {new_cite.title}")
        print(f"The author(s) of the artical is/are: {new_cite.author}")
        print(f"The date the artical was created is: {str_month_date}")

        new_cite.date_format()
        new_cite.author_format(new_cite.author)

        print(f"\n\nReference\n{new_cite.APA_cite_generator()}")
        new_cite.clear_cite_obj()
        for i in range(3):
            user_input = input("\nDo you want to create another citation?(y/n): ")
            if user_input.lower() == "n":
                print("Goodbye")
                loop = False
                break
            elif user_input.lower() == "y":
                break
            else:
                print("Input not valid")
            if i == 2:
                print("To many invalid inputs goodbye.")
                loop = False
                break
         