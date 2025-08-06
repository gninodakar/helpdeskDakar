<template>
  <div class="flex flex-col h-full">
    <LayoutHeader>
      <template #left-header>
        <h2 class="text-2xl font-bold">Ticket Billing Status</h2>
      </template>
      <template #right-header>
        <Button @click="saveChanges" variant="solid"> Save Changes </Button>
      </template>
    </LayoutHeader>

    <!-- Filters Section -->
    <div class="p-4 border-b bg-gray-50">
      <div class="flex flex-wrap gap-4">
        <div class="flex flex-col">
          <label class="text-sm text-gray-600">From Date</label>
          <input
            v-model="filters.fromDate"
            type="date"
            class="border rounded px-3 py-2"
          />
        </div>
        <div class="flex flex-col">
          <label class="text-sm text-gray-600">To Date</label>
          <input
            v-model="filters.toDate"
            type="date"
            class="border rounded px-3 py-2"
          />
        </div>
        <div class="flex flex-col">
          <label class="text-sm text-gray-600">Customer</label>
          <input
            v-model="filters.customer"
            type="text"
            placeholder="Search customer"
            class="border rounded px-3 py-2"
          />
        </div>
        <div class="flex items-end">
          <Button @click="applyFilters" variant="solid">Apply Filters</Button>
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
              {{ row.name }}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
              <input
                type="checkbox"
                :checked="row.billed"
                @change="updateBilledStatus(row.name, $event.target.checked)"
                class="h-5 w-5 text-blue-600 rounded focus:ring-blue-500"
              />
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
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from "vue";
import { FeatherIcon } from "frappe-ui";
import { LayoutHeader } from "@/components";

// Columns definition
const columns = [
  { key: "billed", label: "Billed" },
  { key: "name", label: "ID" },
  { key: "creation", label: "Created" },
  { key: "customer", label: "Customer" },
  { key: "ticket_type", label: "Ticket Type" },
  { key: "time_expended", label: "Time Expended" },
  { key: "raised_by", label: "Raised By" },
];

// Reactive data
const originalData = ref([]);
const data = ref([]);
const loading = ref(false);
const error = ref(null);
const currentPage = ref(1);
const pageSize = ref(10); // Default page size
const totalRecords = ref(0);

// Filters
const filters = ref({
  fromDate: "",
  toDate: "",
  customer: "",
});

// Initialize with dummy data
onMounted(() => {
  // Generate dummy data (increased to show pagination better)
  const dummyData = [];
  for (let i = 1; i <= 2000; i++) {
    dummyData.push({
      name: `TKT-${String(i).padStart(4, "0")}`,
      billed: Math.random() > 0.7, // 30% chance of being billed
      creation: new Date(
        Date.now() - Math.floor(Math.random() * 30) * 24 * 60 * 60 * 1000
      )
        .toISOString()
        .split("T")[0],
      customer: `Customer ${String.fromCharCode(65 + (i % 26))}`,
      ticket_type: ["Bug", "Feature", "Support", "Maintenance"][
        Math.floor(Math.random() * 4)
      ],
      time_expended: (Math.random() * 10).toFixed(1),
      raised_by: `user${Math.floor(Math.random() * 10) + 1}@company.com`,
    });
  }

  originalData.value = dummyData;
  applyFilters();
});

// Computed properties
const totalPages = computed(() => {
  return Math.ceil(totalRecords.value / pageSize.value);
});

const paginatedData = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value;
  const end = start + pageSize.value;
  return data.value.slice(start, end);
});

// Visible pages for pagination controls
const visiblePages = computed(() => {
  const pages = [];
  const maxVisiblePages = 5;
  let startPage = Math.max(
    1,
    currentPage.value - Math.floor(maxVisiblePages / 2)
  );
  let endPage = Math.min(totalPages.value, startPage + maxVisiblePages - 1);

  // Adjust if we're near the end
  if (endPage - startPage + 1 < maxVisiblePages) {
    startPage = Math.max(1, endPage - maxVisiblePages + 1);
  }

  for (let i = startPage; i <= endPage; i++) {
    pages.push(i);
  }

  return pages;
});

// Watch pageSize changes
watch(pageSize, (newPageSize) => {
  // Reset to first page when changing page size
  currentPage.value = 1;
});

// Methods
function handlePageSizeChange() {
  currentPage.value = 1; // Reset to first page when changing page size
}

function goToFirstPage() {
  currentPage.value = 1;
}

function goToPreviousPage() {
  if (currentPage.value > 1) {
    currentPage.value--;
  }
}

function goToNextPage() {
  if (currentPage.value < totalPages.value) {
    currentPage.value++;
  }
}

function goToLastPage() {
  currentPage.value = totalPages.value;
}

function applyFilters() {
  loading.value = true;

  try {
    let result = [...originalData.value];

    // Apply filters
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
    currentPage.value = 1; // Reset to first page when applying filters
  } catch (err) {
    error.value = err.message || "Failed to filter data";
  } finally {
    loading.value = false;
  }
}

function updateBilledStatus(ticketId, isBilled) {
  const ticket = data.value.find((item) => item.name === ticketId);
  if (ticket) {
    ticket.billed = isBilled;
  }

  // Also update in original data
  const originalTicket = originalData.value.find(
    (item) => item.name === ticketId
  );
  if (originalTicket) {
    originalTicket.billed = isBilled;
  }
}

function saveChanges() {
  // In a real app, you would send the updated data to your backend
  console.log(
    "Saving changes:",
    data.value.filter((item) => item.billed)
  );
  alert(
    `Saved ${data.value.filter((item) => item.billed).length} billed tickets`
  );
}

function formatDate(dateString) {
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
  background-color: #f9fafb;
  z-index: 10;
}
</style>
