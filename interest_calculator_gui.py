"""
Interest Rate Calculator - Desktop GUI Application
Phase 1: Basic Application Structure

Simple Tkinter desktop app with project list management.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime
from pathlib import Path


class InterestRateCalculator:
    def __init__(self):
        self.root = tk.Tk()
        self.projects_dir = Path("projects")
        self.projects_dir.mkdir(exist_ok=True)
        
        # App version and metadata
        self.version = "1.0.0"
        self.last_updated = "2025-09-06"
        self.launch_time = datetime.now().strftime("%H:%M:%S")
        
        self.setup_window()
        self.create_widgets()
        self.load_projects()
        
    def setup_window(self):
        """Setup main window properties."""
        # Title with version info and runtime
        self.start_time = datetime.now()
        title = f"Interest Rate Calculator v{self.version} - Last Updated: {self.last_updated} - Launched: {self.launch_time} - Runtime: {self.start_time.strftime('%H:%M:%S')}"
        self.root.title(title)
        
        # Window size and positioning
        self.root.geometry("800x600")
        self.root.minsize(600, 400)
        
        # Center the window
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (800 // 2)
        y = (self.root.winfo_screenheight() // 2) - (600 // 2)
        self.root.geometry(f"800x600+{x}+{y}")
        
        # Bring to front but don't stay on top permanently
        self.root.lift()
        self.root.focus_force()
        
        # Update runtime every second
        self.update_runtime()
        
    def create_widgets(self):
        """Create main UI widgets."""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="Interest Rate Calculator", 
                               font=("Arial", 16, "bold"))
        title_label.pack(pady=(0, 20))
        
        # Projects section
        projects_frame = ttk.LabelFrame(main_frame, text="Projects", padding="10")
        projects_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # Project list
        self.project_listbox = tk.Listbox(projects_frame, height=10)
        self.project_listbox.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Bind double-click to open project editor
        self.project_listbox.bind('<Double-1>', self.on_double_click)
        
        # Project buttons
        button_frame = ttk.Frame(projects_frame)
        button_frame.pack(fill=tk.X)
        
        self.new_btn = ttk.Button(button_frame, text="New Project", width=18, 
                                command=self.new_project)
        self.new_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.edit_btn = ttk.Button(button_frame, text="Edit Project", width=18,
                                 command=self.edit_project)
        self.edit_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.delete_btn = ttk.Button(button_frame, text="Delete Project", width=18,
                                   command=self.delete_project)
        self.delete_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, 
                             relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(fill=tk.X, pady=(10, 0))
        
    def load_projects(self):
        """Load existing projects from JSON files."""
        self.project_listbox.delete(0, tk.END)
        
        if not self.projects_dir.exists():
            return
            
        project_files = list(self.projects_dir.glob("*.json"))
        
        if not project_files:
            self.project_listbox.insert(tk.END, "No projects found")
            self.status_var.set("No projects available")
            return
            
        for project_file in sorted(project_files):
            try:
                with open(project_file, 'r') as f:
                    project_data = json.load(f)
                    project_name = project_data.get('title', project_file.stem)
                    self.project_listbox.insert(tk.END, project_name)
            except Exception as e:
                self.project_listbox.insert(tk.END, f"Error loading {project_file.name}")
                
        self.status_var.set(f"Loaded {len(project_files)} projects")
        
    def new_project(self):
        """Create a new project."""
        messagebox.showinfo("New Project", "New project creation will be implemented in Phase 2")
        self.status_var.set("New project feature coming in Phase 2")
        
    def edit_project(self):
        """Edit selected project."""
        selection = self.project_listbox.curselection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a project to edit")
            return
            
        project_name = self.project_listbox.get(selection[0])
        
        # Find the project file
        project_files = list(self.projects_dir.glob("*.json"))
        for project_file in project_files:
            try:
                with open(project_file, 'r') as f:
                    project_data = json.load(f)
                    if project_data.get('title', project_file.stem) == project_name:
                        # Open project editing window
                        self.open_project_editor(project_data, project_file)
                        return
            except Exception as e:
                continue
                
        messagebox.showerror("Error", f"Could not load project: {project_name}")
        
    def delete_project(self):
        """Delete selected project."""
        selection = self.project_listbox.curselection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a project to delete")
            return
            
        project_name = self.project_listbox.get(selection[0])
        
        if messagebox.askyesno("Delete Project", f"Are you sure you want to delete '{project_name}'?"):
            # Find and delete the project file
            project_files = list(self.projects_dir.glob("*.json"))
            for project_file in project_files:
                try:
                    with open(project_file, 'r') as f:
                        project_data = json.load(f)
                        if project_data.get('title', project_file.stem) == project_name:
                            project_file.unlink()
                            self.load_projects()
                            self.status_var.set(f"Deleted project: {project_name}")
                            return
                except Exception as e:
                    continue
                    
            messagebox.showerror("Error", f"Could not delete project: {project_name}")
    
    def on_double_click(self, event):
        """Handle double-click on project list."""
        selection = self.project_listbox.curselection()
        if selection:
            self.edit_project()
    
    def open_project_editor(self, project_data, project_file):
        """Open project editing window."""
        editor = ProjectEditor(self.root, project_data, project_file, self)
        editor.show()
    
    def update_runtime(self):
        """Update runtime in title bar every second."""
        current_time = datetime.now()
        runtime = current_time - self.start_time
        runtime_str = str(runtime).split('.')[0]  # Remove microseconds
        
        title = f"Interest Rate Calculator v{self.version} - Last Updated: {self.last_updated} - Launched: {self.launch_time} - Runtime: {runtime_str}"
        self.root.title(title)
        
        # Schedule next update
        self.root.after(1000, self.update_runtime)
            
    def run(self):
        """Start the application."""
        # Ensure window is visible and persistent
        self.root.deiconify()  # Make sure window is not minimized
        self.root.lift()       # Bring to front
        self.root.focus_force()  # Focus the window
        
        # Start the main loop
        self.root.mainloop()


class ProjectEditor:
    """Project editing window."""
    
    def __init__(self, parent, project_data, project_file, main_app):
        self.parent = parent
        self.project_data = project_data.copy()
        self.project_file = project_file
        self.main_app = main_app
        
        self.window = tk.Toplevel(parent)
        self.window.title(f"Edit Project: {project_data.get('title', 'Untitled')}")
        self.window.geometry("600x500")
        self.window.transient(parent)
        self.window.grab_set()
        
        # Center the window
        self.window.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() // 2) - (600 // 2)
        y = parent.winfo_y() + (parent.winfo_height() // 2) - (500 // 2)
        self.window.geometry(f"600x500+{x}+{y}")
        
        self.create_widgets()
        self.load_data()
        
    def create_widgets(self):
        """Create editor widgets."""
        main_frame = ttk.Frame(self.window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Project Title
        ttk.Label(main_frame, text="Project Title:").pack(anchor=tk.W)
        self.title_var = tk.StringVar()
        title_entry = ttk.Entry(main_frame, textvariable=self.title_var, width=50)
        title_entry.pack(fill=tk.X, pady=(0, 10))
        
        # Dates Frame
        dates_frame = ttk.LabelFrame(main_frame, text="Dates", padding="10")
        dates_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(dates_frame, text="Billing Date (YYYY-MM-DD):").pack(anchor=tk.W)
        self.billing_date_var = tk.StringVar()
        ttk.Entry(dates_frame, textvariable=self.billing_date_var, width=20).pack(anchor=tk.W, pady=(0, 5))
        
        ttk.Label(dates_frame, text="As-of Date (YYYY-MM-DD):").pack(anchor=tk.W)
        self.as_of_date_var = tk.StringVar()
        ttk.Entry(dates_frame, textvariable=self.as_of_date_var, width=20).pack(anchor=tk.W)
        
        # Rates Frame
        rates_frame = ttk.LabelFrame(main_frame, text="Interest Rates", padding="10")
        rates_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(rates_frame, text="Grace Days:").pack(anchor=tk.W)
        self.grace_days_var = tk.StringVar()
        ttk.Entry(rates_frame, textvariable=self.grace_days_var, width=10).pack(anchor=tk.W, pady=(0, 5))
        
        ttk.Label(rates_frame, text="Annual Rate (e.g., 0.18 for 18%):").pack(anchor=tk.W)
        self.annual_rate_var = tk.StringVar()
        ttk.Entry(rates_frame, textvariable=self.annual_rate_var, width=10).pack(anchor=tk.W, pady=(0, 5))
        
        ttk.Label(rates_frame, text="Monthly Rate (e.g., 0.015 for 1.5%):").pack(anchor=tk.W)
        self.monthly_rate_var = tk.StringVar()
        ttk.Entry(rates_frame, textvariable=self.monthly_rate_var, width=10).pack(anchor=tk.W)
        
        # Principals Frame
        principals_frame = ttk.LabelFrame(main_frame, text="Principal Amounts", padding="10")
        principals_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(principals_frame, text="Flood/Wind Principal:").pack(anchor=tk.W)
        self.principal_fw_var = tk.StringVar()
        ttk.Entry(principals_frame, textvariable=self.principal_fw_var, width=20).pack(anchor=tk.W, pady=(0, 5))
        
        ttk.Label(principals_frame, text="Drywall Principal:").pack(anchor=tk.W)
        self.principal_dw_var = tk.StringVar()
        ttk.Entry(principals_frame, textvariable=self.principal_dw_var, width=20).pack(anchor=tk.W)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(20, 0))
        
        ttk.Button(button_frame, text="Save", command=self.save_project, width=12).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Generate Report", command=self.generate_report, width=18).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Cancel", command=self.window.destroy, width=12).pack(side=tk.LEFT)
        
    def load_data(self):
        """Load project data into form fields."""
        self.title_var.set(self.project_data.get('title', ''))
        self.billing_date_var.set(self.project_data.get('billing_date', ''))
        self.as_of_date_var.set(self.project_data.get('as_of_date', ''))
        self.grace_days_var.set(str(self.project_data.get('grace_days', '')))
        self.annual_rate_var.set(str(self.project_data.get('annual_rate', '')))
        self.monthly_rate_var.set(str(self.project_data.get('monthly_rate', '')))
        self.principal_fw_var.set(str(self.project_data.get('principal_fw', '')))
        self.principal_dw_var.set(str(self.project_data.get('principal_dw', '')))
        
    def save_project(self):
        """Save project data."""
        try:
            # Update project data
            self.project_data['title'] = self.title_var.get()
            self.project_data['billing_date'] = self.billing_date_var.get()
            self.project_data['as_of_date'] = self.as_of_date_var.get()
            self.project_data['grace_days'] = int(self.grace_days_var.get())
            self.project_data['annual_rate'] = float(self.annual_rate_var.get())
            self.project_data['monthly_rate'] = float(self.monthly_rate_var.get())
            self.project_data['principal_fw'] = float(self.principal_fw_var.get())
            self.project_data['principal_dw'] = float(self.principal_dw_var.get())
            
            # Save to file
            with open(self.project_file, 'w') as f:
                json.dump(self.project_data, f, indent=2)
            
            messagebox.showinfo("Success", "Project saved successfully!")
            self.main_app.load_projects()  # Refresh project list
            self.window.destroy()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save project: {str(e)}")
    
    def generate_report(self):
        """Generate report for this project."""
        messagebox.showinfo("Generate Report", "Report generation will be implemented in Phase 3")
    
    def show(self):
        """Show the editor window."""
        self.window.focus()
        self.window.wait_window()


def main():
    """Main entry point."""
    app = InterestRateCalculator()
    app.run()


if __name__ == "__main__":
    main()
