import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from threading import Thread, Event
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import UnexpectedAlertPresentException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import requests
import random
import threading

class FacebookMessengerSpammer:
    def __init__(self):
        self.cookies_file_path = None
        self.send_file_path = None
        self.accounts_file_path = None
        self.root = tk.Tk()
        self.root.title("Tool Spam Messenger Facebook")
        self.process_event = Event()

        self.login_type = tk.IntVar()
        self.login_type.set(1)  # Default to login with token

        self.create_widgets()

    def create_widgets(self):

        # Label and Entry for accounts file
        label_accounts_file = tk.Label(self.root, text="File Accounts:")
        label_accounts_file.grid(row=1, column=0, sticky="w")
        self.entry_accounts_file_path = tk.Entry(self.root, width=40)
        self.entry_accounts_file_path.grid(row=1, column=1, padx=10, pady=5)
        button_browse_accounts = tk.Button(self.root, text="Chọn Tệp", command=self.browse_accounts_file)
        button_browse_accounts.grid(row=1, column=2, padx=10, pady=5)

        # Label and Entry for file to send
        label_send_file = tk.Label(self.root, text="File để gửi:")
        label_send_file.grid(row=2, column=0, sticky="w")
        self.entry_send_file_path = tk.Entry(self.root, width=40)
        self.entry_send_file_path.grid(row=2, column=1, padx=10, pady=5)
        button_browse_send_file = tk.Button(self.root, text="Chọn Tệp", command=self.browse_send_file)
        button_browse_send_file.grid(row=2, column=2, padx=10, pady=5)

        label_ids_file = tk.Label(self.root, text="File IDs:")
        label_ids_file.grid(row=3, column=0, sticky="w")
        self.entry_ids_file_path = tk.Entry(self.root, width=40)
        self.entry_ids_file_path.grid(row=3, column=1, padx=4, pady=5)
        button_browse_ids_file = tk.Button(self.root, text="Chọn Tệp", command=self.browse_ids_file)
        button_browse_ids_file.grid(row=3, column=2, padx=10, pady=5)


        # Label and Textbox for API keys
        label_api_keys = tk.Label(self.root, text="API Keys:")
        label_api_keys.grid(row=1, column=3, sticky="w")
        self.text_api_keys = tk.Text(self.root, width=40, height=10)
        self.text_api_keys.grid(row=2, column=3, padx=20, pady=5)

        # Label and Entry for group size
        label_group_size = tk.Label(self.root, text="Số ID muốn gửi trên 1 token:")
        label_group_size.grid(row=4, column=0, padx=10, pady=5)
        self.entry_group_size = tk.Entry(self.root, width=40)
        self.entry_group_size.grid(row=4, column=1, padx=10, pady=5)

        # Label and Entry for number of tokens
        label_num_tokens = tk.Label(self.root, text="Số luồng:")
        label_num_tokens.grid(row=4, column=2, padx=10, pady=5)
        self.entry_num_tokens = tk.Entry(self.root, width=40)
        self.entry_num_tokens.grid(row=4, column=3, padx=10, pady=5)

        # Label and Textbox for message
        label_message = tk.Label(self.root, text="Nội dung tin nhắn:")
        label_message.grid(row=5, column=0, padx=3, pady=5)
        self.message_text_box = tk.Text(self.root, width=40, height=5)
        self.message_text_box.grid(row=5, column=1, padx=5, pady=5, columnspan=3)

        # Start and Stop buttons
        self.button_start = tk.Button(self.root, text="Bắt đầu", command=self.start_sending)
        self.button_start.grid(row=10, column=0, columnspan=2, padx=10, pady=10)

        self.button_stop = tk.Button(self.root, text="Dừng lại", command=self.stop_sending, state="disabled")
        self.button_stop.grid(row=10, column=2, columnspan=2, padx=10, pady=10)

        self.data_columns = ("ID tài khoản", "UID cần gửi", "Trạng thái")
        self.data_grid = ttk.Treeview(self.root, columns=self.data_columns, show="headings", height=10)
        for col in self.data_columns:
            self.data_grid.heading(col, text=col)
        self.data_grid.grid(row=9, column=0, columnspan=4, padx=7, pady=10)

    def add_data_to_datagridview(self, email, recipient_id, status):
        self.data_grid.insert("", "end", values=(email, recipient_id, status))

    def browse_send_file(self):
        self.send_file_path = filedialog.askopenfilename()
        if self.send_file_path:
            self.entry_send_file_path.delete(0, tk.END)
            self.entry_send_file_path.insert(tk.END, self.send_file_path)

    def browse_accounts_file(self):
        self.accounts_file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if self.accounts_file_path:
            self.entry_accounts_file_path.delete(0, tk.END)
            self.entry_accounts_file_path.insert(tk.END, self.accounts_file_path)

    def browse_ids_file(self):
        self.ids_file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if self.ids_file_path:
            self.entry_ids_file_path.delete(0, tk.END)
            self.entry_ids_file_path.insert(tk.END, self.ids_file_path)

    def start_sending(self):
        if not self.send_file_path:
            messagebox.showerror("Lỗi", "Vui lòng chọn file để gửi")
            return
            
        if not self.accounts_file_path:
            messagebox.showerror("Lỗi", "Vui lòng chọn file accounts")
            return
            
        if not self.ids_file_path:
            messagebox.showerror("Lỗi", "Vui lòng chọn file IDs")
            return
        
        # Get group size
        group_size_input = self.entry_group_size.get().strip()
        group_size = 1 if group_size_input == '' else int(group_size_input)

        # Get number of tokens to open
        num_tokens_input = self.entry_num_tokens.get().strip()
        num_tokens_to_open = None
        if num_tokens_input:
            num_tokens_to_open = int(num_tokens_input)

        message_text = self.message_text_box.get("1.0", tk.END).strip()

        with open(self.accounts_file_path, 'r') as file:
            accounts = file.readlines()

        with open(self.ids_file_path, 'r') as file:
            ids = file.readlines()

        api_keys = self.text_api_keys.get("1.0", tk.END).strip().split("\n")
        api_keys = [api_key.strip() for api_key in api_keys if api_key.strip()] 

        num_tokens = min(len(accounts), len(ids))  # Number of tokens will be equal to the minimum of IDs or tokens
        num_tokens_to_open = num_tokens if num_tokens_to_open is None else min(num_tokens, num_tokens_to_open)

        self.process_event.clear()
        self.button_start.config(state="disabled")
        self.button_stop.config(state="normal")

        ids_per_account = group_size
        num_groups = len(ids) // ids_per_account
        remainder = len(ids) % ids_per_account
        if remainder > 0:
            num_groups += 1  # Add one group for the remainder

        start_index = 0
        for account in random.sample(accounts[:num_tokens_to_open], num_tokens_to_open):
            if self.process_event.is_set():
                break
            email, password, token_2fa = self.parse_account_info(account.strip())
            end_index = min(start_index + ids_per_account, len(ids))
            group_ids = ids[start_index:end_index]
            process_thread = Thread(target=self.process_account, args=(email, password, token_2fa, self.send_file_path, group_ids, api_keys, num_tokens_to_open, message_text))
            process_thread.start()
            start_index = end_index

    def stop_sending(self):
        self.process_event.set()
        self.button_start.config(state="normal")
        self.button_stop.config(state="disabled")

    def clear_print(self):
        self.print_text.delete("1.0", tk.END)

    def process_account(self, email, password, token_2fa, file_path, all_ids, api_key, num_tokens_to_open, message_text):
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        prefs = {"profile.default_content_setting_values.notifications": 2}
        chrome_options.add_experimental_option("prefs", prefs)
        service = Service(ChromeDriverManager().install())

        sent_ids = []

        proxy = self.get_proxy(api_key)
        if proxy:
            chrome_options.add_argument(f'--proxy-server={proxy}')
        chrome_options.add_experimental_option("prefs", prefs)
        with webdriver.Chrome(service=service, options=chrome_options) as driver:
            while True:
                self.login_with_account(driver, email, password, token_2fa)

                num_ids = len(all_ids)
                ids_per_account = num_ids // num_tokens_to_open
                remainder = num_ids % num_tokens_to_open
                start_index = 0
                for _ in range(num_tokens_to_open):
                    if remainder > 0:
                        end_index = start_index + ids_per_account + 1
                        remainder -= 1
                    else:
                        end_index = start_index + ids_per_account
                    group_ids = all_ids[start_index:end_index]
                    start_index = end_index
                    for recipient in group_ids:
                        recipient = recipient.strip()
                        success = self.send_file_to_recipient(driver, recipient, file_path, token_2fa, message_text)
                        if success:
                            sent_ids.append(recipient)
                            self.add_data_to_datagridview(email, recipient, "Thành công")
                        else:
                            self.add_data_to_datagridview(email, recipient, "Lỗi")

                        # Check if account is locked
                        if self.is_account_locked(driver):
                            self.remove_locked_account(email, password, token_2fa)
                            return  # Return to try another account
                    
                self.remove_sent_ids(self.ids_file_path, sent_ids)

    def process_account_with_new_thread(self, driver, email, password, token_2fa, file_path, all_ids, api_key, num_tokens_to_open, message_text):
        group_size_input = self.entry_group_size.get().strip()
        group_size = 1 if group_size_input == '' else int(group_size_input)

        num_tokens_input = self.entry_num_tokens.get().strip()
        num_tokens_to_open = None
        if num_tokens_input:
            num_tokens_to_open = int(num_tokens_input)

        message_text = self.message_text_box.get("1.0", tk.END).strip()

        api_keys = self.text_api_keys.get("1.0", tk.END).strip().split("\n")
        api_keys = [api_key.strip() for api_key in api_keys if api_key.strip()] 

        num_tokens = min(len(all_ids), len(api_keys))  # Số lượng token sẽ bằng số lượng IDs hoặc số lượng tokens
        num_tokens_to_open = num_tokens if num_tokens_to_open is None else min(num_tokens, num_tokens_to_open)

        

        ids_per_account = group_size
        num_groups = len(all_ids) // ids_per_account
        remainder = len(all_ids) % ids_per_account
        if remainder > 0:
            num_groups += 1

        start_index = 0
        for account in random.sample(range(num_tokens_to_open), num_tokens_to_open):
            if self.process_event.is_set():
                break
            email, password, token_2fa = self.parse_account_info(account.strip())
            end_index = min(start_index + ids_per_account, len(all_ids))
            group_ids = all_ids[start_index:end_index]
            process_thread = threading.Thread(target=self.process_account, args=(email, password, token_2fa, self.send_file_path, group_ids, api_keys, num_tokens_to_open, message_text))
            process_thread.start()
            start_index = end_index
            start_index = end_index

    def is_account_locked(self, driver):
        try:
            driver.find_element(By.XPATH, "//div[@class='x9f619 x1n2onr6 x1ja2u2z x193iq5w xeuugli x6s0dn4 x78zum5 x2lah0s x1fbi1t2 xl8fo4v']")
            return True
        except NoSuchElementException:
            try:
                driver.find_element(By.XPATH, "//span[@class='x193iq5w xeuugli x13faqbe x1vvkbs x1xmvt09 x1lliihq x1s928wv xhkezso x1gmr53x x1cpjm7i x1fgarty x1943h6x xudqn12 x3x7a5m x6prxxf xvq8zen x1s688f xtk6v10']")
                return True
            except NoSuchElementException:
                return False
        
    def remove_locked_account(self, email, password, token_2fa):
        with open(self.accounts_file_path, 'r+') as file:
            lines = file.readlines()
            file.seek(0)
            account_locked = False
            for line in lines:
                account_email, _, _ = line.split('|')
                if account_email.strip() == email.strip():
                    account_locked = True
                else:
                    file.write(line)
            file.truncate()
            if account_locked:
                self.process_account_with_new_thread(email, password, token_2fa)  # Đã thêm tham số đúng

    def remove_sent_ids(self, ids_file_path, sent_ids):
        with open(ids_file_path, 'r+') as file:
            lines = file.readlines()
            file.seek(0)
            for line in lines:
                if line.strip() not in sent_ids:
                    file.write(line)
            file.truncate()
        sent_ids.clear()


    def login_with_account(self, driver, email, password, token_2fa):
        driver.get("https://www.facebook.com")
        email_input = driver.find_element(By.ID, "email")
        email_input.send_keys(email)
        password_input = driver.find_element(By.ID, "pass")
        password_input.send_keys(password)
        login_button = driver.find_element(By.NAME, "login")
        login_button.click()
        time.sleep(5)

        # Check if 2FA is required
        if "checkpoint" in driver.current_url:
            fa_code = self.get_2fa_code(token_2fa)
            code_input = driver.find_element(By.ID, "approvals_code")
            code_input.send_keys(fa_code)
            time.sleep(3)
            continue_button = driver.find_element(By.XPATH, "//button")
            continue_button.click()
            time.sleep(3)
            continue_button = driver.find_element(By.XPATH, "//button")
            continue_button.click()
            
            # Wait for main page to load
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "facebook")))


    def send_file_to_recipient(self, driver, recipient, file_path, token_2fa, message_text):
        try:
            time.sleep(3)
            driver.get("https://www.facebook.com/messages/t/" + recipient.strip())
            time.sleep(2)
        
            # Send the file
            message_input = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//input[@type='file']")))
            message_input.send_keys(file_path)
            message_text_box = driver.find_element(By.XPATH, "//p[@class='xat24cr xdj266r']")
            message_text_box.send_keys(message_text)
            time.sleep(1)

            try:
                message_send = driver.find_element(By.XPATH, "//div[@aria-label='Nhấn Enter để gửi']")
                driver.execute_script("arguments[0].click();", message_send)
            except NoSuchElementException:
                try:
                    message_send = driver.find_element(By.XPATH, "//div[@aria-label='Press enter to send']")
                    message_send.click()
                except NoSuchElementException:
                    print("Không tìm thấy phần tử để gửi tin nhắn")
            except UnexpectedAlertPresentException:
                # Handle unexpected alert
                alert = driver.switch_to.alert
                alert.accept()
                print("Đã xác nhận cảnh báo không mong đợi")
        
            time.sleep(2)
            print(f"Gửi tin nhắn đến UID {recipient} thành công!")
            return True
        except Exception as e:
            print(f"Lỗi khi gửi tin nhắn đến {recipient}")
            return False

    def get_proxy(self, api_key, location=None, provider=None):
        url = f"http://proxy.shoplike.vn/Api/getNewProxy?access_token={api_key}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if data['status'] == 'success':
                proxy = data['data']['proxy']
                return proxy
            else:
                print("Không thể lấy được proxy từ API.")
                return None
        else:
            print(f"Lỗi khi gửi yêu cầu: {response.status_code}")
            return None
    
    def get_2fa_code(self, token_2fa):
        url = f"https://api.code.pro.vn/2fa/v1/get-code?secretKey={token_2fa}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            code = data.get('code')
            return code
        else:
            print(f"Lỗi khi gửi yêu cầu: {response.status_code}")
            return None

    def parse_account_info(self, account):
        # Split account string into email, password, and 2FA token
        email, password, token_2fa = account.split('|')
        return email.strip(), password.strip(), token_2fa.strip()

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = FacebookMessengerSpammer()
    app.run()