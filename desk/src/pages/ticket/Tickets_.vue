<template>
  <div class="time-sheet-form p-4 border rounded-md bg-white shadow-sm">
    <div class="flex flex-col sm:flex-row justify-start mb-4 gap-2">
      <button
        class="rounded bg-teal-500 px-3 py-1.5 text-base font-medium text-white hover:bg-teal-600 focus:outline-none focus:ring-2 focus:ring-teal-500 focus:ring-offset-2"
        @click="sendmailpdf" title="Email Ticket as PDF">
        Email Time Sheet
      </button>
      <button
        class="rounded bg-amber-600 px-3 py-1.5 text-base font-medium text-white hover:bg-amber-700 focus:outline-none focus:ring-2 focus:ring-amber-600 focus:ring-offset-2"
        @click="downloadPdfDirect" title="Download Report">
        Download Time Sheet
      </button>
    </div>

    <div v-if="tickets.length" class="mt-8">
      <h4 class="text-md font-semibold mb-3 text-gray-800">
        Current Time Sheet Entries
      </h4>
      <div class="overflow-x-auto border border-gray-200 rounded-md">
        <table class="table-auto w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <!-- checkbox header -->
              <th class="px-4 py-2">
                <input type="checkbox" v-model="allSelected"
                  class="h-4 w-4 text-teal-600 border-gray-300 rounded focus:ring-teal-500" />
              </th>
              <!-- dynamic data headers -->
              <th v-for="col in ticketColumns" :key="col.key as string" scope="col" :class="col.thClass">
                {{ col.label }}
              </th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-for="ticket in tickets" :key="ticket.name" class="hover:bg-gray-50">
              <!-- checkbox -->
              <td class="px-4 py-2">
                <input type="checkbox" :checked="selectedTickets.includes(ticket.name)"
                  @change="toggleSelection(ticket.name)"
                  class="h-4 w-4 text-teal-600 border-gray-300 rounded focus:ring-teal-500" />
              </td>
              <!-- dynamic data cells -->
              <td v-for="col in ticketColumns" :key="col.key as string" :class="col.tdClass">
                <!-- Soporta cell custom o valor directo -->
                <span v-if="col.cell">{{ col.cell(ticket) }}</span>
                <span v-else>{{ ticket[col.key] }}</span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <div v-else class="mt-8 p-4 text-center text-gray-500 border border-dashed rounded-md">
      No time sheet entries added yet.
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from "vue";
import { toast, createResource } from "frappe-ui";

/* ========= Interfaces ========= */
interface Ticket {
  name: string;
  creation: string;
  resolution: string;
  status: string;
  subject: string;
  assigned_to: string;
  sla_status: string;
  customer: string;
  priority: string;
  contact: string;
  ticket_type: string;
  raised_by: string;
}

type Column<T> = {
  label: string;
  key: keyof T;
  thClass?: string;
  tdClass?: string;
  cell?: (row: T) => any; // opcional para celdas custom
};

interface TicketsParams {
  user?: string;
  company?: string;
}

interface TicketsResponse {
  message?: any[];
  tickets?: any[];
}

const selectedTickets = ref<string[]>([]);
const allSelected = computed({
  get: () => tickets.value.length > 0 && selectedTickets.value.length === tickets.value.length,
  set: (value: boolean) => {
    selectedTickets.value = value ? tickets.value.map(t => t.name) : [];
  }
});


function toggleSelection(id: string) {
  if (selectedTickets.value.includes(id)) {
    selectedTickets.value = selectedTickets.value.filter(item => item !== id);
  } else {
    selectedTickets.value.push(id);
  }
}

/* ======= Columnas ========= */
const thclass =
  "px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider";
const tdClass =
  "px-2 py-1 whitespace-nowrap text-sm font-medium text-gray-900";

