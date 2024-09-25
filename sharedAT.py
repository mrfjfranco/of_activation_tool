import tkinter as tk
import logging
from tkinter import messagebox
from tkinter import scrolledtext
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time
import requests
import sys
import subprocess
from database import export_to_excel, open_directory, fetch_activation_errors, fetch_available_dates
import os


# Enable logging to capture any issues with the download or version compatibility
logging.basicConfig(level=logging.INFO)


def initizalize_browser():
    # global driver
    chrome_options = Options()
    # chrome_options.add_argument("--headless")  # Run in headless mode
    chrome_options.add_argument("--disable-extensions")  # Disable extensions
    chrome_options.add_argument("--no-sandbox")  # Bypass OS security model
    chrome_options.add_argument("--disable-dev-shm-usage")  # Disable shared memory usage
    chrome_options.add_argument("--disable-dev-tools")  # Disable DevTools
    chrome_options.add_argument("--remote-debugging-port=0")  # Disable DevTools by using an invalid port
    chrome_options.add_argument("--log-level=3")  # Suppress most logs
    chrome_options.add_argument("--disable-logging")  # Disable logging
    chrome_options.add_argument("--disable-password-manager-reauth")  # Disable password manager errors


    # Specify a known path for the cache
    cache_dir = os.path.join(os.getcwd(), "webdriver_cache")
    if not os.path.exists(cache_dir):
        os.makedirs(cache_dir)

    try:
        # Attempt to use webdriver-manager without the 'path' argument
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
        driver.minimize_window()
        time.sleep(0)
    except Exception as e:
        print(f"WebDriverManager failed: {e}")
        # Fallback to local driver, assuming chromedriver.exe is in the current directory
        chrome_driver_path = os.path.join(os.getcwd(), "chromedriver.exe")
        driver = webdriver.Chrome(service=Service(chrome_driver_path))  # Correct way to pass service
        driver.minimize_window()
    return driver

