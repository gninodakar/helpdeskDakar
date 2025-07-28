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
    try:
        events_list = frappe.db.get_list(
            "HD Time Sheet Events", 
            filters={},            
            fields=[
                "name",                  
                "ts_event_code",         
                "ts_event_type", 
                "ts_event_date",                    
                "ts_event_duration",                     
                "ts_event_description",                
                "ts_agent",                              
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