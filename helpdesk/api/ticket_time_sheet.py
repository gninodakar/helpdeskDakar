import frappe 
from frappe import _
from frappe.utils.pdf import get_pdf 
from frappe.utils import now_datetime, get_url



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
    
##############################
# send ticket by pdf
##############################
@frappe.whitelist(allow_guest=False)
def send_report_pdf(ticket_id=None):  
    print(ticket_id)  
    recipients = ['guillermo@albanss.com']    
    product_data = {
        'Samsung Galaxy S20': 10,
        'iPhone 13': 80
    }

    # Generate PDF HTML content
    html_content = """"
    
    """
    # html_content += '<ol>'
    # # Loop correctly over the dictionary items
    # for item, qty in product_data.items():
    #     html_content += f'<li>{frappe.utils.escape_html(item)} - {qty}</li>' # Escape HTML for safety
    # html_content += '</ol>'

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
# download pdf
##############################
@frappe.whitelist(allow_guest=False)
def download_report_pdf(ticket_id=None):    
    image_path = f"/assets/helpdesk/images/logo.png"              
    logo_url = f"http://127.0.0.1:8000{image_path}"
    html_content = frappe.render_template('helpdesk/templates/pdf/ticket_time_sheet_report.html')
        
    html_content2 = f"""    
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>Report</title>
        <style>
      body {{
        font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
        margin: 0;
        padding: 0;
        background-color: white;
        position: relative;
      }}
      

      /* Letter size simulation */
      .letter-container {{        
        width: 100%;
        height: 1220PX; 
        margin: 0 auto;        
        box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
        position: relative;        
        box-sizing: border-box;
        display: flex;                 
        flex-direction: column;
      }}

      /* Header styles */
      .header {{
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        margin-bottom: 20px;
      }}

      .logo {{
        width: 250px;
        margin-bottom: 20px;
      }}

      .address {{
        text-align: right;
        font-size: 12px;
        line-height: 1.3;
      }}

      /* Main content styles */
      h1 {{
        color: #0a0a0a;
        margin-top: 0;
        font-size: 16px;
      }}

      h2 {{
        color: #5b72a0;
        margin-top: 10px;
        font-size: 25px;
      }}

      p {{
        font-size: 12px;
        margin: 5px 0;
      }}

      /* Modern table styles with rounded corners */
      table {{
        width: 100%;
        border-collapse: separate;
        border-spacing: 1;
        margin: 15px 0;
        font-size: 11px;
        border-radius: 5px;
        overflow: hidden;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
      }}

      th {{
        background: rgb(195, 200, 204);
        color: rgb(26, 25, 25);
        padding: 12px 8px;
        text-align: left;
        font-weight: 600;
        font-size: 11px;
      }}

      td {{
        padding: 10px 8px;
        border-bottom: 1px solid #c2bcbc;
        text-align: left;
      }}

      tr:last-child td {{
        border-bottom: none;
      }}

      tr:nth-child(even) {{
        background-color: #f8f9fa;
      }}

      tr:hover {{
        background-color: #e3f2fd;
        transition: background-color 0.2s ease;
      }}

      /* Rounded corners for table */
      th:first-child {{
        border-top-left-radius: 5px;
      }}

      th:last-child {{
        border-top-right-radius: 5px;
      }}

      tr:last-child td:first-child {{
        border-bottom-left-radius: 5px;
      }}

      tr:last-child td:last-child {{
        border-bottom-right-radius: 5px;
      }}

      /* Two-column footer styles */
      .footer-container {{
        width: 100%;
        position: absolute;
        bottom: 0in;        
        border-top: 1px solid #a9aeb4;
        padding-top: 8px;
        font-size: 11px;
        color: #626568;
      }}

      .footer-columns {{
        display: flex;
        justify-content: space-between;
      }}

      .footer-column {{
        flex: 1;
      }}

      .footer-column:first-child {{
        text-align: left;
      }}

      .footer-column:last-child {{
        text-align: right;
      }}

      .footer-item {{
        margin: 2px 0;
      }}

      /* Watermark styles */
      .watermark {{
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        z-index: -1; /* Behind content */
        pointer-events: none; /* Doesn't interfere with clicks */
        background-image: url("{logo_url}");
        background-repeat: no-repeat;
        background-position: center;
        background-size: 600px auto;
        opacity: 0.1; /* Make it subtle but visible */
      }}

      /* Ensure content doesn't overlap with footer */
      .content {{
        margin-bottom: 50px;
      }}    
        </style>
    </head>
     <body>
    <div class="letter-container">
      <!-- Watermark -->
      <div class="watermark"></div>

      <!-- Header -->
      <div class="header">
        <img
          src="{logo_url}"
          alt="Dakar Logo"
          class="logo"
        />
        <div class="address">
          Dakar Software Systems<br />
          Level 4 Dakar Buildings<br />
          Triq Henry Calleja<br />
          San Giljan STJ 1390<br />
          Malta
        </div>
      </div>

      <!-- Main Content -->
      <div class="content">
        <h1>Ticket:[ 0602 ] Dakar employee list - CMD</h1>
        <h2>Timesheets</h2>

        <p>
          <strong>CUSTOMER:</strong> Cleansing & Maintenance Division, Patrick
          Briffa
        </p>

        <table>
          <thead>
            <tr>
              <th>DATE</th>
              <th>EMPLOYEE</th>
              <th>TYPE OF EVENT</th>
              <th>DESCRIPTION</th>
              <th>TIME SPENT</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>21/04/2025</td>
              <td>Miguel Fenech</td>
              <td>Meeting</td>
              <td>Deletion of selective employees. Analysis & Selection.</td>
              <td>01:00</td>
            </tr>
            <tr>
              <td>21/04/2025</td>
              <td>Eugene Debono</td>
              <td>Meeting</td>
              <td>Assisting with employee removal</td>
              <td>03:00</td>
            </tr>
            <tr>
              <td>21/04/2025</td>
              <td>Eugene Debono</td>
              <td>Meeting</td>
              <td>Investigated issue and communicated with client</td>
              <td>01:30</td>
            </tr>
            <tr>
                        <tr>
              <td>21/04/2025</td>
              <td>Eugene Debono</td>
              <td>Meeting</td>
              <td>Investigated issue and communicated with client</td>
              <td>01:30</td>
            </tr>
            <tr>
              <td colspan="4" style="text-align: right">
                <strong>Total (Hours)</strong>
              </td>
              <td><strong>05:30</strong></td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Two-column Footer -->
      <div class="footer-container">
        <div class="footer-columns">
          <div class="footer-column">
            <p class="footer-item"><strong>CONTACT INFORMATION:</strong></p>
            <p class="footer-item">Telephone: +356 2137 4078</p>
            <p class="footer-item">Email: support@dakarsoftware.com</p>
            <p class="footer-item">Website: http://dakarsoftware.com</p>
          </div>
          <div class="footer-column">
            <p class="footer-item"><strong>COMPANY DETAILS:</strong></p>
            <p class="footer-item">Vat number: MT10102012</p>
            <p class="footer-item">Page 1 / 1</p>
          </div>
        </div>
      </div>
    </div>
  </body>
    </html>
    """
    
    try:
        # 2. Generate the PDF content as bytes
        pdf_bytes = get_pdf(html_content, options={
            'margin-top': '10mm',
            'margin-right': '10mm',
            'margin-bottom': '10mm',
            'margin-left': '10mm',
            'orientation': 'Portrait',
            'page-size': 'Letter',
        })

        # 3. Set Frappe's response to send binary PDF data
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

        print(formatted_events)
        print(total_time_spent)
                
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
    print(f"******************{duration}********************")    
    if not all([ticket_id, event_type_name, duration, date,description]):
        frappe.throw("Ticket ID, Event Type, Duration, and Date are required.")

    # if not isinstance(duration, (int, float)) or duration <= 0:
    #     frappe.throw("Duration must be a positive number.")

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


        