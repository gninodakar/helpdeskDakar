<template>
  <div class="flex flex-col h-full">
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

    <div class="p-4 border-b bg-gray-50">
      <div class="p-4 border-b bg-gray-50">
        <div class="flex flex-wrap gap-4 items-end">
          <!-- From Date Filter -->
          <div class="flex flex-col">
            <label class="text-sm text-gray-600 mb-1">From Date</label>
            <DatePicker v-model="filters.fromDate" placeholder="Select from date"
              class="w-48 border border-gray-300 rounded-md" />
          </div>
          <!-- To Date Filter -->
          <div class="flex flex-col">
            <label class="text-sm text-gray-600 mb-1">To Date</label>
            <DatePicker v-model="filters.toDate" placeholder="Select to date"
              class="w-48 border border-gray-300 rounded-md" />
          </div>
          <!-- Customer Filter -->
          <div class="flex flex-col">
            <label class="text-sm text-gray-600 mb-1">Customer</label>
            <Input v-model="filters.customer" placeholder="Search customer" class="w-64" />
          </div>

          <!-- Action Buttons -->
          <div class="flex items-end gap-2">
            <Button @click="applyFilters" variant="solid">Apply Filters</Button>
            <Button @click="clearFilters" variant="outline">Clear Filters</Button>
          </div>

          <!-- Right-aligned refresh button -->
          <div class="ml-auto">
            <Button variant="ghost" @click="refreshScreen">
              <FeatherIcon name="refresh-ccw" class="h-5 w-5" />
            </Button>
          </div>
        </div>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="flex-1 flex items-center justify-center">
      <div class="text-gray-500">Loading...</div>
    </div>
    <!-- Error State -->
    <div v-else-if="error" class="flex-1 flex items-center justify-center">
      <div class="text-red-500">Error: {{ error }}</div>
    </div>

    <!-- Data Table -->
    <div v-else class="flex-1 overflow-auto">
      <table class="min-w-full table-fixed divide-y divide-gray-200">
        <thead class="bg-gray-50 sticky top-0">
          <tr>
            <th v-for="col in columns" :key="col.key" :style="{ width: col.widthRem + 'rem' }"
              class="px-2 py-2 text-center text-xs font-medium text-gray-100 uppercase tracking-wider">
              {{ col.label }}
            </th>
          </tr>
        </thead>

        <tbody class="bg-white divide-y divide-gray-200">
          <tr v-for="row in paginatedData" :key="row.name" class="hover:bg-gray-50 cursor-pointer" @click="$router.push({
            name: 'TicketAgent',
            params: { ticketId: row.name },
            query: { fromLabel: 'Tickets Temp View', fromRoute: 'TicketsAgentTemp', fromPath: route.fullPath }
          })">
            <!-- Checkbox -->
            <td :style="colW('checkbox')" class="px-2 py-1 whitespace-nowrap text-sm text-gray-900">
              <input type="checkbox" :checked="row.billed"
                @change="handleBilledStatusChange(row.name, $event.target.checked)"
                class="h-5 w-5 text-blue-600 rounded focus:ring-blue-500" />
            </td>

            <!-- Ticket ID -->
            <td :style="colW('name')" class="px-2 py-1 whitespace-nowrap text-sm text-gray-900">
              <RouterLink :to="{
                name: 'TicketAgent',
                params: { ticketId: row.name },
                query: { fromLabel: 'Tickets Temp View', fromRoute: 'TicketsAgentTemp', fromPath: route.fullPath }
              }"
                class="text-blue-600 hover:underline font-medium block overflow-hidden text-ellipsis whitespace-nowrap"
                :title="row.name">
                {{ row.name }}
              </RouterLink>
            </td>

            <!-- Created -->
            <td :style="colW('creation')" class="px-2 py-1 whitespace-nowrap text-sm text-gray-900">
              <div class="overflow-hidden text-ellipsis whitespace-nowrap" :title="formatDate(row.creation)">
                {{ formatDate(row.creation) }}
              </div>
            </td>

            <!-- Status (dot + text, left aligned) -->
            <td :style="colW('status')" class="px-2 py-1 whitespace-nowrap text-sm text-gray-900">
              <div class="flex items-center gap-2 overflow-hidden">
                <span class="inline-block w-3 h-3 rounded-full shrink-0" :class="{
                  'bg-red-500': row.status === 'Open',
                  'bg-blue-500': row.status === 'Replied',
                  'bg-green-600': row.status === 'Resolved',
                  'bg-gray-800': row.status === 'Closed'
                }"></span>
                <span class="text-gray-600 font-medium overflow-hidden text-ellipsis whitespace-nowrap"
                  :title="row.status">
                  {{ row.status }}
                </span>
              </div>
            </td>

            <!-- Subject -->
            <td :style="colW('subject')" class="px-2 py-1 whitespace-nowrap text-sm text-gray-900 overflow-hidden">
              <div class="w-full overflow-hidden text-ellipsis whitespace-nowrap" :title="row.subject">
                {{ row.subject }}
              </div>
            </td>

            <!-- Assigned To -->
            <td :style="colW('assigned_to')" class="px-2 py-1 whitespace-nowrap text-sm text-gray-900">
              <div class="overflow-hidden text-ellipsis whitespace-nowrap" :title="row.assigned_to">
                {{ row.assigned_to }}
              </div>
            </td>

            <!-- Response By -->
            <td :style="colW('response_by')" class="px-2 py-1 whitespace-nowrap text-sm text-gray-900">
              <div class="overflow-hidden text-ellipsis whitespace-nowrap" :title="row.response_by">
                {{ row.response_by }}
              </div>
            </td>

            <!-- SLA Status -->
            <td :style="colW('sla_status')" class="px-2 py-1 whitespace-nowrap text-sm text-gray-900">
              <div class="px-1 py-1">
                <Badge variant="outline" size="sm" :theme="slaStatusTheme[row.sla_status] || 'gray'"
                  :label="row.sla_status" class="px-3 py-3" />
              </div>
            </td>


            <!-- Customer -->
            <td :style="colW('customer')" class="px-2 py-1 whitespace-nowrap text-sm text-gray-900">
              <div class="overflow-hidden text-ellipsis whitespace-nowrap" :title="row.customer">
                {{ row.customer }}
              </div>
            </td>

            <!-- Priority -->
            <td :style="colW('priority')" class="px-2 py-1 whitespace-nowrap text-sm text-gray-900">
              <div class="overflow-hidden text-ellipsis whitespace-nowrap" :title="row.priority">
                {{ row.priority }}
              </div>
            </td>

            <!-- Contact -->
            <td :style="colW('contact')" class="px-2 py-1 whitespace-nowrap text-sm text-gray-900">
              <div class="overflow-hidden text-ellipsis whitespace-nowrap" :title="row.contact">
                {{ row.contact }}
              </div>
            </td>

            <!-- Rating -->
            <td :style="colW('rating')" class="px-2 py-1 whitespace-nowrap text-sm text-gray-900">
              <Rating v-model="row.rating" :readonly="true" size="md" />
            </td>

            <!-- Ticket Type -->
            <td :style="colW('ticket_type')" class="px-2 py-1 whitespace-nowrap text-sm text-gray-900">
              <div class="overflow-hidden text-ellipsis whitespace-nowrap" :title="row.ticket_type">
                {{ row.ticket_type }}
              </div>
            </td>

            <!-- Raised By -->
            <td :style="colW('raised_by')" class="px-2 py-1 whitespace-nowrap text-sm text-gray-900">
              <div class="overflow-hidden text-ellipsis whitespace-nowrap" :title="row.raised_by">
                {{ row.raised_by }}
              </div>
            </td>
          </tr>
        </tbody>
      </table>

      <!-- Empty State -->
      <div v-if="paginatedData.length === 0" class="flex flex-col items-center justify-center p-12 text-gray-500">
        <p>No tickets found</p>
      </div>
    </div>

    <!-- Pagination Controls -->
    <div v-if="paginatedData.length > 0" class="border-t px-4 py-3 flex items-center justify-between">
      <div class="flex items-center gap-4">
        <div class="text-sm text-gray-700">
          Showing {{ (currentPage - 1) * pageSize + 1 }} to
          {{ Math.min(currentPage * pageSize, totalRecords) }} of
          {{ totalRecords }} results
        </div>
        <div class="flex items-center gap-2">
          <label class="text-sm text-gray-700">Rows per page:</label>
          <select v-model="pageSize" @change="handlePageSizeChange" class="border rounded px-2 py-1 text-sm pr-8">
            <option :value="10">10</option>
            <option :value="20">20</option>
            <option :value="50">50</option>
          </select>
        </div>
      </div>
      <div class="flex items-center gap-2">
        <div class="text-sm text-gray-700">Page {{ currentPage }} of {{ totalPages }}</div>
        <div class="flex gap-1">
          <Button @click="goToFirstPage" :disabled="currentPage === 1" variant="outline" size="sm">
            <FeatherIcon name="chevrons-left" class="h-4 w-4" />
          </Button>
          <Button @click="goToPreviousPage" :disabled="currentPage === 1" variant="outline" size="sm">
            <FeatherIcon name="chevron-left" class="h-4 w-4" />
          </Button>
          <Button v-for="page in visiblePages" :key="page" @click="currentPage = page"
            :variant="currentPage === page ? 'solid' : 'outline'" size="sm">
            {{ page }}
          </Button>
          <Button @click="goToNextPage" :disabled="currentPage === totalPages" variant="outline" size="sm">
            <FeatherIcon name="chevron-right" class="h-4 w-4" />
          </Button>
          <Button @click="goToLastPage" :disabled="currentPage === totalPages" variant="outline" size="sm">
            <FeatherIcon name="chevrons-right" class="h-4 w-4" />
          </Button>
        </div>
      </div>
    </div>

    <!-- Confirmation Dialog -->
    <div v-if="showConfirmDialog" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg p-6 w-96">
        <h3 class="text-lg font-medium mb-4">Confirm Billing Status Change</h3>
        <p class="mb-6">
          Are you sure you want to mark ticket <strong>{{ confirmDialogData.ticketId }}</strong> as
          <strong>{{ confirmDialogData.newStatus ? "billed" : "unbilled" }}</strong>?
        </p>
        <div class="flex justify-end gap-3">
          <Button @click="cancelStatusChange" variant="outline">Cancel</Button>
          <Button @click="confirmStatusChange" variant="solid">Confirm</Button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch, Ref } from "vue";
