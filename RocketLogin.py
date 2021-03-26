import selenium
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from fake_useragent import UserAgent
import time
import random
import requests
import webbrowser


api_keys = set()


def start_driver():
    ua = UserAgent()
    user_agent = ua.random
    print(user_agent)

    opts = Options()
    opts.add_argument(f'user-agent={user_agent}')

    driver = webdriver.Chrome(r'C:\Users\preve\PycharmProjects\ConnectHealthcareScrape\chromedriver.exe', options=opts)
    return driver


def login_with_gmail(name, email, password):
    try:
        driver = start_driver()

        driver.maximize_window()
        driver.get("https://rocketreach.co/signup?next=%2F")

        time.sleep(random.randint(2, 4))
        ele_user_name = driver.find_element_by_id("name")
        ele_user_name.clear()
        ele_user_name.send_keys(name)
        time.sleep(1)

        ele_user_email = driver.find_element_by_id("email")
        ele_user_email.clear()
        ele_user_email.send_keys(email)
        time.sleep(1)

        ele_user_password = driver.find_element_by_id("password")
        ele_user_password.clear()
        ele_user_password.send_keys(password)
        time.sleep(3)

        driver.execute_script("document.getElementsByClassName('btn btn-primary ng-binding')[0].click()")
        time.sleep(15)
        driver.get('https://rocketreach.co/api?section=api_section_ov_gs')
        time.sleep(15)

        api_key = driver.find_element_by_class_name("rr-content-pane-sub-section").text

        prefix = "Get Started\nThe RocketReach API allows you to programatically search & lookup contact info over 450 million professionals, and 17 million companies. We constantly work on improving functionality and accuracy of our data. RocketReach is free to try for individual use.\nFor all calls to the RocketReach API, you will need the an API key. Your unique API key is"
        suffix = "You can always visit the account page to view api usage or manage RocketReach api settings."

        api_key_stripped = api_key.strip(prefix)
        api_key_stripped = api_key_stripped.strip(suffix)

        print(api_key_stripped)

        if len(api_key_stripped) < 8:
            api_key_stripped = "ERROR WHEN CREATING KEY WITH: " + email

        keys_out = open("api_keys", "a")
        keys_out.write(api_key_stripped + " | " + email + "\n")
        # api_keys.add(api_key)

        keys_out.close()
        driver.close()

    except Exception as e:
        failure_message = "ERROR WHEN CREATING KEY WITH: " + email
        keys_out = open("api_keys", "a")
        keys_out.write(failure_message + "\n")
        keys_out.close()

        print(e.args)


def generate_info():
    f_first = open("first_name", "r")
    f_last = open("last_name", "r")

    names_out = open("generated_names", "w")
    emails_out = open("generated_emails", "w")

    for i in range(1, 200):
        for p in range(1, 200):

            first = f_first.readline().strip("\n")
            last = f_last.readline().strip("\n")

            names_out.write(first + " " + last+"\n")
            emails_out.write(first+"."+last+"."+str(random.randint(0,50))+"@gmail.com\n")

    f_first.close()
    names_out.close()
    emails_out.close()


def get_keys():
    names = open("generated_names", "r")
    emails = open("generated_emails", "r")

    try:
        first_loop = True
        email = emails.readline().strip("\n")
        while email != "":
            name = names.readline().strip("\n")
            if not first_loop:
                login_with_gmail(name, email, "TempPasswordForNow2021!")

            first_loop = False

            email = emails.readline().strip("\n")

    except Exception as e:
        print("Error in get_keys()")
        print(e.args)

    names.close()
    emails.close()


def cycle_through_names():
    id_file = open("id file", "r")
    key_file = open("cropped_api_keys", "r")

    try:
        current_id = id_file.readline().strip("\n")
        current_key = key_file.readline().strip("\n")
        while current_id != "" and current_key != "":
            if len(current_id) < 14:
                try:
                    print(current_id)
                    print(current_key)
                    value = get_info(current_key, current_id)

                    while value == "Failed":
                        current_key = key_file.readline().strip("\n")
                        value = get_info(current_key, current_id)

                except Exception as e:
                    print("API Key done? " + current_key)
                    current_key = key_file.readline().strip("\n")
                    print(e.args)
            current_id = id_file.readline().strip("\n")

        id_file.close()
        key_file.close()

    except Exception as e:
        print("Error in cycle_through_names()")
        id_file.close()
        key_file.close()
        print(e.args)


