import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox
from datetime import datetime

def load_file():
    global df, file_path
    file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
    if file_path:
        try:
            df = pd.read_csv(file_path)
            filename_label.config(text=f"Selected File: {file_path}")
            messagebox.showinfo("Success", "File loaded successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load file: {e}")

def filter_data():
    if 'df' not in globals():
        messagebox.showwarning("Warning", "Please load a file first.")
        return
    
    df_filtered = df.copy()  # Make a copy to avoid modifying the original data
    
    # Remove the 'Address' column (case-insensitive)
    address_col = [col for col in df_filtered.columns if col.lower() == 'address']
    if address_col:
        df_filtered.drop(columns=address_col, inplace=True)

    # Remove rows where any column contains "Not Found"
    df_filtered = df_filtered[~df_filtered.isin(["Not Found"]).any(axis=1)]

    # Ensure the 'Cargo Carried' column exists
    if 'Cargo Carried' not in df_filtered.columns:
        messagebox.showerror("Error", "Missing 'Cargo Carried' column in the file.")
        return

    # Filter rows where 'Cargo Carried' contains 'General Freight'
    mask_general_freight = df_filtered['Cargo Carried'].str.contains('General Freight', na=False, case=False)

    # Filter rows where 'Cargo Carried' contains one of the specific types
    specific_types = ['Mobile Homes', 'Oilfield Equipment', 'Passengers', 'Garbage/Refuse']
    mask_specific_types = df_filtered['Cargo Carried'].apply(lambda x: any(item in str(x) for item in specific_types) if pd.notna(x) else False)

    # Combine both filters
    mask_combined = mask_general_freight | mask_specific_types

    # Apply date range filter if provided
    start_date_str = start_date_entry.get()
    end_date_str = end_date_entry.get()

    if 'MCS-150 Form Date' in df_filtered.columns:
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
            df_filtered['MCS-150 Form Date'] = pd.to_datetime(df_filtered['MCS-150 Form Date'], errors='coerce')  # Convert to datetime
            mask_date = (df_filtered['MCS-150 Form Date'] >= start_date) & (df_filtered['MCS-150 Form Date'] <= end_date)
            mask_combined = mask_combined & mask_date
        except ValueError:
            messagebox.showerror("Error", "Invalid date format. Please use YYYY-MM-DD.")
            return
    else:
        messagebox.showwarning("Warning", "No 'MCS-150 Form Date' column found. Filtering without date range.")

    # Apply final filtering
    df_filtered = df_filtered[mask_combined]

    if df_filtered.empty:
        messagebox.showinfo("Info", "No data matched the filters.")
    else:
        # Save the filtered data to a new CSV file
        new_filename = file_path.rsplit('.', 1)[0] + '_Fil.csv'
        df_filtered.to_csv(new_filename, index=False)
        messagebox.showinfo("Success", f"Filtered data saved to {new_filename}")

# Initialize main window
root = tk.Tk()
root.title("Data Filter")

# File selection
load_button = tk.Button(root, text="Load File", command=load_file)
load_button.pack(pady=10)

filename_label = tk.Label(root, text="No file selected")
filename_label.pack(pady=5)

# Date range inputs
today = datetime.today().strftime('%Y-%m-%d')
start_year = 2024 if datetime.now().year < 2024 else 2025
start_date_default = f"{start_year}-01-01"

start_date_label = tk.Label(root, text="Start Date (YYYY-MM-DD):")
start_date_label.pack(pady=5)
start_date_entry = tk.Entry(root)
start_date_entry.insert(0, start_date_default)  # Preselect start date
start_date_entry.pack(pady=5)

end_date_label = tk.Label(root, text="End Date (YYYY-MM-DD):")
end_date_label.pack(pady=5)
end_date_entry = tk.Entry(root)
end_date_entry.insert(0, today)  # Preselect end date as today
end_date_entry.pack(pady=5)

# Filter button
filter_button = tk.Button(root, text="Filter Data", command=filter_data)
filter_button.pack(pady=20)

# Run the application
root.mainloop()
