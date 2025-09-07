"""
Interest Rate Calculator - Desktop GUI Application
Phase 1.5: Single Window with Integrated Project Editor and Payment Management

All functionality in one window with payment table for aging calculations.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import tkinter.font as tkfont
import json
import os
from datetime import datetime
from pathlib import Path
import traceback

def convert_to_american_date(date_str):
    """Convert YYYY-MM-DD format to MM/DD/YYYY format."""
    if not date_str:
        return ''
    try:
        if '/' in date_str:  # Already American format
            return date_str
        # Convert from YYYY-MM-DD to MM/DD/YYYY
        dt = datetime.strptime(date_str, '%Y-%m-%d')
        return dt.strftime('%m/%d/%Y')
    except:
        return date_str

def convert_to_iso_date(date_str):
    """Convert MM/DD/YYYY format to YYYY-MM-DD format for storage."""
    if not date_str:
        return ''
    try:
        if '-' in date_str and len(date_str.split('-')[0]) == 4:  # Already ISO format
            return date_str
        # Convert from MM/DD/YYYY to YYYY-MM-DD
        dt = datetime.strptime(date_str, '%m/%d/%Y')
        return dt.strftime('%Y-%m-%d')
    except:
        return date_str

def format_currency(value):
    """Format a number as currency."""
    try:
        if isinstance(value, str):
            # Remove existing formatting
            clean_value = value.replace('$', '').replace(',', '')
            if not clean_value:
                return ''
            value = float(clean_value)
        return f"${value:,.2f}"
    except:
        return str(value)

def parse_currency(value_str):
    """Parse a currency string to float."""
    try:
        if isinstance(value_str, (int, float)):
            return float(value_str)
        clean_value = str(value_str).replace('$', '').replace(',', '')
        return float(clean_value) if clean_value else 0.0
    except:
        return 0.0

def format_percentage(value):
    """Format a decimal as percentage."""
    try:
        if isinstance(value, str):
            # If already has %, just return it
            if '%' in value:
                return value
            value = float(value)
        return f"{value * 100:.1f}%"
    except:
        return str(value)

def parse_percentage(value_str):
    """Parse a percentage string to decimal."""
    try:
        if isinstance(value_str, (int, float)):
            return float(value_str)
        clean_value = str(value_str).replace('%', '')
        return float(clean_value) / 100 if clean_value else 0.0
    except:
        return 0.0


class CollapsibleSection(ttk.Frame):
    """A truly collapsible section with 30% larger, bold header that removes all space when collapsed."""
    
    def __init__(self, parent, title: str):
        super().__init__(parent)
        self._collapsed = False
        
        # Create 30% larger, bold header font
        base_font = tkfont.nametofont("TkDefaultFont")
        header_font = (base_font.actual("family"), max(1, int(base_font.actual("size") * 1.3)), "bold")
        
        # Header label with hand cursor
        self.header = ttk.Label(self, text=title, font=header_font, cursor="hand2")
        self.header.pack(fill=tk.X, pady=(2, 0))
        self.header.bind("<Button-1>", self.toggle)
        
        # Content frame that gets shown/hidden
        self.content = ttk.Frame(self)
        self.content.pack(fill=tk.BOTH, expand=True, pady=(6, 0))
    
    def set_content(self, widget):
        """Set the content widget for this section."""
        # Remove widget from its current parent and add to our content frame
        widget.pack_forget()
        widget.master = self.content
        widget.pack(fill=tk.BOTH, expand=True)
    
    def collapse(self):
        """Collapse the section - hide content completely."""
        if not self._collapsed:
            self.content.pack_forget()
            self._collapsed = True
    
    def expand(self):
        """Expand the section - show content."""
        if self._collapsed:
            self.content.pack(fill=tk.BOTH, expand=True, pady=(6, 0))
            self._collapsed = False
    
    def toggle(self, *args):
        """Toggle between collapsed and expanded states."""
        if self._collapsed:
            self.expand()
        else:
            self.collapse()


class InterestRateCalculator:
    def __init__(self):
        try:
            self.root = tk.Tk()
            self.projects_dir = Path("projects")
            self.projects_dir.mkdir(exist_ok=True)
            
            # App version and metadata
            self.version = "1.0.0"
            self.last_updated = "2025-09-06"
            self.launch_time = datetime.now().strftime("%H:%M:%S")
            
            # Current project data
            self.current_project = None
            self.current_project_file = None
            
            self.setup_window()
            self.create_widgets()
            self.load_projects()
            
        except Exception as e:
            print(f"Error initializing application: {e}")
            traceback.print_exc()
            raise
        
    def setup_window(self):
        """Setup main window properties."""
        # Title with version info and runtime
        self.start_time = datetime.now()
        title = f"Interest Rate Calculator v{self.version} - Last Updated: {self.last_updated} - Launched: {self.launch_time} - Runtime: {self.start_time.strftime('%H:%M:%S')}"
        self.root.title(title)
        
        # Window size and positioning
        self.root.geometry("1200x800")
        self.root.minsize(1000, 700)
        
        # Simple centering without complex calculations
        self.root.update_idletasks()
        width = self.root.winfo_screenwidth()
        height = self.root.winfo_screenheight()
        x = (width - 1200) // 2
        y = (height - 800) // 2
        self.root.geometry(f"1200x800+{x}+{y}")
        
        # Update runtime every second
        self.update_runtime()
        
    def create_widgets(self):
        """Create main UI widgets."""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="Interest Rate Calculator", 
                               font=("Arial", 16, "bold"))
        title_label.pack(pady=(0, 10))
        
        # Project Selection Section (Always at top)
        self.create_project_selection_section(main_frame)
        
        # Main content area
        self.content_frame = ttk.Frame(main_frame)
        self.content_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, 
                             relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(fill=tk.X, pady=(10, 0))
        
    def create_project_selection_section(self, parent):
        """Create project selection section at the top."""
        # Project selection frame - collapsible
        self.project_frame = CollapsibleSection(parent, "Project Selection")
        self.project_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Content frame for project selection
        project_content = ttk.Frame(self.project_frame.content, padding="10")
        self.project_frame.set_content(project_content)
        
        # Project list and buttons in one row
        top_frame = ttk.Frame(project_content)
        top_frame.pack(fill=tk.X)
        
        # Project list with TreeView for better display
        list_frame = ttk.Frame(top_frame)
        list_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        ttk.Label(list_frame, text="Available Projects:").pack(anchor=tk.W)
        
        # Create TreeView with columns for project details
        columns = ('Title', 'Last Modified', 'Status')
        self.project_tree = ttk.Treeview(list_frame, columns=columns, show='tree headings', height=6)
        
        # Configure column headings and widths
        self.project_tree.heading('#0', text='File', anchor=tk.W)
        self.project_tree.column('#0', width=120, minwidth=80)
        
        for col in columns:
            self.project_tree.heading(col, text=col, anchor=tk.W)
            if col == 'Title':
                self.project_tree.column(col, width=200, minwidth=150)
            elif col == 'Last Modified':
                self.project_tree.column(col, width=120, minwidth=100)
            else:  # Status
                self.project_tree.column(col, width=80, minwidth=60)
        
        # Add scrollbar for TreeView
        tree_scroll = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.project_tree.yview)
        self.project_tree.configure(yscrollcommand=tree_scroll.set)
        
        # Pack TreeView and scrollbar
        self.project_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, pady=(5, 0))
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y, pady=(5, 0))
        
        # Bind double-click to open project editor
        self.project_tree.bind('<Double-1>', self.on_double_click)
        
        # Also keep the old listbox reference for compatibility (hidden)
        self.project_listbox = self.project_tree
        
        # Project buttons
        button_frame = ttk.Frame(top_frame)
        button_frame.pack(side=tk.RIGHT)
        
        self.new_btn = ttk.Button(button_frame, text="New Project", width=15, 
                                command=self.new_project)
        self.new_btn.pack(pady=2)
        
        self.edit_btn = ttk.Button(button_frame, text="Edit Project", width=15,
                                 command=self.edit_project)
        self.edit_btn.pack(pady=2)
        
        self.delete_btn = ttk.Button(button_frame, text="Delete Project", width=15,
                                   command=self.delete_project)
        self.delete_btn.pack(pady=2)
        
        # Separator
        ttk.Separator(button_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=5)
        
        # Import/Export buttons
        self.import_btn = ttk.Button(button_frame, text="Import Project", width=15,
                                   command=self.import_project)
        self.import_btn.pack(pady=2)
        
        self.export_btn = ttk.Button(button_frame, text="Export Project", width=15,
                                   command=self.export_project)
        self.export_btn.pack(pady=2)
        
        
    def load_projects(self):
        """Load existing projects from JSON files into TreeView."""
        # Clear existing items
        for item in self.project_tree.get_children():
            self.project_tree.delete(item)
        
        if not self.projects_dir.exists():
            return
            
        project_files = list(self.projects_dir.glob("*.json"))
        
        if not project_files:
            # Insert a placeholder item
            self.project_tree.insert('', tk.END, text="No projects found", 
                                   values=("", "", ""))
            self.status_var.set("No projects available")
            return
            
        loaded_count = 0
        for project_file in sorted(project_files):
            try:
                with open(project_file, 'r') as f:
                    project_data = json.load(f)
                    
                # Get project details
                project_title = project_data.get('title', project_file.stem)
                
                # Get file modification time
                mod_time = datetime.fromtimestamp(project_file.stat().st_mtime)
                mod_time_str = mod_time.strftime('%m/%d/%Y %H:%M')
                
                # Determine status based on project data
                status = "Ready"
                if not project_data.get('title'):
                    status = "Incomplete"
                elif not project_data.get('as_of_date'):
                    status = "Missing Date"
                
                # Insert into TreeView
                self.project_tree.insert('', tk.END, 
                                       text=project_file.name,
                                       values=(project_title, mod_time_str, status),
                                       tags=(project_file.name,))  # Store filename in tags
                loaded_count += 1
                
            except Exception as e:
                # Insert error item
                self.project_tree.insert('', tk.END, 
                                       text=project_file.name,
                                       values=(f"Error: {str(e)[:30]}...", "", "Error"),
                                       tags=(project_file.name,))
                
        self.status_var.set(f"Loaded {loaded_count} projects")
        
    def new_project(self):
        """Create a new project using modal dialog."""
        dialog = NewProjectDialog(self.root)
        if dialog.result:
            # Create new project with the provided data
            project_data = {
                'title': dialog.result['title'],
                'description': dialog.result.get('description', ''),
                'as_of_date': dialog.result.get('as_of_date', ''),
                'grace_days': dialog.result.get('grace_days', 30),
                'annual_rate': dialog.result.get('annual_rate', 0.18),
                'monthly_rate': dialog.result.get('monthly_rate', 0.015),
                'payments': [],
                'invoices': []
            }
            
            # Show the project editor and load the new project data
            self.show_project_editor()
            
            # Create a temporary file path for the new project
            safe_filename = "".join(c for c in dialog.result['title'] if c.isalnum() or c in (' ', '-', '_')).rstrip()
            safe_filename = safe_filename.replace(' ', '_') + '.json'
            temp_file = self.projects_dir / safe_filename
            
            self.load_project_data(project_data, temp_file)
            self.status_var.set(f"Created new project: {dialog.result['title']}")
        else:
            self.status_var.set("New project creation cancelled")
        
    def edit_project(self):
        """Edit selected project."""
        selection = self.project_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a project to edit")
            return
            
        # Get the selected item
        item = selection[0]
        filename = self.project_tree.item(item, 'text')
        
        # Skip if it's a placeholder item
        if filename == "No projects found":
            return
        
        # Find the project file
        project_file = self.projects_dir / filename
        if not project_file.exists():
            messagebox.showerror("Error", f"Project file not found: {filename}")
            return
            
        try:
            with open(project_file, 'r') as f:
                project_data = json.load(f)
            self.show_project_editor()  # Create form first
            self.load_project_data(project_data, project_file)  # Then load data
        except Exception as e:
            messagebox.showerror("Error", f"Could not load project: {str(e)}")
        
    def show_project_editor(self):
        """Show the project editor sections."""
        # Clear existing content
        for widget in self.content_frame.winfo_children():
            widget.destroy()
            
        # Create collapsible sections
        self.create_collapsible_sections()
        
    def create_collapsible_sections(self):
        """Create collapsible sections for project editing."""
        # Condensed Project Information Section (dates, rates, principals)
        self.create_project_info_section()
        
        # Invoices Section (under project information)
        self.create_invoices_section()
        
        # Payments Section
        self.create_payments_section()
        
        # Action Buttons
        self.create_action_buttons()
        
    def create_project_info_section(self):
        """Create condensed project information section with dates, rates, and principals."""
        self.info_frame = CollapsibleSection(self.content_frame, "Project Information")
        self.info_frame.pack(fill=tk.X, pady=(0, 5))
        
        # Content frame for project info
        info_content = ttk.Frame(self.info_frame.content, padding="10")
        self.info_frame.set_content(info_content)
        
        # Project Title
        ttk.Label(info_content, text="Project Title:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10), pady=2)
        self.title_var = tk.StringVar()
        title_entry = ttk.Entry(info_content, textvariable=self.title_var, width=50)
        title_entry.grid(row=0, column=1, columnspan=3, sticky=tk.W, pady=2)
        
        # Payments Calculated Through Date Row with Date Picker
        ttk.Label(info_content, text="Payments Calculated Through Date:").grid(row=1, column=0, sticky=tk.W, padx=(0, 5), pady=2)
        
        # Date entry frame with picker button
        date_frame = ttk.Frame(info_content)
        date_frame.grid(row=1, column=1, sticky=tk.W, pady=2)
        
        self.as_of_date_var = tk.StringVar()
        date_entry = ttk.Entry(date_frame, textvariable=self.as_of_date_var, width=12)
        date_entry.pack(side=tk.LEFT)
        
        # Date picker button
        date_picker_btn = ttk.Button(date_frame, text="📅", width=3, 
                                    command=lambda: self.show_date_picker(self.as_of_date_var))
        date_picker_btn.pack(side=tk.LEFT, padx=(2, 0))
        
        # Today button for quick date entry
        today_btn = ttk.Button(date_frame, text="Today", width=6,
                              command=lambda: self.set_today_date(self.as_of_date_var))
        today_btn.pack(side=tk.LEFT, padx=(2, 0))
        
        # Rates Row with enhanced validation
        ttk.Label(info_content, text="Grace Days:").grid(row=2, column=0, sticky=tk.W, padx=(0, 5), pady=2)
        
        # Grace days with validation
        grace_frame = ttk.Frame(info_content)
        grace_frame.grid(row=2, column=1, sticky=tk.W, pady=2)
        
        self.grace_days_var = tk.StringVar()
        grace_entry = ttk.Entry(grace_frame, textvariable=self.grace_days_var, width=8)
        grace_entry.pack(side=tk.LEFT)
        grace_entry.bind('<KeyRelease>', lambda e: self.validate_numeric_input(self.grace_days_var, 'integer'))
        
        # Grace days info label
        ttk.Label(grace_frame, text="days", foreground="gray").pack(side=tk.LEFT, padx=(2, 0))
        
        # Annual Rate with auto-calculation
        ttk.Label(info_content, text="Annual Rate (%):").grid(row=2, column=2, sticky=tk.W, padx=(10, 5), pady=2)
        
        annual_frame = ttk.Frame(info_content)
        annual_frame.grid(row=2, column=3, sticky=tk.W, pady=2)
        
        self.annual_rate_var = tk.StringVar()
        annual_rate_entry = ttk.Entry(annual_frame, textvariable=self.annual_rate_var, width=8)
        annual_rate_entry.pack(side=tk.LEFT)
        annual_rate_entry.bind('<KeyRelease>', self.on_annual_rate_change)
        annual_rate_entry.bind('<FocusOut>', self.format_annual_rate)
        
        # Auto-calc button
        auto_calc_btn = ttk.Button(annual_frame, text="Auto", width=4,
                                  command=self.auto_calculate_monthly_rate)
        auto_calc_btn.pack(side=tk.LEFT, padx=(2, 0))
        
        # Monthly Rate Row with validation
        ttk.Label(info_content, text="Monthly Rate (%):").grid(row=3, column=0, sticky=tk.W, padx=(0, 5), pady=2)
        
        monthly_frame = ttk.Frame(info_content)
        monthly_frame.grid(row=3, column=1, sticky=tk.W, pady=2)
        
        self.monthly_rate_var = tk.StringVar()
        monthly_rate_entry = ttk.Entry(monthly_frame, textvariable=self.monthly_rate_var, width=8)
        monthly_rate_entry.pack(side=tk.LEFT)
        monthly_rate_entry.bind('<KeyRelease>', lambda e: self.validate_numeric_input(self.monthly_rate_var, 'percentage'))
        monthly_rate_entry.bind('<FocusOut>', self.format_monthly_rate)
        
        # Rate relationship indicator
        self.rate_status_label = ttk.Label(monthly_frame, text="", foreground="gray")
        self.rate_status_label.pack(side=tk.LEFT, padx=(5, 0))
        
        # Note: Principal amounts are now managed through individual invoices
        # Each invoice represents a principal amount that accrues interest from its invoice date
    
    def format_annual_rate(self, event=None):
        """Format annual rate as percentage"""
        try:
            value = self.annual_rate_var.get()
            if value and not value.endswith('%'):
                # If it's a decimal like 0.18, convert to percentage
                num_value = float(value)
                if num_value <= 1.0:
                    formatted = f"{num_value * 100:.1f}%"
                else:
                    formatted = f"{num_value:.1f}%"
                self.annual_rate_var.set(formatted)
        except:
            pass
    
    def format_monthly_rate(self, event=None):
        """Format monthly rate as percentage"""
        try:
            value = self.monthly_rate_var.get()
            if value and not value.endswith('%'):
                # If it's a decimal like 0.015, convert to percentage
                num_value = float(value)
                if num_value <= 1.0:
                    formatted = f"{num_value * 100:.1f}%"
                else:
                    formatted = f"{num_value:.1f}%"
                self.monthly_rate_var.set(formatted)
        except:
            pass
    
    # Principal formatting methods removed - principals are now managed through invoices
        
    def create_invoices_section(self):
        """Create collapsible invoices section with table."""
        self.invoices_frame = CollapsibleSection(self.content_frame, "Invoices")
        self.invoices_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 5))
        
        # Content frame for invoices
        invoices_content = ttk.Frame(self.invoices_frame.content, padding="10")
        self.invoices_frame.set_content(invoices_content)
        
        # Invoice buttons at the top
        invoice_btn_frame = ttk.Frame(invoices_content)
        invoice_btn_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(invoice_btn_frame, text="Add Invoice", command=self.add_invoice, width=15).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(invoice_btn_frame, text="Edit Invoice", command=self.edit_invoice, width=15).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(invoice_btn_frame, text="Delete Invoice", command=self.delete_invoice, width=15).pack(side=tk.LEFT)
        
        # Invoice table with proper formatting
        columns = ('ID', 'Date', 'Description', 'Amount')
        self.invoices_tree = ttk.Treeview(invoices_content, columns=columns, show='headings', height=8)
        
        # Configure column widths and headings
        self.invoices_tree.heading('ID', text='Invoice ID')
        self.invoices_tree.heading('Date', text='Date')
        self.invoices_tree.heading('Description', text='Description')
        self.invoices_tree.heading('Amount', text='Amount')
        
        self.invoices_tree.column('ID', width=100, anchor='center')
        self.invoices_tree.column('Date', width=100, anchor='center')
        self.invoices_tree.column('Description', width=180, anchor='center')
        self.invoices_tree.column('Amount', width=100, anchor='center')
        
        # Add scrollbar
        invoice_scrollbar = ttk.Scrollbar(invoices_content, orient=tk.VERTICAL, command=self.invoices_tree.yview)
        self.invoices_tree.configure(yscrollcommand=invoice_scrollbar.set)
        
        # Pack table and scrollbar
        self.invoices_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        invoice_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def add_invoice(self):
        """Add a new invoice."""
        print("DEBUG: add_invoice() called")
        dialog = InvoiceDialog(self.root, "Add Invoice")
        
        # Wait for the dialog to complete (modal behavior)
        self.root.wait_window(dialog.window)
        
        print(f"DEBUG: Dialog completed, dialog.result = {dialog.result}")
        
        if dialog.result:
            print(f"DEBUG: Dialog result exists: {dialog.result}")
            # Add to tree view with new 4-column format (ID, Date, Description, Amount)
            values = (
                dialog.result['id'],
                dialog.result['date'],
                dialog.result['desc'],
                f"${dialog.result['amount']:,.2f}"
            )
            print(f"DEBUG: Inserting values: {values}")
            
            self.invoices_tree.insert('', 'end', values=values)
            print("DEBUG: Invoice inserted into tree")
            
            # Update status
            self.status_var.set(f"Invoice {dialog.result['id']} added successfully")
        else:
            print("DEBUG: No dialog result - user cancelled or error occurred")
            
    def edit_invoice(self):
        """Edit selected invoice."""
        selection = self.invoices_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select an invoice to edit")
            return
            
        item = self.invoices_tree.item(selection[0])
        values = item['values']
        
        # Parse existing data (new 4-column format: ID, Date, Description, Amount)
        existing_data = {
            'id': values[0],
            'date': values[1],
            'desc': values[2],
            'amount': float(values[3].replace('$', '').replace(',', ''))
        }
        
        dialog = InvoiceDialog(self.root, "Edit Invoice", existing_data)
        
        # Wait for the dialog to complete (modal behavior)
        self.root.wait_window(dialog.window)
        
        if dialog.result:
            # Update tree view with new 4-column format
            self.invoices_tree.item(selection[0], values=(
                dialog.result['id'],
                dialog.result['date'],
                dialog.result['desc'],
                f"${dialog.result['amount']:,.2f}"
            ))
            
    def delete_invoice(self):
        """Delete selected invoice."""
        selection = self.invoices_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select an invoice to delete")
            return
            
        if messagebox.askyesno("Delete Invoice", "Are you sure you want to delete this invoice?"):
            self.invoices_tree.delete(selection[0])
        
    def create_payments_section(self):
        """Create collapsible payments section with improved table."""
        self.payments_frame = CollapsibleSection(self.content_frame, "Payments")
        self.payments_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 5))
        
        # Content frame for payments
        payments_content = ttk.Frame(self.payments_frame.content, padding="10")
        self.payments_frame.set_content(payments_content)
        
        # Payment buttons at the top
        payment_btn_frame = ttk.Frame(payments_content)
        payment_btn_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(payment_btn_frame, text="Add Payment", command=self.add_payment, width=15).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(payment_btn_frame, text="Edit Payment", command=self.edit_payment, width=15).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(payment_btn_frame, text="Delete Payment", command=self.delete_payment, width=15).pack(side=tk.LEFT)
        
        # Payment table with proper formatting
        columns = ('Date', 'Description', 'Amount')
        self.payments_tree = ttk.Treeview(payments_content, columns=columns, show='headings', height=8)
        
        # Configure column widths and headings
        self.payments_tree.heading('Date', text='Date')
        self.payments_tree.heading('Description', text='Description')
        self.payments_tree.heading('Amount', text='Amount')
        
        self.payments_tree.column('Date', width=120, anchor='center')
        self.payments_tree.column('Description', width=200, anchor='center')
        self.payments_tree.column('Amount', width=120, anchor='center')
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(payments_content, orient=tk.VERTICAL, command=self.payments_tree.yview)
        self.payments_tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack table and scrollbar
        self.payments_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
    def create_action_buttons(self):
        """Create action buttons section."""
        action_frame = ttk.Frame(self.content_frame)
        action_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(action_frame, text="Save Project", command=self.save_project, width=15).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(action_frame, text="Generate Report", command=self.generate_report, width=18).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(action_frame, text="Clear Form", command=self.clear_form, width=15).pack(side=tk.LEFT)
        
    def on_double_click(self, event):
        """Handle double-click on project list."""
        self.edit_project()
        
    def load_project_data(self, project_data, project_file):
        """Load project data into editor form."""
        try:
            self.current_project = project_data.copy()
            self.current_project_file = project_file
            
            # Check if form variables exist (form must be created first)
            if not hasattr(self, 'title_var'):
                messagebox.showerror("Error", "Form not initialized. Please try again.")
                return
            
            # Load basic data
            self.title_var.set(project_data.get('title', ''))
            self.as_of_date_var.set(convert_to_american_date(project_data.get('as_of_date', '')))
            self.grace_days_var.set(str(project_data.get('grace_days', '')))
            
            # Format rates as percentages
            annual_rate = project_data.get('annual_rate', '')
            if annual_rate:
                self.annual_rate_var.set(format_percentage(annual_rate))
            
            monthly_rate = project_data.get('monthly_rate', '')
            if monthly_rate:
                self.monthly_rate_var.set(format_percentage(monthly_rate))
            
            # Format principals as currency
            # Principal amounts are now managed through individual invoices
            
            # Load invoices and payments
            self.load_invoices(project_data.get('invoices', []))
            self.load_payments(project_data.get('payments', []))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load project data: {str(e)}")
    
    def load_invoices(self, invoices):
        """Load invoices into the tree view."""
        # Clear existing items
        for item in self.invoices_tree.get_children():
            self.invoices_tree.delete(item)
            
        # Add invoices
        for invoice in invoices:
            # Generate ID if missing (for backward compatibility)
            invoice_id = invoice.get('id', f"INV-{len(invoices):04d}")
            self.invoices_tree.insert('', 'end', values=(
                invoice_id,
                convert_to_american_date(invoice.get('date', '')),
                invoice.get('desc', ''),
                f"${invoice.get('amount', 0):,.2f}"
            ))
        
    def load_payments(self, payments):
        """Load payments into the tree view."""
        # Clear existing items
        for item in self.payments_tree.get_children():
            self.payments_tree.delete(item)
            
        # Add payments
        for payment in payments:
            self.payments_tree.insert('', 'end', values=(
                convert_to_american_date(payment.get('date', '')),
                payment.get('desc', ''),
                f"${payment.get('amount', 0):,.2f}"
            ))
            
    def add_payment(self):
        """Add a new payment."""
        dialog = PaymentDialog(self.root, "Add Payment")
        
        # Wait for the dialog to complete (modal behavior)
        self.root.wait_window(dialog.window)
        
        if dialog.result:
            # Add to tree view
            self.payments_tree.insert('', 'end', values=(
                dialog.result['date'],
                dialog.result['desc'],
                f"${dialog.result['amount']:,.2f}"
            ))
            
    def edit_payment(self):
        """Edit selected payment."""
        selection = self.payments_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a payment to edit")
            return
            
        item = self.payments_tree.item(selection[0])
        values = item['values']
        
        # Parse existing data
        existing_data = {
            'date': values[0],
            'desc': values[1],
            'amount': float(values[2].replace('$', '').replace(',', ''))
        }
        
        dialog = PaymentDialog(self.root, "Edit Payment", existing_data)
        
        # Wait for the dialog to complete (modal behavior)
        self.root.wait_window(dialog.window)
        
        if dialog.result:
            # Update tree view
            self.payments_tree.item(selection[0], values=(
                dialog.result['date'],
                dialog.result['desc'],
                f"${dialog.result['amount']:,.2f}"
            ))
            
    def delete_payment(self):
        """Delete selected payment."""
        selection = self.payments_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a payment to delete")
            return
            
        if messagebox.askyesno("Delete Payment", "Are you sure you want to delete this payment?"):
            self.payments_tree.delete(selection[0])
            
    def save_project(self):
        """Save project data."""
        try:
            # Collect form data
            project_data = {
                'title': self.title_var.get(),
                'as_of_date': convert_to_iso_date(self.as_of_date_var.get()),
                'grace_days': int(self.grace_days_var.get()) if self.grace_days_var.get() else 0,
                'annual_rate': parse_percentage(self.annual_rate_var.get()),
                'monthly_rate': parse_percentage(self.monthly_rate_var.get()),
                'invoices': [],
                'payments': []
            }
            
            # Collect invoices from tree view
            for item in self.invoices_tree.get_children():
                values = self.invoices_tree.item(item)['values']
                invoice = {
                    'id': values[0],
                    'date': convert_to_iso_date(values[1]),
                    'desc': values[2],
                    'amount': float(values[3].replace('$', '').replace(',', ''))
                }
                project_data['invoices'].append(invoice)
            
            # Collect payments from tree view
            for item in self.payments_tree.get_children():
                values = self.payments_tree.item(item)['values']
                payment = {
                    'date': convert_to_iso_date(values[0]),
                    'desc': values[1],
                    'amount': float(values[2].replace('$', '').replace(',', ''))
                }
                project_data['payments'].append(payment)
            
            # Determine file path
            if not self.current_project_file:
                # New project - create filename from title
                safe_title = "".join(c for c in project_data['title'] if c.isalnum() or c in (' ', '-', '_')).rstrip()
                safe_title = safe_title.replace(' ', '-').lower()
                self.current_project_file = self.projects_dir / f"{safe_title}.json"
            
            # Save to file
            with open(self.current_project_file, 'w') as f:
                json.dump(project_data, f, indent=2)
            
            messagebox.showinfo("Success", "Project saved successfully!")
            self.load_projects()  # Refresh project list
            self.status_var.set(f"Saved project: {project_data['title']}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save project: {str(e)}")
    
    def generate_report(self):
        """Generate report for this project."""
        messagebox.showinfo("Generate Report", "Report generation will be implemented in Phase 3")
    
    def clear_form(self):
        """Clear all form fields."""
        self.title_var.set('')
        self.as_of_date_var.set('')
        self.grace_days_var.set('')
        self.annual_rate_var.set('')
        self.monthly_rate_var.set('')
        
        # Clear invoices
        for item in self.invoices_tree.get_children():
            self.invoices_tree.delete(item)
        
        # Clear payments
        for item in self.payments_tree.get_children():
            self.payments_tree.delete(item)
            
        self.current_project = None
        self.current_project_file = None
        self.status_var.set("Form cleared - ready for new project")
    
    def delete_project(self):
        """Delete selected project with enhanced confirmation."""
        selection = self.project_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a project to delete")
            return
            
        # Get the selected item details
        item = selection[0]
        filename = self.project_tree.item(item, 'text')
        project_title = self.project_tree.item(item, 'values')[0]  # Get title from TreeView
        
        # Skip if it's a placeholder item
        if filename == "No projects found":
            return
            
        # Enhanced confirmation dialog with more details
        confirm_msg = f"Are you sure you want to delete this project?\n\n"
        confirm_msg += f"File: {filename}\n"
        confirm_msg += f"Title: {project_title}\n\n"
        confirm_msg += "This action cannot be undone!"
        
        if messagebox.askyesno("Delete Project", confirm_msg, icon='warning'):
            project_file = self.projects_dir / filename
            
            try:
                if project_file.exists():
                    project_file.unlink()
                    self.load_projects()  # Refresh the TreeView
                    self.status_var.set(f"Deleted project: {project_title}")
                    
                    # Clear the editor if this project was being edited
                    if hasattr(self, 'current_project_file') and self.current_project_file == project_file:
                        self.clear_form()
                        for widget in self.content_frame.winfo_children():
                            widget.destroy()
                else:
                    messagebox.showerror("Error", f"Project file not found: {filename}")
                    
            except Exception as e:
                messagebox.showerror("Error", f"Could not delete project: {str(e)}")
    
    def import_project(self):
        """Import a project from a JSON file."""
        from tkinter import filedialog
        
        try:
            # Open file dialog to select JSON file
            file_path = filedialog.askopenfilename(
                title="Import Project",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
                initialdir=str(Path.home() / "Documents")
            )
            
            if not file_path:
                return  # User cancelled
                
            # Load and validate the project file
            with open(file_path, 'r') as f:
                project_data = json.load(f)
            
            # Basic validation
            required_fields = ['title']
            for field in required_fields:
                if field not in project_data:
                    messagebox.showerror("Import Error", 
                                       f"Invalid project file: missing '{field}' field")
                    return
            
            # Check if project already exists
            project_title = project_data['title']
            safe_filename = "".join(c for c in project_title if c.isalnum() or c in (' ', '-', '_')).rstrip()
            safe_filename = safe_filename.replace(' ', '_') + '.json'
            target_file = self.projects_dir / safe_filename
            
            if target_file.exists():
                if not messagebox.askyesno("Project Exists", 
                                         f"A project named '{project_title}' already exists.\n\n"
                                         f"Do you want to overwrite it?"):
                    return
            
            # Copy the project file to projects directory
            import shutil
            shutil.copy2(file_path, target_file)
            
            # Refresh the project list
            self.load_projects()
            
            # Select the imported project in the TreeView
            for item in self.project_tree.get_children():
                if self.project_tree.item(item, 'text') == safe_filename:
                    self.project_tree.selection_set(item)
                    self.project_tree.focus(item)
                    break
            
            self.status_var.set(f"Successfully imported project: {project_title}")
            messagebox.showinfo("Import Successful", 
                              f"Project '{project_title}' has been imported successfully!")
            
        except json.JSONDecodeError:
            messagebox.showerror("Import Error", "Invalid JSON file format")
        except Exception as e:
            messagebox.showerror("Import Error", f"Failed to import project: {str(e)}")
    
    def export_project(self):
        """Export selected project to a JSON file."""
        from tkinter import filedialog
        
        try:
            # Get selected project
            selection = self.project_tree.selection()
            if not selection:
                messagebox.showwarning("No Selection", "Please select a project to export")
                return
                
            # Get the selected item details
            item = selection[0]
            filename = self.project_tree.item(item, 'text')
            project_title = self.project_tree.item(item, 'values')[0]
            
            # Skip if it's a placeholder item
            if filename == "No projects found":
                return
                
            # Load the project data
            project_file = self.projects_dir / filename
            if not project_file.exists():
                messagebox.showerror("Error", f"Project file not found: {filename}")
                return
                
            with open(project_file, 'r') as f:
                project_data = json.load(f)
            
            # Open save dialog
            safe_title = "".join(c for c in project_title if c.isalnum() or c in (' ', '-', '_')).rstrip()
            default_filename = safe_title.replace(' ', '_') + '_export.json'
            
            save_path = filedialog.asksaveasfilename(
                title="Export Project",
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
                initialdir=str(Path.home() / "Documents"),
                initialfile=default_filename
            )
            
            if not save_path:
                return  # User cancelled
            
            # Add export metadata
            export_data = project_data.copy()
            export_data['export_info'] = {
                'exported_on': datetime.now().isoformat(),
                'exported_from': 'Interest Rate Calculator v' + self.version,
                'original_filename': filename
            }
            
            # Save the project data
            with open(save_path, 'w') as f:
                json.dump(export_data, f, indent=2)
            
            self.status_var.set(f"Successfully exported project: {project_title}")
            messagebox.showinfo("Export Successful", 
                              f"Project '{project_title}' has been exported to:\n{save_path}")
            
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export project: {str(e)}")
    
    def show_date_picker(self, date_var):
        """Show a simple date picker dialog."""
        try:
            # Create a simple date picker dialog
            picker_window = tk.Toplevel(self.root)
            picker_window.title("Select Date")
            picker_window.geometry("300x250")
            picker_window.transient(self.root)
            picker_window.grab_set()
            
            # Center the window
            picker_window.update_idletasks()
            x = self.root.winfo_x() + (self.root.winfo_width() // 2) - (300 // 2)
            y = self.root.winfo_y() + (self.root.winfo_height() // 2) - (250 // 2)
            picker_window.geometry(f"300x250+{x}+{y}")
            
            main_frame = ttk.Frame(picker_window, padding="20")
            main_frame.pack(fill=tk.BOTH, expand=True)
            
            # Current date or parse existing date
            current_date = datetime.now()
            existing_date = date_var.get().strip()
            if existing_date:
                try:
                    current_date = datetime.strptime(existing_date, '%m/%d/%Y')
                except ValueError:
                    pass  # Use current date if parsing fails
            
            # Year selection
            year_frame = ttk.Frame(main_frame)
            year_frame.pack(fill=tk.X, pady=(0, 10))
            ttk.Label(year_frame, text="Year:").pack(side=tk.LEFT)
            year_var = tk.StringVar(value=str(current_date.year))
            year_spinbox = tk.Spinbox(year_frame, from_=2020, to=2030, textvariable=year_var, width=10)
            year_spinbox.pack(side=tk.LEFT, padx=(10, 0))
            
            # Month selection
            month_frame = ttk.Frame(main_frame)
            month_frame.pack(fill=tk.X, pady=(0, 10))
            ttk.Label(month_frame, text="Month:").pack(side=tk.LEFT)
            months = ["January", "February", "March", "April", "May", "June",
                     "July", "August", "September", "October", "November", "December"]
            month_var = tk.StringVar(value=months[current_date.month - 1])
            month_combo = ttk.Combobox(month_frame, textvariable=month_var, values=months, 
                                     state="readonly", width=12)
            month_combo.pack(side=tk.LEFT, padx=(10, 0))
            
            # Day selection
            day_frame = ttk.Frame(main_frame)
            day_frame.pack(fill=tk.X, pady=(0, 20))
            ttk.Label(day_frame, text="Day:").pack(side=tk.LEFT)
            day_var = tk.StringVar(value=str(current_date.day))
            day_spinbox = tk.Spinbox(day_frame, from_=1, to=31, textvariable=day_var, width=10)
            day_spinbox.pack(side=tk.LEFT, padx=(10, 0))
            
            # Buttons
            button_frame = ttk.Frame(main_frame)
            button_frame.pack(fill=tk.X)
            
            def set_date():
                try:
                    year = int(year_var.get())
                    month = months.index(month_var.get()) + 1
                    day = int(day_var.get())
                    
                    # Validate date
                    selected_date = datetime(year, month, day)
                    date_var.set(selected_date.strftime('%m/%d/%Y'))
                    picker_window.destroy()
                except ValueError as e:
                    messagebox.showerror("Invalid Date", "Please select a valid date")
            
            ttk.Button(button_frame, text="Set Date", command=set_date).pack(side=tk.LEFT, padx=(0, 10))
            ttk.Button(button_frame, text="Cancel", command=picker_window.destroy).pack(side=tk.LEFT)
            
        except Exception as e:
            messagebox.showerror("Error", f"Could not open date picker: {str(e)}")
    
    def set_today_date(self, date_var):
        """Set the date variable to today's date."""
        today = datetime.now()
        date_var.set(today.strftime('%m/%d/%Y'))
    
    def validate_numeric_input(self, var, input_type):
        """Validate numeric input in real-time."""
        try:
            value = var.get().strip()
            if not value:
                return  # Allow empty values
                
            if input_type == 'integer':
                # Allow only digits
                if not value.replace('.', '').isdigit():
                    # Remove invalid characters
                    clean_value = ''.join(c for c in value if c.isdigit() or c == '.')
                    var.set(clean_value)
                    
            elif input_type == 'percentage':
                # Allow digits and decimal point
                try:
                    float(value.replace('%', ''))
                except ValueError:
                    # Remove invalid characters
                    clean_value = ''.join(c for c in value if c.isdigit() or c in '.%')
                    var.set(clean_value)
                    
            elif input_type == 'currency':
                # Allow digits, decimal point, and currency symbols
                clean_value = value.replace('$', '').replace(',', '')
                try:
                    float(clean_value)
                except ValueError:
                    # Remove invalid characters
                    clean_value = ''.join(c for c in clean_value if c.isdigit() or c == '.')
                    var.set(clean_value)
                    
        except Exception:
            pass  # Ignore validation errors
    
    def on_annual_rate_change(self, event):
        """Handle annual rate changes and update monthly rate."""
        try:
            annual_value = self.annual_rate_var.get().strip().replace('%', '')
            if annual_value:
                annual_rate = float(annual_value)
                monthly_rate = annual_rate / 12
                
                # Update status label
                if hasattr(self, 'rate_status_label'):
                    self.rate_status_label.config(text=f"≈ {monthly_rate:.3f}% monthly")
                    
        except ValueError:
            if hasattr(self, 'rate_status_label'):
                self.rate_status_label.config(text="")
    
    def auto_calculate_monthly_rate(self):
        """Auto-calculate monthly rate from annual rate."""
        try:
            annual_value = self.annual_rate_var.get().strip().replace('%', '')
            if not annual_value:
                messagebox.showwarning("Missing Value", "Please enter an annual rate first")
                return
                
            annual_rate = float(annual_value)
            monthly_rate = annual_rate / 12
            
            # Set the monthly rate
            self.monthly_rate_var.set(f"{monthly_rate:.3f}")
            
            # Update status
            if hasattr(self, 'rate_status_label'):
                self.rate_status_label.config(text="[OK] Auto-calculated")
                
            self.status_var.set(f"Monthly rate auto-calculated: {monthly_rate:.3f}%")
            
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid annual rate")
    
    def set_quick_amount(self, var, amount):
        """Set a quick amount for principal fields."""
        var.set(format_currency(amount))
        self.status_var.set(f"Set amount: {format_currency(amount)}")
    
    def update_runtime(self):
        """Update runtime in title bar every second."""
        try:
            if not self.root or not self.root.winfo_exists():
                return
                
            current_time = datetime.now()
            runtime = current_time - self.start_time
            runtime_str = str(runtime).split('.')[0]  # Remove microseconds
            
            title = f"Interest Rate Calculator v{self.version} - Last Updated: {self.last_updated} - Launched: {self.launch_time} - Runtime: {runtime_str}"
            self.root.title(title)
            
            # Schedule next update
            self.root.after(1000, self.update_runtime)
        except Exception as e:
            # Silently handle any runtime update errors
            pass
            
    def ensure_visible(self):
        """Ensure the window is visible and focused"""
        try:
            # Make sure window is not minimized
            self.root.deiconify()
            
            # Bring to front
            self.root.lift()
            self.root.attributes('-topmost', True)
            self.root.focus_force()
            
            # Update window to ensure it's drawn
            self.root.update()
            
            # Remove topmost after a moment
            self.root.after(1000, lambda: self.root.attributes('-topmost', False))
            
            print("[OK] Window visibility ensured")
            
        except Exception as e:
            print(f"Warning: Could not ensure window visibility: {e}")
            
    def run(self):
        """Start the application."""
        try:
            # Ensure window is visible and focused
            self.ensure_visible()
            
            # Print status
            print("[OK] Interest Rate Calculator is starting...")
            print("[OK] Window should be visible on your screen")
            
            # Start main loop
            self.root.mainloop()
            
        except KeyboardInterrupt:
            print("Application interrupted by user")
        except Exception as e:
            print(f"Error in main loop: {e}")
            traceback.print_exc()
            
            # Try to show error to user
            try:
                messagebox.showerror("Application Error", 
                                   f"An error occurred:\n{str(e)}\n\nCheck console for details.")
            except:
                pass


