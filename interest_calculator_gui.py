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

def ensure_window_visibility(window, parent=None, min_width=500, min_height=400):
    """Ensure window is properly sized and all controls are visible."""
    # Force update to get actual required size
    window.update_idletasks()
    
    # Get screen dimensions
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    
    # Calculate maximum usable screen space (leave margins)
    max_width = int(screen_width * 0.8)
    max_height = int(screen_height * 0.8)
    
    # Get required size from window
    req_width = window.winfo_reqwidth()
    req_height = window.winfo_reqheight()
    
    # Ensure minimum sizes with extra padding
    final_width = max(min_width, req_width + 100)  # Extra padding
    final_height = max(min_height, req_height + 150)  # Extra padding for buttons
    
    # Ensure we don't exceed screen size
    final_width = min(final_width, max_width)
    final_height = min(final_height, max_height)
    
    # Set window size and minimum size
    window.geometry(f"{final_width}x{final_height}")
    window.minsize(final_width, final_height)
    
    # Center on screen or parent
    if parent:
        try:
            x = parent.winfo_x() + (parent.winfo_width() // 2) - (final_width // 2)
            y = parent.winfo_y() + (parent.winfo_height() // 2) - (final_height // 2)
        except:
            x = (screen_width - final_width) // 2
            y = (screen_height - final_height) // 2
    else:
        x = (screen_width - final_width) // 2
        y = (screen_height - final_height) // 2
    
    # Ensure window is on screen
    x = max(0, min(x, screen_width - final_width))
    y = max(0, min(y, screen_height - final_height))
    
    window.geometry(f"{final_width}x{final_height}+{x}+{y}")
    
    return final_width, final_height


class CollapsibleSection(ttk.Frame):
    """A truly collapsible section with 30% larger, bold header that removes all space when collapsed."""
    
    def __init__(self, parent, title: str):
        super().__init__(parent)
        self._collapsed = False
        self._original_title = title
        
        # Create 30% larger, bold header font
        base_font = tkfont.nametofont("TkDefaultFont")
        header_font = (base_font.actual("family"), max(1, int(base_font.actual("size") * 1.3)), "bold")
        
        # Header label with hand cursor and visual indicator
        self.header = ttk.Label(self, text=f"▼ {title}", font=header_font, cursor="hand2")
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
            # Update header text to show collapsed state
            self.header.config(text=f"▶ {self._original_title}")
            # Remove all padding when collapsed to save maximum space
            self.pack_configure(pady=0)
    
    def expand(self):
        """Expand the section - show content."""
        if self._collapsed:
            self.content.pack(fill=tk.BOTH, expand=True, pady=(6, 0))
            self._collapsed = False
            # Update header text to show expanded state
            self.header.config(text=f"▼ {self._original_title}")
            # Restore normal padding when expanded
            self.pack_configure(pady=(0, 10))
    
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
        """Create reorganized project information section with new layout."""
        self.info_frame = CollapsibleSection(self.content_frame, "Project Information")
        self.info_frame.pack(fill=tk.X, pady=(0, 5))
        
        # Content frame for project info
        info_content = ttk.Frame(self.info_frame.content, padding="10")
        self.info_frame.set_content(info_content)
        
        # LINE 1: Project Title | Payments Calculated Through Date | Grace Days
        line1_frame = ttk.Frame(info_content)
        line1_frame.pack(fill=tk.X, pady=(0, 5))
        
        # Project Title
        ttk.Label(line1_frame, text="Project Title:").pack(side=tk.LEFT)
        self.title_var = tk.StringVar()
        title_entry = ttk.Entry(line1_frame, textvariable=self.title_var, width=25)
        title_entry.pack(side=tk.LEFT, padx=(5, 15))
        
        # Payments Calculated Through Date
        ttk.Label(line1_frame, text="Calc Through:").pack(side=tk.LEFT)
        date_frame = ttk.Frame(line1_frame)
        date_frame.pack(side=tk.LEFT, padx=(5, 15))
        
        self.as_of_date_var = tk.StringVar()
        date_entry = ttk.Entry(date_frame, textvariable=self.as_of_date_var, width=12)
        date_entry.pack(side=tk.LEFT)
        
        # Date picker button
        date_picker_btn = ttk.Button(date_frame, text="📅", width=3, 
                                    command=lambda: self.show_date_picker(self.as_of_date_var))
        date_picker_btn.pack(side=tk.LEFT, padx=(2, 0))
        
        # Today button
        today_btn = ttk.Button(date_frame, text="Today", width=6,
                              command=lambda: self.set_today_date(self.as_of_date_var))
        today_btn.pack(side=tk.LEFT, padx=(2, 0))
        
        # Grace Days
        ttk.Label(line1_frame, text="Grace Days:").pack(side=tk.LEFT)
        grace_frame = ttk.Frame(line1_frame)
        grace_frame.pack(side=tk.LEFT, padx=(5, 0))
        
        self.grace_days_var = tk.StringVar()
        grace_entry = ttk.Entry(grace_frame, textvariable=self.grace_days_var, width=6)
        grace_entry.pack(side=tk.LEFT)
        grace_entry.bind('<KeyRelease>', lambda e: self.validate_numeric_input(self.grace_days_var, 'integer'))
        
        ttk.Label(grace_frame, text="days", foreground="gray").pack(side=tk.LEFT, padx=(2, 0))
        
        # LINE 2: Annual Rate | Monthly Rate  
        line2_frame = ttk.Frame(info_content)
        line2_frame.pack(fill=tk.X, pady=(0, 5))
        
        # Annual Rate
        ttk.Label(line2_frame, text="Annual Rate (%):").pack(side=tk.LEFT)
        annual_frame = ttk.Frame(line2_frame)
        annual_frame.pack(side=tk.LEFT, padx=(5, 20))
        
        self.annual_rate_var = tk.StringVar()
        annual_rate_entry = ttk.Entry(annual_frame, textvariable=self.annual_rate_var, width=8)
        annual_rate_entry.pack(side=tk.LEFT)
        annual_rate_entry.bind('<KeyRelease>', self.on_annual_rate_change)
        annual_rate_entry.bind('<FocusOut>', self.format_annual_rate)
        
        # Auto-calc button
        auto_calc_btn = ttk.Button(annual_frame, text="Auto", width=4,
                                  command=self.auto_calculate_monthly_rate)
        auto_calc_btn.pack(side=tk.LEFT, padx=(2, 0))
        
        # Monthly Rate
        ttk.Label(line2_frame, text="Monthly Rate (%):").pack(side=tk.LEFT)
        monthly_frame = ttk.Frame(line2_frame)
        monthly_frame.pack(side=tk.LEFT, padx=(5, 0))
        
        self.monthly_rate_var = tk.StringVar()
        monthly_rate_entry = ttk.Entry(monthly_frame, textvariable=self.monthly_rate_var, width=8)
        monthly_rate_entry.pack(side=tk.LEFT)
        monthly_rate_entry.bind('<KeyRelease>', lambda e: self.validate_numeric_input(self.monthly_rate_var, 'percentage'))
        monthly_rate_entry.bind('<FocusOut>', self.format_monthly_rate)
        
        # Rate relationship indicator
        self.rate_status_label = ttk.Label(monthly_frame, text="", foreground="gray")
        self.rate_status_label.pack(side=tk.LEFT, padx=(5, 0))
        
        # LINE 3: Description (wrapping text)
        line3_frame = ttk.Frame(info_content)
        line3_frame.pack(fill=tk.X, pady=(5, 0))
        
        ttk.Label(line3_frame, text="Description:").pack(anchor=tk.W)
        
        # Text widget for wrapping description
        desc_frame = ttk.Frame(line3_frame)
        desc_frame.pack(fill=tk.X, pady=(2, 0))
        
        self.description_text = tk.Text(desc_frame, height=2, width=60, wrap=tk.WORD)
        self.description_text.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Scrollbar for description
        desc_scrollbar = ttk.Scrollbar(desc_frame, orient=tk.VERTICAL, command=self.description_text.yview)
        self.description_text.configure(yscrollcommand=desc_scrollbar.set)
        desc_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Note about invoices
        note_frame = ttk.Frame(info_content)
        note_frame.pack(fill=tk.X, pady=(10, 0))
        
        note_label = ttk.Label(note_frame, 
                              text="Note: Principal amounts are managed through individual invoices below.",
                              foreground="gray", font=("Arial", 9, "italic"))
        note_label.pack(anchor=tk.W)
    
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
        
        # Bind double-click for editing
        self.invoices_tree.bind('<Double-1>', self.on_invoice_double_click)
    
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
            
            # CRITICAL: Also add to the current project data
            if hasattr(self, 'current_project') and self.current_project:
                if 'invoices' not in self.current_project:
                    self.current_project['invoices'] = []
                
                # Add the new invoice to project data
                self.current_project['invoices'].append({
                    'id': dialog.result['id'],
                    'date': convert_to_iso_date(dialog.result['date']),
                    'desc': dialog.result['desc'],
                    'amount': dialog.result['amount']
                })
                
                # Auto-save the project
                self.save_project()
                self.status_var.set(f"Invoice {dialog.result['id']} added and saved")
            else:
                self.status_var.set(f"Invoice {dialog.result['id']} added (save project to persist)")
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
        ttk.Button(payment_btn_frame, text="Delete Payment", command=self.delete_payment, width=15).pack(side=tk.LEFT, padx=(0, 10))
        # NEW: Payment assignment functionality
        ttk.Button(payment_btn_frame, text="Assign to Invoice", command=self.assign_payment_to_invoice, width=18).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(payment_btn_frame, text="View Assignments", command=self.view_payment_assignments, width=18).pack(side=tk.LEFT)
        
        # Payment table with assignment information
        columns = ('Date', 'Description', 'Amount', 'Assigned', 'Unassigned', 'Status')
        self.payments_tree = ttk.Treeview(payments_content, columns=columns, show='headings', height=8)
        
        # Configure column widths and headings
        self.payments_tree.heading('Date', text='Date')
        self.payments_tree.heading('Description', text='Description')
        self.payments_tree.heading('Amount', text='Total Amount')
        self.payments_tree.heading('Assigned', text='Assigned')
        self.payments_tree.heading('Unassigned', text='Unassigned')
        self.payments_tree.heading('Status', text='Status')
        
        self.payments_tree.column('Date', width=100, anchor='center')
        self.payments_tree.column('Description', width=180, anchor='center')
        self.payments_tree.column('Amount', width=100, anchor='center')
        self.payments_tree.column('Assigned', width=100, anchor='center')
        self.payments_tree.column('Unassigned', width=100, anchor='center')
        self.payments_tree.column('Status', width=80, anchor='center')
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(payments_content, orient=tk.VERTICAL, command=self.payments_tree.yview)
        self.payments_tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack table and scrollbar
        self.payments_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind double-click for editing
        self.payments_tree.bind('<Double-1>', self.on_payment_double_click)
        
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
    
    def on_invoice_double_click(self, event):
        """Handle double-click on invoice table."""
        selection = self.invoices_tree.selection()
        if not selection:
            return
        
        # Get the selected item
        item_id = selection[0]
        values = self.invoices_tree.item(item_id, 'values')
        
        if values:
            # Parse the invoice data from the tree
            existing_data = {
                'id': values[0],
                'date': values[1],
                'desc': values[2],
                'amount': float(values[3].replace('$', '').replace(',', ''))  # Remove $ and commas
            }
            
            # Open edit dialog
            dialog = InvoiceDialog(self.root, "Edit Invoice", existing_data)
            self.root.wait_window(dialog.window)
            
            if dialog.result:
                # Update the tree with new values
                new_values = (
                    dialog.result['id'],
                    dialog.result['date'], 
                    dialog.result['desc'],
                    f"${dialog.result['amount']:,.2f}"
                )
                self.invoices_tree.item(item_id, values=new_values)
                
                # CRITICAL: Also update the underlying project data
                if hasattr(self, 'current_project') and self.current_project and 'invoices' in self.current_project:
                    # Find and update the corresponding invoice in the project data
                    invoice_updated = False
                    for invoice in self.current_project['invoices']:
                        if invoice.get('id') == existing_data['id']:  # Match by original ID
                            invoice['id'] = dialog.result['id']
                            invoice['date'] = convert_to_iso_date(dialog.result['date'])
                            invoice['desc'] = dialog.result['desc']
                            invoice['amount'] = dialog.result['amount']
                            invoice_updated = True
                            break
                    
                    # Debug: write to file to confirm update
                    debug_file = Path("debug_invoice_edit.txt")
                    with open(debug_file, "w") as df:
                        df.write(f"DEBUG: Invoice edit attempt\n")
                        df.write(f"DEBUG: Original ID: {existing_data['id']}\n")
                        df.write(f"DEBUG: New data: {dialog.result}\n")
                        df.write(f"DEBUG: Invoice updated in current_project: {invoice_updated}\n")
                        df.write(f"DEBUG: Current project invoices count: {len(self.current_project['invoices'])}\n")
                        for i, inv in enumerate(self.current_project['invoices']):
                            df.write(f"DEBUG: Invoice {i}: {inv}\n")
                
                # Auto-save the project after editing
                try:
                    self.save_project()
                    self.status_var.set(f"Invoice {dialog.result['id']} updated and saved")
                except Exception as e:
                    messagebox.showerror("Save Error", f"Failed to save project: {str(e)}")
                    self.status_var.set(f"Invoice updated but save failed: {str(e)}")
    
    def on_payment_double_click(self, event):
        """Handle double-click on payment table."""
        selection = self.payments_tree.selection()
        if not selection:
            return
        
        # Get the selected item
        item_id = selection[0]
        values = self.payments_tree.item(item_id, 'values')
        
        if values:
            # Parse the payment data from the tree
            existing_data = {
                'date': values[0],
                'desc': values[1],
                'amount': float(values[2].replace('$', '').replace(',', ''))  # Remove $ and commas
            }
            
            # Find the full payment data with assignments from current_project
            if hasattr(self, 'current_project') and self.current_project:
                for payment in self.current_project.get('payments', []):
                    # Match by date and description since that's what we have from the tree
                    payment_date = convert_to_american_date(payment.get('date', ''))
                    payment_desc = payment.get('description', payment.get('desc', ''))
                    
                    if (payment_date == existing_data['date'] and 
                        payment_desc == existing_data['desc']):
                        # Found the payment - add assignment data
                        existing_data['assignments'] = payment.get('assignments', [])
                        existing_data['unassigned_amount'] = payment.get('unassigned_amount', existing_data['amount'])
                        break
            
            # Open edit dialog
            available_invoices = self.current_project.get('invoices', []) if hasattr(self, 'current_project') and self.current_project else []
            dialog = PaymentDialog(self.root, "Edit Payment", existing_data, available_invoices)
            self.root.wait_window(dialog.window)
            
            if dialog.result:
                # Update the tree with new values - we need to recalculate assigned/unassigned amounts
                # For now, let's just update the basic fields and keep the assignment status
                new_values = (
                    dialog.result['date'],
                    dialog.result['desc'],
                    f"${dialog.result['amount']:,.2f}",
                    values[3],  # Keep existing assigned amount
                    values[4],  # Keep existing unassigned amount  
                    values[5]   # Keep existing status
                )
                self.payments_tree.item(item_id, values=new_values)
                
                # CRITICAL: Also update the underlying project data
                if hasattr(self, 'current_project') and self.current_project and 'payments' in self.current_project:
                    # Find and update the corresponding payment in the project data
                    for payment in self.current_project['payments']:
                        # Match by date and original description (since payments don't have unique IDs in tree)
                        if (payment.get('date') == convert_to_iso_date(existing_data['date']) and 
                            payment.get('description', payment.get('desc', '')) == existing_data['desc']):
                            payment['date'] = convert_to_iso_date(dialog.result['date'])
                            # Update both possible field names for compatibility
                            payment['description'] = dialog.result['desc']
                            payment['desc'] = dialog.result['desc'] 
                            payment['amount'] = dialog.result['amount']
                            break
                
                # Auto-save the project after editing
                self.save_project()
                self.status_var.set(f"Payment updated and saved")
        
    def load_project_data(self, project_data, project_file):
        """Load project data into editor form."""
        # Write debug info to file so we can see it even if app crashes
        debug_file = Path("debug_load.txt")
        try:
            with open(debug_file, "w") as df:
                df.write("DEBUG: Starting load_project_data\n")
                df.flush()
                
                # Use deep copy to ensure we have a proper mutable copy
                import copy
                self.current_project = copy.deepcopy(project_data)
                self.current_project_file = project_file
                
                # Debug: Log the loaded project structure
                df.write(f"DEBUG: Loaded current_project with {len(self.current_project.get('invoices', []))} invoices\n")
                for i, inv in enumerate(self.current_project.get('invoices', [])):
                    df.write(f"DEBUG: Loaded invoice {i}: ID={inv.get('id')}, desc='{inv.get('desc')}'\n")
                
                # Check if form variables exist (form must be created first)
                df.write("DEBUG: Checking form variables\n")
                df.flush()
                if not hasattr(self, 'title_var'):
                    df.write("DEBUG: Form variables not found\n")
                    df.flush()
                    messagebox.showerror("Error", "Form not initialized. Please try again.")
                    return
                
                df.write("DEBUG: Loading basic data\n")
                df.flush()
                # Load basic data
                self.title_var.set(project_data.get('title', ''))
                self.as_of_date_var.set(convert_to_american_date(project_data.get('as_of_date', '')))
                self.grace_days_var.set(str(project_data.get('grace_days', '')))
                
                df.write("DEBUG: Loading description\n")
                df.flush()
                # Load description into text widget
                if hasattr(self, 'description_text'):
                    self.description_text.delete('1.0', tk.END)
                    self.description_text.insert('1.0', project_data.get('description', ''))
                
                df.write("DEBUG: Loading rates\n")
                df.flush()
                # Format rates as percentages
                annual_rate = project_data.get('annual_rate', '')
                if annual_rate:
                    self.annual_rate_var.set(format_percentage(annual_rate))
                
                monthly_rate = project_data.get('monthly_rate', '')
                if monthly_rate:
                    self.monthly_rate_var.set(format_percentage(monthly_rate))
                
                df.write("DEBUG: Loading invoices\n")
                df.flush()
                # Load invoices and payments
                self.load_invoices(project_data.get('invoices', []))
                
                df.write("DEBUG: Loading payments\n")
                df.flush()
                self.load_payments(project_data.get('payments', []))
                
                df.write("DEBUG: load_project_data completed successfully\n")
                df.flush()
                
                # Add post-load monitoring
                self.root.after(2000, lambda: self.debug_post_load("2 seconds post-load"))
                self.root.after(10000, lambda: self.debug_post_load("10 seconds post-load"))
                self.root.after(30000, lambda: self.debug_post_load("30 seconds post-load"))
        except Exception as e:
            # Write error to debug file
            with open(debug_file, "a") as df:
                df.write(f"DEBUG: Exception in load_project_data: {e}\n")
                import traceback
                df.write(f"DEBUG: Traceback:\n{traceback.format_exc()}\n")
            messagebox.showerror("Error", f"Failed to load project data: {str(e)}")
    
    def debug_post_load(self, message):
        """Debug method to track app state after project loading"""
        try:
            debug_file = Path("debug_load.txt")
            with open(debug_file, "a") as df:
                df.write(f"DEBUG: {message} - App still running\n")
                df.write(f"  - Window exists: {self.root.winfo_exists() if hasattr(self, 'root') and self.root else False}\n")
                df.write(f"  - Current project: {bool(self.current_project)}\n")
                df.flush()
        except Exception as e:
            # Silently handle debug errors
            pass
    
    def load_invoices(self, invoices):
        """Load invoices into the tree view."""
        try:
            print(f"DEBUG: Loading {len(invoices)} invoices")
            # Clear existing items
            for item in self.invoices_tree.get_children():
                self.invoices_tree.delete(item)
                
            # Add invoices
            for i, invoice in enumerate(invoices):
                print(f"DEBUG: Processing invoice {i}: {invoice.get('id', 'No ID')}")
                # Generate ID if missing (for backward compatibility)
                invoice_id = invoice.get('id', f"INV-{len(invoices):04d}")
                self.invoices_tree.insert('', 'end', values=(
                    invoice_id,
                    convert_to_american_date(invoice.get('date', '')),
                    invoice.get('desc', ''),
                    f"${invoice.get('amount', 0):,.2f}"
                ))
            print("DEBUG: Invoices loaded successfully")
        except Exception as e:
            print(f"DEBUG: Error in load_invoices: {e}")
            import traceback
            traceback.print_exc()
        
    def load_payments(self, payments):
        """Load payments into the tree view with assignment information."""
        try:
            print(f"DEBUG: Loading {len(payments)} payments")
            # Clear existing items
            for item in self.payments_tree.get_children():
                self.payments_tree.delete(item)
                
            # Add payments with assignment information
            for i, payment in enumerate(payments):
                print(f"DEBUG: Processing payment {i}: {payment.get('description', payment.get('desc', 'No Desc'))}")
                try:
                    # Calculate assignment totals with better error handling
                    total_assigned = 0
                    for assignment in payment.get('assignments', []):
                        assigned_amount = assignment.get('assigned_amount', 0)
                        if isinstance(assigned_amount, (int, float)):
                            total_assigned += assigned_amount
                        else:
                            # Try to convert string to float
                            total_assigned += float(str(assigned_amount))
                    
                    unassigned = payment.get('unassigned_amount', payment.get('amount', 0))
                    
                    # Ensure unassigned is a number
                    if not isinstance(unassigned, (int, float)):
                        unassigned = float(str(unassigned))
                    
                    # Determine status
                    if total_assigned == 0:
                        status = 'Unassigned'
                    elif unassigned <= 0.01:  # Handle floating point precision
                        status = 'Fully Assigned'
                    else:
                        status = 'Partial'
                    
                    self.payments_tree.insert('', 'end', values=(
                        convert_to_american_date(payment.get('date', '')),
                        payment.get('description', payment.get('desc', '')),  # Handle both field names
                        f"${payment.get('amount', 0):,.2f}",
                        f"${total_assigned:,.2f}",
                        f"${unassigned:,.2f}",
                        status
                    ))
                except (ValueError, TypeError) as e:
                    print(f"Warning: Error processing payment {payment.get('description', 'Unknown')}: {e}")
                    # Add with default values if there's an error
                    self.payments_tree.insert('', 'end', values=(
                        convert_to_american_date(payment.get('date', '')),
                        payment.get('description', payment.get('desc', 'Error')),
                        f"${payment.get('amount', 0):,.2f}",
                        "$0.00",
                        f"${payment.get('amount', 0):,.2f}",
                        'Error'
                    ))
            print("DEBUG: Payments loaded successfully")
        except Exception as e:
            print(f"DEBUG: Error in load_payments: {e}")
            import traceback
            traceback.print_exc()
            
    def add_payment(self):
        """Add a new payment."""
        # Pass available invoices for assignment
        available_invoices = self.current_project.get('invoices', []) if hasattr(self, 'current_project') and self.current_project else []
        dialog = PaymentDialog(self.root, "Add Payment", available_invoices=available_invoices)
        
        # Wait for the dialog to complete (modal behavior)
        self.root.wait_window(dialog.window)
        
        if dialog.result:
            # Handle assignment if provided
            assignments = []
            assigned_amount = 0
            unassigned_amount = dialog.result['amount']
            
            if 'assignment' in dialog.result:
                assignment = dialog.result['assignment']
                assignments = [assignment]
                assigned_amount = assignment['assigned_amount']
                unassigned_amount = dialog.result['amount'] - assigned_amount
            
            # Determine status
            if assigned_amount == 0:
                status = 'Unassigned'
            elif unassigned_amount <= 0.01:  # Handle floating point precision
                status = 'Fully Assigned'
            else:
                status = 'Partial'
                
            # Add to tree view with all columns
            self.payments_tree.insert('', 'end', values=(
                dialog.result['date'],
                dialog.result['desc'],
                f"${dialog.result['amount']:,.2f}",
                f"${assigned_amount:,.2f}",
                f"${unassigned_amount:,.2f}",
                status
            ))
            
            # CRITICAL: Also add to the current project data
            if hasattr(self, 'current_project') and self.current_project:
                if 'payments' not in self.current_project:
                    self.current_project['payments'] = []
                
                # Add the new payment to project data
                import uuid
                self.current_project['payments'].append({
                    'id': f"PAY-{str(uuid.uuid4())[:8].upper()}",
                    'date': convert_to_iso_date(dialog.result['date']),
                    'description': dialog.result['desc'],
                    'amount': dialog.result['amount'],
                    'assignments': assignments,
                    'unassigned_amount': unassigned_amount
                })
                
                # Auto-save the project
                self.save_project()
                self.status_var.set(f"Payment added and saved")
            else:
                self.status_var.set(f"Payment added (save project to persist)")
            
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
        
        available_invoices = self.current_project.get('invoices', []) if hasattr(self, 'current_project') and self.current_project else []
        dialog = PaymentDialog(self.root, "Edit Payment", existing_data, available_invoices)
        
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
    
    def assign_payment_to_invoice(self):
        """Assign selected payment to an invoice - CRITICAL BUSINESS FUNCTIONALITY"""
        selection = self.payments_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a payment to assign")
            return
        
        # Get selected payment data from tree
        item_values = self.payments_tree.item(selection[0])['values']
        payment_date = item_values[0]
        payment_desc = item_values[1]
        payment_amount_str = item_values[2].replace('$', '').replace(',', '')
        unassigned_str = item_values[4].replace('$', '').replace(',', '')
        
        try:
            unassigned_amount = float(unassigned_str)
            if unassigned_amount <= 0:
                messagebox.showwarning("No Unassigned Amount", "This payment is fully assigned. Use 'View Assignments' to manage existing assignments.")
                return
        except ValueError:
            messagebox.showerror("Error", "Invalid payment amount format")
            return
        
        # Create payment assignment dialog
        dialog = PaymentAssignmentDialog(self.root, payment_desc, unassigned_amount, self.get_available_invoices())
        
        # Wait for dialog completion
        self.root.wait_window(dialog.window)
        
        if dialog.result:
            # Apply the assignment using the calculation engine
            self.apply_payment_assignment(payment_date, payment_desc, dialog.result)
    
    def get_available_invoices(self):
        """Get list of invoices available for payment assignment"""
        invoices = []
        for item in self.invoices_tree.get_children():
            values = self.invoices_tree.item(item)['values']
            invoice_id = values[0]
            invoice_desc = values[2] 
            invoice_amount = values[3].replace('$', '').replace(',', '')
            
            invoices.append({
                'id': invoice_id,
                'description': invoice_desc,
                'amount': float(invoice_amount)
            })
        
        return invoices
    
    def apply_payment_assignment(self, payment_date, payment_desc, assignment_data):
        """Apply payment assignment and update the project data"""
        try:
            # Import the calculation engine
            from interest_calculation_engine import InterestCalculationEngine
            
            # Find the payment in current project data
            if not self.current_project:
                messagebox.showerror("Error", "No project loaded")
                return
            
            payment_found = None
            for payment in self.current_project.get('payments', []):
                if (payment.get('description', payment.get('desc', '')) == payment_desc and 
                    payment.get('date', '') == convert_to_iso_date(payment_date)):
                    payment_found = payment
                    break
            
            if not payment_found:
                messagebox.showerror("Error", "Could not find payment in project data")
                return
            
            # Find the target invoice
            invoice_found = None
            for invoice in self.current_project.get('invoices', []):
                if invoice['id'] == assignment_data['invoice_id']:
                    invoice_found = invoice
                    break
            
            if not invoice_found:
                messagebox.showerror("Error", "Could not find target invoice")
                return
            
            # Initialize calculation engine with project parameters
            engine = InterestCalculationEngine(
                monthly_rate=self.current_project.get('monthly_rate', 0.015),
                annual_rate=self.current_project.get('annual_rate', 0.18),
                grace_days=self.current_project.get('grace_days', 30)
            )
            
            # Apply the payment assignment
            updated_invoice, updated_payment = engine.apply_payment_to_invoice(
                invoice_found,
                payment_found,
                assignment_data['assigned_amount'],
                assignment_data['assignment_date'],
                assignment_data.get('notes', '')
            )
            
            # Update the project data
            for i, invoice in enumerate(self.current_project['invoices']):
                if invoice['id'] == updated_invoice['id']:
                    self.current_project['invoices'][i] = updated_invoice
                    break
            
            for i, payment in enumerate(self.current_project['payments']):
                if payment['id'] == updated_payment['id']:
                    self.current_project['payments'][i] = updated_payment
                    break
            
            # Refresh the UI displays
            self.load_invoices(self.current_project.get('invoices', []))
            self.load_payments(self.current_project.get('payments', []))
            
            # Show success message with calculation details
            messagebox.showinfo("Assignment Successful", 
                f"Payment assignment completed!\n\n"
                f"Payment: ${assignment_data['assigned_amount']:,.2f}\n"
                f"Applied to: {invoice_found['description']}\n"
                f"Assignment Date: {assignment_data['assignment_date']}\n\n"
                f"Invoice Status: {updated_invoice['status']}\n"
                f"Invoice Balance: ${updated_invoice['balance']:,.2f}\n"
                f"Payment Unassigned: ${updated_payment['unassigned_amount']:,.2f}")
            
            self.status_var.set(f"Payment assigned: ${assignment_data['assigned_amount']:,.2f} to {invoice_found['id']}")
            
        except Exception as e:
            messagebox.showerror("Assignment Error", f"Failed to assign payment: {str(e)}")
    
    def view_payment_assignments(self):
        """View and manage payment assignments"""
        selection = self.payments_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a payment to view assignments")
            return
        
        # Get payment data
        item_values = self.payments_tree.item(selection[0])['values']
        payment_desc = item_values[1]
        
        # Find payment in project data
        payment_found = None
        if self.current_project:
            for payment in self.current_project.get('payments', []):
                if payment.get('description', payment.get('desc', '')) == payment_desc:
                    payment_found = payment
                    break
        
        if not payment_found:
            messagebox.showerror("Error", "Could not find payment in project data")
            return
        
        # Create assignment viewer dialog
        dialog = PaymentAssignmentViewerDialog(self.root, payment_found, self.current_project.get('invoices', []))
        self.root.wait_window(dialog.window)
        
        # Handle reassignment or removal results
        if dialog.result:
            self.handle_payment_reassignment(dialog.result, payment_found)
            self.refresh_payment_display()
    
    def handle_payment_reassignment(self, result, payment):
        """Handle payment reassignment or removal operations"""
        try:
            if result['action'] == 'remove':
                # Remove assignment and add amount back to unassigned
                assignments = payment.get('assignments', [])
                invoice_id = result['invoice_id']
                amount = result['amount']
                
                # Find and remove the assignment
                for i, assignment in enumerate(assignments):
                    if assignment['invoice_id'] == invoice_id:
                        assignments.pop(i)
                        payment['unassigned_amount'] += amount
                        self.status_var.set(f"Assignment removed: ${amount:,.2f} returned to unassigned")
                        break
                        
            elif result['action'] == 'reassign':
                # Move assignment from one invoice to another
                assignments = payment.get('assignments', [])
                old_invoice_id = result['old_invoice_id']
                new_invoice_id = result['new_invoice_id']
                amount = result['amount']
                date = result['date']
                notes = result['notes']
                
                # Find and update the assignment
                for assignment in assignments:
                    if assignment['invoice_id'] == old_invoice_id:
                        assignment['invoice_id'] = new_invoice_id
                        assignment['assignment_date'] = convert_to_iso_date(date)
                        assignment['notes'] = notes
                        self.status_var.set(f"Payment reassigned: ${amount:,.2f} moved from {old_invoice_id} to {new_invoice_id}")
                        break
                        
        except Exception as e:
            messagebox.showerror("Error", f"Failed to process reassignment: {str(e)}")
    
    def refresh_payment_display(self):
        """Refresh the payment table display after reassignment changes"""
        if not hasattr(self, 'payments_tree'):
            return
            
        # Clear existing payments
        for item in self.payments_tree.get_children():
            self.payments_tree.delete(item)
        
        # Reload payments from current project data
        if self.current_project and 'payments' in self.current_project:
            for payment in self.current_project['payments']:
                # Calculate assigned and unassigned amounts
                total_assigned = sum(assignment.get('assigned_amount', 0) 
                                   for assignment in payment.get('assignments', []))
                unassigned_amount = payment.get('unassigned_amount', 0)
                total_amount = payment.get('amount', 0)
                
                # Determine status
                if unassigned_amount <= 0.01:
                    status = "Fully Assigned"
                elif total_assigned <= 0.01:
                    status = "Unassigned"
                else:
                    status = "Partially Assigned"
                
                values = (
                    convert_to_american_date(payment.get('date', '')),
                    payment.get('description', payment.get('desc', '')),
                    f"${total_amount:,.2f}",
                    f"${total_assigned:,.2f}",
                    f"${unassigned_amount:,.2f}",
                    status
                )
                
                self.payments_tree.insert('', 'end', values=values)
            
    def save_project(self):
        """Save project data."""
        # Write debug info to a file so we can see it even if app crashes
        debug_file = Path("debug_save.txt")
        try:
            with open(debug_file, "w") as df:
                df.write("DEBUG: Starting save_project\n")
                df.flush()
                
                # Collect form data
                df.write("DEBUG: Collecting form data\n")
                df.flush()
                project_data = {
                    'title': self.title_var.get(),
                    'description': self.description_text.get('1.0', tk.END).strip() if hasattr(self, 'description_text') else '',
                    'as_of_date': convert_to_iso_date(self.as_of_date_var.get()),
                    'grace_days': int(self.grace_days_var.get()) if self.grace_days_var.get() else 0,
                    'annual_rate': parse_percentage(self.annual_rate_var.get()),
                    'monthly_rate': parse_percentage(self.monthly_rate_var.get()),
                    'invoices': [],
                    'payments': []
                }
                
                # Use existing invoice data from current_project if available (to preserve edits)
                if hasattr(self, 'current_project') and self.current_project and 'invoices' in self.current_project:
                    df.write("DEBUG: Using current_project invoice data\n")
                    df.flush()
                    project_data['invoices'] = self.current_project['invoices'].copy()
                    # Debug: Log what we're saving
                    for i, inv in enumerate(project_data['invoices']):
                        df.write(f"DEBUG: Saving invoice {i}: ID={inv.get('id')}, desc={inv.get('desc')}\n")
                else:
                    # Fallback: Collect invoices from tree view
                    df.write("DEBUG: Collecting invoices from tree view (fallback)\n")
                    df.flush()
                    for item in self.invoices_tree.get_children():
                        values = self.invoices_tree.item(item)['values']
                        df.write(f"DEBUG: Invoice values: {values}\n")
                        df.flush()
                        invoice = {
                            'id': values[0],
                            'date': convert_to_iso_date(values[1]),
                            'desc': values[2],
                            'amount': float(values[3].replace('$', '').replace(',', ''))
                        }
                        project_data['invoices'].append(invoice)
            
                # Collect payments from tree view - properly handle the 6-column format
                df.write("DEBUG: Collecting payments from tree view\n")
                df.flush()
                if hasattr(self, 'current_project') and self.current_project and 'payments' in self.current_project:
                    # Use the original payment data from current_project to preserve assignments
                    df.write("DEBUG: Using current_project payments data\n")
                    df.flush()
                    project_data['payments'] = self.current_project['payments'].copy()
                else:
                    # Fallback: collect basic payment data from tree view
                    df.write("DEBUG: Collecting payments from tree view (fallback)\n")
                    df.flush()
                    for item in self.payments_tree.get_children():
                        values = self.payments_tree.item(item)['values']
                        df.write(f"DEBUG: Payment values: {values}\n")
                        df.flush()
                        if len(values) >= 3:  # Ensure we have at least the basic columns
                            payment = {
                                'date': convert_to_iso_date(values[0]),
                                'description': values[1],  # Use 'description' consistently
                                'amount': float(values[2].replace('$', '').replace(',', '')),
                                'assignments': [],  # New payments have no assignments
                                'unassigned_amount': float(values[2].replace('$', '').replace(',', ''))
                            }
                            project_data['payments'].append(payment)
                
                # Determine file path
                df.write("DEBUG: Determining file path\n")
                df.flush()
                if not self.current_project_file:
                    # New project - create filename from title
                    safe_title = "".join(c for c in project_data['title'] if c.isalnum() or c in (' ', '-', '_')).rstrip()
                    safe_title = safe_title.replace(' ', '-').lower()
                    self.current_project_file = self.projects_dir / f"{safe_title}.json"
                
                df.write(f"DEBUG: Saving to file: {self.current_project_file}\n")
                df.flush()
                # Save to file
                with open(self.current_project_file, 'w') as f:
                    json.dump(project_data, f, indent=2)
                
                df.write("DEBUG: File saved successfully\n")
                df.flush()
                messagebox.showinfo("Success", "Project saved successfully!")
                self.load_projects()  # Refresh project list
                self.status_var.set(f"Saved project: {project_data['title']}")
                df.write("DEBUG: save_project completed successfully\n")
                
        except Exception as e:
            # Write error to debug file
            with open(debug_file, "a") as df:
                df.write(f"DEBUG: ERROR in save_project: {str(e)}\n")
                import traceback
                df.write(f"DEBUG: Traceback:\n{traceback.format_exc()}\n")
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
            
            # Schedule next update with safety check
            if self.root and self.root.winfo_exists():
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
        self.existing_data = existing_data
        
        self.window = tk.Toplevel(parent)
        self.window.title(title)
        self.window.transient(parent)
        self.window.grab_set()
        
        # Create widgets first
        self.create_widgets(existing_data)
        
        # Then ensure proper sizing - this is the key fix
        min_width = 650 if self.available_invoices else 550
        min_height = 600 if self.available_invoices else 450
        ensure_window_visibility(self.window, parent, min_width, min_height)
        
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
        self.amount_entry = ttk.Entry(amount_frame, textvariable=self.amount_var, width=25, font=("Arial", 10))
        self.amount_entry.pack(anchor=tk.W, pady=(5, 0))
        
        # Bind currency formatting events
        self.amount_entry.bind('<KeyRelease>', self.format_amount_field)
        self.amount_entry.bind('<FocusOut>', self.format_amount_field)
        
        # Invoice assignment section (only show if invoices are available)
        if self.available_invoices:
            assignment_frame = ttk.LabelFrame(main_frame, text="Assignment (Optional)", padding="10")
            assignment_frame.pack(fill=tk.X, pady=(0, 15))
            
            ttk.Label(assignment_frame, text="Assign to Invoice:", font=("Arial", 10, "bold")).pack(anchor=tk.W)
            
            # Invoice dropdown
            self.invoice_var = tk.StringVar()
            invoice_combo = ttk.Combobox(assignment_frame, textvariable=self.invoice_var, 
                                       state="readonly", width=50, font=("Arial", 9))
            
            # Populate invoice options
            invoice_options = ["-- No Assignment --"]  # Default option
            for invoice in self.available_invoices:
                desc = invoice.get('desc', invoice.get('description', 'No Description'))
                option = f"{invoice['id']} - {desc} (${invoice['amount']:,.2f})"
                invoice_options.append(option)
            
            invoice_combo['values'] = invoice_options
            
            # Set current assignment if editing existing payment
            current_assignment_set = False
            if self.existing_data and 'assignments' in self.existing_data and self.existing_data['assignments']:
                # If payment has existing assignments, show the first one
                first_assignment = self.existing_data['assignments'][0]
                for option in invoice_options:
                    if option.startswith(first_assignment.get('invoice_id', '')):
                        invoice_combo.set(option)
                        current_assignment_set = True
                        break
            
            if not current_assignment_set:
                invoice_combo.set("-- No Assignment --")  # Default selection
                
            invoice_combo.pack(fill=tk.X, pady=(5, 10))
            
            # Assignment amount (auto-fills with payment amount when invoice is selected)
            ttk.Label(assignment_frame, text="Assignment Amount ($):", font=("Arial", 10, "bold")).pack(anchor=tk.W)
            self.assignment_amount_var = tk.StringVar()
            
            # Pre-populate assignment amount if editing existing payment
            if self.existing_data and 'assignments' in self.existing_data and self.existing_data['assignments']:
                first_assignment = self.existing_data['assignments'][0]
                self.assignment_amount_var.set(str(first_assignment.get('assigned_amount', '')))
            
            assignment_amount_entry = ttk.Entry(assignment_frame, textvariable=self.assignment_amount_var, 
                                               width=25, font=("Arial", 10))
            assignment_amount_entry.pack(anchor=tk.W, pady=(5, 10))
            
            # Bind events to auto-fill assignment amount when invoice is selected
            invoice_combo.bind('<<ComboboxSelected>>', self.on_invoice_selected)
            
            # Assignment notes
            ttk.Label(assignment_frame, text="Assignment Notes:", font=("Arial", 10, "bold")).pack(anchor=tk.W)
            self.assignment_notes_text = tk.Text(assignment_frame, height=3, width=50, font=("Arial", 9))
            
            # Pre-populate assignment notes if editing existing payment
            if self.existing_data and 'assignments' in self.existing_data and self.existing_data['assignments']:
                first_assignment = self.existing_data['assignments'][0]
                self.assignment_notes_text.insert('1.0', first_assignment.get('notes', ''))
            
            self.assignment_notes_text.pack(fill=tk.X, pady=(5, 0))
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(button_frame, text="Save", command=self.ok_clicked, width=12).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Clear", command=self.clear_fields, width=12).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Cancel", command=self.window.destroy, width=12).pack(side=tk.LEFT)
    
    def format_amount_field(self, event=None):
        """Format amount field as currency while typing."""
        current_value = self.amount_var.get()
        
        # Remove all non-digit characters except decimal point
        cleaned = ''.join(c for c in current_value if c.isdigit() or c == '.')
        
        if cleaned and cleaned != '.':
            try:
                # Convert to float and format as currency
                amount = float(cleaned)
                formatted = f"{amount:,.2f}"
                
                # Only update if the formatted value is different to avoid cursor jumping
                if formatted != current_value:
                    self.amount_var.set(formatted)
            except ValueError:
                # If conversion fails, keep the current value
                pass
        
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
            
            # Parse currency-formatted amount (remove commas)
            amount_str = self.amount_var.get().replace(',', '')
            try:
                amount_float = float(amount_str)
            except ValueError:
                messagebox.showerror("Error", "Please enter a valid amount")
                return
                
            self.result = {
                'date': self.date_var.get(),
                'desc': self.desc_var.get(),
                'amount': amount_float
            }
            
            # Handle assignment if one was selected
            if hasattr(self, 'invoice_var') and self.invoice_var.get() != "-- No Assignment --":
                invoice_selection = self.invoice_var.get()
                # Extract invoice ID from selection (format: "ID - desc (amount)")
                invoice_id = invoice_selection.split(' - ')[0]
                
                # Get assignment amount (default to full payment amount if not specified)
                assignment_amount = amount_float
                if hasattr(self, 'assignment_amount_var') and self.assignment_amount_var.get().strip():
                    try:
                        assignment_amount = float(self.assignment_amount_var.get().replace(',', ''))
                    except ValueError:
                        assignment_amount = amount_float
                
                # Get assignment notes
                assignment_notes = ""
                if hasattr(self, 'assignment_notes_text'):
                    assignment_notes = self.assignment_notes_text.get('1.0', tk.END).strip()
                
                # Add assignment info to result
                self.result['assignment'] = {
                    'invoice_id': invoice_id,
                    'assigned_amount': assignment_amount,
                    'assignment_date': self.date_var.get(),
                    'notes': assignment_notes
                }
            
            self.window.destroy()
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid amount")

    def on_invoice_selected(self, event=None):
        """Handle invoice selection in dropdown."""
        if hasattr(self, 'assignment_amount_var') and self.amount_var.get().strip():
            # Auto-fill assignment amount with payment amount
            self.assignment_amount_var.set(self.amount_var.get())

    def clear_fields(self):
        """Clear all form fields."""
        self.date_var.set('')
        self.desc_var.set('')
        self.amount_var.set('')
        
        if hasattr(self, 'invoice_var'):
            self.invoice_var.set("-- No Assignment --")
        if hasattr(self, 'assignment_amount_var'):
            self.assignment_amount_var.set('')
        if hasattr(self, 'assignment_notes_text'):
            self.assignment_notes_text.delete('1.0', tk.END)


class InvoiceDialog:
    """Dialog for adding/editing invoices."""
    
    def __init__(self, parent, title, existing_data=None):
        self.result = None
        
        self.window = tk.Toplevel(parent)
        self.window.title(title)
        self.window.transient(parent)
        self.window.grab_set()
        
        # Create widgets first
        self.create_widgets(existing_data)
        
        # Then ensure proper sizing
        ensure_window_visibility(self.window, parent, 550, 400)
        
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
        self.amount_entry = ttk.Entry(amount_frame, textvariable=self.amount_var, width=25, font=("Arial", 10))
        self.amount_entry.pack(anchor=tk.W, pady=(5, 0))
        
        # Bind currency formatting events
        self.amount_entry.bind('<KeyRelease>', self.format_amount_field)
        self.amount_entry.bind('<FocusOut>', self.format_amount_field)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(button_frame, text="Save", command=self.ok_clicked, width=12).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Clear", command=self.clear_fields, width=12).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Cancel", command=self.window.destroy, width=12).pack(side=tk.LEFT)
        
    def format_amount_field(self, event=None):
        """Format amount field as currency while typing."""
        current_value = self.amount_var.get()
        
        # Remove all non-digit characters except decimal point
        cleaned = ''.join(c for c in current_value if c.isdigit() or c == '.')
        
        if cleaned and cleaned != '.':
            try:
                # Convert to float and format as currency
                amount = float(cleaned)
                formatted = f"{amount:,.2f}"
                
                # Only update if the formatted value is different to avoid cursor jumping
                if formatted != current_value:
                    self.amount_var.set(formatted)
            except ValueError:
                # If conversion fails, keep the current value
                pass
        
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
            
            # Parse currency-formatted amount (remove commas)
            try:
                amount_float = float(amount_val.replace(',', ''))
            except ValueError:
                messagebox.showerror("Error", "Please enter a valid amount")
                return
            
            print(f"DEBUG: Creating result with invoice_id: {self.invoice_id}")
            self.result = {
                'id': self.invoice_id,
                'date': date_val,
                'desc': desc_val,
                'amount': amount_float
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


class PaymentAssignmentDialog:
    """Dialog for assigning payments to invoices with pre-invoice payment support"""
    
    def __init__(self, parent, payment_description, unassigned_amount, available_invoices):
        self.parent = parent
        self.payment_description = payment_description
        self.unassigned_amount = unassigned_amount
        self.available_invoices = available_invoices
        self.result = None
        
        self.create_dialog()
    
    def create_dialog(self):
        """Create the payment assignment dialog"""
        self.window = tk.Toplevel(self.parent)
        self.window.title("Assign Payment to Invoice")
        self.window.geometry("600x500")
        self.window.resizable(True, True)
        
        # Make dialog modal
        self.window.transient(self.parent)
        self.window.grab_set()
        
        # Center the dialog
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() - self.window.winfo_width()) // 2
        y = (self.window.winfo_screenheight() - self.window.winfo_height()) // 2
        self.window.geometry(f"+{x}+{y}")
        
        # Main frame
        main_frame = ttk.Frame(self.window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="Assign Payment to Invoice", 
                               font=("Arial", 14, "bold"))
        title_label.pack(pady=(0, 20))
        
        # Payment info
        payment_info_frame = ttk.LabelFrame(main_frame, text="Payment Information", padding="10")
        payment_info_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(payment_info_frame, text=f"Payment: {self.payment_description}").pack(anchor=tk.W)
        ttk.Label(payment_info_frame, text=f"Unassigned Amount: ${self.unassigned_amount:,.2f}").pack(anchor=tk.W)
        
        # Assignment details
        assignment_frame = ttk.LabelFrame(main_frame, text="Assignment Details", padding="10")
        assignment_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # Invoice selection
        invoice_frame = ttk.Frame(assignment_frame)
        invoice_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(invoice_frame, text="Target Invoice:").pack(anchor=tk.W)
        self.invoice_var = tk.StringVar()
        invoice_combo = ttk.Combobox(invoice_frame, textvariable=self.invoice_var, 
                                   state="readonly", width=50)
        
        # Populate invoice dropdown
        invoice_options = []
        for invoice in self.available_invoices:
            option = f"{invoice['id']} - {invoice['description']} (${invoice['amount']:,.2f})"
            invoice_options.append(option)
        
        invoice_combo['values'] = invoice_options
        invoice_combo.pack(fill=tk.X, pady=(2, 0))
        invoice_combo.bind('<<ComboboxSelected>>', self.on_invoice_selected)
        
        # Assignment amount
        amount_frame = ttk.Frame(assignment_frame)
        amount_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(amount_frame, text="Assignment Amount:").pack(anchor=tk.W)
        self.amount_var = tk.StringVar(value=str(self.unassigned_amount))
        amount_entry = ttk.Entry(amount_frame, textvariable=self.amount_var, width=20)
        amount_entry.pack(anchor=tk.W, pady=(2, 0))
        
        # Assignment date
        date_frame = ttk.Frame(assignment_frame)
        date_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(date_frame, text="Assignment Date (MM/DD/YYYY):").pack(anchor=tk.W)
        self.date_var = tk.StringVar(value=datetime.now().strftime("%m/%d/%Y"))
        date_entry = ttk.Entry(date_frame, textvariable=self.date_var, width=20)
        date_entry.pack(anchor=tk.W, pady=(2, 0))
        
        # Notes
        notes_frame = ttk.Frame(assignment_frame)
        notes_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        ttk.Label(notes_frame, text="Notes (optional):").pack(anchor=tk.W)
        self.notes_text = tk.Text(notes_frame, height=4, width=50)
        self.notes_text.pack(fill=tk.BOTH, expand=True, pady=(2, 0))
        
        # CRITICAL: Pre-invoice payment warning
        warning_frame = ttk.Frame(assignment_frame)
        warning_frame.pack(fill=tk.X, pady=(10, 0))
        
        warning_label = ttk.Label(warning_frame, 
                                 text="Note: Payments can be assigned before invoice dates.\n"
                                      "This will reduce the principal amount when interest calculation begins.",
                                 foreground="blue", font=("Arial", 9, "italic"))
        warning_label.pack(anchor=tk.W)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        ttk.Button(button_frame, text="Assign Payment", command=self.ok_clicked, 
                  width=15).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Cancel", command=self.cancel_clicked, 
                  width=15).pack(side=tk.LEFT)
        
        # Bind keys
        self.window.bind('<Return>', lambda e: self.ok_clicked())
        self.window.bind('<Escape>', lambda e: self.cancel_clicked())
    
    def on_invoice_selected(self, event):
        """Handle invoice selection to provide helpful info"""
        if self.invoice_var.get():
            # Extract invoice ID from selection
            invoice_id = self.invoice_var.get().split(' - ')[0]
            
            # Find selected invoice
            selected_invoice = None
            for invoice in self.available_invoices:
                if invoice['id'] == invoice_id:
                    selected_invoice = invoice
                    break
            
            if selected_invoice:
                # Update notes with helpful info
                current_notes = self.notes_text.get("1.0", tk.END).strip()
                if not current_notes:
                    self.notes_text.insert("1.0", 
                        f"Payment assignment to {selected_invoice['description']}\n"
                        f"Invoice Amount: ${selected_invoice['amount']:,.2f}")
    
    def ok_clicked(self):
        """Handle Assign Payment button click with validation"""
        try:
            # Validate invoice selection
            if not self.invoice_var.get():
                messagebox.showerror("Error", "Please select an invoice")
                return
            
            # Extract invoice ID
            invoice_id = self.invoice_var.get().split(' - ')[0]
            
            # Validate assignment amount
            try:
                assigned_amount = float(self.amount_var.get())
                if assigned_amount <= 0:
                    messagebox.showerror("Error", "Assignment amount must be greater than 0")
                    return
                if assigned_amount > self.unassigned_amount:
                    messagebox.showerror("Error", f"Assignment amount cannot exceed unassigned amount (${self.unassigned_amount:,.2f})")
                    return
            except ValueError:
                messagebox.showerror("Error", "Please enter a valid assignment amount")
                return
            
            # Validate assignment date
            assignment_date = self.date_var.get().strip()
            if not assignment_date:
                messagebox.showerror("Error", "Please enter an assignment date")
                return
            
            try:
                datetime.strptime(assignment_date, '%m/%d/%Y')
            except ValueError:
                messagebox.showerror("Error", "Please enter assignment date in MM/DD/YYYY format")
                return
            
            # Get notes
            notes = self.notes_text.get("1.0", tk.END).strip()
            
            # Create result
            self.result = {
                'invoice_id': invoice_id,
                'assigned_amount': assigned_amount,
                'assignment_date': convert_to_iso_date(assignment_date),
                'notes': notes
            }
            
            self.window.destroy()
            
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
    
    def cancel_clicked(self):
        """Handle Cancel button click"""
        self.result = None
        self.window.destroy()


