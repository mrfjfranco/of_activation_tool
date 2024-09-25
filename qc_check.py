import tkinter as tk
from tkinter import messagebox, scrolledtext
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from sharedAT import custom_warning, custom_pass, toggle_log, launch_login, launch_qc
#from mainAT import qc_check_var

def show_qc_check_window(driver, root, sim_number=None, qc_check_var=None):
    qc_window = tk.Toplevel(root)
    qc_window.title("QC Check")
    qc_window.geometry("400x500")  # Match the size of the activation window
    qc_window.attributes("-topmost", True)  # Keep window on top
    qc_window.grid_columnconfigure(0, weight=1)
    qc_window.grid_columnconfigure(1, weight=1)
    qc_window.grid_columnconfigure(2, weight=1)
    qc_window.grid_columnconfigure(3, weight=1)
    qc_window.grid_rowconfigure(5, weight=1) # Log area expands in height
    

    launch_login(driver) 


    tk.Label(qc_window, text="Serial/IMEI Number:").grid(row=0, column=1, padx=3, pady=5, sticky="e")

    sim_number_entry = tk.Entry(qc_window, width=30)
    sim_number_entry.grid(row=0, column=2, padx=5, pady=5, sticky="w")

      # Automatically set the serial number if provided
    if sim_number:
        sim_number_entry.insert(0, sim_number)

    # Set focus to the Serial Number field as soon as the window is displayed
    sim_number_entry.focus_set()  # Immediate focus setting
    qc_window.after(100, lambda: sim_number_entry.focus_set())

    time.sleep(0)
    launch_qc(driver)

    def qc_process():
        start_time = time.time()
        sim_number = sim_number_entry.get()
        
        # log_area.insert(tk.END, "Waiting for the Serial Number input field...\n")
        log_area.yview(tk.END)
        sim_start_time = time.time()
        sim_number_field = WebDriverWait(driver, 0).until(
            EC.presence_of_element_located((By.ID, "ll_input_esn"))
        )
        sim_number_field.clear()
        sim_number_field.send_keys(sim_number)
        log_area.insert(tk.END, "Serial Number entered.\n")
        log_area.insert(tk.END, f"SIM Number: {sim_number}\n")
        # log_area.insert(tk.END, "Waiting for the Submit button...\n")
        submit_button = WebDriverWait(driver, 1).until(
            EC.element_to_be_clickable((By.NAME, "status"))
        )
        submit_button.click()
        log_area.insert(tk.END, "Submit button clicked.\n")
        log_area.yview(tk.END)
        
        #time.sleep(1)
        
        log_area.insert(tk.END, "Waiting for result message...\n")
        log_area.yview(tk.END)
        result_start_time = time.time()

        error_box = None
        message_box = None
        
        try:
            error_box = WebDriverWait(driver, 0).until(
                EC.presence_of_element_located((By.CLASS_NAME, "errorBox"))
            )
        except:
            pass

        try:
            message_box = WebDriverWait(driver, 0).until(
                EC.presence_of_element_located((By.CLASS_NAME, "msgBox"))
            )
        except:
            pass
            
        log_area.insert(tk.END, f"Result message processed in {time.time() - result_start_time:.2f} seconds\n")
        log_area.yview(tk.END)
        
        # Determine if an error occurred based on the presence of error_box or background color
        if error_box:
            message_text = error_box.text
            is_error = True
        elif message_box:
            message_text = message_box.text
            is_error = False
        else:
            message_text = "Unknown result"
            is_error = True

        # Handle result based on error or success
        if is_error:
            full_error_message = f"\nActivation failed with error:\n{message_text}\n\nSIM Number: {sim_number}\n"
            log_area.insert(tk.END, full_error_message)
            log_area.yview(tk.END)
            
            # Show custom warning and clear fields after clicking OK
            def clear_and_focus():
                sim_number_entry.delete(0, tk.END)
                sim_number_entry.focus_set()
                log_area.insert(tk.END, "\nInput cleared. Ready for next input.\n")
                log_area.yview(tk.END)
            
            # Call the custom warning
            custom_warning(root, "QC Check", full_error_message)
            
            # Clear the input and return focus after the warning is closed
            qc_window.after(100, clear_and_focus)
            
            return  # Exit the function
        
        else:
            log_area.insert(tk.END, f"QC Check Passed: {message_text}\n")
            log_area.yview(tk.END)
            custom_pass(root, "QC Check", message_text)

        end_time = time.time()
        log_area.insert(tk.END, f"Total processing time: {end_time - start_time:.2f} seconds\n")
        log_area.yview(tk.END)
        
        sim_number_entry.delete(0, tk.END)  # Clear input field after result is shown
        # Force focus back to the input field after message box is closed
        qc_window.after(100, lambda: sim_number_entry.focus_set())

            
    def cancel_qc_check():
       qc_window.destroy()
       root.deiconify()  # Show the main window again         
        

    # Add the Submit button
    submit_button = tk.Button(qc_window, text="Submit", command=qc_process, width=10)
    submit_button.grid(row=3, column=1, padx=5, pady=5)

    # Bind the Enter key of serial_number_entry to automatically invoke the activation process
    sim_number_entry.bind("<Return>", lambda event: submit_button.invoke())

    # Add the Cancel button
    cancel_button = tk.Button(qc_window, text="Cancel", command=cancel_qc_check, width=10)
    cancel_button.grid(row=3, column=2, padx=5, pady=5)

    # Log area as in the activation window
    log_area = scrolledtext.ScrolledText(qc_window, wrap=tk.WORD, height=18)
    log_area.grid(row=5, column=0, columnspan=4, padx=5, pady=5, sticky="nsew")

    # Toggle log button
    toggle_log_button = tk.Button(qc_window, text="Hide Log", command=lambda: toggle_log(log_area, toggle_log_button))
    toggle_log_button.grid(row=4, column=1, columnspan=2, pady=5)
    
    # Copyright label
    copyright_label = tk.Label(qc_window, text="Developed By Francisco J. Franco\n@mr.fjfranco - 2024 - Version: 3.0.", font=("Arial", 8))
    copyright_label.grid(row=6, column=1, columnspan=2, pady=5)


    qc_window.transient(root)
    qc_window.grab_set()
    root.wait_window(qc_window)
    

