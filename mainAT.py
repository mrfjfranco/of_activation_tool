import tkinter as tk
from tkinter import simpledialog, messagebox, scrolledtext
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
import time
from sharedAT import close_program, launch_login, custom_warning, toggle_log, check_authorization, check_message, custom_pass, show_activation_errors, check_chromedriver_version, initizalize_browser
from qc_check import show_qc_check_window
import os
import sys
from database import insert_activation_error, export_to_excel, open_directory
from activation_fix import main_window_fix_activation
 



def show_activation_window(option, driver, root, is_phone_activation=False):
    # global driver
    activation_window = tk.Toplevel(root)
    activation_window.title("Activation - Input Fields")
    activation_window.geometry("400x510")  # Increased window size
    activation_window.attributes("-topmost", True)  # Keep window on top
    activation_window.grid_columnconfigure(0, weight=1)
    activation_window.grid_columnconfigure(1, weight=1)
    activation_window.grid_columnconfigure(2, weight=1)
    activation_window.grid_columnconfigure(3, weight=1)
    activation_window.grid_rowconfigure(5, weight=1)  # Log area expands in height
    
    # initizalize_browser()
    launch_login(driver)

    # Entry fields for Ticket ID, Serial Number, and (for phones) SIM Number
    ticket_id_entry = tk.Entry(activation_window, width=20)
    serial_number_entry = tk.Entry(activation_window, width=25)
    sim_number_entry = None

    # Labels and Entry fields
    tk.Label(activation_window, text="Ticket ID:").grid(row=0, column=1, padx=3, pady=5, sticky="e")
    ticket_id_entry.grid(row=0, column=2, padx=5, pady=5, sticky="w")
    ticket_id_entry.focus_set()

    tk.Label(activation_window, text="Serial/IMEI Number:").grid(row=1, column=1, padx=3, pady=5, sticky="e")
    serial_number_entry.grid(row=1, column=2, padx=5, pady=5, sticky="w")
    
    # Focus on the Serial Number field after Ticket ID is scanned
    ticket_id_entry.bind("<Return>", lambda event: serial_number_entry.focus_set())


    
    # If it's a phone activation, add SIM Number field
    if is_phone_activation:
        tk.Label(activation_window, text="SIM Number:").grid(row=2, column=1, padx=3, pady=5, sticky="e")
        sim_number_entry = tk.Entry(activation_window, width=25)
        sim_number_entry.grid(row=2, column=2, padx=5, pady=5, sticky="w")
    
        # Bind Enter key to move from Serial Number field to SIM Number field
        serial_number_entry.bind("<Return>", lambda event: sim_number_entry.focus_set())        
        
        # After scanning SIM, automatically trigger the Activate button
        sim_number_entry.bind("<Return>", lambda event: activate_button.invoke())
    
    else:
         # For BYOP (non-phone), bind the Enter key to directly trigger the activate button
        serial_number_entry.bind("<Return>", lambda event: activate_button.invoke())




    # Function to send the information to the browser fields and trigger the activate process
    def activation_process():
        global driver
        start_time = time.time()
        ticket_id = ticket_id_entry.get()
        serial_number = serial_number_entry.get()
        
        # Determine SIM number based on activation type
        if is_phone_activation:
            sim_number = sim_number_entry.get()  # Use the SIM number input field for phones
        else:
            sim_number = serial_number  # Use serial number as SIM number for BYOP
    
        try:
            # Automatically adjust the serial number if needed
            if option in ["C4", "VZ", "C7"]:
                serial_number = serial_number[5:]  # Adjust for these options
            elif option == "C5":
                serial_number = serial_number[4:]  # Adjust for C5

            log_area.insert(tk.END, f"Processing input:\nTicket ID = {ticket_id}\nSerial Number = {serial_number}\nSIM Number = {sim_number}\nLoading, please wait...\n")
            log_area.yview(tk.END)
            root.update()  # Force the GUI to update and show the message

            # Wait for the ticket ID field to be present
            # log_area.insert(tk.END, "Waiting for Ticket ID field...\n")
            log_area.yview(tk.END)
            ticket_id_field = WebDriverWait(driver, 0).until(EC.presence_of_element_located((By.NAME, "ticketid")))  # Increased timeout for safety
            ticket_id_field.send_keys(ticket_id)
            log_area.insert(tk.END, "Ticket ID entered\n")
            log_area.yview(tk.END)
            
            # Serial Number field (Phones & BYOPs)
            # log_area.insert(tk.END, "Waiting for Serial Number field...\n")
            serial_number_field = WebDriverWait(driver, 0).until(EC.presence_of_element_located((By.NAME, "esn")))
            serial_number_field.send_keys(serial_number)
            log_area.insert(tk.END, "Serial Number entered\n")
            log_area.yview(tk.END)
            
            # Serial Number field (Phones & BYOPs)
            # log_area.insert(tk.END, "Waiting for Sim Number field...\n")
            sim_number_field = WebDriverWait(driver, 0).until(EC.presence_of_element_located((By.NAME, "sim")))
            sim_number_field.send_keys(sim_number)
            log_area.insert(tk.END, "Sim Number entered\n")
            log_area.yview(tk.END)
                
            # Only click "Activate" after both fields have been filled
            # log_area.insert(tk.END, "Waiting for Activate button...\n")
            activate_button = WebDriverWait(driver, 1).until(EC.element_to_be_clickable((By.NAME, "activate")))
            activate_button.click()
            log_area.insert(tk.END, "Activate button clicked\n")
            log_area.yview(tk.END)
            
            log_area.insert(tk.END, "Waiting for result message...\n")
            result_start_time = time.time()
            
            error_box = None
            message_box = None

            try:
                error_box = WebDriverWait(driver, 1).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "errorBox"))
                )
            except:
                pass

            try:
                message_box = WebDriverWait(driver, 1).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "msgBox"))
                )
            except:
                pass

            log_area.insert(tk.END, f"Result message processed in {time.time() - result_start_time:.2f} seconds\n")
            log_area.yview(tk.END)

            # Determine if an error occurred based on the presence of error_box or background color
            if error_box:
                message_text = error_box.text
                full_error_message = f"\nActivation failed with error:\n{message_text}\n\nTicked ID: {ticket_id}\nSerial Number: {serial_number}\nSIM Number: {sim_number}\n"
                log_area.insert(tk.END,full_error_message)
                log_area.yview(tk.END)
                custom_warning(root, "BYOP Activation Robot", full_error_message)
                
                print(f"Inserting activation error: Ticket ID: {ticket_id}, Serial Number: {serial_number}, SIM Number: {sim_number}, Error: {message_text}")
            
                
                #Insert the error into the database
                insert_activation_error(ticket_id, serial_number, sim_number, message_text)
                
                activation_window.destroy()
                # root.deiconify()
                driver.quit()
                driver = initizalize_browser()
                launch_login(driver)
                            
            else:
                message_text = message_box.text if message_box else "Activation successful"
                log_area.insert(tk.END, f"Activation successful: {message_text}\n")
                log_area.yview(tk.END)
                custom_pass(root, "BYOP Activation Robot", message_text)

                # Clear fields for the next activation
                clear_button = WebDriverWait(driver, 0).until(EC.element_to_be_clickable((By.NAME, "clear")))
                clear_button.click()
                log_area.insert(tk.END, "Clear button clicked\n")
                log_area.yview(tk.END)
                ticket_id_entry.delete(0, tk.END)
                serial_number_entry.delete(0, tk.END)
                # Clear the sim_number_entry if it exists (for phone activations)
                if sim_number_entry:
                    sim_number_entry.delete(0, tk.END)
                activation_window.after(100, lambda: ticket_id_entry.focus_set())

            end_time = time.time()
            log_area.insert(tk.END, f"Total processing time: {end_time - start_time:.2f} seconds\n")
            log_area.yview(tk.END)

        except Exception as e:
            if log_area.winfo_exists():  # Ensure the log_area still exists
                log_area.insert(tk.END, f"An error occurred: {e}\n")
                log_area.yview(tk.END)
            launch_login(driver)

    # Add the Activate button
    activate_button = tk.Button(activation_window, text="Activate", command=activation_process, width=10)
    activate_button.grid(row=3, column=1, padx=5, pady=5)

    # # Bind the Enter key of serial_number_entry to automatically invoke the activation process
    # serial_number_entry.bind("<Return>", lambda event: activate_button.invoke())

    # Add the Cancel button
    cancel_button = tk.Button(activation_window, text="Cancel", command=lambda: activation_window.destroy(), width=10)
    cancel_button.grid(row=3, column=2, padx=5, pady=5)

    # Create a log area
    log_height = 15 if is_phone_activation else 17
    log_area = scrolledtext.ScrolledText(activation_window, wrap=tk.WORD, height=log_height)
    log_area.grid(row=5, column=0, columnspan=4, padx=5, pady=5, sticky="nsew")

    # Toggle log button
    toggle_log_button = tk.Button(activation_window, text="Hide Log", command=lambda: toggle_log(log_area, toggle_log_button))
    toggle_log_button.grid(row=4, column=1, columnspan=2, pady=5)

    # Copyright label
    copyright_label = tk.Label(activation_window, text="Developed By Francisco J. Franco\n@mr.fjfranco - 2024 - Version: 3.0.", font=("Arial", 8))
    copyright_label.grid(row=6, column=1, columnspan=2, pady=5)




