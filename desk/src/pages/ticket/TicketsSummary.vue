<template>
  <div>
  <LayoutHeader>
    <template #left-header>
      <h1 class="text-lg font-semibold text-ink-gray-8">Tickets Summary</h1>
    </template>
  </LayoutHeader>

    <!-- Stats Boxes -->
    <div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4 p-4">
      <TicketStatsBox
        v-for="(box, index) in ticketStats"
        :key="index"
        :title="box.title"
        :email="box.email"
        :closed="box.closed"
        :slaRate="box.slaRate"
        :open="box.open"
        :unassigned="box.unassigned"
        :urgent="box.urgent"
        :failed="box.failed"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import TicketStatsBox from "@/components/ticket/TicketStatsBox.vue";
import { LayoutHeader } from "@/components";
// import ViewBreadcrumbs from "@/components/ViewBreadcrumbs.vue";
import { usePageMeta } from "frappe-ui";

usePageMeta(() => ({
  title: "Tickets Summary",
}));

// Data dummy
const ticketStats = [
  {
    title: "Dakar Support",
    email: "support@dakarsoftware.com",
    closed: 84,
    slaRate: 54.55,
    open: 74,
    unassigned: 7,
    urgent: 1,
    failed: 31,
  },
  {
    title: "HR Support",
    email: "hr@dakarsoftware.com",
    closed: 91,
    slaRate: 67.89,
    open: 63,
    unassigned: 2,
    urgent: 3,
    failed: 21,
  },
  {
    title: "IT Helpdesk",
    email: "it@dakarsoftware.com",
    closed: 120,
    slaRate: 72.0,
    open: 45,
    unassigned: 4,
    urgent: 2,
    failed: 10,
  },
  {
    title: "Payroll Queries",
    email: "payroll@dakarsoftware.com",
    closed: 64,
    slaRate: 80.0,
    open: 22,
    unassigned: 0,
    urgent: 0,
    failed: 5,
  },
  {
    title: "Finance Desk",
    email: "finance@dakarsoftware.com",
    closed: 103,
    slaRate: 65.2,
    open: 37,
    unassigned: 1,
    urgent: 2,
    failed: 14,
  },
];
</script>
