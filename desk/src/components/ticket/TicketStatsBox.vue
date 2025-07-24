<template>
  <div class="rounded-lg border shadow-sm p-4 bg-white dark:bg-gray-900 max-w-md">
    <div class="flex items-center justify-between mb-4">
      <div>
        <h2 class="text-lg font-semibold text-gray-900 dark:text-white">{{ title }}</h2>
        <p class="text-sm text-gray-500 dark:text-gray-400">
          <a :href="`mailto:${email}`" class="hover:underline">
            {{ email }}
          </a>
        </p>
        <!-- button -->
        <a
        href="/helpdesk/tickets"
        target="_blank"
        class="inline-block mt-2 text-sm px-3 py-1 bg-blue-500 text-white rounded hover:bg-blue-600 transition"
        >
        View Details
        </a>
      </div>
      <div class="text-right">
        <p class="text-sm text-gray-500">Tickets Closed</p>
        <p class="text-lg font-semibold text-gray-900 dark:text-white">{{ closed }}</p>
        <p class="text-sm text-gray-500 mt-1">SLA Success Rate</p>
        <p class="text-lg font-semibold text-gray-900 dark:text-white">{{ slaRate }} %</p>
      </div>
    </div>
    <div class="grid grid-cols-4 text-center border-t pt-4 text-sm text-gray-600 dark:text-gray-300">
      <div>
        <div class="text-xl font-bold text-primary">{{ open }}</div>
        <div class="mt-1">Open</div>
      </div>
      <div>
        <div class="text-xl font-bold">{{ unassigned }}</div>
        <div class="mt-1">Unassigned</div>
      </div>
      <div>
        <div class="text-xl font-bold text-red-600">{{ urgent }}</div>
        <div class="mt-1">Urgent</div>
      </div>
      <div>
        <div class="text-xl font-bold text-red-500">{{ failed }}</div>
        <div class="mt-1">Failed</div>
      </div>
    </div>
  </div>
</template>


<script setup lang="ts">
defineProps<{
  title: string;
  email: string;
  closed: number;
  slaRate: number;
  open: number;
  unassigned: number;
  urgent: number;
  failed: number;
}>();
</script>
