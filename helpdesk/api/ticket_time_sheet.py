import frappe

@frappe.whitelist(allow_guest=True) 
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
    

@frappe.whitelist(allow_guest=True) 
def get_events(ticket_id=None):
    # print(ticket_id)
    try:
        if not ticket_id:
            frappe.throw("Ticket ID is required to fetch time sheet events.")
        events_list = frappe.db.get_list(
            "HD Ticket Time Sheet Events",
            filters={
                "ts_ticket_id": ticket_id
            }, 
            fields=[
                "tts_id",                  
                "tts_agent",         
                "tts_ticket_id",                 
                "tts_event_type",
                "ts_event_duration",
                "tts_event_type",
                "tts_event_duration",                     
                "tts_event_date",                
                "tts_event_description",                              
            ],
            order_by="ts_event_code asc" 
        )
        return [{
            'event_code': item.ts_event_code,
            'event_type': item.ts_event_type,
            'event_duration': item.ts_event_duration,
            'event_date': item.ts_event_date if hasattr(item, 'entry_date') else None, 
            'event_description': item.ts_event_description,
            'event_agent': item.ts_agent,
            'name': item.name 
        } for item in events_list]

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Failed to fetch events from HD Time Sheet Events")
        return []
    

@frappe.whitelist(allow_guest=False) 
def add_time_sheet_entry(ticket_id=None, event_type_name=None, duration=None, date=None, description=None):
    print(ticket_id, event_type_name, duration, date, description)
    return "ok"
    # if not all([ticket_id, event_type_name, duration, date]):
    #     frappe.throw("Ticket ID, Event Type, Duration, and Date are required.")

    # if not isinstance(duration, (int, float)) or duration <= 0:
    #     frappe.throw("Duration must be a positive number.")

    # try:
    #     current_user = frappe.session.user

    #     doc = frappe.new_doc("HD Time Sheet Events")

    #     doc.ts_ticket_id = ticket_id
    #     doc.ts_event_type = event_type_name # Assign the NAME of the linked document
    #     doc.ts_event_duration = float(duration)
    #     # doc.ts_event_date = date
    #     doc.ts_event_description = description
    #     doc.ts_agent = current_user
    #     doc.ts_ticket_name = ticket_name

    #     # For ts_event_code, consider if it's auto-generated in your DocType
    #     # If not, ensure it's unique.
    #     # Example if you need to generate a unique code:
    #     doc.ts_event_code = f"{ticket_id}-{event_type_name}-{frappe.utils.now_datetime().strftime('%Y%m%d%H%M%S')}"

    #     doc.insert()
    #     frappe.db.commit()

    #     frappe.msgprint("Time Sheet entry added successfully!")
    #     return {"message": "Time Sheet entry added successfully!", "name": doc.name}

    # except Exception as e:
    #     frappe.db.rollback()
    #     frappe.log_error(frappe.get_traceback(), "Failed to add time sheet entry")
    #     frappe.throw(f"Failed to add time sheet entry: {e}")

        