class PaymentDialog:
    """Dialog for adding/editing payments."""
    
    def __init__(self, parent, title, existing_data=None, available_invoices=None):
        self.result = None
        self.available_invoices = available_invoices or []
        
        self.window = tk.Toplevel(parent)
        self.window.title(title)
        self.window.geometry("500x400")  # Made larger to fit invoice selection
        self.window.transient(parent)
        self.window.grab_set()
        
        # Center the window
        self.window.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() // 2) - (500 // 2)
        y = parent.winfo_y() + (parent.winfo_height() // 2) - (400 // 2)
        self.window.geometry(f"500x400+{x}+{y}")
        
        self.create_widgets(existing_data)
        
    def create_widgets(self, existing_data):
        """Create dialog widgets."""
        main_frame = ttk.Frame(self.window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="Payment Information", font=("Arial", 12, "bold"))
        title_label.pack(pady=(0, 15))
        
        # Date field
        date_frame = ttk.Frame(main_frame)
        date_frame.pack(fill=tk.X, pady=(0, 15))
        ttk.Label(date_frame, text="Date (MM/DD/YYYY):", font=("Arial", 10, "bold")).pack(anchor=tk.W)
        self.date_var = tk.StringVar()
        self.date_var.set(existing_data.get('date', '') if existing_data else '')
        date_entry = ttk.Entry(date_frame, textvariable=self.date_var, width=25, font=("Arial", 10))
        date_entry.pack(anchor=tk.W, pady=(5, 0))
        
        # Description field
        desc_frame = ttk.Frame(main_frame)
        desc_frame.pack(fill=tk.X, pady=(0, 15))
        ttk.Label(desc_frame, text="Description:", font=("Arial", 10, "bold")).pack(anchor=tk.W)
        self.desc_var = tk.StringVar()
        self.desc_var.set(existing_data.get('desc', '') if existing_data else '')
        desc_entry = ttk.Entry(desc_frame, textvariable=self.desc_var, width=40, font=("Arial", 10))
        desc_entry.pack(anchor=tk.W, pady=(5, 0))
        
        # Amount field
        amount_frame = ttk.Frame(main_frame)
        amount_frame.pack(fill=tk.X, pady=(0, 20))
        ttk.Label(amount_frame, text="Amount ($):", font=("Arial", 10, "bold")).pack(anchor=tk.W)
        self.amount_var = tk.StringVar()
        self.amount_var.set(str(existing_data.get('amount', '')) if existing_data else '')
        amount_entry = ttk.Entry(amount_frame, textvariable=self.amount_var, width=25, font=("Arial", 10))
        amount_entry.pack(anchor=tk.W, pady=(5, 0))
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(button_frame, text="Save", command=self.ok_clicked, width=12).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Clear", command=self.clear_fields, width=12).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Cancel", command=self.window.destroy, width=12).pack(side=tk.LEFT)
        
    def clear_fields(self):
        """Clear all input fields."""
        self.date_var.set('')
        self.desc_var.set('')
        self.amount_var.set('')
        
    def ok_clicked(self):
        """Handle Save button click."""
        try:
            # Validate required fields
            if not self.date_var.get().strip():
                messagebox.showerror("Error", "Please enter a date")
                return
            if not self.desc_var.get().strip():
                messagebox.showerror("Error", "Please enter a description")
                return
            if not self.amount_var.get().strip():
                messagebox.showerror("Error", "Please enter an amount")
                return
                
            self.result = {
                'date': self.date_var.get(),
                'desc': self.desc_var.get(),
                'amount': float(self.amount_var.get())
            }
            self.window.destroy()
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid amount")