class PaymentAssignmentViewerDialog:
    """Dialog for viewing and managing payment assignments"""
    
    def __init__(self, parent, payment, invoices):
        self.parent = parent
        self.payment = payment
        self.invoices = invoices
        self.result = None
        
        self.create_dialog()
    
    def create_dialog(self):
        """Create the payment assignment viewer dialog"""
        self.window = tk.Toplevel(self.parent)
        self.window.title("Payment Assignment Details")
        self.window.resizable(True, True)
        self.window.transient(self.parent)
        self.window.grab_set()
        
        # Main frame
        main_frame = ttk.Frame(self.window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="Payment Assignment Details", 
                               font=("Arial", 14, "bold"))
        title_label.pack(pady=(0, 20))
        
        # Payment summary
        summary_frame = ttk.LabelFrame(main_frame, text="Payment Summary", padding="10")
        summary_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(summary_frame, text=f"Payment ID: {self.payment.get('id', 'N/A')}").pack(anchor=tk.W)
        ttk.Label(summary_frame, text=f"Date: {convert_to_american_date(self.payment.get('date', ''))}").pack(anchor=tk.W)
        ttk.Label(summary_frame, text=f"Description: {self.payment.get('description', self.payment.get('desc', 'N/A'))}").pack(anchor=tk.W)
        ttk.Label(summary_frame, text=f"Total Amount: ${self.payment.get('amount', 0):,.2f}").pack(anchor=tk.W)
        ttk.Label(summary_frame, text=f"Unassigned Amount: ${self.payment.get('unassigned_amount', 0):,.2f}").pack(anchor=tk.W)
        
        # Assignments table
        assignments_frame = ttk.LabelFrame(main_frame, text="Current Assignments", padding="10")
        assignments_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # Create treeview for assignments
        columns = ('Invoice ID', 'Invoice Description', 'Assigned Amount', 'Assignment Date', 'Notes')
        self.assignments_tree = ttk.Treeview(assignments_frame, columns=columns, show='headings', height=10)
        
        # Configure columns
        self.assignments_tree.heading('Invoice ID', text='Invoice ID')
        self.assignments_tree.heading('Invoice Description', text='Description')
        self.assignments_tree.heading('Assigned Amount', text='Amount')
        self.assignments_tree.heading('Assignment Date', text='Date')
        self.assignments_tree.heading('Notes', text='Notes')
        
        self.assignments_tree.column('Invoice ID', width=100)
        self.assignments_tree.column('Invoice Description', width=200)
        self.assignments_tree.column('Assigned Amount', width=100)
        self.assignments_tree.column('Assignment Date', width=100)
        self.assignments_tree.column('Notes', width=150)
        
        # Add scrollbar
        assignments_scrollbar = ttk.Scrollbar(assignments_frame, orient=tk.VERTICAL, 
                                            command=self.assignments_tree.yview)
        self.assignments_tree.configure(yscrollcommand=assignments_scrollbar.set)
        
        # Pack tree and scrollbar
        self.assignments_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        assignments_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Populate assignments
        self.load_assignments()
        
        # Add double-click binding for editing
        self.assignments_tree.bind('<Double-1>', self.on_assignment_double_click)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        ttk.Button(button_frame, text="Edit Assignment", command=self.edit_assignment, 
                  width=18).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Remove Assignment", command=self.remove_assignment, 
                  width=18).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Reassign Payment", command=self.reassign_payment, 
                  width=18).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Save Changes", command=self.save_changes, 
                  width=15).pack(side=tk.RIGHT, padx=(10, 0))
        ttk.Button(button_frame, text="Close", command=self.close_clicked, 
                  width=15).pack(side=tk.RIGHT)
        
        # Bind Escape key
        self.window.bind('<Escape>', lambda e: self.close_clicked())
        
        # Ensure proper window sizing after all widgets are created
        ensure_window_visibility(self.window, self.parent, 850, 650)
    
    def load_assignments(self):
        """Load payment assignments into the tree"""
        assignments = self.payment.get('assignments', [])
        
        if not assignments:
            # Show message if no assignments
            self.assignments_tree.insert('', 'end', values=('No assignments', '', '', '', ''))
            return
        
        for assignment in assignments:
            # Find invoice description
            invoice_desc = 'Unknown Invoice'
            for invoice in self.invoices:
                if invoice['id'] == assignment.get('invoice_id'):
                    invoice_desc = invoice.get('desc', invoice.get('description', 'Unknown Invoice'))
                    break
            
            self.assignments_tree.insert('', 'end', values=(
                assignment.get('invoice_id', 'N/A'),
                invoice_desc,
                f"${assignment.get('assigned_amount', 0):,.2f}",
                convert_to_american_date(assignment.get('assignment_date', '')),
                assignment.get('notes', '')
            ))
    
    def remove_assignment(self):
        """Remove the selected assignment and return amount to unassigned"""
        selection = self.assignments_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an assignment to remove")
            return
        
        # Get selected assignment details
        item_id = selection[0]
        values = self.assignments_tree.item(item_id, 'values')
        
        if values[0] == 'No assignments':
            return
        
        invoice_id = values[0]
        assigned_amount_str = values[2].replace('$', '').replace(',', '')
        
        try:
            assigned_amount = float(assigned_amount_str)
        except ValueError:
            messagebox.showerror("Error", "Invalid amount format")
            return
        
        # Confirm removal
        result = messagebox.askyesno("Confirm Removal", 
                                   f"Remove assignment of ${assigned_amount:,.2f} from {invoice_id}?\n"
                                   f"This amount will be returned to unassigned.")
        
        if result:
            self.result = {
                'action': 'remove',
                'invoice_id': invoice_id,
                'amount': assigned_amount
            }
            messagebox.showinfo("Success", "Assignment removed. Please close dialog to apply changes.")
    
    def reassign_payment(self):
        """Reassign the selected assignment to a different invoice"""
        selection = self.assignments_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an assignment to reassign")
            return
        
        # Get selected assignment details
        item_id = selection[0]
        values = self.assignments_tree.item(item_id, 'values')
        
        if values[0] == 'No assignments':
            return
        
        current_invoice_id = values[0]
        assigned_amount_str = values[2].replace('$', '').replace(',', '')
        assignment_date = values[3]
        notes = values[4]
        
        try:
            assigned_amount = float(assigned_amount_str)
        except ValueError:
            messagebox.showerror("Error", "Invalid amount format")
            return
        
        # Create reassignment dialog
        ReassignmentDialog(self, current_invoice_id, assigned_amount, assignment_date, 
                          notes, self.invoices, self.on_reassignment_complete)
    
    def on_reassignment_complete(self, reassignment_data):
        """Handle completion of reassignment dialog"""
        self.result = {
            'action': 'reassign',
            'old_invoice_id': reassignment_data['old_invoice_id'],
            'new_invoice_id': reassignment_data['new_invoice_id'],
            'amount': reassignment_data['amount'],
            'date': reassignment_data['date'],
            'notes': reassignment_data['notes']
        }
        messagebox.showinfo("Success", "Payment reassigned. Please close dialog to apply changes.")
    
    def close_clicked(self):
        """Handle Close button click"""
        self.window.destroy()
    
    def on_assignment_double_click(self, event):
        """Handle double-click on assignment for editing"""
        self.edit_assignment()
    
    def edit_assignment(self):
        """Edit the selected assignment"""
        selection = self.assignments_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an assignment to edit")
            return
        
        item_id = selection[0]
        values = self.assignments_tree.item(item_id, 'values')
        
        if values[0] == 'No assignments':
            return
        
        # Extract assignment data
        invoice_id = values[0]
        assigned_amount_str = values[2].replace('$', '').replace(',', '')
        assignment_date = values[3]
        notes = values[4]
        
        # Find the assignment in payment data
        assignment_index = -1
        for i, assignment in enumerate(self.payment.get('assignments', [])):
            if assignment.get('invoice_id') == invoice_id:
                assignment_index = i
                break
        
        if assignment_index == -1:
            messagebox.showerror("Error", "Could not find assignment data")
            return
        
        # Create edit dialog
        edit_dialog = AssignmentEditDialog(self.window, {
            'invoice_id': invoice_id,
            'assigned_amount': float(assigned_amount_str),
            'assignment_date': assignment_date,
            'notes': notes
        }, self.invoices, self.payment.get('unassigned_amount', 0))
        
        self.window.wait_window(edit_dialog.window)
        
        if edit_dialog.result:
            # Update the assignment in payment data
            assignment = self.payment['assignments'][assignment_index]
            old_amount = assignment['assigned_amount']
            new_amount = edit_dialog.result['assigned_amount']
            amount_difference = new_amount - old_amount
            
            # Update assignment
            assignment.update(edit_dialog.result)
            
            # Update unassigned amount
            self.payment['unassigned_amount'] = max(0, self.payment['unassigned_amount'] - amount_difference)
            
            # Refresh display
            self.refresh_display()
            
            messagebox.showinfo("Success", "Assignment updated successfully")
    
    def save_changes(self):
        """Save changes and notify parent"""
        if self.result:
            messagebox.showinfo("Success", "Changes will be applied when you close this dialog")
        else:
            self.result = {'action': 'save', 'payment': self.payment}
            messagebox.showinfo("Success", "Changes saved successfully")
    
    def refresh_display(self):
        """Refresh the assignments display"""
        # Clear existing items
        for item in self.assignments_tree.get_children():
            self.assignments_tree.delete(item)
        
        # Reload assignments
        self.load_assignments()
        
        # Update payment summary (unassigned amount may have changed)
        summary_frame = self.window.winfo_children()[0].winfo_children()[1]  # Get summary frame
        for widget in summary_frame.winfo_children():
            widget.destroy()
        
        # Recreate summary labels
        ttk.Label(summary_frame, text=f"Payment ID: {self.payment.get('id', 'N/A')}").pack(anchor=tk.W)
        ttk.Label(summary_frame, text=f"Date: {convert_to_american_date(self.payment.get('date', ''))}").pack(anchor=tk.W)
        ttk.Label(summary_frame, text=f"Description: {self.payment.get('description', self.payment.get('desc', 'N/A'))}").pack(anchor=tk.W)
        ttk.Label(summary_frame, text=f"Total Amount: ${self.payment.get('amount', 0):,.2f}").pack(anchor=tk.W)
        ttk.Label(summary_frame, text=f"Unassigned Amount: ${self.payment.get('unassigned_amount', 0):,.2f}").pack(anchor=tk.W)


