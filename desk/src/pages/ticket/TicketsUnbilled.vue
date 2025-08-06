<template>
  <div class="flex flex-col h-full">
    <LayoutHeader>
      <template #left-header>
        <div class="text-lg font-medium text-gray-900">
          Ticket Billing Status
        </div>
      </template>
      <template #right-header>
        <!-- <Button @click="saveChanges" variant="solid"> Save Changes </Button> -->
      </template>
    </LayoutHeader>

    <div class="p-4 border-b bg-gray-50">
      <div class="p-4 border-b bg-gray-50">
        <div class="flex flex-wrap gap-4 items-end">
          <div class="flex flex-col">
            <label class="text-sm text-gray-600">From Date</label>
            <input
              v-model="filters.fromDate"
              type="date"
              class="border rounded px-2 py-1"
            />
          </div>

          <!-- To Date Filter -->
          <div class="flex flex-col">
            <label class="text-sm text-gray-600">To Date</label>
            <input
              v-model="filters.toDate"
              type="date"
              class="border rounded px-2 py-1"
            />
          </div>

          <!-- Customer Filter -->
          <div class="flex flex-col">
            <label class="text-sm text-gray-600">Customer</label>
            <input
              v-model="filters.customer"
              type="text"
              placeholder="Search customer"
              class="border rounded px-2 py-1"
            />
          </div>

          <!-- Action Buttons -->
          <div class="flex items-end gap-2">
            <Button @click="applyFilters" variant="solid">Apply Filters</Button>
            <Button @click="clearFilters" variant="outline"
              >Clear Filters</Button
            >
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
      <table class="min-w-full divide-y divide-gray-200">
        <thead class="bg-gray-50 sticky top-0">
          <tr>
            <th
              v-for="column in columns"
              :key="column.key"
              class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
            >
              {{ column.label }}
            </th>
          </tr>
        </thead>
        <tbody class="bg-white divide-y divide-gray-200">
          <tr
            v-for="row in paginatedData"
            :key="row.name"
            class="hover:bg-gray-50"
          >
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
              <input
                type="checkbox"
                :checked="row.billed"
                @change="
                  handleBilledStatusChange(row.name, $event.target.checked)
                "
                class="h-5 w-5 text-blue-600 rounded focus:ring-blue-500"
              />
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
              {{ row.name }}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
              {{ formatDate(row.creation) }}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
              {{ row.customer }}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
              {{ row.ticket_type }}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
              {{ row.time_expended }}h
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
              {{ row.raised_by }}
            </td>
          </tr>
        </tbody>
      </table>
      <!-- Empty State -->
      <div
        v-if="paginatedData.length === 0"
        class="flex flex-col items-center justify-center p-12 text-gray-500"
      >
        <p>No tickets found</p>
      </div>
    </div>
    <!-- Pagination Controls -->
    <div
      v-if="paginatedData.length > 0"
      class="border-t px-4 py-3 flex items-center justify-between"
    >
      <div class="flex items-center gap-4">
        <div class="text-sm text-gray-700">
          Showing {{ (currentPage - 1) * pageSize + 1 }} to
          {{ Math.min(currentPage * pageSize, totalRecords) }} of
          {{ totalRecords }} results
        </div>
        <div class="flex items-center gap-2">
          <label class="text-sm text-gray-700">Rows per page:</label>
          <select
            v-model="pageSize"
            @change="handlePageSizeChange"
            class="border rounded px-2 py-1 text-sm pr-8"
          >
            <option :value="10">10</option>
            <option :value="20">20</option>
            <option :value="50">50</option>
          </select>
        </div>
      </div>
      <div class="flex items-center gap-2">
        <div class="text-sm text-gray-700">
          Page {{ currentPage }} of {{ totalPages }}
        </div>
        <div class="flex gap-1">
          <Button
            @click="goToFirstPage"
            :disabled="currentPage === 1"
            variant="outline"
            size="sm"
          >
            <FeatherIcon name="chevrons-left" class="h-4 w-4" />
          </Button>
          <Button
            @click="goToPreviousPage"
            :disabled="currentPage === 1"
            variant="outline"
            size="sm"
          >
            <FeatherIcon name="chevron-left" class="h-4 w-4" />
          </Button>
          <Button
            v-for="page in visiblePages"
            :key="page"
            @click="currentPage = page"
            :variant="currentPage === page ? 'solid' : 'outline'"
            size="sm"
          >
            {{ page }}
          </Button>
          <Button
            @click="goToNextPage"
            :disabled="currentPage === totalPages"
            variant="outline"
            size="sm"
          >
            <FeatherIcon name="chevron-right" class="h-4 w-4" />
          </Button>
          <Button
            @click="goToLastPage"
            :disabled="currentPage === totalPages"
            variant="outline"
            size="sm"
          >
            <FeatherIcon name="chevrons-right" class="h-4 w-4" />
          </Button>
        </div>
      </div>
    </div>

    <!-- Confirmation Dialog -->
    <div
      v-if="showConfirmDialog"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
    >
      <div class="bg-white rounded-lg p-6 w-96">
        <h3 class="text-lg font-medium mb-4">Confirm Billing Status Change</h3>
        <p class="mb-6">
          Are you sure you want to mark ticket
          <strong>{{ confirmDialogData.ticketId }}</strong> as
          <strong>{{
            confirmDialogData.newStatus ? "billed" : "unbilled"
          }}</strong
          >?
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
import { FeatherIcon, toast } from "frappe-ui";
import { LayoutHeader } from "@/components";

