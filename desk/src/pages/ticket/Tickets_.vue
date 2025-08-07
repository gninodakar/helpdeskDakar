<template>
  <div>
    <LayoutHeader>
      <template #left-header>
        <ViewBreadcrumbs
          label="Tickets"
          :route-name="isCustomerPortal ? 'TicketsCustomer' : 'TicketsAgent'"
          :current-view="currentView"
        />
      </template>
      <template #right-header>
        <RouterLink
          :to="{ name: isCustomerPortal ? 'TicketNew' : 'TicketAgentNew' }"
        >
          <Button label="Create" theme="gray" variant="solid">
            <template #prefix>
              <LucidePlus class="h-4 w-4" />
            </template>
          </Button>
        </RouterLink>
      </template>
    </LayoutHeader>

    <!-- 🔍 Filtros -->
    <div class="mb-4 flex flex-wrap gap-4 items-end px-4">
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1"
          >Assign To</label
        >
        <Input v-model="filterAssignedTo" placeholder="Email" class="w-64" />
      </div>
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1"
          >Date Created</label
        >
        <DateRangePicker v-model="filterDateRange" class="w-72" />
      </div>
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1"
          >Status</label
        >
        <select
          v-model="filterStatus"
          class="w-40 border rounded px-2 py-1 text-sm"
        >
          <option value="">All</option>
          <option v-for="status in statusOptions" :key="status" :value="status">
            {{ status }}
          </option>
        </select>
      </div>
      <div class="flex gap-2">
        <Button @click="fetchTickets" label="Search" theme="gray" />
        <Button @click="exportToExcel" label="Export" theme="gray" />
      </div>
    </div>

    <!-- 📋 Tabla personalizada -->
    <div class="px-4">
      <p class="text-sm text-gray-500">
        Registros cargados: {{ tickets.length }}
      </p>
      <table class="min-w-full border border-gray-300 mt-4">
        <thead>
          <tr class="bg-gray-100">
            <th class="text-left p-2 border">Name</th>
            <th class="text-left p-2 border">Subject</th>
            <th class="text-left p-2 border">Status</th>
            <th class="text-left p-2 border">Created</th>
            <th class="text-left p-2 border">Assigned To</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="ticket in tickets" :key="ticket.name">
            <td class="p-2 border">{{ ticket.name }}</td>
            <td class="p-2 border">{{ ticket.subject }}</td>
            <td class="p-2 border">{{ ticket.status }}</td>
            <td class="p-2 border">{{ ticket.creation }}</td>
            <td class="p-2 border">{{ ticket._assign ?? "—" }}</td>
          </tr>
        </tbody>
      </table>

      <div
        v-if="tickets.length === 0"
        class="text-center text-sm text-gray-500 mt-8"
      >
        No tickets found.
      </div>

      <!-- Paginación -->
      <div class="flex justify-between mt-4 text-sm">
        <Button
          :disabled="start === 0"
          @click="
            start = Math.max(0, start - limit);
            fetchTickets();
          "
          label="Previous"
        />
        <Button
          :disabled="!hasMore"
          @click="
            start += limit;
            fetchTickets();
          "
          label="Next"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { LayoutHeader } from "@/components";
import ViewBreadcrumbs from "@/components/ViewBreadcrumbs.vue";
import { Input, DateRangePicker, Button } from "frappe-ui";
import { call } from "frappe-ui";
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";
import { dayjs } from "@/dayjs";
import { isCustomerPortal } from "@/utils";

const router = useRouter();

const currentView = ref({
  label: "Tickets",
});

const tickets = ref([]);
const filterAssignedTo = ref("");
const filterDateRange = ref([]);
const filterStatus = ref("");
const statusOptions = ref<string[]>([]);

const start = ref(0);
const limit = 20;
const hasMore = ref(false);

async function fetchTickets() {
  const filters: any[] = [];

  if (filterAssignedTo.value.trim()) {
    filters.push(["_assign", "like", `%${filterAssignedTo.value.trim()}%`]);
  }

  const [from, to] = filterDateRange.value ?? [];
  if (from && to) {
    filters.push([
      "creation",
      "between",
      [dayjs(from).format("YYYY-MM-DD"), dayjs(to).format("YYYY-MM-DD")],
    ]);
  }

  if (filterStatus.value) {
    filters.push(["status", "=", filterStatus.value]);
  }

  try {
    console.log("🚀 Enviando filtros:", filters); // 👈 VERIFICA QUE LOS FILTROS ESTÁN CORRECTOS

    const response = await call("frappe.client.get_list", {
      doctype: "HD Ticket",
      fields: ["name", "subject", "status", "creation", "_assign"],
      filters: filters.length ? filters : undefined,
      order_by: "creation desc",
      limit_start: start.value,
      limit_page_length: limit,
    });

    console.log("✅ Respuesta completa:", response); // 👈 MUESTRA TODO EL OBJETO

    const message = response?.message;
    if (Array.isArray(message)) {
      tickets.value = message;
      hasMore.value = message.length === limit;

      if (statusOptions.value.length === 0) {
        const uniqueStatuses = Array.from(
          new Set(message.map((t) => t.status))
        );
        statusOptions.value = uniqueStatuses;
      }
    } else {
      tickets.value = [];
      hasMore.value = false;
    }
  } catch (err) {
    console.error("❌ Error al cargar tickets:", err);
    tickets.value = [];
    hasMore.value = false;
  }
}

function goToTicket(name: string) {
  router.push({
    name: isCustomerPortal.value ? "TicketCustomer" : "TicketAgent",
    params: { ticketId: name },
  });
}

function exportToExcel() {
  const filters: any[] = [];

  if (filterAssignedTo.value.trim()) {
    filters.push(["_assign", "like", `%${filterAssignedTo.value.trim()}%`]);
  }

  const [from, to] = filterDateRange.value ?? [];
  if (from && to) {
    filters.push([
      "creation",
      "between",
      [dayjs(from).format("YYYY-MM-DD"), dayjs(to).format("YYYY-MM-DD")],
    ]);
  }

  if (filterStatus.value) {
    filters.push(["status", "=", filterStatus.value]);
  }

  const encodedFilters = encodeURIComponent(JSON.stringify(filters));
  const fields = encodeURIComponent(
    JSON.stringify(["name", "subject", "status", "creation", "_assign"])
  );

  const url = `/api/method/frappe.desk.reportview.export_query?doctype=HD Ticket&file_format_type=Excel&filters=${encodedFilters}&fields=${fields}&order_by=creation desc&start=${start.value}&page_length=${limit}&view=Report`;

  window.open(url, "_blank");
}

onMounted(fetchTickets);
</script>