import { useRoute } from "vue-router";
import { Badge, Rating, FeatherIcon, toast, Input, DatePicker } from "frappe-ui";
import { LayoutHeader } from "@/components";


const slaStatusTheme = {
  'First Response Due': 'orange',
  'Paused': 'blue',
  'Fulfilled': 'green'
}


interface Ticket {
  name: string;
  billed?: boolean;
  creation: string;
  status?: string;
  subject?: string;
  assigned_to?: string;
  response_by?: string;
  sla_status?: string;
  customer?: string;
  priority?: string;
  contact?: string;
  rating?: number | string;
  ticket_type?: string;
  raised_by?: string;
}

interface Column {
  key: string;
  label: string;
  widthRem: number;
}

interface Filters {
  fromDate: string;
  toDate: string;
  customer: string;
}

interface ConfirmDialogData {
  ticketId: string | null;
  newStatus: boolean | null;
}

/** ───────── Column ───────── **/
const columns: Column[] = [
  { label: "", key: "checkbox", widthRem: 1 },
  { label: "ID", key: "name", widthRem: 2 },
  { label: "Created", key: "creation", widthRem: 4 },
  { label: "Status", key: "status", widthRem: 4 },
  { label: "Subject", key: "subject", widthRem: 8 },
  { label: "Assigned To", key: "assigned_to", widthRem: 4 },
  { label: "Response By", key: "response_by", widthRem: 4 },
  { label: "SLA Status", key: "sla_status", widthRem: 4 },
  { label: "Customer", key: "customer", widthRem: 4 },
  { label: "Priority", key: "priority", widthRem: 4 },
  { label: "Contact", key: "contact", widthRem: 4 },
  { label: "Rating", key: "rating", widthRem: 4 },
  { label: "Ticket Type", key: "ticket_type", widthRem: 4 },
  { label: "Raised By", key: "raised_by", widthRem: 4 }
];

