import frappe 
from frappe import _
from frappe.utils.pdf import get_pdf 
from frappe.utils import now_datetime



TIME_SHEET_DOCTYPE = "HD Ticket Time Sheet Events"
HD_EVENTS_TYPE_DOCTYPE = "HD Events Type"

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
            HD_EVENTS_TYPE_DOCTYPE,
            filters={}, # filters here
            fields=["DISTINCT hd_event_ts_name as name"], 
        )        
        return [{'event_name': item.name, 'value': item.name} for item in event_names]
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Failed to fetch event type names")
        return [] 
    
##################################
# send ticket time sheet to pdf
##################################
@frappe.whitelist(allow_guest=False)
def send_report_pdf(ticket_id=None):  
    print(ticket_id)  
    recipients = ['guillermo@albanss.com']
    image_path = f"/assets/helpdesk/images/logo.png"              
    logo_url = f"http://127.0.0.1:8000{image_path}"

    tts = get_events(ticket_id)        
    ticket_subject = frappe.db.get_value("HD Ticket", ticket_id, "subject") 
    customer_name = frappe.db.get_value("HD Ticket", ticket_id, "customer")   

    context = {
        'logo_url': logo_url,
        'ticket_id': ticket_id,
        "ticket_subject" : ticket_subject,
        "customer_name": customer_name,
        "timesheet_entries": tts["events"],
        "total_time_spent": tts["total_time_spent"]
    }

    html_content = frappe.render_template('helpdesk/templates/pdf/ticket_time_sheet_report.html', context)
    
    message = """
    <p>Dear Customer,</p>
    <p>Attached is the report for your consideration.</p>        
    <p>Best regards,</p>        
    <p>
    <p>Dakar Software Team</p>
    """

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
            subject=f'Time Sheet Report Support Ticket {ticket_id}',
            message=message, 
            # template="This a demo email template",
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
# download pdf
##############################
@frappe.whitelist(allow_guest=False)
def download_report_pdf(ticket_id=None):    
    image_path = f"/assets/helpdesk/images/logo.png"              
    logo_url = f"http://127.0.0.1:8000{image_path}"    

    tts = get_events(ticket_id)        
    ticket_subject = frappe.db.get_value("HD Ticket", ticket_id, "subject") 
    customer_name = frappe.db.get_value("HD Ticket", ticket_id, "customer")   

    context = {
        'logo_url': logo_url,
        'ticket_id': ticket_id,
        "ticket_subject" : ticket_subject,
        "customer_name": customer_name,
        "timesheet_entries": tts["events"],
        "total_time_spent": tts["total_time_spent"]
    }

    html_content = frappe.render_template('helpdesk/templates/pdf/ticket_time_sheet_report.html', context)
                
    try:
        #Generate the PDF content as bytes
        pdf_bytes = get_pdf(html_content, options={
            'margin-top': '10mm',
            'margin-right': '10mm',
            'margin-bottom': '10mm',
            'margin-left': '10mm',
            'orientation': 'Portrait',
            'page-size': 'Letter',
        })

        #Set Frappe's response to send binary PDF data
        frappe.local.response.filename = f"reporte-{now_datetime().strftime('%Y-%m-%d')}.pdf"
        frappe.local.response.filecontent = pdf_bytes
        frappe.local.response.type = "download"
        
        return {"status": "success", "message": ("PDF generated and ready for download.")}

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Failed to generate PDF for download")
        frappe.throw(("Failed to generate PDF: {0}").format(str(e)))


##############################
# Fetch events by ticket ID
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
            TIME_SHEET_DOCTYPE,
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
            order_by="name asc" 
        )
        # calculate time spended
        total_time_spent = frappe.db.sql("""
            SELECT SUBSTRING_INDEX(
                SEC_TO_TIME(SUM(TIME_TO_SEC(tts_event_duration))),
                ':', 2
            ) FROM `tab%s`
            WHERE tts_ticket_id = %s
        """ % (TIME_SHEET_DOCTYPE, "%s"), ticket_id)[0][0] or "00:00"
        

        if not events_list:
            print("No events found for this ticket ID.")        
        formatted_events  = [{
            "tts_id": item.name,
            "tts_agent": item.tts_agent,
            "tts_ticket_id": item.tts_ticket_id,
            "tts_event_type": item.tts_event_type,
            "tts_event_duration": item.tts_event_duration,    
            "tts_event_date": item.tts_event_date  if hasattr(item, 'entry_date') else None,
            "tts_event_description": item.tts_event_description 
            
        } for item in events_list]

                        
        return {
            "events": formatted_events,
            "total_time_spent": total_time_spent
        }

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Failed to fetch events from HD Time Sheet Events")
        return []
    

##############################
# Add new events
##############################
@frappe.whitelist(allow_guest=False) 
def add_time_sheet_entry(ticket_id=None, event_type_name=None, duration=None, date=None, description=None):             
    if not all([ticket_id, event_type_name, duration, date,description]):
        frappe.throw("Ticket ID, Event Type, Duration, and Date are required.")    

    try:
        current_user = frappe.session.user
        user_doc = frappe.get_doc("User", current_user)
        full_name = user_doc.full_name


        print(current_user)
        doc = frappe.new_doc(TIME_SHEET_DOCTYPE)
        doc.tts_agent = full_name
        doc.tts_ticket_id = ticket_id
        doc.tts_event_type = event_type_name 
        doc.tts_event_duration = duration
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
def delete_time_sheet_entry(tts_id):
    print(tts_id)
    # return "ok"
    if not tts_id:
        frappe.throw("Entry ID is required to delete a time sheet record.")

    try:
        if not frappe.db.exists(TIME_SHEET_DOCTYPE, tts_id):
            frappe.throw(f"Time Sheet Entry with ID '{tts_id}' not found.")
        
        frappe.delete_doc(TIME_SHEET_DOCTYPE, tts_id)
        frappe.db.commit()

        frappe.msgprint(f"Time Sheet Entry '{tts_id}' deleted successfully!")
        return {"message": "Time Sheet Entry deleted successfully!", "deleted_id": tts_id}

    except frappe.DoesNotExistError:        
        frappe.log_error(f"Attempted to delete non-existent Time Sheet Entry: {tts_id}", "Delete Time Sheet Entry Error")
        frappe.throw(f"Time Sheet Entry with ID '{tts_id}' not found or already deleted.")
    except Exception as e:
        frappe.db.rollback() # Rollback in case of partial deletion or other issues
        frappe.log_error(frappe.get_traceback(), f"Failed to delete time sheet entry: {tts_id}")
        frappe.throw(f"Failed to delete time sheet entry: {e}")


        