// Define interfaces
interface Ticket {
  name: string;
  billed: boolean;
  creation: string;
  customer: string;
  ticket_type: string;
  time_expended: string;
  raised_by: string;
}

interface Column {
  key: string;
  label: string;
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

// Columns definition with type
const columns: Column[] = [
  { key: "billed", label: "Billed" },
  { key: "name", label: "ID" },
  { key: "creation", label: "Created" },
  { key: "customer", label: "Customer" },
  { key: "ticket_type", label: "Ticket Type" },
  { key: "time_expended", label: "Time Expended" },
  { key: "raised_by", label: "Raised By" },
];

// Reactive data with types
const originalData: Ref<Ticket[]> = ref([]);
const data: Ref<Ticket[]> = ref([]);
const loading = ref(false);
const error = ref<string | null>(null);
const currentPage = ref(1);
const pageSize = ref(10);
const totalRecords = ref(0);

// Confirmation dialog
const showConfirmDialog = ref(false);
const confirmDialogData: Ref<ConfirmDialogData> = ref({
  ticketId: null,
  newStatus: null,
});

// Clear filters
function clearFilters(): void {
  filters.value = {
    fromDate: "",
    toDate: "",
    customer: "",
  };
  applyFilters();
  toast.info("Filters cleared");
}

// Filters
const filters: Ref<Filters> = ref({
  fromDate: "",
  toDate: "",
  customer: "",
});

// Initialize with data from Frappe
onMounted(async () => {
  await fetchDataFromFrappe();
});

async function fetchDataFromFrappe(): Promise<void> {
  loading.value = true;
  error.value = null;

  try {
    const response = await fetch(
      "/api/method/helpdesk.api.ticket.get_unbilled_tickets",
      {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
          // Add authentication headers if is necessary
          // "Authorization": "token your_api_key:your_api_secret",
        },
      }
    );

    const result = await response.json();

    if (result.message) {
      const frappeData: Ticket[] = result.message.map((item: any) => ({
        name: item.name,
        billed: item.ticket_billed || false,
        creation: item.creation ? item.creation.split(" ")[0] : "",
        customer: item.customer || "",
        ticket_type: item.ticket_type || "",
        time_expended: item.time_expended || "00:00",
        raised_by: item.raised_by || "",
      }));

      originalData.value = frappeData;
      applyFilters();
    } else {
      //dummy data for testing
      // generateDummyData();
    }
  } catch (err: any) {
    error.value = err.message || "Failed to fetch data from Frappe";
    console.error("Frappe API Error:", err);
    //test data
    //generateDummyData();
  } finally {
    loading.value = false;
  }
}

// Generate dummy data with types
// function generateDummyData(): void {
//   const dummyData: Ticket[] = [];
//   for (let i = 1; i <= 2000; i++) {
//     dummyData.push({
//       name: `TKT-${String(i).padStart(4, "0")}`,
//       billed: Math.random() > 0.7,
//       creation: new Date(
//         Date.now() - Math.floor(Math.random() * 30) * 24 * 60 * 60 * 1000
//       )
//         .toISOString()
//         .split("T")[0],
//       customer: `Customer ${String.fromCharCode(65 + (i % 26))}`,
//       ticket_type: ["Bug", "Feature", "Support", "Maintenance"][
//         Math.floor(Math.random() * 4)
//       ],
//       time_expended: (Math.random() * 10).toFixed(1),
//       raised_by: `user${Math.floor(Math.random() * 10) + 1}@company.com`,
//     });
//   }
//   originalData.value = dummyData;
//   applyFilters();
// }