# Function to get ChromeDriver version
def check_chromedriver_version():
    driver_path = ChromeDriverManager().install()
    print(f"ChromeDriver path: {driver_path}")
    try:
        result = subprocess.run([driver_path, '--version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(result.stdout.decode().strip())  # Prints ChromeDriver version
    except Exception as e:
        print(f"Error occurred while checking ChromeDriver version: {e}")

# Call the function before the rest of your code
check_chromedriver_version()


# Define the toggle_log function
def toggle_log(log_area, toggle_log_button):
    if log_area.winfo_viewable():
        log_area.grid_remove()  # Hide the log area
        toggle_log_button.config(text="Show Log")
    else:
        log_area.grid()  # Show the log area
        toggle_log_button.config(text="Hide Log")

def custom_pass(root, title, message_text, auto_close_time=1000):
    popup = tk.Toplevel(root)
    popup.title(title)
    popup.configure(bg='#00ff00')  # green background
    
    tk.Label(popup, text=message_text, bg='#00ff00').pack(padx=20, pady=20)
    
    # Create the OK button
    ok_button = tk.Button(popup, text="OK", command=popup.destroy, width=10)
    ok_button.pack(pady=10)
    ok_button.focus_set()  # Set focus to the OK button
    
    # If auto_close_time is provided, auto-close the popup after that time
    if auto_close_time:
        popup.after(auto_close_time, popup.destroy)
    
    # Center the popup
    popup.update_idletasks()
    x = (popup.winfo_screenwidth() // 2) - (popup.winfo_reqwidth() // 2)
    y = (popup.winfo_screenheight() // 2) - (popup.winfo_reqheight() // 2)
    popup.geometry(f"+{x}+{y}")
    
    popup.transient(root)
    popup.grab_set()
    root.wait_window(popup)


# Custom warning function with pale red background
def custom_warning(root, title, message_text):
    warning_popup = tk.Toplevel(root)
    warning_popup.title(title)
    warning_popup.configure(bg='#FF0000')  # red background
    
    # Create a label to show the message_text in yellow
    tk.Label(warning_popup, text=message_text, bg='#FF0000', fg='yellow').pack(padx=20, pady=5)
    
    # Create OK button
    ok_button = tk.Button(warning_popup, text="OK", command=warning_popup.destroy, width=10)
    ok_button.pack(pady=10)
    ok_button.focus_set()
    
    # Bind the Enter key to trigger the OK button action
    warning_popup.bind('<Return>', lambda event: ok_button.invoke())

    # Make the popup always on top
    warning_popup.attributes('-topmost', True)

    # Center the popup
    warning_popup.update_idletasks()
    x = (warning_popup.winfo_screenwidth() // 2) - (warning_popup.winfo_reqwidth() // 2)
    y = (warning_popup.winfo_screenheight() // 2) - (warning_popup.winfo_reqheight() // 2)
    warning_popup.geometry(f"+{x}+{y}")

    warning_popup.transient(root)
    warning_popup.grab_set()
    root.wait_window(warning_popup)

# Function to open the browser and log in
def launch_login(driver):
    print("Navigating to login page...")
    driver.get("https://direct.tracfone.com/lifeline/bpoint/controller.block.do?__blockname=lifeline.bpoint.login")
    time.sleep(0)
    print("Filling in login details...")
    username_field = driver.find_element(By.NAME, "username")
    password_field = driver.find_element(By.NAME, "password")
    username_field.send_keys("bs_cfernandez")
    password_field.send_keys("C00p3rG.SL!")
    login_button = driver.find_element(By.NAME, "login")
    login_button.click()
    driver.minimize_window()
    time.sleep(0)
    #return driver





def close_program(driver, root):
    if messagebox.askokcancel("Quit", "Do you want to quit?"):
        driver.quit()  # Close the browser
        root.quit()  # Stop the Tkinter mainloop
        root.destroy()  # Destroy the Tkinter window
        sys.exit()  # Exit the program

    
    
def launch_qc(driver):
    print("Navigating to QC Check tab...")
    qc_check_tab = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.LINK_TEXT, "QC Check"))
    )
    qc_check_tab.click()
    print("QC Check tab opened, ready for input.")
    #qc_check.show_qc_check_window(root, driver, serial_number=sim_number)








def check_authorization():
    # GitHub raw URL for the JSON file with a timestamp to avoid caching
    api_url = f"https://raw.githubusercontent.com/mrfjfranco/authorization-check/main/auth_at.json"

    try:
        response = requests.get(api_url)
        print(f"Status code: {response.status_code}")
        # print(f"Response headers: {response.headers}")
        
        # Parse the response as JSON
        json_content = response.json()
        
        # Print the JSON content for diagnostics
        print(f"JSON content: {json_content}")

        # Check if the authorization phrase is correct
        expected_phrase = "FR@%c!$C0"  # Replace with your expected phrase
        if json_content.get("authorization_phrase") == expected_phrase:
            print("Authorization successful, continuing execution...")
        else:
            failure_message = json_content.get("failure_message", "Authorization failed.")
            show_error_and_exit(f"Authorization failed: {failure_message}")

    except Exception as e:
        show_error_and_exit(f"Failed to check authorization: {str(e)}")
        
        
        
# Function to display an error and exit the program
def show_error_and_exit(message):
    root = tk.Tk()
    root.withdraw()  # Hide the root window
    messagebox.showerror("Authorization Failed", message)
    root.destroy()
    sys.exit()  # Use sys.exit() instead of exit()








# Function to check the message from GitHub using the API
def check_message():
    # GitHub repository and file details
    api_url = f"https://raw.githubusercontent.com/mrfjfranco/message-check/main/message_at.csv"

    try:
        # Fetch the file content from the GitHub API
        response = requests.get(api_url)
        print(f"Status code: {response.status_code}")
        print(f"Response content: {response.text}")
        response.raise_for_status()  # Ensure the request was successful
        csv_content=response.text.splitlines()

        # Check if the first line contains a message
        if csv_content and csv_content[0].strip():  # Ensures the first line is not empty
            message = csv_content[0].strip()
            show_message_popup(message)
        else:
            print("No message found, continuing as normal...")

    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}, continuing as normal...")

# Function to show the message in a pop-up window
def show_message_popup(message):
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    messagebox.showinfo("Message", message)  # Show the message in a pop-up
    root.quit()  # Close the pop-up and return to the main program
    





def show_activation_errors(root):
    # Create a new window for activation errors
    error_window = tk.Toplevel(root)
    error_window.title("Activation Errors")
    error_window.geometry("1100x700")
    error_window.attributes("-topmost", True)

    # Add a title to the window
    title_label = tk.Label(error_window, text="Activation Errors:", font=("Arial", 14, "bold"))
    title_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")

    # Create a frame to hold the dropdowns, filter button, and search fields
    control_frame = tk.Frame(error_window)
    control_frame.grid(row=1, column=0, padx=10, pady=10, sticky="w")

    # Fetch available dates
    available_dates = fetch_available_dates()
    if not available_dates:
        tk.messagebox.showerror("Error", "No dates available in the database.")
        return

    
        # Function to clear filters, reset fields, and clear the text area
    def clear_filters():
        # Clear the Ticket ID and SIM search fields
        ticket_id_entry.delete(0, tk.END)
        sim_entry.delete(0, tk.END)

        # Reset the date dropdowns to default values
        start_date_var.set(available_dates[0])
        end_date_var.set(available_dates[-1])

        # Clear the text area where data is displayed
        text_area.delete('1.0', tk.END)

        # Reset the error count label
        error_count_label.config(text="Total Errors: 0")

        # Optionally reset the df to None if you want to clear everything
        global df
        df = None
    
    
    
    # Dropdown for start date
    tk.Label(control_frame, text="Start Date:", font=("Arial", 10, "bold")).grid(row=0, column=0, padx=5, pady=5, sticky="w")
    start_date_var = tk.StringVar(control_frame)
    start_date_var.set(available_dates[0])  # Set default value
    start_date_dropdown = tk.OptionMenu(control_frame, start_date_var, *available_dates)
    start_date_dropdown.grid(row=0, column=1, padx=5, pady=5, sticky="w")

    # Dropdown for end date
    tk.Label(control_frame, text="End Date:", font=("Arial", 10, "bold")).grid(row=0, column=2, padx=5, pady=5, sticky="w")
    end_date_var = tk.StringVar(control_frame)
    end_date_var.set(available_dates[-1])  # Set default value to the latest date
    end_date_dropdown = tk.OptionMenu(control_frame, end_date_var, *available_dates)
    end_date_dropdown.grid(row=0, column=3, padx=10, pady=5, sticky="w")

    # Search by Ticket ID
    tk.Label(control_frame, text="Search by Ticket ID:", font=("Arial", 10, "bold")).grid(row=1, column=0, padx=5, pady=5, sticky="w")
    ticket_id_entry = tk.Entry(control_frame)
    ticket_id_entry.grid(row=1, column=1, padx=5, pady=5, sticky="w")

    # Search by SIM
    tk.Label(control_frame, text="Search by SIM:", font=("Arial", 10, "bold")).grid(row=1, column=2, padx=5, pady=5, sticky="w")
    sim_entry = tk.Entry(control_frame)
    sim_entry.grid(row=1, column=3, padx=5, pady=5, sticky="w")

    # Define df globally so it's accessible in other functions
    global df
    df = None  # Initialize it as None

    # Add a filter button to execute the date-based filter
    filter_button = tk.Button(control_frame, text="Filter Date", command=lambda: filter_errors(start_date_var.get(), end_date_var.get(), ticket_id_entry.get(), sim_entry.get()))
    filter_button.grid(row=0, column=4, padx=10, pady=5, sticky="w")

    # Add a search button to execute the Ticket ID and SIM-based search
    search_button = tk.Button(control_frame, text="Search", command=lambda: search_errors(ticket_id_entry.get(), sim_entry.get()))
    search_button.grid(row=1, column=4, padx=10, pady=5, sticky="w")
    
    # Add a clear button to reset filters and search fields
    clear_button = tk.Button(control_frame, text="Clear Filters", command=clear_filters)
    clear_button.grid(row=1, column=5, padx=10, pady=5, sticky="w")


    # Label to display the total number of errors found after filtering
    error_count_label = tk.Label(error_window, text="Total Errors: 0", font=("Arial", 10, "bold"))
    error_count_label.grid(row=2, column=0, padx=10, pady=5, sticky="w")

    # ScrolledText widget for displaying data
    text_area = scrolledtext.ScrolledText(error_window, wrap=tk.WORD)
    text_area.grid(row=3, column=0, padx=10, pady=10, sticky="nsew")

    # Adjust row and column weights so the text_area expands properly
    error_window.grid_rowconfigure(3, weight=1)
    error_window.grid_columnconfigure(0, weight=1)

    # Function to fetch and filter errors based on date and optionally by Ticket ID and SIM
    def filter_errors(start_date, end_date, ticket_id, sim):
        global df  # Allow df to be modified
        df = fetch_activation_errors(start_date, end_date)

        if df is not None and not df.empty:
            # Ensure 'Ticket_ID' is the first column
            if 'Ticket_ID' in df.columns:
                columns = ['Ticket_ID'] + [col for col in df.columns if col != 'Ticket_ID']
                df = df[columns]

            # Capitalize and bold column headers
            df.columns = [col.upper() for col in df.columns]

            # If a Ticket ID or SIM is provided, apply an additional filter
            if ticket_id:
                df = df[df['TICKET_ID'].str.contains(ticket_id, case=False, na=False)]
            if sim:
                df = df[df['SIM'].str.contains(sim, case=False, na=False)]

            # Clear existing data
            text_area.delete('1.0', tk.END)

            # Display filtered data in the ScrolledText widget
            text_area.insert(tk.END, df.to_string(index=False))

            # Update the label with the count of errors
            error_count = len(df)
            error_count_label.config(text=f"Total Errors: {error_count}")
        else:
            tk.messagebox.showinfo("No Data", "No errors found for the selected date range.")
            error_count_label.config(text="Total Errors: 0")

    # Function to search errors based only on Ticket ID or SIM
    def search_errors(ticket_id, sim):
        global df
        # Ensure the data is fetched first
        if df is None:
            tk.messagebox.showerror("Error", "Please filter by date first to load data.")
            return

        if df is not None and not df.empty:
            search_df = df.copy()

            # Apply Ticket ID or SIM filters
            if ticket_id:
                search_df = search_df[search_df['TICKET_ID'].str.contains(ticket_id, case=False, na=False)]
            if sim:
                search_df = search_df[search_df['SIM'].str.contains(sim, case=False, na=False)]

            # Clear existing data
            text_area.delete('1.0', tk.END)

            # Display the search results in the ScrolledText widget
            if not search_df.empty:
                text_area.insert(tk.END, search_df.to_string(index=False))

                # Update the label with the count of errors found
                error_count = len(search_df)
                error_count_label.config(text=f"Total Errors: {error_count}")
            else:
                tk.messagebox.showinfo("No Data", "No errors found for the search criteria.")
                error_count_label.config(text="Total Errors: 0")
        else:
            tk.messagebox.showerror("Error", "No data available to search.")

    # Export to Excel and open directory functionality
    def export_data():
        if df is not None and not df.empty:
            file_path = os.path.join(os.path.expanduser("~"), "Desktop", "activation_errors_filtered.xlsx")
            export_to_excel(df, file_path)
            tk.messagebox.showinfo("Export Successful", f"Data exported to {file_path}")
        else:
            tk.messagebox.showerror("Error", "No data available for export")

    # Menu for exporting to Excel and opening directory
    menu_bar = tk.Menu(error_window)
    error_window.config(menu=menu_bar)
    file_menu = tk.Menu(menu_bar, tearoff=0)
    menu_bar.add_cascade(label="File", menu=file_menu)

    file_menu.add_command(label="Export to Excel", command=export_data)
    file_menu.add_command(label="Close", command=error_window.destroy)

    # close button
    close_button = tk.Button(error_window, text="Close", command=error_window.destroy)
    close_button.grid(row=4, column=0, pady=10)

    # Add the copyright label below the Close button and center it
    copyright_label = tk.Label(error_window, text="Developed By Francisco J. Franco - @mr.fjfranco - 2024 - Version: 3.0.", font=("Arial", 8))
    copyright_label.grid(row=5, column=0, columnspan=2, pady=5, sticky="ew")
    


