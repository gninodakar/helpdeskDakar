<template>
  <div>
    <LayoutHeader>
      <template #left-header>
        <ViewBreadcrumbs
          label="Tickets Summary"          
        />
      </template> 
    </LayoutHeader> 
    <!-- Stats Box -->
    <div class="p-4">
      <TicketStatsBox
        title="Dakar Support"
        email="support@dakarsoftware.com"
        :closed="84"
        :slaRate="54.55"
        :open="74"
        :unassigned="7"
        :urgent="1"
        :failed="31"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import TicketStatsBox from "@/components/ticket/TicketStatsBox.vue";
import { LayoutHeader } from "@/components";
import ViewBreadcrumbs from "@/components/ViewBreadcrumbs.vue";
import { usePageMeta } from "frappe-ui";

usePageMeta(() => {
  return {
    title: "Tickets Summary",
  };
});
</script>
