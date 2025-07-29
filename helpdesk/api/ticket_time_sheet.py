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
# @frappe.whitelist(allow_guest = False)
# def send_report_pdf(ticket_id):
#     print(ticket_id)
@frappe.whitelist(allow_guest=False)
def send_report_pdf(
    recipients,
    pdf_title="Documento Personalizado",
    pdf_text_content="No se ha proporcionado contenido.",
    email_subject=None,
    email_message=None,
    sender_email_address=None, # <--- CAMBIADO: Ahora se espera la DIRECCIÓN de correo del remitente
):
    """
    Genera un PDF con contenido de texto personalizado y lo envía como un adjunto de correo electrónico.

    :param recipients: Dirección(es) de correo electrónico a las que se enviará el PDF (cadena separada por comas o lista).
    :param pdf_title: Título que aparecerá en la parte superior del PDF y como nombre de archivo.
    :param pdf_text_content: El contenido de texto principal que se colocará dentro del PDF.
    :param email_subject: Asunto personalizado del correo electrónico. Si es None, se genera uno por defecto.
    :param email_message: Cuerpo del mensaje del correo electrónico (puede ser HTML). Si es None, se genera uno por defecto.
    :param sender_email_address: La dirección de correo electrónico exacta (Email Id) de la "Cuenta de Correo" configurada en Frappe a usar como remitente.
                                 Si es None, Frappe utilizará la cuenta de correo saliente predeterminada.
    """
    if not recipients:
        frappe.throw(_("Se requieren destinatarios para enviar el correo electrónico."))
    if not pdf_title:
        frappe.throw(_("Se requiere el título del PDF."))

    try:
        # Asegurarse de que recipients sea una lista
        if isinstance(recipients, str):
            recipients = [r.strip() for r in recipients.split(",") if r.strip()]

        # Preparar asunto y mensaje predeterminados si no se proporcionan
        if not email_subject:
            email_subject = _("Tu Documento Personalizado: {0}").format(pdf_title)
        if not email_message:
            email_message = _(
                """Estimado(a) destinatario(a),

                Adjunto encontrarás el documento PDF personalizado que solicitaste: "{0}".

                Saludos cordiales,
                {1}"""
            ).format(pdf_title, frappe.session.user)

        # 1. Crear contenido HTML para el PDF
        pdf_html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>{pdf_title}</title>
            <style>
                body {{ font-family: sans-serif; margin: 40px; }}
                h1 {{ color: #333; font-size: 24px; margin-bottom: 20px; }}
                pre {{ white-space: pre-wrap; word-wrap: break-word; font-family: monospace; background-color: #f8f8f8; border: 1px solid #ddd; padding: 15px; border-radius: 5px; }}
                p {{ line-height: 1.6; }}
            </style>
        </head>
        <body>
            <h1>{pdf_title}</h1>
            <pre>{frappe.utils.escape_html(pdf_text_content)}</pre>
            <p>Generado el {frappe.utils.formatdate(frappe.utils.nowdate())} por {frappe.session.user}</p>
        </body>
        </html>
        """

        # 2. Generar los bytes del PDF a partir del contenido HTML
        actual_file_name = f"{pdf_title.replace(' ', '_').replace('/', '-')}.pdf"
        pdf_bytes = get_pdf(pdf_html_content)

        # 3. Preparar el diccionario del adjunto
        attachment = {
            "fname": actual_file_name,
            "fcontent": pdf_bytes,
            "is_private": 0
        }

        # --- CAMBIO CLAVE: Usar frappe.sendmail() con el parámetro 'sender' ---
        frappe.sendmail(
            recipients=recipients,
            sender=sender_email_address, # <--- Usar la dirección de correo del remitente aquí
            subject=email_subject,
            message=email_message,
            attachments=[attachment],
            # Puedes añadir reference_doctype y reference_name si quieres que el email
            # aparezca en la línea de tiempo de un documento específico (ej. un ticket)
            # reference_doctype="HD Ticket",
            # reference_name="TICKET-001"
        )
        # --- FIN CAMBIO CLAVE ---

        frappe.msgprint(_("Correo electrónico con PDF personalizado enviado exitosamente a {0}").format(", ".join(recipients)))
        return {"status": "success", "message": _("¡Correo enviado exitosamente!")}

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), _("Error al enviar correo electrónico con PDF personalizado."))
        frappe.throw(_("Error al enviar correo: {0}").format(str(e)))
    
 
    
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
            "tts_event_type": item.tts_event_type,            
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


        