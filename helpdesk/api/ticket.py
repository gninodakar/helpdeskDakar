import frappe
from frappe import _

from helpdesk.utils import agent_only


def assign_ticket_to_agent(ticket_id, agent_id=None):
    if not ticket_id:
        return

    ticket_doc = frappe.get_doc("HD Ticket", ticket_id)

    if not agent_id:
        # assign to self
        agent_id = frappe.session.user

    if not frappe.db.exists("HD Agent", agent_id):
        frappe.throw(_("Tickets can only be assigned to agents"))

    ticket_doc.assign_agent(agent_id)
    return ticket_doc


@frappe.whitelist()
@agent_only
def bulk_assign_ticket_to_agent(ticket_ids, agent_id=None):
    if ticket_ids:
        ticket_docs = []
        for ticket_id in ticket_ids:
            ticket_doc = assign_ticket_to_agent(ticket_id, agent_id)
            ticket_docs.append(ticket_doc)
        return ticket_docs


@frappe.whitelist()
def get_unbilled_tickets():
    try:
        get_unbilled_tickets = frappe.db.sql("""
            SELECT 
                ht.name,
                ht.ticket_billed AS billed,
                ht.creation AS creation,
                ht.customer AS customer,
                ht.ticket_type AS ticket_type,            
                SEC_TO_TIME(COALESCE(SUM(TIME_TO_SEC(tse.tts_event_duration)), 0)) as time_expended,                                                
                ht.raised_by
                
            FROM 
                `tabHD Ticket` AS ht
            LEFT JOIN 
                `tabHD Ticket Time Sheet Events` tse ON ht.name = tse.tts_ticket_id
            WHERE 
                ht.ticket_billed = 0 
                AND ht.customer IS NOT NULL
                AND ht.raised_by IS NOT NULL
            GROUP BY 
                ht.name, ht.customer, ht.creation, ht.first_response_time, ht.raised_by
            ORDER BY 
                ht.creation DESC
        """, as_dict=True)
        return get_unbilled_tickets
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Failed to fetch unbilled tickets")
        return []


@frappe.whitelist()
def update_ticket_billing_status(ticket_name, billed_status):
    try:
        frappe.db.set_value("HD Ticket", ticket_name, "ticket_billed", int(billed_status))
        return {"status": "success", "message": "Ticket updated successfully"}
    except Exception as e:
        frappe.log_error(f"Error updating ticket {ticket_name}: {str(e)}")
        frappe.throw(f"Failed to update ticket: {str(e)}")