const ticketColumns: Column<Ticket>[] = [
  { label: "ID", key: "name", thClass: thclass, tdClass: tdClass },
  { label: "Created", key: "creation", thClass: thclass, tdClass: tdClass },
  { label: "Resolution", key: "resolution", thClass: thclass, tdClass: tdClass },
  { label: "Status", key: "status", thClass: thclass, tdClass: tdClass },
  { label: "Subject", key: "subject", thClass: thclass, tdClass: tdClass + " truncate max-w-[200px]" },
  { label: "Assigned To", key: "assigned_to", thClass: thclass, tdClass: tdClass },
  { label: "SLA Status", key: "sla_status", thClass: thclass, tdClass: tdClass },
  { label: "Customer", key: "customer", thClass: thclass, tdClass: tdClass },
  { label: "Priority", key: "priority", thClass: thclass, tdClass: tdClass },
  { label: "Contact", key: "contact", thClass: thclass, tdClass: tdClass },
  { label: "Ticket Type", key: "ticket_type", thClass: thclass, tdClass: tdClass },
  { label: "Raised By", key: "raised_by", thClass: thclass, tdClass: tdClass + " truncate max-w-[200px]" },
];

/* ======= Mapper ========= */
function mapToTicket(item: any): Ticket {
  return {
    name: item.name,
    creation: item.creation ? String(item.creation).split(" ")[0] : "",
    resolution: item.resolution ? String(item.resolution).split(" ")[0] : "",
    status: item.status || "",
    subject: item.subject || "",
    assigned_to: item.assigned_to || "",
    sla_status: item.sla_status || "",
    customer: item.customer || "",
    priority: item.priority || "",
    contact: item.contact || "",
    ticket_type: item.ticket_type || "",
    raised_by: item.raised_by || "",
  };
}

/* ======= Estado ========= */
const tickets = ref<Ticket[]>([]);
const dummyTickets: Ticket[] = [];

/* ======= Resource ========= */
const fetchTickets = createResource({
  url: "helpdesk.api.ticket.get_tickets_list",
  auto: true,
  makeParams: (): TicketsParams => ({
    user: "",
    company: "",
  }),
  onSuccess: (data: TicketsResponse) => {
    const items = Array.isArray(data?.tickets)
      ? data.tickets!
      : Array.isArray(data?.message)
        ? data.message!
        : [];

    tickets.value = items.length ? items.map(mapToTicket) : dummyTickets;
  },
  onError: (error: any) => {
    console.error("Failed to fetch time sheet entries from API.", error);
    toast.error(
      "Failed to fetch time sheet entries: " +
      (error?.messages ? error.messages.join(", ") : error?.message || "Unknown error")
    );
    tickets.value = dummyTickets;
  },
});

/* Opcional: funciones de los botones */
function sendmailpdf() { /* ... */ }
function downloadPdfDirect() { /* ... */ }
</script>


<!-- ************************* 
 styles 
<!-- ************************ -->
<style scoped>
/* Basic styling for the form elements */
label {
  display: block;
  margin-bottom: 0.25rem;
}

input[type="text"],
input[type="number"],
input[type="date"],
select {
  padding: 0.5rem 0.75rem;
  border-width: 1px;
  border-color: #d1d5db;
  border-radius: 0.375rem;
  box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
  width: 100%;
}

input:focus,
select:focus,
textarea:focus {
  outline: none;
  ring-width: 2px;
  ring-color: #3b82f6;
  border-color: #3b82f6;
}

/* Table specific styling - Tailwind classes are quite verbose, but effective */
table {
  width: 100%;
  border-collapse: collapse;
}

th,
/* td {
  padding: 0.5rem 1.5rem;
  text-align: left;
} */

thead th {
  background-color: #f3f3f3;
  border-bottom-width: 1px;
  border-color: #e5e7eb;
  color: #272727;
  /* font-size: 0.75rem; */
  /* font-weight: 500; */
  /* color: #6b7280; */
  text-transform: uppercase;
  /* letter-spacing: 0.05em; */
}

tbody td {
  border-bottom-width: 1px;
  border-color: #e5e7eb;
}

tbody tr:last-child td {
  border-bottom: none;
}
</style>
