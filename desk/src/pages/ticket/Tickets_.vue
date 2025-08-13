<template>
  <LayoutHeader>
    <template #left-header>
      <ViewBreadcrumbs label="Tickets Temp View"
        :route-name="isCustomerPortal ? 'TicketsCustomer' : 'TicketsAgentTemp'" />
    </template>
    <template #right-header>
      <RouterLink :to="{ name: isCustomerPortal ? 'TicketNew' : 'TicketAgentNew' }">
        <Button label="Create" theme="gray" variant="solid">
          <template #prefix>
            <LucidePlus class="h-4 w-4" />
          </template>
        </Button>
      </RouterLink>
    </template>
  </LayoutHeader>

  <div class="p-2 ">
    <!-- filter -->
    <div class="flex flex-col sm:flex-row justify-start mb-4 gap-2">
      <!-- id -->
      <div class="flex flex-col">
        <label class="text-sm text-gray-600 mb-1">ID</label>
        <Input v-model="filters.id" placeholder="Ticket ID" class="w-64" @keyup.enter="fetchTickets.reload()" />
      </div>
      <!-- customer -->
      <div class="flex flex-col">
        <label class="text-sm text-gray-600 mb-1">Customer</label>
        <Input v-model="filters.customer" placeholder="Custumer Name" class="w-64"
          @keyup.enter="fetchTickets.reload()" />
      </div>
      <!-- agent -->
      <div class="flex flex-col">
        <label class="text-sm text-gray-600 mb-1">Agent</label>
        <Input v-model="filters.agent" placeholder="Agent Name" class="w-64" @keyup.enter="fetchTickets.reload()" />
      </div>
      <!-- status  -->
      <div class="flex flex-col">
        <label class="text-sm text-gray-600 mb-1">Status</label>
        <Input v-model="filters.status" placeholder="Status" class="w-64" @keyup.enter="fetchTickets.reload()" />
      </div>
      <!-- Action Buttons -->
      <div class="flex items-end gap-2">
        <Button @click="fetchTickets.reload()" variant="solid">Apply Filters</Button>
        <Button @click="clearFilters" variant="outline">Clear Filters</Button>
      </div>

      <!-- Right-aligned refresh button -->
      <div class="ml-auto">
        <Button variant="ghost" @click="fetchTickets.reload()">
          <FeatherIcon name="refresh-ccw" class="h-5 w-5" />
        </Button>
      </div>
    </div>


    <!-- table -->
    <div v-if="tickets.length" class="mt-8">
      <p class="text-sm text-gray-700 mb-2">Total Tickets Found: {{ tickets.length }}</p>
      <div class="overflow-x-auto border border-gray-200 rounded-md">
        <div class="max-h-[calc(100vh-170px)] overflow-y-auto">
          <table class="min-w-full table-auto divide-y divide-gray-200">
            <thead class="bg-gray-50">
              <tr>
                <!-- checkbox header -->
                <th class="sticky top-0 z-10 px-4 py-2 text-center align-middle w-10 bg-gray-50">
                  <input type="checkbox" v-model="allSelected"
                    class="h-4 w-4 text-teal-600 border-gray-300 rounded focus:ring-teal-500" />
                </th>
                <!-- dynamic data headers -->
                <th v-for="col in ticketColumns" :key="col.key as string" scope="col" :class="[
                  col.thClass,
                  'sticky top-0 z-10 bg-gray-50'
                ]">
                  {{ col.label }}
                </th>
              </tr>
            </thead>

            <tbody class="bg-white divide-y divide-gray-200">
              <!-- dynamic ticket rows -->
              <tr v-for="ticket in tickets" :key="ticket.name" class="hover:bg-gray-100 cursor-pointer"
                @click="goToTicket(ticket)">
                <!-- checkbox -->
                <td class="px-4 py-2 text-center align-middle w-10">
                  <input type="checkbox" :checked="selectedTickets.includes(ticket.name)"
                    @change="toggleSelection(ticket.name)" @click.stop
                    class="h-4 w-4 text-teal-600 border-gray-300 rounded focus:ring-teal-500" />
                </td>
                <!-- dynamic data cells -->
                <td v-for="col in ticketColumns" :key="col.key" :class="col.tdClass"
                  :title="typeof col.tooltip === 'function' ? col.tooltip(ticket) : col.tooltip">
                  <component v-if="col.cell" :is="{ render: () => col.cell(ticket) }" />
                  <span v-else>{{ ticket[col.key] }}</span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
    <div v-else class="mt-8 p-4 text-center text-gray-500 border border-dashed rounded-md">
      No tickets found
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, h, reactive, onMounted, onBeforeUnmount, type VNode } from "vue";
import { useRouter, useRoute } from 'vue-router'
import { toast, createResource, Input } from "frappe-ui";