class AssignmentEditDialog:
    """Dialog for editing assignment details"""
    
    def __init__(self, parent, assignment_data, invoices, max_unassigned_amount):
        self.assignment_data = assignment_data
        self.invoices = invoices
        self.max_unassigned_amount = max_unassigned_amount
        self.result = None
        
        self.window = tk.Toplevel(parent)
        self.window.title("Edit Assignment")
        self.window.transient(parent)
        self.window.grab_set()
        
        # Create widgets first
        self.create_widgets()
        
        # Then ensure proper sizing
        ensure_window_visibility(self.window, parent, 650, 550)
    
    def create_widgets(self):
        """Create dialog widgets"""
        main_frame = ttk.Frame(self.window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="Edit Assignment", font=("Arial", 14, "bold"))
        title_label.pack(pady=(0, 20))
        
        # Invoice (dropdown for selection)
        invoice_frame = ttk.Frame(main_frame)
        invoice_frame.pack(fill=tk.X, pady=(0, 15))
        ttk.Label(invoice_frame, text="Invoice:", font=("Arial", 10, "bold")).pack(anchor=tk.W)
        
        self.invoice_var = tk.StringVar()
        invoice_combo = ttk.Combobox(invoice_frame, textvariable=self.invoice_var, 
                                   state="readonly", width=50, font=("Arial", 9))
        
        # Populate invoice options
        invoice_options = []
        current_selection = None
        for invoice in self.invoices:
            desc = invoice.get('desc', invoice.get('description', 'No Description'))
            option = f"{invoice['id']} - {desc} (${invoice['amount']:,.2f})"
            invoice_options.append(option)
            
            # Set current selection if this matches the assignment's current invoice
            if invoice['id'] == self.assignment_data['invoice_id']:
                current_selection = option
        
        invoice_combo['values'] = invoice_options
        if current_selection:
            invoice_combo.set(current_selection)
        invoice_combo.pack(fill=tk.X, pady=(5, 0))
        
        # Assignment amount
        amount_frame = ttk.Frame(main_frame)
        amount_frame.pack(fill=tk.X, pady=(0, 15))
        ttk.Label(amount_frame, text="Assignment Amount ($):", font=("Arial", 10, "bold")).pack(anchor=tk.W)
        self.amount_var = tk.StringVar(value=str(self.assignment_data['assigned_amount']))
        amount_entry = ttk.Entry(amount_frame, textvariable=self.amount_var, width=25)
        amount_entry.pack(anchor=tk.W, pady=(5, 0))
        
        # Assignment date
        date_frame = ttk.Frame(main_frame)
        date_frame.pack(fill=tk.X, pady=(0, 15))
        ttk.Label(date_frame, text="Assignment Date (MM/DD/YYYY):", font=("Arial", 10, "bold")).pack(anchor=tk.W)
        self.date_var = tk.StringVar(value=self.assignment_data['assignment_date'])
        date_entry = ttk.Entry(date_frame, textvariable=self.date_var, width=25)
        date_entry.pack(anchor=tk.W, pady=(5, 0))
        
        # Notes
        notes_frame = ttk.Frame(main_frame)
        notes_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        ttk.Label(notes_frame, text="Notes:", font=("Arial", 10, "bold")).pack(anchor=tk.W)
        self.notes_text = tk.Text(notes_frame, height=6, width=50)
        self.notes_text.insert('1.0', self.assignment_data['notes'])
        self.notes_text.pack(fill=tk.BOTH, expand=True, pady=(5, 0))
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        ttk.Button(button_frame, text="Save", command=self.save_clicked, width=12).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Cancel", command=self.window.destroy, width=12).pack(side=tk.LEFT)
    
    def save_clicked(self):
        """Handle Save button click"""
        try:
            # Validate amount
            amount = float(self.amount_var.get())
            if amount <= 0:
                messagebox.showerror("Error", "Assignment amount must be greater than 0")
                return
            
            old_amount = self.assignment_data['assigned_amount']
            amount_increase = amount - old_amount
            
            if amount_increase > self.max_unassigned_amount:
                messagebox.showerror("Error", f"Cannot increase assignment by ${amount_increase:,.2f}. Only ${self.max_unassigned_amount:,.2f} is available.")
                return
            
            # Validate date
            date_str = self.date_var.get().strip()
            if not date_str:
                messagebox.showerror("Error", "Please enter an assignment date")
                return
            
            # Get selected invoice ID from dropdown
            invoice_selection = self.invoice_var.get()
            if not invoice_selection:
                messagebox.showerror("Error", "Please select an invoice")
                return
            
            # Extract invoice ID from selection (format: "ID - desc (amount)")
            selected_invoice_id = invoice_selection.split(' - ')[0]
            
            self.result = {
                'invoice_id': selected_invoice_id,
                'assigned_amount': amount,
                'assignment_date': convert_to_iso_date(date_str),
                'notes': self.notes_text.get('1.0', tk.END).strip()
            }
            
            self.window.destroy()
            
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid amount")


