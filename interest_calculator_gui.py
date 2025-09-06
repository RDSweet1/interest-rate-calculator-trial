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
        
        # Project list
        list_frame = ttk.Frame(top_frame)
        list_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        ttk.Label(list_frame, text="Available Projects:").pack(anchor=tk.W)
        self.project_listbox = tk.Listbox(list_frame, height=4)
        self.project_listbox.pack(fill=tk.BOTH, expand=True, pady=(5, 0))
        
        # Bind double-click to open project editor
        self.project_listbox.bind('<Double-1>', self.on_double_click)
        
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
        self.clear_form()
        self.show_project_editor()
        self.status_var.set("Ready to create new project")
        
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
                        self.show_project_editor()  # Create form first
                        self.load_project_data(project_data, project_file)  # Then load data
                        return
            except Exception as e:
                continue
                
        messagebox.showerror("Error", f"Could not load project: {project_name}")
        
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
        
        # Dates Row
        ttk.Label(info_content, text="Billing Date:").grid(row=1, column=0, sticky=tk.W, padx=(0, 5), pady=2)
        self.billing_date_var = tk.StringVar()
        ttk.Entry(info_content, textvariable=self.billing_date_var, width=12).grid(row=1, column=1, sticky=tk.W, pady=2)
        
        ttk.Label(info_content, text="As-of Date:").grid(row=1, column=2, sticky=tk.W, padx=(10, 5), pady=2)
        self.as_of_date_var = tk.StringVar()
        ttk.Entry(info_content, textvariable=self.as_of_date_var, width=12).grid(row=1, column=3, sticky=tk.W, pady=2)
        
        # Rates Row
        ttk.Label(info_content, text="Grace Days:").grid(row=2, column=0, sticky=tk.W, padx=(0, 5), pady=2)
        self.grace_days_var = tk.StringVar()
        ttk.Entry(info_content, textvariable=self.grace_days_var, width=8).grid(row=2, column=1, sticky=tk.W, pady=2)
        
        ttk.Label(info_content, text="Annual Rate (%):").grid(row=2, column=2, sticky=tk.W, padx=(10, 5), pady=2)
        self.annual_rate_var = tk.StringVar()
        annual_rate_entry = ttk.Entry(info_content, textvariable=self.annual_rate_var, width=8)
        annual_rate_entry.grid(row=2, column=3, sticky=tk.W, pady=2)
        annual_rate_entry.bind('<FocusOut>', self.format_annual_rate)
        
        # Monthly Rate Row
        ttk.Label(info_content, text="Monthly Rate (%):").grid(row=3, column=0, sticky=tk.W, padx=(0, 5), pady=2)
        self.monthly_rate_var = tk.StringVar()
        monthly_rate_entry = ttk.Entry(info_content, textvariable=self.monthly_rate_var, width=8)
        monthly_rate_entry.grid(row=3, column=1, sticky=tk.W, pady=2)
        monthly_rate_entry.bind('<FocusOut>', self.format_monthly_rate)
        
        # Principals Row
        ttk.Label(info_content, text="Flood/Wind Principal ($):").grid(row=3, column=2, sticky=tk.W, padx=(10, 5), pady=2)
        self.principal_fw_var = tk.StringVar()
        fw_entry = ttk.Entry(info_content, textvariable=self.principal_fw_var, width=15)
        fw_entry.grid(row=3, column=3, sticky=tk.W, pady=2)
        fw_entry.bind('<FocusOut>', self.format_fw_principal)
        
        ttk.Label(info_content, text="Drywall Principal ($):").grid(row=4, column=0, sticky=tk.W, padx=(0, 5), pady=2)
        self.principal_dw_var = tk.StringVar()
        dw_entry = ttk.Entry(info_content, textvariable=self.principal_dw_var, width=15)
        dw_entry.grid(row=4, column=1, sticky=tk.W, pady=2)
        dw_entry.bind('<FocusOut>', self.format_dw_principal)
    
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
    
    def format_fw_principal(self, event=None):
        """Format flood/wind principal as currency"""
        try:
            value = self.principal_fw_var.get()
            if value and not value.startswith('$'):
                formatted = format_currency(value)
                self.principal_fw_var.set(formatted)
        except:
            pass
    
    def format_dw_principal(self, event=None):
        """Format drywall principal as currency"""
        try:
            value = self.principal_dw_var.get()
            if value and not value.startswith('$'):
                formatted = format_currency(value)
                self.principal_dw_var.set(formatted)
        except:
            pass
        
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
        columns = ('Date', 'Description', 'Amount')
        self.invoices_tree = ttk.Treeview(invoices_content, columns=columns, show='headings', height=8)
        
        # Configure column widths and headings
        self.invoices_tree.heading('Date', text='Date')
        self.invoices_tree.heading('Description', text='Description')
        self.invoices_tree.heading('Amount', text='Amount')
        
        self.invoices_tree.column('Date', width=120, anchor='center')
        self.invoices_tree.column('Description', width=200, anchor='center')
        self.invoices_tree.column('Amount', width=120, anchor='center')
        
        # Add scrollbar
        invoice_scrollbar = ttk.Scrollbar(invoices_content, orient=tk.VERTICAL, command=self.invoices_tree.yview)
        self.invoices_tree.configure(yscrollcommand=invoice_scrollbar.set)
        
        # Pack table and scrollbar
        self.invoices_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        invoice_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def add_invoice(self):
        """Add a new invoice."""
        dialog = InvoiceDialog(self.root, "Add Invoice")
        if dialog.result:
            # Add to tree view
            self.invoices_tree.insert('', 'end', values=(
                dialog.result['date'],
                dialog.result['desc'],
                f"${dialog.result['amount']:,.2f}"
            ))
            
    def edit_invoice(self):
        """Edit selected invoice."""
        selection = self.invoices_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select an invoice to edit")
            return
            
        item = self.invoices_tree.item(selection[0])
        values = item['values']
        
        # Parse existing data
        existing_data = {
            'date': values[0],
            'desc': values[1],
            'amount': float(values[2].replace('$', '').replace(',', ''))
        }
        
        dialog = InvoiceDialog(self.root, "Edit Invoice", existing_data)
        if dialog.result:
            # Update tree view
            self.invoices_tree.item(selection[0], values=(
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
            self.billing_date_var.set(convert_to_american_date(project_data.get('billing_date', '')))
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
            fw_principal = project_data.get('principal_fw', '')
            if fw_principal:
                self.principal_fw_var.set(format_currency(fw_principal))
            
            dw_principal = project_data.get('principal_dw', '')
            if dw_principal:
                self.principal_dw_var.set(format_currency(dw_principal))
            
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
            self.invoices_tree.insert('', 'end', values=(
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
                'billing_date': convert_to_iso_date(self.billing_date_var.get()),
                'as_of_date': convert_to_iso_date(self.as_of_date_var.get()),
                'grace_days': int(self.grace_days_var.get()) if self.grace_days_var.get() else 0,
                'annual_rate': parse_percentage(self.annual_rate_var.get()),
                'monthly_rate': parse_percentage(self.monthly_rate_var.get()),
                'principal_fw': parse_currency(self.principal_fw_var.get()),
                'principal_dw': parse_currency(self.principal_dw_var.get()),
                'invoices': [],
                'payments': []
            }
            
            # Collect invoices from tree view
            for item in self.invoices_tree.get_children():
                values = self.invoices_tree.item(item)['values']
                invoice = {
                    'date': convert_to_iso_date(values[0]),
                    'desc': values[1],
                    'amount': float(values[2].replace('$', '').replace(',', ''))
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
        self.billing_date_var.set('')
        self.as_of_date_var.set('')
        self.grace_days_var.set('')
        self.annual_rate_var.set('')
        self.monthly_rate_var.set('')
        self.principal_fw_var.set('')
        self.principal_dw_var.set('')
        
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
            
            print("✓ Window visibility ensured")
            
        except Exception as e:
            print(f"Warning: Could not ensure window visibility: {e}")
    
    def run(self):
        """Start the application."""
        try:
            # Ensure window is visible and focused
            self.ensure_visible()
            
            # Print status
            print("✓ Interest Rate Calculator is starting...")
            print("✓ Window should be visible on your screen")
            
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
    
    def __init__(self, parent, title, existing_data=None):
        self.result = None
        
        self.window = tk.Toplevel(parent)
        self.window.title(title)
        self.window.geometry("450x300")  # Made larger to fit all fields
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