/* ========= Router ========= */
const router = useRouter()
const route = useRoute()

function goToTicket(ticket) {
  router.push({
    name: 'TicketAgent',
    params: { ticketId: ticket.name },
    query: {
      fromLabel: 'Tickets Temp View',
      fromRoute: 'TicketsAgentTemp',
      fromPath: route.fullPath
    }
  })
}

/* ========= Interfaces ========= */
interface Ticket {
  name: string;
  creation: string;
  resolution: string;
  status: string;
  subject: string;
  assigned_to: string;
  assigned_to_mail: string;
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
  cell?: any;
  tooltip?: string | ((row: T) => string)

};

interface TicketsParams {
  user?: string;
  company?: string;
}

interface TicketsResponse {
  message?: any[];
  tickets?: any[];
}

//filters
interface Filters {
  id: string;
  customer: string;
  agent: string;
  status: string;
}

const filters = reactive<Filters>({
  id: "",
  customer: "",
  agent: "",
  status: "",
});

// Clear filters
function clearFilters(): void {
  filters.id = "";
  filters.customer = "";
  filters.agent = "";
  filters.status = "";
  fetchTickets.reload()
  toast.info("Filters cleared");
}


/* ========= checkbox ========= */
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

/* ======= Columns template  ========= */
const thclass =
  "px-2 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider";
const tdClass =
  "px-2 py-1 text-left whitespace-nowrap text-sm font-medium text-gray-900";

// set definition by status
const statusColors: Record<string, { bg: string; border: string }> = {
  Open: { bg: 'bg-red-100', border: 'border-red-600' },
  Replied: { bg: 'bg-blue-100', border: 'border-blue-600' },
  Resolved: { bg: 'bg-green-100', border: 'border-green-700' },
  Closed: { bg: 'bg-gray-200', border: 'border-gray-700' }
}

// sla status colors
const slaStatusColors: Record<string, { bg: string; border: string }> = {
  'First Response Due': { bg: 'bg-orange-200', border: 'border-orange-700' },
  Fulfilled: { bg: 'bg-green-100', border: 'border-green-700' },
  Paused: { bg: 'bg-blue-100', border: 'border-blue-600' },
  Failed: { bg: 'bg-red-100', border: 'border-red-600' }
}

// rendering of the column **Status**
function renderStatusCell(row: Ticket) {
  const colors = statusColors[row.status] || { bg: 'bg-gray-100', border: 'border-gray-500' }
  return h('div', { class: ['flex items-center gap-2 px-2 py-1 rounded-full w-fit', colors.bg] }, [
    h('span', { class: ['inline-block w-3 h-3 rounded-full shrink-0 border-2 bg-transparent', colors.border] }),
    h('span', { class: 'text-sm font-medium text-gray-800' }, row.status ?? '')
  ])
}

// rendering of the column **SLA Status**
function renderSlaStatusCell(row: Ticket) {
  const colors = slaStatusColors[row.sla_status] || { bg: 'bg-gray-100', border: 'border-gray-500' }
  return h('div', { class: ['flex items-center gap-2 px-2 py-1 rounded-full w-fit', colors.bg] }, [
    h('span', { class: ['inline-block w-3 h-3 rounded-full shrink-0 border-2 bg-transparent', colors.border] }),
    h('span', { class: 'text-sm font-medium text-gray-800' }, row.sla_status ?? '')
  ])
}