// helper to apply width to tds without relying on array order
const colW = (key: string) => {
  const w = columns.find(c => c.key === key)?.widthRem ?? 12;
  return { width: `${w}rem` };
};

const originalData: Ref<Ticket[]> = ref([]);
const data: Ref<Ticket[]> = ref([]);
const loading = ref(false);
const error = ref<string | null>(null);
const currentPage = ref(1);
const pageSize = ref(10);
const totalRecords = ref(0);
const route = useRoute();

/** Refresh */
function refreshScreen(): void {
  fetchDataFromFrappe();
}

/** Confirm dialog */
const showConfirmDialog = ref(false);
const confirmDialogData: Ref<ConfirmDialogData> = ref({ ticketId: null, newStatus: null });

/** Filters */
const filters: Ref<Filters> = ref({ fromDate: "", toDate: "", customer: "" });

function clearFilters(): void {
  filters.value = { fromDate: "", toDate: "", customer: "" };
  applyFilters();
  toast.info("Filters cleared");
}

/** Fetch */
onMounted(async () => {
  await fetchDataFromFrappe();
});

async function fetchDataFromFrappe(): Promise<void> {
  loading.value = true;
  error.value = null;
  try {
    const response = await fetch("/api/method/helpdesk.api.ticket.get_tickets_list", {
      method: "GET",
      headers: { "Content-Type": "application/json" }
    });
    const result = await response.json();

    if (result.message) {
      const frappeData: Ticket[] = result.message.map((item: any) => ({
        name: item.name,
        creation: item.creation ? item.creation.split(" ")[0] : "",
        status: item.status || "",
        subject: item.subject || "",
        assigned_to: item.assigned_to || "",
        response_by: item.response_by || "",
        sla_status: item.sla_status || "",
        customer: item.customer || "",
        priority: item.priority || "",
        contact: item.contact || "",
        rating: Math.round((Number(item.rating) * 10) / 2) ?? 0,
        ticket_type: item.ticket_type || "",
        raised_by: item.raised_by || "",
        billed: item.ticket_billed ?? false
      }));
      originalData.value = frappeData;
      console.log("Frappe Data:", frappeData);

      applyFilters();
    }
  } catch (err: any) {
    error.value = err.message || "Failed to fetch data from Frappe";
    console.error("Frappe API Error:", err);
  } finally {
    loading.value = false;
  }
}

