import tkinter as tk
from tkinter import scrolledtext
import threading

from backend import create_gpt3_client, manage_incoming_message

class SLTravelApp:
    def __init__(self, root):
        self.root = root
        self.root.title("SL Travel Assistant")
        self.root.geometry("600x500")
        
        self.CHATGPT_API_KEY = "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"
        self.GPT_MODEL = "gpt-4o-mini"
        self.CURRENT_STATION_ID = "300109001"  # T-Centralen
        self.SL_API_KEY = "TRAFIKLAB-SLAPI-INTEGRATION-2024"
        
        self.client = create_gpt3_client(self.CHATGPT_API_KEY)
        
        # Create UI elements
        self.create_widgets()
    
    def create_widgets(self):
        # Frame for input area
        input_frame = tk.Frame(self.root)
        input_frame.pack(pady=10, padx=10, fill=tk.X)
        
        # Label for input
        input_label = tk.Label(input_frame, text="Where would you like to go?")
        input_label.pack(anchor='w')
        
        # Input field and send button in one row
        input_row = tk.Frame(input_frame)
        input_row.pack(fill=tk.X, pady=5)
        
        self.input_field = tk.Entry(input_row)
        self.input_field.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.input_field.bind("<Return>", self.send_message)
        
        send_button = tk.Button(input_row, text="Send", command=self.send_message)
        send_button.pack(side=tk.RIGHT)
        
        # Output area
        output_frame = tk.Frame(self.root)
        output_frame.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)
        
        output_label = tk.Label(output_frame, text="Response:")
        output_label.pack(anchor='w')
        
        self.output_text = scrolledtext.ScrolledText(output_frame, wrap=tk.WORD, height=15)
        self.output_text.pack(fill=tk.BOTH, expand=True)
        self.output_text.config(state=tk.DISABLED)
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        status_bar = tk.Label(self.root, textvariable=self.status_var, bd=1, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def send_message(self, event=None):
        user_input = self.input_field.get().strip()
        if not user_input:
            return
        
        # Clear input field
        self.input_field.delete(0, tk.END)
        
        # Update status
        self.status_var.set("Processing...")
        
        # Disable input while processing
        self.input_field.config(state=tk.DISABLED)
        
        # Process message in a separate thread to keep UI responsive
        threading.Thread(target=self.process_message, args=(user_input,), daemon=True).start()
    
    def process_message(self, user_input):
        try:
            # Add user input to output area
            self.update_output(f"You: {user_input}\n")
            
            # Process the request
            response = manage_incoming_message(
                user_input, 
                self.client, 
                self.GPT_MODEL, 
                self.CURRENT_STATION_ID, 
                self.SL_API_KEY
            )
            
            # Add response to output area
            self.update_output(f"Assistant: {response}\n\n")
            
            # Update status
            self.status_var.set("Ready")
        except Exception as e:
            self.update_output(f"Error: {str(e)}\n\n")
            self.status_var.set("Error occurred")
        finally:
            # Re-enable input
            self.root.after(0, lambda: self.input_field.config(state=tk.NORMAL))
    
    def update_output(self, text):
        def _update():
            self.output_text.config(state=tk.NORMAL)
            self.output_text.insert(tk.END, text)
            self.output_text.see(tk.END)
            self.output_text.config(state=tk.DISABLED)
        
        # Schedule UI update from the main thread
        self.root.after(0, _update)

def main():
    root = tk.Tk()
    app = SLTravelApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()