//render tooltip to assigned to 
function renderAssignedToCell(row: Ticket): VNode {
  const showBox = ref(false);
  const name = row.assigned_to ?? "";
  const mail = row.assigned_to_mail ?? "";

  // Cierra si se hace click fuera
  const handleClickOutside = (event: MouseEvent) => {
    const target = event.target as HTMLElement;
    if (!target.closest(`#agent-cell-${row.name}`)) {
      showBox.value = false;
    }
  };

  onMounted(() => {
    document.addEventListener("click", handleClickOutside);
  });

  onBeforeUnmount(() => {
    document.removeEventListener("click", handleClickOutside);
  });

  return h(
    "div",
    {
      id: `agent-cell-${row.name}`,
      class: "relative inline-flex items-center cursor-pointer",
      onClick: () => {
        showBox.value = !showBox.value;
      },
    },
    [
      // Texto visible
      h("span", {
        class: "truncate max-w-[180px]",
        title: name,
        innerHTML: name,
      }),

      // Caja condicional
      showBox.value &&
      h(
        "div",
        {
          class:
            "absolute bottom-full mb-2 left-1/2 -translate-x-1/2 " +
            "bg-white shadow-lg border border-gray-200 rounded-lg p-3 w-56 " +
            "transition-opacity z-10 text-gray-800 space-y-2",
        },
        [
          h("div", { class: "font-semibold text-sm" }, name),
          h(
            "a",
            {
              href: `mailto:${mail}`,
              class: "text-xs text-blue-600 hover:underline break-all",
            },
            mail || ""
          ),
          // más elementos futuros aquí...
        ]
      ),
    ]
  );
}


//structure to render cells
const ticketColumns: Column<Ticket>[] = [
  { label: "ID", key: "name", thClass: thclass, tdClass: tdClass },
  { label: "Created", key: "creation", thClass: thclass, tdClass: tdClass },
  { label: "Resolution", key: "resolution", thClass: thclass, tdClass: tdClass },
  { label: "Status", key: "status", thClass: thclass, tdClass: tdClass, cell: renderStatusCell },
  { label: "Subject", key: "subject", thClass: thclass, tdClass: tdClass + " truncate max-w-[200px]", tooltip: (row) => `Subject: ${row.subject}` },
  { label: "Assigned To", key: "assigned_to", thClass: thclass, tdClass: tdClass, cell: renderAssignedToCell },
  { label: "SLA Status", key: "sla_status", thClass: thclass, tdClass: tdClass, cell: renderSlaStatusCell },
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
    assigned_to_mail: item.assigned_to_mail || "",
    sla_status: item.sla_status || "",
    customer: item.customer || "",
    priority: item.priority || "",
    contact: item.contact || "",
    ticket_type: item.ticket_type || "",
    raised_by: item.raised_by || "",
  };
}

/* ======= status ========= */
const tickets = ref<Ticket[]>([]);
const dummyTickets: Ticket[] = [];

/* ======= Resource ========= */
const fetchTickets = createResource({
  url: "helpdesk.api.ticket.get_tickets_list",
  auto: true,
  makeParams: (): Partial<Filters> => {
    const params: Partial<Filters> = {};
    if (filters.id) params.id = filters.id;
    if (filters.customer) params.customer = filters.customer;
    if (filters.agent) params.agent = filters.agent;
    if (filters.status) params.status = filters.status;
    return params;
  },
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

/* Optional: button functions */
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

/* th,td {
  padding: 0.5rem 1.5rem;
  text-align: left;
}  */

thead th {
  background-color: #f3f3f3;
  border-bottom-width: 1px;
  border-color: #e5e7eb;
  color: #272727;
  text-transform: uppercase;

}

tbody td {
  border-bottom-width: 1px;
  border-color: #e5e7eb;
  color: #868484;
}

tbody tr:last-child td {
  border-bottom: none;
}
</style>
