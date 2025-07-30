import frappe 
from frappe import _
from frappe.utils.pdf import get_pdf 

##############################
# Fetch event types selectbox
##############################
@frappe.whitelist(allow_guest=False) 
def get_event_type_names():    
    """
    Retrieves all distinct hd_event_ts_name values from the HD Event Time Sheet DocType.
    This is used to populate the event type dropdown.
    """
    try:        
        event_names = frappe.db.get_list(
            "HD Events Type",
            filters={}, # filters here
            fields=["DISTINCT hd_event_ts_name as name"], 
        )        
        return [{'event_name': item.name, 'value': item.name} for item in event_names]
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Failed to fetch event type names")
        return [] 
    
##############################
# send ticket by pdf
##############################
@frappe.whitelist(allow_guest=False)
def send_report_pdf():    
    recipients = ['guillermo@albanss.com']    
    product_data = {
        'Samsung Galaxy S20': 10,
        'iPhone 13': 80
    }

    # Generate PDF HTML content
    html_content = '<h1>Invoice from Star Electronics e-Store!</h1>'
    html_content += '<ol>'
    # Loop correctly over the dictionary items
    for item, qty in product_data.items():
        html_content += f'<li>{frappe.utils.escape_html(item)} - {qty}</li>' # Escape HTML for safety
    html_content += '</ol>'

    # Generate PDF
    pdf_bytes = get_pdf(html_content, options={
        'margin-top': 10,
        'margin-right': 10,
        'margin-bottom': 10,
        'margin-left': 10,
        'orientation': 'Portrait',
        'page-size': 'Letter',
    })

    # Send email
    try:
        frappe.sendmail(
            recipients=recipients,
            subject='Invoice from Star Electronics e-Store',
            message=html_content, 
            attachments=[{
                'fname': 'invoice.pdf',
                'fcontent': pdf_bytes
            }],            
            now = True
        )
        frappe.db.commit() 

        frappe.msgprint(("Email sent successfully to {0}").format(", ".join(recipients)))
        return {"status": "success", "message": ("Email sent successfully!")}

    except Exception as e:
        frappe.db.rollback() 
        frappe.log_error(frappe.get_traceback(), "Failed to send report PDF")
        frappe.throw(("Failed to send email: {0}").format(str(e)))
       
##############################
# Fetch events storeged
##############################
@frappe.whitelist(allow_guest=False) 
def get_events(ticket_id=None):
    # print(ticket_id)
    """
    ttt prefix = ticket time sheet
    """
    try:
        if not ticket_id:
            frappe.throw("Ticket ID is required to fetch time sheet events.")
        events_list = frappe.db.get_list(
            "HD Ticket Time Sheet Events",
            filters={
                "tts_ticket_id": ticket_id
            }, 
            fields=[
                "name",                  
                "tts_agent",         
                "tts_ticket_id",                 
                "tts_event_type",
                "tts_event_duration",
                "tts_event_type",             
                "tts_event_date",                
                "tts_event_description",                              
            ],
            order_by="ts_event_code asc" 
        )
        return [{
            "tts_id": item.name,
            "tts_agent": item.tts_agent,
            "tts_ticket_id": item.tts_ticket_id,
            "tts_event_type": item.tts_event_type,
            "tts_event_duration": item.tts_event_duration,    
            "tts_event_date": item.tts_event_date  if hasattr(item, 'entry_date') else None,
            "tts_event_description": item.tts_event_description 
            
        } for item in events_list]

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Failed to fetch events from HD Time Sheet Events")
        return []
    

##############################
# Add new events
##############################
@frappe.whitelist(allow_guest=False) 
def add_time_sheet_entry(ticket_id=None, event_type_name=None, duration=None, date=None, description=None):  
    print(ticket_id, event_type_name, duration, date,description)      
    if not all([ticket_id, event_type_name, duration, date,description]):
        frappe.throw("Ticket ID, Event Type, Duration, and Date are required.")

    if not isinstance(duration, (int, float)) or duration <= 0:
        frappe.throw("Duration must be a positive number.")

    try:
        current_user = frappe.session.user
        user_doc = frappe.get_doc("User", current_user)
        full_name = user_doc.full_name


        print(current_user)
        doc = frappe.new_doc("HD Ticket Time Sheet Events")
        doc.tts_agent = full_name
        doc.tts_ticket_id = ticket_id
        doc.tts_event_type = event_type_name 
        doc.tts_event_duration = float(duration)
        doc.tts_event_date = date
        doc.tts_event_description = description    
        doc.insert()
        frappe.db.commit()

        frappe.msgprint("Time Sheet entry added successfully!")
        return {"message": "Time Sheet entry added successfully!", "name": doc.name}
    
    except Exception as e:
        frappe.db.rollback()
        frappe.log_error(frappe.get_traceback(), "Failed to add time sheet entry")
        frappe.throw(f"Failed to add time sheet entry: {e}")

##############################
# Delete event
##############################
@frappe.whitelist(allow_guest=False)
def delete_time_sheet_entry(entry_id):
    print(entry_id)
    # return "ok"
    if not entry_id:
        frappe.throw("Entry ID is required to delete a time sheet record.")

    try:
        # Check if the document exists before attempting to delete
        if not frappe.db.exists("HD Ticket Time Sheet Events", entry_id):
            frappe.throw(f"Time Sheet Entry with ID '{entry_id}' not found.")

        # Delete the document
        frappe.delete_doc("HD Ticket Time Sheet Events", entry_id)
        frappe.db.commit()

        frappe.msgprint(f"Time Sheet Entry '{entry_id}' deleted successfully!")
        return {"message": "Time Sheet Entry deleted successfully!", "deleted_id": entry_id}

    except frappe.DoesNotExistError:
        # This can be caught if frappe.delete_doc tries to delete a non-existent doc,
        # though the frappe.db.exists check above should prevent it.
        frappe.log_error(f"Attempted to delete non-existent Time Sheet Entry: {entry_id}", "Delete Time Sheet Entry Error")
        frappe.throw(f"Time Sheet Entry with ID '{entry_id}' not found or already deleted.")
    except Exception as e:
        frappe.db.rollback() # Rollback in case of partial deletion or other issues
        frappe.log_error(frappe.get_traceback(), f"Failed to delete time sheet entry: {entry_id}")
        frappe.throw(f"Failed to delete time sheet entry: {e}")


        