class InvoiceDialog:
    """Dialog for adding/editing invoices."""
    
    def __init__(self, parent, title, existing_data=None):
        self.result = None
        
        self.window = tk.Toplevel(parent)
        self.window.title(title)
        self.window.geometry("450x300")  # Same size as payment dialog
        self.window.transient(parent)
        self.window.grab_set()
        
        # Center the window
        self.window.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() // 2) - (450 // 2)
        y = parent.winfo_y() + (parent.winfo_height() // 2) - (300 // 2)
        self.window.geometry(f"450x300+{x}+{y}")
        
        self.create_widgets(existing_data)
        
    def create_widgets(self, existing_data):
        """Create dialog widgets."""
        main_frame = ttk.Frame(self.window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="Invoice Information", font=("Arial", 12, "bold"))
        title_label.pack(pady=(0, 15))
        
        # Invoice ID (auto-generated, display only)
        id_frame = ttk.Frame(main_frame)
        id_frame.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(id_frame, text="Invoice ID:", font=("Arial", 10, "bold")).pack(side=tk.LEFT)
        
        # Generate or use existing ID
        if existing_data and 'id' in existing_data:
            invoice_id = existing_data['id']
            print(f"DEBUG: Using existing invoice ID: {invoice_id}")
        else:
            import uuid
            invoice_id = f"INV-{str(uuid.uuid4())[:8].upper()}"
            print(f"DEBUG: Generated new invoice ID: {invoice_id}")
        
        self.invoice_id = invoice_id
        print(f"DEBUG: Set self.invoice_id = {self.invoice_id}")
        ttk.Label(id_frame, text=invoice_id, foreground="blue").pack(side=tk.LEFT, padx=(10, 0))
        
        # Date field
        date_frame = ttk.Frame(main_frame)
        date_frame.pack(fill=tk.X, pady=(0, 15))
        ttk.Label(date_frame, text="Date (MM/DD/YYYY):", font=("Arial", 10, "bold")).pack(anchor=tk.W)
        self.date_var = tk.StringVar()
        self.date_var.set(existing_data.get('date', '') if existing_data else '')
        date_entry = ttk.Entry(date_frame, textvariable=self.date_var, width=25, font=("Arial", 10))
        date_entry.pack(anchor=tk.W, pady=(5, 0))
        
        # Description field
        desc_frame = ttk.Frame(main_frame)
        desc_frame.pack(fill=tk.X, pady=(0, 15))
        ttk.Label(desc_frame, text="Description:", font=("Arial", 10, "bold")).pack(anchor=tk.W)
        self.desc_var = tk.StringVar()
        self.desc_var.set(existing_data.get('desc', '') if existing_data else '')
        desc_entry = ttk.Entry(desc_frame, textvariable=self.desc_var, width=40, font=("Arial", 10))
        desc_entry.pack(anchor=tk.W, pady=(5, 0))
        
        # Amount field
        amount_frame = ttk.Frame(main_frame)
        amount_frame.pack(fill=tk.X, pady=(0, 20))
        ttk.Label(amount_frame, text="Amount ($):", font=("Arial", 10, "bold")).pack(anchor=tk.W)
        self.amount_var = tk.StringVar()
        self.amount_var.set(str(existing_data.get('amount', '')) if existing_data else '')
        amount_entry = ttk.Entry(amount_frame, textvariable=self.amount_var, width=25, font=("Arial", 10))
        amount_entry.pack(anchor=tk.W, pady=(5, 0))
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(button_frame, text="Save", command=self.ok_clicked, width=12).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Clear", command=self.clear_fields, width=12).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Cancel", command=self.window.destroy, width=12).pack(side=tk.LEFT)
        
    def clear_fields(self):
        """Clear all input fields."""
        self.date_var.set('')
        self.desc_var.set('')
        self.amount_var.set('')
        
    def ok_clicked(self):
        """Handle Save button click."""
        print("DEBUG: InvoiceDialog ok_clicked() called")
        try:
            # Validate required fields
            date_val = self.date_var.get().strip()
            desc_val = self.desc_var.get().strip()
            amount_val = self.amount_var.get().strip()
            
            print(f"DEBUG: Form values - Date: '{date_val}', Desc: '{desc_val}', Amount: '{amount_val}'")
            
            if not date_val:
                print("DEBUG: Date validation failed")
                messagebox.showerror("Error", "Please enter a date")
                return
            if not desc_val:
                print("DEBUG: Description validation failed")
                messagebox.showerror("Error", "Please enter a description")
                return
            if not amount_val:
                print("DEBUG: Amount validation failed")
                messagebox.showerror("Error", "Please enter an amount")
                return
            
            print(f"DEBUG: Creating result with invoice_id: {self.invoice_id}")
            self.result = {
                'id': self.invoice_id,
                'date': date_val,
                'desc': desc_val,
                'amount': float(amount_val)
            }
            print(f"DEBUG: Result created: {self.result}")
            self.window.destroy()
            print("DEBUG: Dialog window destroyed")
        except ValueError as e:
            print(f"DEBUG: ValueError in ok_clicked: {e}")
            messagebox.showerror("Error", "Please enter a valid amount")
        except Exception as e:
            print(f"DEBUG: Unexpected error in ok_clicked: {e}")
            messagebox.showerror("Error", f"An error occurred: {str(e)}")


