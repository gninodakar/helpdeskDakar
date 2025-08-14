import LucideBookOpen from "~icons/lucide/book-open";
import LucideCloudLightning from "~icons/lucide/cloud-lightning";
import LucideContact2 from "~icons/lucide/contact-2";
import LucideTicket from "~icons/lucide/ticket";
import TicketPercent from "~icons/lucide/ticket-percent";
import Unbilled from "~icons/lucide/receipt-euro";
import Remove from "~icons/lucide/ticket-x";

import { OrganizationsIcon } from "../icons";

export const agentPortalSidebarOptions = [
  {
    label: "Tickets Summary",
    icon: TicketPercent,
    to: "TicketNewView",
  },
  {
    label: "Tickets List",
    icon: LucideTicket,
    to: "TicketsAgent",
  },
  {
    label: "Unbilled Tickets",
    icon: Unbilled,
    to: "UnbilledTickets",
  },
  {
    label: "Knowledge Base",
    icon: LucideBookOpen,
    to: "AgentKnowledgeBase",
  },
  {
    label: "Message Templates",
    icon: LucideCloudLightning,
    to: "CannedResponses",
  },
  {
    label: "Customers",
    icon: OrganizationsIcon,
    to: "CustomerList",
  },
  {
    label: "Contacts",
    icon: LucideContact2,
    to: "ContactList",
  },

  //old list view
  {
    label: "Old View Tickets",
    // icon: LucideTicket,
    icon: Remove,
    to: "TicketsAgentOld",
  },
];

export const customerPortalSidebarOptions = [
  {
    label: "Tickets",
    icon: LucideTicket,
    to: "TicketsCustomer",
  },
  {
    label: "Knowledge Base",
    icon: LucideBookOpen,
    to: "CustomerKnowledgeBase",
  },
];