// Computed properties with types
const totalPages = computed<number>(() => {
  return Math.ceil(totalRecords.value / pageSize.value);
});

const paginatedData = computed<Ticket[]>(() => {
  const start = (currentPage.value - 1) * pageSize.value;
  const end = start + pageSize.value;
  return data.value.slice(start, end);
});

const visiblePages = computed<number[]>(() => {
  const pages: number[] = [];
  const maxVisiblePages = 5;
  let startPage = Math.max(
    1,
    currentPage.value - Math.floor(maxVisiblePages / 2)
  );
  let endPage = Math.min(totalPages.value, startPage + maxVisiblePages - 1);
  if (endPage - startPage + 1 < maxVisiblePages) {
    startPage = Math.max(1, endPage - maxVisiblePages + 1);
  }
  for (let i = startPage; i <= endPage; i++) {
    pages.push(i);
  }
  return pages;
});

// Watch pageSize changes
watch(pageSize, (newPageSize: number) => {
  currentPage.value = 1;
});

// Methods with types
function handlePageSizeChange(): void {
  currentPage.value = 1;
}

function goToFirstPage(): void {
  currentPage.value = 1;
}

function goToPreviousPage(): void {
  if (currentPage.value > 1) {
    currentPage.value--;
  }
}

function goToNextPage(): void {
  if (currentPage.value < totalPages.value) {
    currentPage.value++;
  }
}

function goToLastPage(): void {
  currentPage.value = totalPages.value;
}

function applyFilters(): void {
  loading.value = true;
  try {
    let result: Ticket[] = [...originalData.value];
    if (filters.value.fromDate) {
      result = result.filter((item) => item.creation >= filters.value.fromDate);
    }
    if (filters.value.toDate) {
      result = result.filter((item) => item.creation <= filters.value.toDate);
    }
    if (filters.value.customer) {
      const searchTerm = filters.value.customer.toLowerCase();
      result = result.filter((item) =>
        item.customer.toLowerCase().includes(searchTerm)
      );
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

// Handle checkbox change with confirmation
function handleBilledStatusChange(ticketId: string, newStatus: boolean): void {
  // Show confirmation dialog
  confirmDialogData.value = {
    ticketId,
    newStatus,
  };
  showConfirmDialog.value = true;
}

async function cancelStatusChange(): Promise<void> {
  showConfirmDialog.value = false;
  await fetchDataFromFrappe();
}

async function confirmStatusChange(): Promise<void> {
  const { ticketId, newStatus } = confirmDialogData.value;

  if (ticketId === null || newStatus === null) {
    return;
  }

  showConfirmDialog.value = false;

  try {
    const response = await fetch(
      "/api/method/helpdesk.api.ticket.update_ticket_billing_status",
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-Frappe-CSRF-Token": window.csrf_token || "",
        },
        body: JSON.stringify({
          ticket_name: ticketId,
          billed_status: newStatus ? 1 : 0,
        }),
      }
    );

    const result = await response.json();

    if (!response.ok) {
      throw new Error(result.message || "Failed to update ticket");
    }

    updateBilledStatus(ticketId, newStatus);
    toast.success(
      `Ticket ${ticketId} marked as ${newStatus ? "billed" : "unbilled"}`
    );
    await fetchDataFromFrappe();
  } catch (err: any) {
    console.error("Error updating ticket:", err);
    toast.error(
      `Failed to update ticket ${ticketId}: ${err.message || "Unknown error"}`
    );
    updateBilledStatus(ticketId, !newStatus);
  }
}

function updateBilledStatus(ticketId: string, isBilled: boolean): void {
  const ticket = data.value.find((item) => item.name === ticketId);
  if (ticket) {
    ticket.billed = isBilled;
  }

  const originalTicket = originalData.value.find(
    (item) => item.name === ticketId
  );
  if (originalTicket) {
    originalTicket.billed = isBilled;
  }
}

function saveChanges(): void {
  console.log(
    "Saving changes:",
    data.value.filter((item) => item.billed)
  );
  alert(
    `Saved ${data.value.filter((item) => item.billed).length} billed tickets`
  );
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
  color: rgb(255, 255, 255);
  z-index: 10;
  border-right: 0.2rem solid;
}
</style>
