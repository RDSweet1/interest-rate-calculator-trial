#!/usr/bin/env python3
"""
Debug Viewer - Shows debug_save.txt in a popup window with copy functionality
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from pathlib import Path
import pyperclip

class DebugViewer:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Debug Viewer")
        self.root.geometry("900x700")  # Larger window
        self.root.minsize(600, 400)    # Minimum size
        
        # Center the window on screen
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() - width) // 2
        y = (self.root.winfo_screenheight() - height) // 2
        self.root.geometry(f"{width}x{height}+{x}+{y}")
        
        # Always on top and bring to front
        self.root.attributes('-topmost', True)
        self.root.lift()
        self.root.focus_force()
        
        self.create_widgets()
        self.load_debug_file()
        
    def create_widgets(self):
        """Create the debug viewer interface"""
        # Main frame with proper padding
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="Debug Log Viewer", 
                               font=("Arial", 14, "bold"))
        title_label.pack(pady=(0, 15))
        
        # Text area with scrollbar - use grid for better control
        text_frame = ttk.Frame(main_frame)
        text_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        self.text_area = scrolledtext.ScrolledText(
            text_frame, 
            wrap=tk.WORD,
            width=100,   # Wider to fit more text
            height=35,   # Taller to fit more lines
            font=("Consolas", 9)  # Slightly smaller font to fit more
        )
        self.text_area.pack(fill=tk.BOTH, expand=True)
        
        # Button frame - ensure it's always visible
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        # Buttons with better spacing
        ttk.Button(button_frame, text="Copy All", command=self.copy_all, 
                  width=12).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Refresh", command=self.load_debug_file, 
                  width=12).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Clear", command=self.clear_debug_file, 
                  width=12).pack(side=tk.LEFT, padx=(0, 10))
        
        # Close button on the right with more space
        ttk.Button(button_frame, text="Close", command=self.root.destroy, 
                  width=12).pack(side=tk.RIGHT, padx=(20, 0))
        
        # Status label for feedback
        self.status_label = ttk.Label(button_frame, text="Ready", 
                                     font=("Arial", 9), foreground="gray")
        self.status_label.pack(side=tk.RIGHT, padx=(0, 20))
        
        # Bind Escape key
        self.root.bind('<Escape>', lambda e: self.root.destroy())
        
    def load_debug_file(self):
        """Load and display debug files"""
        debug_save = Path("debug_save.txt")
        debug_load = Path("debug_load.txt")
        
        # Clear current content
        self.text_area.delete(1.0, tk.END)
        
        content_found = False
        all_content = ""
        
        # Check debug_load.txt first (for loading issues)
        if debug_load.exists():
            try:
                with open(debug_load, 'r', encoding='utf-8', errors='ignore') as f:
                    load_content = f.read()
                if load_content:
                    all_content += "=== DEBUG LOAD LOG ===\n" + load_content + "\n\n"
                    content_found = True
            except Exception as e:
                all_content += f"Error reading debug_load.txt: {str(e)}\n\n"
        
        # Check debug_save.txt (for saving issues)  
        if debug_save.exists():
            try:
                with open(debug_save, 'r', encoding='utf-8', errors='ignore') as f:
                    save_content = f.read()
                if save_content:
                    all_content += "=== DEBUG SAVE LOG ===\n" + save_content + "\n\n"
                    content_found = True
            except Exception as e:
                all_content += f"Error reading debug_save.txt: {str(e)}\n\n"
        
        if content_found:
            self.text_area.insert(1.0, all_content)
            # Scroll to bottom to see latest entries
            self.text_area.see(tk.END)
            line_count = len(all_content.splitlines())
            self.status_label.config(text=f"Loaded {line_count} lines from debug files")
        else:
            self.text_area.insert(1.0, "No debug files found (debug_save.txt or debug_load.txt).\nDebug files will be created when the app encounters issues.")
            self.status_label.config(text="No debug files found")
    
    def copy_all(self):
        """Copy all text to clipboard"""
        try:
            content = self.text_area.get(1.0, tk.END).strip()
            if content:
                pyperclip.copy(content)
                self.status_label.config(text="Copied to clipboard!")
                messagebox.showinfo("Copied", "Debug log copied to clipboard!")
            else:
                self.status_label.config(text="Nothing to copy")
                messagebox.showwarning("Nothing to Copy", "Debug log is empty")
        except Exception as e:
            # Fallback if pyperclip fails - copy to system clipboard
            try:
                self.root.clipboard_clear()
                self.root.clipboard_append(content)
                self.root.update()
                self.status_label.config(text="Copied to clipboard!")
                messagebox.showinfo("Copied", "Debug log copied to clipboard!")
            except Exception as e2:
                self.status_label.config(text="Copy failed")
                messagebox.showerror("Copy Failed", f"Failed to copy to clipboard: {str(e2)}")
    
    def clear_debug_file(self):
        """Clear the debug files"""
        debug_save = Path("debug_save.txt")
        debug_load = Path("debug_load.txt")
        
        result = messagebox.askyesno("Clear Debug Log", 
                                   "Are you sure you want to clear the debug log?")
        if result:
            try:
                if debug_save.exists():
                    debug_save.unlink()
                if debug_load.exists():
                    debug_load.unlink()
                self.load_debug_file()  # Refresh display
                self.status_label.config(text="Debug logs cleared")
                messagebox.showinfo("Cleared", "Debug logs cleared")
            except Exception as e:
                self.status_label.config(text="Clear failed")
                messagebox.showerror("Error", f"Failed to clear debug logs: {str(e)}")
    
    def run(self):
        """Run the debug viewer"""
        self.root.mainloop()

def main():
    """Main entry point"""
    try:
        # Try to import pyperclip for better clipboard support
        import pyperclip
    except ImportError:
        print("Note: Install pyperclip for enhanced clipboard support: pip install pyperclip")
        # Define a dummy pyperclip for fallback
        class DummyPyperclip:
            def copy(self, text):
                raise Exception("pyperclip not available")
        pyperclip = DummyPyperclip()
    
    app = DebugViewer()
    app.run()

if __name__ == "__main__":
    main()