def get_info(api_key, employee_id):
    try:
        headers = {
            'Api-Key': api_key,
        }
        params = {
            "id": employee_id
        }

        response = requests.get('https://api.rocketreach.co/v2/api/lookupProfile', headers=headers, params=params)

        json_people_file = open("json employees", "a")
        names_employees = open("names employees", "a")
        emails_employees = open("emails employees", "a")
        positions_employees = open("positions employees", "a")
        phones_employees = open("phones employees", "a")

        response_json = response.json()

        if response_json.get("detail") != "Invalid API key" and response_json.get("detail") != \
                "You have insufficient lookup credits. Visit https://rocketreach.co/pricing or contact sales " \
                "(https://rocketreach.co/contact_us/enterprise) to unlock more lookups." and response_json.get("detail") != "Verify your email in order to use the full API":
            email, status, name, employer, position, phones = get_relevant_info(response_json, True)

            if(response_json.get("status")) != "complete":
                bad_info_file = open("bad info", "a")
                bad_info_file.write(name + ": ERROR, INCOMPLETE INFO")
                bad_info_file.close()

            json_people_file.write(str(response_json) + "\n")
            names_employees.write(name + "\n")
            emails_employees.write(name + ": " + email + "\n")
            positions_employees.write(name + ": " + position + "\n")
            phones_employees.write(name + ": " + phones + "\n")

            json_people_file.close()
            names_employees.close()
            emails_employees.close()
            positions_employees.close()
            phones_employees.close()

            return response.json()

        else:
            json_people_file.close()
            names_employees.close()
            emails_employees.close()
            positions_employees.close()
            phones_employees.close()

            return "Failed"

    except Exception as e:
        print("Error in get_info()")
        print(e.args)


def lookup_person(api_key, employer):
    try:
        headers = {
            'Api-Key': api_key,
            'Content-Type': 'application/json',
        }
        data = '{"query":{"current_employer":[\"' + employer + '\"]}}'
        print(data)
        response = requests.post('https://api.rocketreach.co/v2/api/search', headers=headers, data=data)

        # TODO: CHANGE API KEYS WHEN GETTING 429 ERROR
        # while True:
            # if str(response) != "<Response [429]>":
            #     break
            # time.sleep(1)
        print(str(response))

        i = 0
        selected_person = None
        first_person = True

        for person in response.json().get("profiles"):
            if i > 10:
                break
            if first_person:
                selected_person = person
                first_person = False
            if "operations" in str(person.get("current_title")).lower():
                selected_person = person
                break
            i += 1

        selected_id, status, name, generated_employer, title = get_relevant_info(selected_person, False)

        print(name)

        id_file = open("id file", "a")
        id_file.write(selected_id + "\n")
        id_file.close()

        names_employees = open("names employees", "a")
        names_employees.write(name + "\n")
        names_employees.close()

        positions_employees = open("positions employees", "a")
        positions_employees.write(name + ": " + title + "\n")
        positions_employees.close()

        if status != "complete":
            bad_info_file = open("bad info", "a")
            bad_info_file.write(name + ": ERROR, INCOMPLETE INFO \n")
            bad_info_file.close()

    except Exception as e:
        print("Error in look_up_person(), " + employer)
        employer_errors_file = open("employer errors", "a")
        employer_errors_file.write(employer + "\n")
        employer_errors_file.close()

        id_file = open("id file", "a")
        id_file.write("ERROR WITH COMPANY: " + employer + "\n")
        id_file.close()

        names_employees = open("names employees", "a")
        names_employees.write("ERROR WITH COMPANY: " + employer + "\n")
        names_employees.close()

        positions_employees = open("positions employees", "a")
        positions_employees.write("ERROR WITH COMPANY: " + employer + "\n")
        positions_employees.close()

        print(e.args)


def get_relevant_info(person, is_detailed):
    status = str(person.get("status"))
    name = str(person.get("name"))
    employer = str(person.get("current_employer"))
    title = str(person.get("current_title"))

    if is_detailed:
        email = str(person.get("current_work_email"))
        phones = str(person.get("phones"))
        return email, status, name, employer, title, phones

    selected_id = str(person.get("id"))
    return selected_id, status, name, employer, title


def open_confirm_links():
    driver = start_driver()
    links_file = open("confirm_links", "r")

    link = links_file.readline()

    while link != "":
        driver.maximize_window()
        driver.get("https://rocketreach.co/signup?next=%2F")
        time.sleep(5)
        print("Done")
        link = links_file.readline()

    links_file.close()