def main_window():
    global driver
    
    # driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    # check_chromedriver_version
    try:
        
        root = tk.Tk()
        root.title("CG - Activation Tool")
        root.geometry("250x400")
        
        
        driver = initizalize_browser()
        check_message()
        check_authorization()
    
        
        tk.Label(root, text="Select your option:", font=("Arial", 14, "bold")).pack(fill='both', pady=15, padx=30)
        
        tk.Button(root, text="BYOP: C5", command=lambda: show_activation_window("C5", driver, root), fg='orange').pack(fill='both', pady=5, padx=30)
        tk.Button(root, text="BYOP: C4/C7/VZ", command=lambda: show_activation_window("C7", driver, root), fg='purple').pack(fill='both', pady=5, padx=30)
        tk.Button(root, text="Phones", command=lambda: show_activation_window("Phones", driver, root, is_phone_activation=True), fg='blue').pack(fill='both', pady=5, padx=30)
        tk.Button(root, text="QC Check", command=lambda: show_qc_check_window(driver, root), fg='green').pack(fill='both', pady=5, padx=30)
        tk.Button(root, text="Activation Errors", command=lambda: show_activation_errors(root), fg='red').pack(fill='both', pady=5, padx=30)  # New button for Activation Errors
        tk.Button(root, text="Activation Fix", command=lambda: main_window_fix_activation(driver, root), fg='blue').pack(fill='both', pady=5, padx=30)
        tk.Button(root, text="Close", command=lambda: close_program(driver, root), fg='black').pack(fill='both', pady=25, padx=30)
        
        copyright_label = tk.Label(root, text="Developed By Francisco J. Franco\n@mr.fjfranco - 2024 - Version: 3.0.", font=("Arial", 8))
        copyright_label.pack(side="bottom", pady=10)
        
        root.protocol("WM_DELETE_WINDOW", lambda: close_program(driver, root))
        root.mainloop()

    except Exception as e:
        # Log the error and inform the user
        with open("error_log.txt", "w") as f:
            f.write(f"An error occurred: {str(e)}\n")
        messagebox.showerror("Error", f"An error occurred: {str(e)}\nPlease check the log file.")
        if driver:
            driver.quit()
        sys.exit(1)

# authorization.start_program
main_window()