class NewProjectDialog:
    """Dialog for creating new projects with validation."""
    
    def __init__(self, parent):
        self.result = None
        
        self.window = tk.Toplevel(parent)
        self.window.title("Create New Project")
        self.window.geometry("500x400")
        self.window.transient(parent)
        self.window.grab_set()
        
        # Center the window
        self.window.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() // 2) - (500 // 2)
        y = parent.winfo_y() + (parent.winfo_height() // 2) - (400 // 2)
        self.window.geometry(f"500x400+{x}+{y}")
        
        self.create_widgets()
        
        # Wait for dialog to close
        self.window.wait_window()
        
    def create_widgets(self):
        """Create dialog widgets."""
        main_frame = ttk.Frame(self.window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="Create New Project", 
                               font=("Arial", 14, "bold"))
        title_label.pack(pady=(0, 20))
        
        # Project Title (Required)
        title_frame = ttk.LabelFrame(main_frame, text="Project Information", padding="10")
        title_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(title_frame, text="Project Title: *", font=("Arial", 10, "bold")).pack(anchor=tk.W)
        self.title_var = tk.StringVar()
        title_entry = ttk.Entry(title_frame, textvariable=self.title_var, width=50, font=("Arial", 10))
        title_entry.pack(fill=tk.X, pady=(5, 10))
        title_entry.focus()  # Set focus to title field
        
        ttk.Label(title_frame, text="Description (Optional):", font=("Arial", 10)).pack(anchor=tk.W)
        self.desc_var = tk.StringVar()
        desc_entry = ttk.Entry(title_frame, textvariable=self.desc_var, width=50, font=("Arial", 10))
        desc_entry.pack(fill=tk.X, pady=(5, 0))
        
        # Default Values (Optional)
        defaults_frame = ttk.LabelFrame(main_frame, text="Default Values (Optional)", padding="10")
        defaults_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Date fields
        dates_frame = ttk.Frame(defaults_frame)
        dates_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Payments Calculated Through Date
        asof_frame = ttk.Frame(dates_frame)
        asof_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Label(asof_frame, text="Payments Calculated Through Date (MM/DD/YYYY):").pack(anchor=tk.W)
        self.as_of_date_var = tk.StringVar()
        ttk.Entry(asof_frame, textvariable=self.as_of_date_var, width=20).pack(anchor=tk.W, pady=(2, 0))
        
        # Rates and principals
        rates_frame = ttk.Frame(defaults_frame)
        rates_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Grace Days
        grace_frame = ttk.Frame(rates_frame)
        grace_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        ttk.Label(grace_frame, text="Grace Days:").pack(anchor=tk.W)
        self.grace_days_var = tk.StringVar(value="30")
        ttk.Entry(grace_frame, textvariable=self.grace_days_var, width=10).pack(anchor=tk.W, pady=(2, 0))
        
        # Annual Rate
        annual_frame = ttk.Frame(rates_frame)
        annual_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Label(annual_frame, text="Annual Rate (%):").pack(anchor=tk.W)
        self.annual_rate_var = tk.StringVar(value="18.0")
        ttk.Entry(annual_frame, textvariable=self.annual_rate_var, width=10).pack(anchor=tk.W, pady=(2, 0))
        
        # Principal amounts
        principals_frame = ttk.Frame(defaults_frame)
        principals_frame.pack(fill=tk.X)
        
        # Note: Principal amounts will be entered as individual invoices after project creation
        ttk.Label(principals_frame, text="Principal amounts will be managed through individual invoices.", 
                 foreground="gray", font=("Arial", 9, "italic")).pack(pady=10)
        
        # Required field note
        note_label = ttk.Label(main_frame, text="* Required field", 
                              font=("Arial", 9, "italic"), foreground="gray")
        note_label.pack(pady=(10, 0))
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(20, 0))
        
        ttk.Button(button_frame, text="Create Project", command=self.ok_clicked, 
                  width=15).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Cancel", command=self.cancel_clicked, 
                  width=15).pack(side=tk.LEFT)
        
        # Bind Enter key to create project
        self.window.bind('<Return>', lambda e: self.ok_clicked())
        self.window.bind('<Escape>', lambda e: self.cancel_clicked())
        
    def ok_clicked(self):
        """Handle Create Project button click."""
        try:
            # Validate required fields
            title = self.title_var.get().strip()
            if not title:
                messagebox.showerror("Error", "Please enter a project title")
                return
                
            # Validate date if provided
            as_of_date = self.as_of_date_var.get().strip()
            
            if as_of_date:
                try:
                    datetime.strptime(as_of_date, '%m/%d/%Y')
                except ValueError:
                    messagebox.showerror("Error", "Please enter payments calculated through date in MM/DD/YYYY format")
                    return
            
            # Validate numeric fields
            try:
                grace_days = int(self.grace_days_var.get()) if self.grace_days_var.get().strip() else 30
                annual_rate = float(self.annual_rate_var.get()) / 100 if self.annual_rate_var.get().strip() else 0.18
                # Principal amounts will be managed through invoices
            except ValueError:
                messagebox.showerror("Error", "Please enter valid numeric values")
                return
                
            # Convert date to ISO format for storage
            as_of_date_iso = convert_to_iso_date(as_of_date) if as_of_date else ''
                
            self.result = {
                'title': title,
                'description': self.desc_var.get().strip(),
                'as_of_date': as_of_date_iso,
                'grace_days': grace_days,
                'annual_rate': annual_rate,
                'monthly_rate': annual_rate / 12  # Calculate monthly rate
            }
            
            self.window.destroy()
            
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
            
    def cancel_clicked(self):
        """Handle Cancel button click."""
        self.result = None
        self.window.destroy()


def main():
    """Main entry point."""
    try:
        app = InterestRateCalculator()
        app.run()
    except Exception as e:
        print(f"Failed to start application: {e}")
        traceback.print_exc()
        input("Press Enter to exit...")


if __name__ == "__main__":
    main()