def get_employees_from_vendors(api_key):
    vendor_file = open("vendor names", "r")

    i = 0
    current_vendor = vendor_file.readline().strip("\n")
    while current_vendor != "":
        if i > 20:
            break
        lookup_person(api_key, current_vendor)
        current_vendor = vendor_file.readline().strip("\n")
        i += 1


cycle_through_names()

# get_employees_from_vendors("6bb7f3kb232cff73f1971c23d808fd9fbc20d98")


# def verify_gmail():


# Client ID
# 70940840324-v5br8a2f7qp7hi858i1rbm97mg2rio9u.apps.googleusercontent.com

# Client Secret
# UapYJ9v5RwrCH8BG2stzVYuc

# tsisyogneeghlau
# tsis yog neeg hlau
# get_keys()

# lookup_person("6bbec2k340597960cec3e8d3d69ac610f23b1e9", "Rocketreach.co")
# test_yahoo_creation("Not", "Robot", "asjdlfhjdbhkjlsdhfvbkls")

# login_with_gmail("Random User", "george.steveyey@gmail.com", "TempPasswordForNow2021!")
# open_confirm_links()


# http://rrl.rocketreach.co/ls/click?upn=6gGgrgmbiMiWKXCAHCtxCOaPtC1IM-2FjsfaGPgGOl0MBfC1Qm5VadxiKmAGgL9I-2BkWSmONMux0qdytUZVkuQeke0vB0SFJJQ7wqjPDt07wtd4liuSfYZKCcgnLBQOdyzBjePgGvYFik6s8bJCp9YDpa-2BiULQZLPp1DTh-2F8zeWTM-2FdGLLk7duWL-2BPVaAzB-2BmwpviV4YS9kOb84Krmz-2F9D6fNmsJD-2FhJ1lECImg-2F5uqTtQsJwu86lqmpj7m85-2FGODULslMIZolikPJLRJ68H5cxDqalESN1cXoc-2FBjtLs-2F67Xze7yzvziUdBk4lOT0J9BJAb_qr_JpQvdVZex3OZ3UX0PF-2FqU1Vtz9v8sP-2FpRr4V9wZnydC2Ja3K2Cz5-2BLhxVZgPltqo9nMbZ78VrnEXTQLOgsX4nSM-2FB3NzgwQMQMuXuADcRsVhW1aHlHrpAMcsq1E5vODm0k7IV6YtSy7bZNHT4fhjtwTI9MKAKq285rx6QEwSCZUoOJdjUH6nEj7CWnpqeAq6CaYpB0qrxHNEImqvhFUAoeT0MhrSB5njbeKUp3Qaux5TwWrq06xWelzRf2vJu2CzCRLNOwApxxeGz-2BEMYQkwJg-3D-3D
# http://rrl.rocketreach.co/ls/click?upn=6gGgrgmbiMiWKXCAHCtxCOaPtC1IM-2FjsfaGPgGOl0MBfC1Qm5VadxiKmAGgL9I-2BkWSmONMux0qdytUZVkuQekd5ysqAWce8mRowYRarpchaIa52YXRa7hzHVGVR6ROfwsIHn9IW-2FS7o-2BbcRH-2BNslTTVMCAFUQRPDhjJAwqjlt-2BgHOa7zuew59iEcNCoGrsk9EO1jNC0Q-2FWiJ7VDH2cyS4Qh0vYLEQtQ7CcHIbXhQ9xNgRvLqWiSu2hNunVpWoKtSo13HYgHHh3MCX8U57IEa2jCU9gR-2BFiIy-2FP3AMoMzHztWw2EC-2BytvP3jlgqwY9EMVa4m3_nTaQQySZHXMxmBXJ-2FCbmTW8g8SG-2B4DwfTAA5C9s40D8N3z2ReOSv9rUKUxiyjgZPcWEfUV9obLCQb1-2Fdn-2BR4Djbj4Bf3956UDU8Vcj4PrEJQ9u4JqHQRiTDGmMC5d2Dp1i5q0aOpv4K9hNzh43jptYqCmNq9bWXARv9hrLYG3-2Bp-2By0xN-2ByfO7sDwPSM4oFop5L3-2BrBjO7eYwXNuASWOPxS2VaT7gBkPyevW3qoKk8m6zSq5jw5nyJbmM2RQhZr-2BCPFYJflyzyqlG-2Bl-2Fiit6X5g-3D-3D