class ReassignmentDialog:
    """Dialog for reassigning a payment from one invoice to another"""
    
    def __init__(self, parent, old_invoice_id, amount, current_date, current_notes, 
                 available_invoices, callback):
        self.parent = parent
        self.old_invoice_id = old_invoice_id
        self.amount = amount
        self.current_date = current_date
        self.current_notes = current_notes
        self.available_invoices = available_invoices
        self.callback = callback
        
        self.create_dialog()
    
    def create_dialog(self):
        """Create the reassignment dialog"""
        self.window = tk.Toplevel(self.parent.window)
        self.window.title("Reassign Payment")
        self.window.resizable(True, True)
        self.window.transient(self.parent.window)
        self.window.grab_set()
        
        # Main frame
        main_frame = ttk.Frame(self.window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="Reassign Payment", 
                               font=("Arial", 14, "bold"))
        title_label.pack(pady=(0, 20))
        
        # Current assignment info
        current_frame = ttk.LabelFrame(main_frame, text="Current Assignment", padding="10")
        current_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(current_frame, text=f"Current Invoice: {self.old_invoice_id}").pack(anchor=tk.W)
        ttk.Label(current_frame, text=f"Amount: ${self.amount:,.2f}").pack(anchor=tk.W)
        ttk.Label(current_frame, text=f"Date: {self.current_date}").pack(anchor=tk.W)
        
        # New assignment details
        new_frame = ttk.LabelFrame(main_frame, text="New Assignment", padding="10")
        new_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # Invoice selection
        ttk.Label(new_frame, text="Target Invoice:").pack(anchor=tk.W)
        self.invoice_var = tk.StringVar()
        invoice_combo = ttk.Combobox(new_frame, textvariable=self.invoice_var, 
                                   state="readonly", width=50)
        
        # Populate invoice dropdown (excluding current invoice)
        invoice_options = []
        for invoice in self.available_invoices:
            if invoice['id'] != self.old_invoice_id:  # Exclude current invoice
                # Use 'desc' field (handle both 'desc' and 'description' for compatibility)
                desc = invoice.get('desc', invoice.get('description', 'No Description'))
                option = f"{invoice['id']} - {desc} (${invoice['amount']:,.2f})"
                invoice_options.append(option)
        
        invoice_combo['values'] = invoice_options
        invoice_combo.pack(fill=tk.X, pady=(2, 10))
        
        # Assignment date
        ttk.Label(new_frame, text="Assignment Date (MM/DD/YYYY):").pack(anchor=tk.W)
        self.date_var = tk.StringVar(value=self.current_date)
        date_entry = ttk.Entry(new_frame, textvariable=self.date_var, width=20)
        date_entry.pack(anchor=tk.W, pady=(2, 10))
        
        # Notes
        ttk.Label(new_frame, text="Notes (optional):").pack(anchor=tk.W)
        self.notes_text = tk.Text(new_frame, height=4, width=50)
        self.notes_text.insert('1.0', self.current_notes)
        self.notes_text.pack(fill=tk.BOTH, expand=True, pady=(2, 0))
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        ttk.Button(button_frame, text="Reassign", command=self.ok_clicked, 
                  width=15).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Cancel", command=self.cancel_clicked, 
                  width=15).pack(side=tk.LEFT)
        
        # Bind keys
        self.window.bind('<Return>', lambda e: self.ok_clicked())
        self.window.bind('<Escape>', lambda e: self.cancel_clicked())
        
        # Ensure proper window sizing after all widgets are created
        ensure_window_visibility(self.window, self.parent.window, 600, 500)
    
    def ok_clicked(self):
        """Handle Reassign button click"""
        if not self.invoice_var.get():
            messagebox.showerror("Error", "Please select a target invoice")
            return
        
        if not self.date_var.get().strip():
            messagebox.showerror("Error", "Please enter an assignment date")
            return
        
        # Extract invoice ID from selection
        invoice_selection = self.invoice_var.get()
        new_invoice_id = invoice_selection.split(' - ')[0]
        
        # Confirm reassignment
        result = messagebox.askyesno("Confirm Reassignment", 
                                   f"Reassign ${self.amount:,.2f} from {self.old_invoice_id} to {new_invoice_id}?")
        
        if result:
            reassignment_data = {
                'old_invoice_id': self.old_invoice_id,
                'new_invoice_id': new_invoice_id,
                'amount': self.amount,
                'date': self.date_var.get().strip(),
                'notes': self.notes_text.get('1.0', 'end-1c').strip()
            }
            
            self.callback(reassignment_data)
            self.window.destroy()
    
    def cancel_clicked(self):
        """Handle Cancel button click"""
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