/** Paging & compute */
const totalPages = computed<number>(() => Math.ceil(totalRecords.value / pageSize.value));
const paginatedData = computed<Ticket[]>(() => {
  const start = (currentPage.value - 1) * pageSize.value;
  return data.value.slice(start, start + pageSize.value);
});
const visiblePages = computed<number[]>(() => {
  const pages: number[] = [];
  const max = 5;
  let start = Math.max(1, currentPage.value - Math.floor(max / 2));
  let end = Math.min(totalPages.value, start + max - 1);
  if (end - start + 1 < max) start = Math.max(1, end - max + 1);
  for (let i = start; i <= end; i++) pages.push(i);
  return pages;
});
watch(pageSize, () => (currentPage.value = 1));

/** Methods */
function handlePageSizeChange(): void { currentPage.value = 1; }
function goToFirstPage(): void { currentPage.value = 1; }
function goToPreviousPage(): void { if (currentPage.value > 1) currentPage.value--; }
function goToNextPage(): void { if (currentPage.value < totalPages.value) currentPage.value++; }
function goToLastPage(): void { currentPage.value = totalPages.value; }

function applyFilters(): void {
  loading.value = true;
  try {
    let result: Ticket[] = [...originalData.value];
    if (filters.value.fromDate) result = result.filter(i => i.creation >= filters.value.fromDate);
    if (filters.value.toDate) result = result.filter(i => i.creation <= filters.value.toDate);
    if (filters.value.customer) {
      const q = filters.value.customer.toLowerCase();
      result = result.filter(i => (i.customer || "").toLowerCase().includes(q));
    }
    data.value = result;
    totalRecords.value = result.length;
    currentPage.value = 1;
  } catch (err: any) {
    error.value = err.message || "Failed to filter data";
  } finally {
    loading.value = false;
  }
}

function handleBilledStatusChange(ticketId: string, newStatus: boolean): void {
  confirmDialogData.value = { ticketId, newStatus };
  showConfirmDialog.value = true;
}

async function cancelStatusChange(): Promise<void> {
  showConfirmDialog.value = false;
  await fetchDataFromFrappe();
}

async function confirmStatusChange(): Promise<void> {
  const { ticketId, newStatus } = confirmDialogData.value;
  if (ticketId === null || newStatus === null) return;
  showConfirmDialog.value = false;

  try {
    const response = await fetch("/api/method/helpdesk.api.ticket.update_ticket_billing_status", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-Frappe-CSRF-Token": (window as any).csrf_token || ""
      },
      body: JSON.stringify({ ticket_name: ticketId, billed_status: newStatus ? 1 : 0 })
    });
    const result = await response.json();
    if (!response.ok) throw new Error(result.message || "Failed to update ticket");
    updateBilledStatus(ticketId, newStatus);
    toast.success(`Ticket ${ticketId} marked as ${newStatus ? "billed" : "unbilled"}`);
    await fetchDataFromFrappe();
  } catch (err: any) {
    console.error("Error updating ticket:", err);
    toast.error(`Failed to update ticket ${ticketId}: ${err.message || "Unknown error"}`);
    updateBilledStatus(ticketId, !newStatus);
  }
}

function updateBilledStatus(ticketId: string, isBilled: boolean): void {
  const t = data.value.find(i => i.name === ticketId);
  if (t) t.billed = isBilled;
  const o = originalData.value.find(i => i.name === ticketId);
  if (o) o.billed = isBilled;
}

function formatDate(dateString: string): string {
  return new Date(dateString).toLocaleDateString();
}
</script>


<style scoped>
table {
  border-collapse: collapse;
}

th {
  position: sticky;
  top: 0;
  background-color: #9fa2a59a;
  color: #ffffff;
  z-index: 10;
  border-right: 0.1rem solid;
}

tbody tr {
  height: 1.5rem;
  /* ~56px */
}
</style>
